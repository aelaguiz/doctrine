---
title: "Doctrine-native solutions from the Lessons symbolic port"
date: 2026-04-11
status: proposal
owners: [aelaguiz]
reviewers: []
related:
  - docs/archive/DOCTRINE_FEATURE_REQUESTS_FROM_LESSONS_SYMBOLIC_PORT_2026-04-11.md
  - docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md
  - docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md
  - docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
---

# TL;DR

This doc answers the problem statements in
[DOCTRINE_FEATURE_REQUESTS_FROM_LESSONS_SYMBOLIC_PORT_2026-04-11.md](DOCTRINE_FEATURE_REQUESTS_FROM_LESSONS_SYMBOLIC_PORT_2026-04-11.md),
but it does not accept the proposed feature shapes at face value.

The clean Doctrine answer is:

- strengthen Doctrine's existing `key` versus human-title split instead of
  adding one-off display fields
- select typed review cases, not anonymous dynamic contracts
- reuse planned inventory and control-plane surfaces instead of inventing vague
  invalidation buckets

If Doctrine takes the Lessons signal seriously, the resulting language should
feel more like Doctrine becoming fully itself, not like Doctrine picking up a
pile of local escape hatches.

# Why this doc exists

The Lessons port found real needs. The earlier feature-request doc captured
those needs honestly, but it still framed them mostly as direct extensions of
current shipped surfaces.

That is not the only way to respond.

Doctrine already has a clear design center:

- keys are structural identities
- human-facing titles and prose are authored deliberately
- control-plane truth stays typed and explicit
- readable markdown is a rendering consequence, not the semantic source of
  truth

So the right question is not "How do we add four tactical knobs?"

The right question is "What would the most Doctrine-native version of each ask
look like if we were designing the language on purpose?"

# Design stance

Three design moves cover almost all of what Lessons is asking for:

1. Bring the `key` versus human-title split to every declaration family that
   humans need to mention in emitted prose.
2. Treat mode-dependent behavior as explicit typed cases, not as one
   declaration projecting a hidden selected sub-declaration.
3. Let inventory declarations name reusable concrete surface groups, then let
   control-plane law consume those groups directly.

Those moves line up with the planned phase docs:

- [../01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md](../01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md)
  establishes the core rule that keys are law while titles are prose.
- [../02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md](../02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md)
  introduces first-class inventory structure through `schema`.
- [../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md](../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md)
  makes typed readable output render beautifully through `properties`,
  `render_profile`, and semantic lowering.
- [../04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md](../04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md)
  is the natural landing zone for case-driven review and reusable
  control-plane integration.

# Phase-fit summary

| Lessons problem | Most Doctrine-native answer | Planned-feature fit | Already solved by planned phases? |
| --- | --- | --- | --- |
| Human-readable concrete owners | Give `agent` the same key/title split as other titled declarations, plus explicit title/key projections in prose and properties | Phase 1 principle, phase 3 rendering polish | No |
| Human-readable enum state | Make enum members titled choices with separate wire values for host I/O | Phase 1 principle, phase 3 rendering polish | No |
| One multi-mode critic with exact gates | Add explicit review cases selected by mode inside `review` or `review_family` | Phase 4 review/control-plane work, phase 3 readable lowering | Partially |
| Concrete invalidation clusters | Extend `schema` into reusable artifact inventories and named surface groups that workflow law can invalidate | Phase 2 inventory work, phase 4 control-plane integration, phase 3 readback polish | Partially |

# 1. Human-readable concrete owners

## Problem

Lessons needs to mention concrete owners in many shared places:

- route labels
- handoff comments
- stop-line prose
- output readback
- shared role-home scaffolding

Today the structured choice is the raw declaration name. That is precise, but
it leaves emitted runtime prose sounding like compiler identifiers.

## Doctrine-native answer

Do not add a special agent-only `display:` escape hatch.

Instead, make concrete agents fully participate in Doctrine's existing
identity model:

- the key remains the structural identity
- the agent also owns a human-facing title
- authored prose can project either the title or the key explicitly
- phase-3 `properties` can render owner identity cleanly anywhere the control
  plane needs a readable field

In other words, the beautiful answer is not "agents need a display string."
The beautiful answer is "agents are title-bearing declarations too."

## Illustrative authored shape

```prompt
agent LessonsProjectLead: "Lessons Project Lead"
    role: "Own unresolved routing, route repair, and blocked follow-up."

agent SectionDossierEngineer: "Section Dossier Engineer"
    role: "Own section dossier work and dossier repair."

workflow RouteOnlyRepair: "Route-Only Repair"
    "If the earliest clear owner is still unclear, {{LessonsProjectLead:title}} keeps the issue."

    law:
        route "Hand the same issue to {{SectionDossierEngineer:title}}." -> SectionDossierEngineer

output RouteRepairComment: "Route Repair Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    readback: "Readback"
        properties:
            next_owner: "{{SectionDossierEngineer:title}}"
            next_owner_key: "{{SectionDossierEngineer:key}}"
```

