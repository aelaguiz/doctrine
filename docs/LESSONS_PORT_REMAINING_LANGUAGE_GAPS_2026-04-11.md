---
title: "Lessons port remaining language gaps and Doctrine-native closure"
date: 2026-04-11
status: proposal
owners: [aelaguiz]
reviewers: []
related:
  - docs/DOCTRINE_FEATURE_REQUESTS_FROM_LESSONS_SYMBOLIC_PORT_2026-04-11.md
  - docs/DOCTRINE_NATIVE_SOLUTIONS_FROM_LESSONS_SYMBOLIC_PORT_2026-04-11.md
  - docs/PHASE4_REVIEW_ROUTE_ONLY_GROUNDING_CONTROL_PLANE_COMPLETION_2026-04-11.md
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
---

# Why this doc exists

The Lessons symbolic port exposed real pressure on Doctrine, but the right
response is not to turn Lessons into a product namespace inside the language.

Lessons is a proving ground.
Doctrine should respond by strengthening framework-level surfaces that will stay
useful across many multi-stage pipelines, not by adding narrow one-off knobs for
one project.

This doc therefore does three jobs:

- say which asks are already solved by Doctrine or are not really Doctrine gaps
- state the remaining framework needs in Doctrine-native terms
- lock the clean final language direction with concrete authored examples and
  rendered intent

# Doctrine standards this doc follows

These are the language conventions the remaining work should continue to honor:

- Keys are structural identity. Titles are human-facing runtime language.
- Typed declarations own semantics. Markdown rendering is a consequence of typed
  structure, not the source of truth.
- Shared workflow truth belongs in declarations, not repeated lane-local prose.
- New surfaces should lower into Doctrine's existing owner paths such as
  `review`, `workflow` law, `schema`, and `output`, not create a shadow control
  plane.
- The compiler should fail loudly when selection, currentness, routing, or
  invalidation is ambiguous.
- Lessons-specific workflow pressure may motivate a feature, but the surface
  itself should remain generic and reusable.

# What should come off the gap list

Several earlier Lessons complaints should not stay in the "remaining Doctrine
gaps" bucket.

## Already solved by shipped Doctrine

### Readable owner identity

Doctrine already has the right identity split for concrete owners:

- concrete agents can carry a human title
- readable refs can project the authored title while keeping the structural key
  available
- render profiles can decide how owner identity appears in emitted markdown

Why this is already solved:

- it removes the need for an agent-specific `display:` escape hatch
- route labels, readback, and shared prose can stay readable without giving up
  structural identity
- example `62_identity_titles_keys_and_wire` is the proof surface

### Readable enum labels without leaking wire strings

Doctrine already supports the required enum split:

- enum member identity stays typed
- human-facing titles can render in markdown
- `wire` stays available for host-facing serialization

Why this is already solved:

- readable runtime prose no longer has to expose host strings
- host I/O can stay stable without polluting human-facing markdown
- example `62_identity_titles_keys_and_wire` is also the proof surface here

### Serious review substrate

Doctrine already supports the core reviewer semantics that Lessons needs:

- `review` as a typed first-class declaration
- review contracts backed by either `workflow` or `schema`
- exact gate export from the selected contract surface
- multi-subject review plus `subject_map`
- carried `active_mode` and `trigger_reason`
- mode-local currentness and route coupling
- shared review scaffolding through reusable inherited review structure

Why this is already solved:

- the framework can already model real reviewer turns without pushing verdict,
  failing gates, current truth, and next-owner routing into prose conventions
- examples `43`, `46`, `47`, `48`, `49`, and `57` already prove this substrate

### Route-only substrate and inventory substrate

Doctrine already has the two key prerequisites for route-only and restart
control-plane work:

- workflow law already supports `current none`, `stop`, guarded readback, and
  explicit reroute
- `schema` already owns reusable `artifacts:` and `groups:`

Why this is already solved:

- route-only behavior already exists as an honest semantic pattern even before a
  dedicated `route_only` declaration is layered on top
- reusable downstream surface inventories already have one correct typed home
- examples `30`, `40`, `41`, `42`, and `63` are the current proof ladder

## Not actually framework gaps

Some Lessons audit findings were real, but they do not require new Doctrine
language:

- route-label interpolation drift was a bug or implementation gap, not a missing
  semantic family
- comment readback shaping belongs to render policy and lowering, not a new
  control-plane concept
- local Lessons route contradictions and metadata-lane ownership mistakes are
  project prompt design problems, not Doctrine language defects

The remaining framework work is therefore narrower than "make Doctrine readable"
or "add review support somehow."