## How this should render

```markdown
If the earliest clear owner is still unclear, Lessons Project Lead keeps the issue.

Route:
- Hand the same issue to Section Dossier Engineer.

## Readback

- Next Owner: Section Dossier Engineer
- Next Owner Key: `SectionDossierEngineer`
```

## Why this solves the Lessons issue

- Shared owner mentions stay drift-proof because they still resolve through the
  declaration graph.
- Runtime prose reads like normal English.
- Structural identity remains available explicitly when a machine-oriented or
  debugging surface needs it.
- The same owner can now appear cleanly in route labels, comment properties,
  and reusable scaffolding without any hard-coded prose copies.

## Why this is more Doctrine-native than the original request

The earlier request asked for a new `display:` field on agents. That would
work, but it would make agents the odd declaration family with a bespoke
human-label mechanism.

Doctrine already wants one general rule: keys are structural, titles are
human-facing. The right move is to make agents honor that same rule directly.

## Planned-feature fit

- [../01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md](../01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md)
  already states the governing principle that keys are law and titles are
  prose. This solution is the direct extension of that rule to `agent`.
- [../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md](../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md)
  would make the readback especially nice through `properties` and
  `render_profile`.

Explicit status: this is **not already solved** by the planned phases. The
phase docs support the direction, but no planned phase currently gives
concrete agents first-class titles.

# 2. Human-readable enum state without leaking wire values

## Problem

Lessons wants some enum members to stay stable and external-safe at the host
boundary while still rendering as normal human language in emitted markdown.

The current shipped enum model makes one authored string do both jobs. That is
simple, but it forces a bad trade:

- readable prose values become poor wire values
- or good wire values leak into human-facing conditions

## Doctrine-native answer

Do not add a one-off enum-member `display:` field while leaving the semantic
model unchanged.

Instead, treat an enum member as a titled choice with an optional external
wire value:

- member key: Doctrine identity
- member title: readable runtime label
- member wire value: host-facing serialization

Then the compiler can decode host inputs through the wire value, but all
Doctrine law, review, and rendering can operate on the typed member identity
and its human title.

## Illustrative authored shape

```prompt
enum ProjectLeadRouteOnlyNextOwner: "Project Lead Route-Only Next Owner"
    section_dossier_engineer: "Section Dossier Engineer"
        wire: "section-dossier-engineer"

    lessons_section_architect: "Lessons Section Architect"
        wire: "lessons-section-architect"

input RouteFacts: "Route Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host facts that say which next owner is currently selected."

agent LessonsProjectLead: "Lessons Project Lead"
    role: "Own unresolved route repair."

agent SectionDossierEngineer: "Section Dossier Engineer"
    role: "Own section dossier work."

workflow RouteOnlyTurn: "Route-Only Turn"
    law:
        match RouteFacts.next_owner as ProjectLeadRouteOnlyNextOwner:
            ProjectLeadRouteOnlyNextOwner.section_dossier_engineer:
                route "When next owner is {{ProjectLeadRouteOnlyNextOwner.section_dossier_engineer:title}}, hand the same issue to {{SectionDossierEngineer:title}}." -> SectionDossierEngineer
```

## How this should render

```markdown
When next owner is Section Dossier Engineer, hand the same issue to Section Dossier Engineer.
```

The host can still pass `"section-dossier-engineer"` at the boundary, but that
wire string no longer has to leak into the readable runtime brief.

## Why this solves the Lessons issue

- Host and JSON stability stay intact.
- Doctrine conditions stay typed and explicit.
- Readable branches, properties, and comments can show human titles instead of
  schema-looking strings.
- Large route-only and control-plane families stop forcing authors to choose
  between machine safety and readable emitted prose.

## Why this is more Doctrine-native than the original request

The earlier request asked for a readable-display surface on enum members. The
more Doctrine-native answer is broader: enum members should have the same
structural-versus-human split that other declaration families have, plus an
explicit wire codec for I/O boundaries.

That makes the human label a first-class semantic property of the member, not
just a rendering override.

## Planned-feature fit

- [../01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md](../01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md)
  provides the design principle: structural keys and human-facing titles are
  different jobs.
- [../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md](../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md)
  would improve how enum-driven branches and properties render once members
  have distinct titles.

Explicit status: this is **not already solved** by the planned phases. The
planned phases improve readable rendering, but they do not yet split enum
member identity, human title, and wire encoding.

# 3. One multi-mode critic with exact gates and no generic wrapper contract

## Problem

Lessons wants one real critic surface that can do all of this at once:

- carry typed review mode
- select a different reviewed subject by mode
- select a different shared contract by mode
- emit the exact failing gates from the selected contract
- keep the readback honest without falling back to generic wrapper gates

The earlier request framed this as "select a contract by mode, then project its
gates." That points at the real pain, but it is still shaped like a patch on
the current single-contract surface.

## Doctrine-native answer

Do not make review semantics depend on an anonymous `selected_contract.*`
projection.

Instead, add explicit typed review cases inside a `review` or `review_family`.
Each case owns:

- the selecting condition or mode tag
- the subject
- the contract
- its local review checks
- its currentness and route consequences

The active case is selected once. After that, Doctrine is no longer operating
on an abstract selected contract. It is operating on one ordinary concrete
review case with one ordinary concrete contract.

That preserves exact gate ownership without inventing generic wrapper gates or
copy-pasting giant `match` trees by hand.

## Illustrative authored shape

```prompt
enum CriticReviewMode: "Critic Review Mode"
    dossier: "Dossier Review"
        wire: "dossier"

    copy: "Copy Review"
        wire: "copy"

review_family LessonsArtifactCritic: "Lessons Artifact Critic"
    selector:
        mode active_review_mode = ReviewState.active_review_mode as CriticReviewMode

    cases:
        dossier: "Dossier Review"
            when CriticReviewMode.dossier
            subject: SectionDossier
            contract: SectionDossierReviewContract

            checks:
                reject contract.handoff_truth when ProducerHandoff.names_wrong_current_artifact
                reject contract.citation_grounding when ReviewState.citations_missing
                accept "The dossier review contract passes." when contract.passes

            on_accept:
                current artifact SectionDossier via LessonsCriticComment.current_artifact
                carry active_mode = CriticReviewMode.dossier
                route "Accepted dossier review returns to {{SectionDossierEngineer:title}}." -> SectionDossierEngineer

            on_reject:
                current artifact SectionDossier via LessonsCriticComment.current_artifact
                carry active_mode = CriticReviewMode.dossier
                route "Rejected dossier review returns to {{SectionDossierEngineer:title}}." -> SectionDossierEngineer

        copy: "Copy Review"
            when CriticReviewMode.copy
            subject: LessonManifest
            contract: CopyReviewContract

            checks:
                reject contract.wording_precision when ReviewState.wording_missing
                reject contract.metadata_alignment when ReviewState.metadata_conflict
                accept "The copy review contract passes." when contract.passes

            on_accept:
                current artifact LessonManifest via LessonsCriticComment.current_artifact
                carry active_mode = CriticReviewMode.copy
                route "Accepted copy review returns to {{CopyEngineer:title}}." -> CopyEngineer

            on_reject:
                current artifact LessonManifest via LessonsCriticComment.current_artifact
                carry active_mode = CriticReviewMode.copy
                route "Rejected copy review returns to {{CopyEngineer:title}}." -> CopyEngineer

review LessonsCriticReview[LessonsArtifactCritic]: "Lessons Review"
    comment_output: LessonsCriticComment

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner
        active_mode: active_mode
```

## How this should render

When the active mode is dossier, the emitted review readback should look like a
normal dossier review, not like a generic wrapper around an abstract contract:

```markdown
## Review Mode

Dossier Review

## Failure Detail

- Failing Gates:
  - Handoff Truth
  - Citation Grounding

## Next Owner

Section Dossier Engineer
```

When the active mode is copy, the same surface should render copy-specific gate
names instead:

```markdown
## Review Mode

Copy Review

## Failure Detail

- Failing Gates:
  - Wording Precision
  - Metadata Alignment

## Next Owner

Copy Engineer
```

## Why this solves the Lessons issue

- One critic surface can stay typed, shared, and durable.
- Gate names stay owned by the original shared contract.
- The case selection explains both subject selection and contract selection in
  one place.
- The emitted markdown reads like the selected real review, not like a local
  adapter layer.
- Authors stop duplicating `match` trees just to keep the rendered gate names
  honest.

## Why this is more Doctrine-native than the original request

The earlier request asked for dynamic contract projection. The more native
Doctrine move is to make mode-dependent review behavior an explicit first-class
case structure.

Doctrine likes explicit branches with explicit consequences. Review cases keep
that same design language:

- explicit selector
- explicit case ownership
- explicit contract
- explicit currentness
- explicit route

That is much closer to Doctrine's workflow and review law style than
introducing a hidden dynamic gate namespace.

## Planned-feature fit