# Remaining Doctrine-native language gaps

Two framework-level needs still deserve a clean final language story.

## Gap 1: one critic surface with case-selected exact review law

### The real framework need

Some reviewer roles are structurally one role but semantically many review
modes.

The framework needs to express all of this at once:

- one reviewer identity
- one shared review scaffold
- many typed modes
- a different reviewed subject per mode
- a different contract per mode
- exact failing gates from the selected real contract
- mode-local currentness and next-owner routing

Doctrine already has most of this substrate.
What still needs a clean final surface is the last mile: how one typed critic
selects the exact subject, contract, checks, and outcome law for one mode
without either duplicating many near-identical reviews or flattening everything
into one giant manually branched wrapper.

### The Doctrine-native answer

The clean answer is explicit case-selected review structure inside `review` or
`review_family`.

That means:

- one typed `selector`
- one exhaustive `cases:` block
- each case owns its own `subject`, `contract`, `checks`, `on_accept`, and
  `on_reject`
- shared reviewer scaffolding stays on the family root
- `contract.*` inside a case resolves only against that case's contract
- failing-gate output uses the exact selected contract gates, not a generic
  wrapper namespace

This is better than dynamic `selected_contract.*` projection because Doctrine
already prefers explicit typed branches with explicit consequences.

### Illustrative authored shape

```prompt
enum CriticMode: "Critic Mode"
    dossier: "Dossier Review"
        wire: "dossier"

    copy: "Copy Review"
        wire: "copy"

review_family ArtifactCritic: "Artifact Critic"
    comment_output: CriticComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner
        active_mode: active_mode

    handoff_first: "Handoff First"
        block "Producer handoff is incomplete." when ProducerHandoff.incomplete

    selector:
        mode active_mode = ReviewState.active_mode as CriticMode

    cases:
        dossier: "Dossier Review"
            when CriticMode.dossier
            subject: PlanningDossier
            contract: DossierReviewContract

            checks:
                reject contract.citation_grounding when ReviewState.citations_missing
                reject contract.scope_boundary when ReviewState.scope_drifted
                accept "The dossier review contract passes." when contract.passes

            on_accept:
                current artifact PlanningDossier via CriticComment.current_artifact
                carry active_mode = CriticMode.dossier
                route "Accepted dossier review returns to Dossier Author." -> DossierAuthor

            on_reject:
                current artifact PlanningDossier via CriticComment.current_artifact
                carry active_mode = CriticMode.dossier
                route "Rejected dossier review returns to Dossier Author." -> DossierAuthor

        copy: "Copy Review"
            when CriticMode.copy
            subject: DraftCopy
            contract: CopyReviewContract

            checks:
                reject contract.wording_precision when ReviewState.wording_missing
                reject contract.metadata_alignment when ReviewState.metadata_conflict
                accept "The copy review contract passes." when contract.passes

            on_accept:
                current artifact DraftCopy via CriticComment.current_artifact
                carry active_mode = CriticMode.copy
                route "Accepted copy review returns to Copy Editor." -> CopyEditor

            on_reject:
                current artifact DraftCopy via CriticComment.current_artifact
                carry active_mode = CriticMode.copy
                route "Rejected copy review returns to Copy Editor." -> CopyEditor
```

### How this should render

When the active mode is dossier, the emitted review should read like a dossier
review, not like a generic wrapper over an abstract selected contract:

```markdown
## Artifact Critic

Selected review mode: Dossier Review.

### Dossier Review

Review subject: Planning Dossier.
Shared review contract: Dossier Review Contract.

#### Checks

Reject: Citation Grounding.
Reject: Scope Boundary.
Accept only if the dossier review contract passes.

#### If Rejected

Current artifact: Planning Dossier.
Route: Rejected dossier review returns to Dossier Author.
```

When the active mode is copy, the same review surface should render copy-owned
gate names and copy-owned routing instead:

```markdown
## Artifact Critic

Selected review mode: Copy Review.

### Copy Review

Review subject: Draft Copy.
Shared review contract: Copy Review Contract.

#### Checks

Reject: Wording Precision.
Reject: Metadata Alignment.
Accept only if the copy review contract passes.

#### If Rejected

Current artifact: Draft Copy.
Route: Rejected copy review returns to Copy Editor.
```

### Why this is the right framework answer

- It keeps the reviewer as one real typed surface instead of a bag of duplicated
  near-reviews.
- It preserves exact gate ownership from the selected contract.
- It keeps selection, currentness, and routing in one semantic place.
- It generalizes to any multi-mode reviewer chain, not only Lessons.

### Current status