- [../04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md](../04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md)
  already plans `review_family`, schema-backed contracts, and control-plane
  convergence. This proposal is the natural extension of that phase.
- [03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md](03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md)
  would let each selected case lower into clean typed markdown readback without
  bespoke formatting logic.

Explicit status: this is **partially solved** by the planned phases. Phase 4
already gives the reusable review scaffold and exact gate export from one
contract. What is still missing is first-class case selection that can bind the
subject, contract, and outcome law together.

# 4. Concrete invalidation clusters instead of vague restart buckets

## Problem

Lessons wants to say something stronger than "some downstream work is
invalidated" without copy-pasting the same file list everywhere.

That is a real control-plane need. The emitted runtime brief should tell the
next owner exactly which downstream surfaces are no longer current.

The earlier request framed this as a standalone `artifact_set`. That would
work, but it misses a more elegant reuse path already implied by Doctrine's
planned inventory work.

## Doctrine-native answer

Do not solve this with an invalidation-only bucket type.

Instead, extend `schema` into the place where reusable concrete artifact
inventories live, then let workflow law target named groups inside that
inventory.

That gives Doctrine one reusable concept:

- `schema.artifacts`: addressable named concrete surfaces
- `schema.groups`: named bundles of those surfaces for control-plane use
- workflow law can invalidate a group
- renderers expand the group into concrete members instead of printing only the
  bucket name

This keeps the inventory typed, addressable, and reusable across outputs,
reviews, and later control-plane surfaces.

## Illustrative authored shape

```prompt
schema LessonBuildSurfaces: "Lesson Build Surfaces"
    artifacts:
        lesson_situations: "Lesson Situations"
            ref: lessons.contracts.lesson_situations.LessonSituationsContract

        lesson_manifest: "Lesson Manifest"
            ref: lessons.contracts.materialization.LessonManifestContract

    groups:
        downstream_rebuild: "Downstream Lesson Build"
            lesson_situations
            lesson_manifest

workflow LessonPlanWorkflow: "Lesson Plan Workflow"
    law:
        when LessonPlan.changed:
            invalidate LessonBuildSurfaces.groups.downstream_rebuild via coordination_handoff.invalidations
            stop "Downstream lesson build surfaces are no longer current."
            route "Return the same issue to {{LessonsProjectLead:title}} for rebuild coordination." -> LessonsProjectLead
```

## How this should render

The control-plane readback should expand the group into the real concrete
surfaces:

```markdown
### Invalidations

- Lesson Situations (`lesson_root/_authoring/LESSON_SITUATIONS.md`) is no longer current.
- Lesson Manifest (`lesson_root/_authoring/lesson_manifest.json`) is no longer current.

### Route

- Return the same issue to Lessons Project Lead for rebuild coordination.
```

The group name remains useful for authored reuse, but the runtime brief stays
concrete.

## Why this solves the Lessons issue

- Restart boundaries become explicit without repeating the member list in every
  workflow.
- Invalidation readback stays concrete and operational.
- The same inventory can later support other control-plane consumers, not just
  invalidation.
- Authors get one durable home for downstream artifact structure instead of a
  scattering of local bucket names.

## Why this is more Doctrine-native than the original request

The earlier request asked for a typed `artifact_set`. The more Doctrine-native
answer is to let the planned inventory declaration own reusable concrete
surface groups and let control-plane law consume those groups.

That avoids a one-purpose type and instead deepens a declaration family
Doctrine already wants: `schema` as reusable inventory structure.

## Planned-feature fit

- [../02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md](../02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md)
  already establishes `schema` as the home for reusable inventory and gate
  structure.
- [../04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md](../04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md)
  already plans control-plane convergence, which is the right place for group
  invalidation consumption.
- [../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md](../03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md)
  would let expanded invalidation readback render tersely or richly depending
  on profile.

Explicit status: this is **partially solved** by the planned phases. Phase 2
already gives the inventory direction, and phase 4 gives the control-plane
landing zone. What is still missing is a first-class way to declare reusable
artifact groups and ask invalidation readback to expand them into concrete
members.

# Recommended language direction

If Doctrine follows the Lessons signal in the cleanest possible way, the next
language wave should bias toward these general upgrades:

- titled agents with explicit title/key projection
- titled enum members with separate wire encoding
- case-driven review selection instead of dynamic contract projection
- schema-owned concrete artifact inventories and named control-plane groups

That is a better long-term language than four isolated "display" or "set"
features. It stays compositional, typed, and render-friendly, which is exactly
the point of building Doctrine in the first place.

# Checks

No code or examples changed in this pass. I did not run `make verify-examples`.
This is a docs-only design proposal grounded in the shipped language docs, the
Lessons feature-request document, and the current phased-plan set.