This gap is no longer an open design mystery.
The current Phase 4 branch already has grammar, model, parser, and compiler
scaffolding for `review_family`, `selector`, and `cases`.

The remaining job is to make this the one honest language story across examples,
live docs, and verification, not to keep debating whether a dynamic contract
projection surface would be cleaner.

## Gap 2: schema-owned restart surfaces that invalidate concretely

### The real framework need

Many workflows have stable restart boundaries:

- one upstream artifact changes
- a reusable downstream set stops being current
- the next owner must see the concrete affected surfaces immediately

The language should let authors state that restart boundary once and then reuse
it in real control-plane law.

The weak alternatives are both bad:

- vague bucket names that hide the real affected artifacts
- repeated manual member lists that drift over time

### The Doctrine-native answer

The clean answer is not a new invalidation-only `artifact_set` type.

The clean answer is:

- `schema.artifacts` names the concrete durable surfaces
- `schema.groups` names reusable bundles of those surfaces
- workflow law can `invalidate SchemaRef.groups.group_key`
- runtime readback expands the group into the concrete member artifacts

That keeps restart truth in the same typed inventory surface that already owns
artifact structure.

### Illustrative authored shape

```prompt
schema BuildSurfaceSchema: "Build Surface Schema"
    artifacts:
        scenario_set: "Scenario Set"
            ref: ScenarioSet

        publish_manifest: "Publish Manifest"
            ref: PublishManifest

        release_notes: "Release Notes"
            ref: ReleaseNotes

    groups:
        downstream_rebuild: "Downstream Rebuild"
            scenario_set
            publish_manifest
            release_notes

workflow PlanningTurn: "Planning Turn"
    law:
        when PlanningDocument.changed:
            invalidate BuildSurfaceSchema.groups.downstream_rebuild via CoordinationHandoff.invalidations
            stop "Downstream build surfaces are no longer current."
            route "Return the same issue to Build Coordinator for rebuild coordination." -> BuildCoordinator
```

### How this should render

The authored group name is reusable structure.
The emitted control-plane readback should stay concrete:

```markdown
### Invalidations

- Scenario Set is no longer current.
- Publish Manifest is no longer current.
- Release Notes are no longer current.

### Route

- Return the same issue to Build Coordinator for rebuild coordination.
```

### Why this is the right framework answer

- Restart boundaries become typed shared truth instead of repeated prose.
- Runtime readback stays operational and concrete.
- The same inventory can later support review, planning, and audit surfaces.
- The feature is generic for any staged artifact pipeline, not just Lessons.

### Current status

This is also no longer an open architectural question.
The current Phase 4 branch already resolves `schema.groups.*` through workflow
law invalidation and expands group members in rendered control-plane surfaces.

The remaining requirement is to make that canonical everywhere instead of
leaving older docs or examples to imply that restart groups are only static
inventory labels.

# How the dedicated Phase 4 surfaces should fit the framework

Phase 4 may still ship dedicated declaration families such as `review_family`,
`route_only`, and `grounding`, but they should follow one hard rule:

- they are declaration-level convenience and reuse surfaces
- they are not separate semantic owner paths

That means:

- `review_family` should stay review-shaped and reuse the same field-binding,
  verdict, currentness, and route semantics as `review`
- `route_only` should lower to ordinary workflow-law truth with `current none`,
  `stop`, guarded readback, and explicit routing
- `grounding` should package a reusable protocol or policy, not invent a second
  source of domain truth beside inputs, outputs, and workflow law

This is the most Doctrine-native outcome because it keeps one semantic system
and allows nicer authoring surfaces on top of it.

The current Phase 4 branch is already directionally correct here:

- `route_only` resolves through the workflow owner path
- `grounding` resolves through the workflow owner path
- case-selected review stays inside the review owner path

That architectural choice should be preserved.

# Recommended language direction

The clean final Doctrine answer to the Lessons signal is:

- keep the already-solved identity and rendering asks off the remaining-gap list
- standardize case-selected typed review structure as the canonical answer for
  one reviewer with many exact review modes
- standardize `schema.groups.*` invalidation with concrete rendered expansion as
  the canonical answer for reusable restart surfaces
- keep dedicated Phase 4 families as wrappers over existing semantics, not a
  second control plane

If Doctrine does that, Lessons becomes what it should be here: a demanding use
case that helped the framework become more explicit, more typed, and more
readable, without turning the language into a bundle of Lessons-specific escape
hatches.

# Checks

No code or examples changed in this pass. I did not run `make verify-examples`.
This is a docs-only language-direction update grounded in the current repo docs
and the in-flight Phase 4 implementation in `doctrine/`.
