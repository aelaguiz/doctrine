---
title: "Doctrine feature requests from the Lessons symbolic port"
date: 2026-04-11
status: proposal
owners: [aelaguiz]
reviewers: []
related:
  - docs/archive/lessons_symbolic_port_issue_classification_2026-04-11.md
  - ../paperclip_agents/docs/LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md
  - ../paperclip_agents/docs/LESSONS_SYMBOLIC_DOCTRINE_PORT_RENDERED_OUTPUT_AUDIT_2026-04-11.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/REVIEW_SPEC.md
  - examples/17_agent_mentions/cases.toml
  - examples/20_authored_prose_interpolation/cases.toml
  - examples/36_invalidation_and_rebuild/cases.toml
  - examples/39_guarded_output_sections/cases.toml
  - examples/42_route_only_handoff_capstone/cases.toml
  - examples/47_review_multi_subject_mode_and_trigger_carry/cases.toml
  - examples/49_review_capstone/cases.toml
---

# TL;DR

- The Lessons symbolic port surfaced one real Doctrine bug and several local
  Lessons prompt or design gaps.
- This doc is not the bug list. It turns the remaining real language asks into
  explicit feature requests for Doctrine.
- The common theme is simple: keep structured Doctrine surfaces readable enough
  that large prompt families do not have to choose between drift-proof
  structure and human-readable emitted `AGENTS.md`.
- The route-label interpolation leak should still be fixed as a bug. It is not
  part of this feature-request list.

# Why this doc exists

The Lessons port did not just find one broken code path. It also found a few
places where Doctrine is behaving exactly as shipped, but the shipped surface
is still weaker than what a large, readability-sensitive prompt family wants.

Those asks should not be smuggled in as bug reports. They should be written
down as feature requests with clear examples, clear boundaries, and a clear
reason for existing.

The bar here is:

- ask for a Doctrine feature only when the current language is honestly too
  weak for the intended structured authoring pattern
- keep local Lessons prompt mistakes out of the language backlog
- show the exact authored shape we want, why it matters, and what it would let
  a real prompt family do

# Non-goal

This doc does not ask Doctrine to absorb every Lessons readability mistake.

It does not ask for:

- automatic rescue of vague local prompt design
- automatic repair of overly generic review contracts
- automatic narrowing of overly broad shared output contracts
- silent interpretation changes that would break shipped examples

## Explicitly excluded bug fix

The workflow-law route-label interpolation leak is a real Doctrine bug and
should be fixed directly. It is not a feature request. See
`docs/archive/lessons_symbolic_port_issue_classification_2026-04-11.md`.

# Feature requests

## 1. Add an explicit human-display surface for concrete agents

### Current limitation

Today `{{AgentRef}}` and `{{AgentRef:name}}` render the raw declaration name.
That is documented and tested behavior. It is useful for structural identity,
but it is not enough when emitted runtime prose needs a human-facing owner name
such as `Lessons Project Lead`.

Right now authors have to choose one of two bad options:

- keep structured refs and accept emitted names like `LessonsProjectLead`
- hard-code human prose like `Lessons Project Lead` and lose drift protection

### What we want

Add one explicit, opt-in display surface for concrete agents. The existing
`{{AgentRef}}` and `{{AgentRef:name}}` behavior should stay unchanged for
backward compatibility.

Illustrative shape:

```prompt
agent LessonsProjectLead:
    display: "Lessons Project Lead"
    role: "You are Lessons Project Lead. You hand work to the right specialist..."

workflow RouteOnlyTurns: "Routing-Only Turns"
    "If the next owner is still unclear, {{lessons.common.agents.LessonsProjectLead:display}} keeps the issue."

    law:
        route "Hand the same issue to {{lessons.common.agents.SectionDossierEngineer:display}}." -> lessons.common.agents.SectionDossierEngineer
```

### Why we want it

Large prompt families need shared owner mentions in many places:

- route labels
- handoff comments
- stop-line prose
- shared role-home scaffolding
- shared output contracts

Those mentions need to stay structured so ownership does not drift. But the
emitted runtime brief also needs to read like normal English.

Concrete agent display text is a stable enough concept to deserve its own
surface. It is not the same thing as full `role:` prose.

### What it would allow

- Keep owner mentions drift-proof in shared prompt owners without falling back
  to hard-coded strings.
- Emit `Lessons Project Lead` instead of `LessonsProjectLead` in runtime prose.
- Preserve the current shipped meaning of `{{AgentRef}}` and `{{AgentRef:name}}`
  while adding a separate readable surface for large prompt families.

### Boundaries

- Do not reinterpret `:name` to mean `role:` text.
- Do not treat full `role:` prose as the display label.
- Do not auto-generate display text from CamelCase names behind the author's
  back.

## 2. Add an explicit readable-display surface for enum members

### Current limitation

Doctrine currently renders enum-driven conditions honestly, but authors have to
reuse the same member string for both machine identity and human-readable
emitted prose.

That is workable for small enums, but it breaks down when the machine-safe
value is intentionally schema-like:

```prompt
enum ProjectLeadRouteOnlyNextOwner: "Project Lead Route-Only Next Owner"
    section_dossier_engineer: "section-dossier-engineer"
    lessons_section_architect: "lessons-section-architect"
```

This is not a Doctrine bug. It is exactly what the authored enum says. But it
pushes authors toward either ugly emitted conditions or weaker local workarounds.

### What we want

Add one explicit display label for enum members so machine-safe values and
readable emitted text do not have to be the same thing.

Illustrative shape:

```prompt
enum ProjectLeadRouteOnlyNextOwner: "Project Lead Route-Only Next Owner"
    section_dossier_engineer:
        value: "section-dossier-engineer"
        display: "Section Dossier Engineer"

    lessons_section_architect:
        value: "lessons-section-architect"
        display: "Lessons Section Architect"
```

Then readable markdown for a branch could say something like:

```text
When next owner is Section Dossier Engineer, hand the same issue to Lessons Project Lead.
```

instead of exposing the schema-like wire value.

### Why we want it

There are real cases where the machine value should stay terse, stable, or
external-facing, while the emitted runtime brief should stay human-readable.

This is especially relevant for:

- route-only facts carried in host-provided JSON
- typed mode or next-owner state that must stay stable across runs
- any family where emitted `AGENTS.md` is meant to be cold-read by humans

### What it would allow

- Keep enum values stable for compiler logic, JSON payloads, and cross-surface
  identity.
- Emit readable branch conditions without forcing authors to choose awkward
  machine strings or drift-prone prose summaries.
- Reduce schema-looking emitted prose in large workflow-law families.

### Boundaries

- Do not silently switch all enum rendering to titles or displays.
- Keep the current exact-value semantics available where authors want them.
- Prefer an explicit display surface over magic heuristics.

## 3. Add a first-class way to bind review gates from a selected contract

### Current limitation

Doctrine already supports exact gate export well when one review contract is
statically named. The friction shows up when one critic role needs:

- one typed review surface
- one carried mode or trigger state
- exact per-mode gate export
- no generic wrapper gates like `Dossier Review Basis`

Without a stronger surface here, authors are pushed toward one of two bad
shapes:

- generic local gates that collapse exact contract detail
- large duplicated `match` trees that restate review gate logic by hand

### What we want

Add a first-class way to select one contract by mode and then export or reject
its real gates directly.

Illustrative shape:

```prompt
review LessonsCriticReview: "Lessons Review"
    subject reviewed_artifact = producer_handoff.current_artifact

    mode_selection:
        mode active_review_mode = review_state.active_review_mode as CriticReviewMode

    contract_by_mode:
        CriticReviewMode.dossier -> lessons.contracts.dossier.SectionDossierReviewContract
        CriticReviewMode.copy -> lessons.contracts.copy.CopyReviewContract
        CriticReviewMode.metadata_lesson_title -> lessons.contracts.metadata_wording.MetadataReviewContract

    reject selected_contract.* when review_state.selected_review_basis_failed
```

Or, if `selected_contract.*` is too implicit, some explicit equivalent that
still keeps the gate set tied to the chosen contract instead of a generic local
wrapper.

### Why we want it

Multi-mode critics are common in real prompt families. They need one review
surface that can carry typed state and still emit the exact gate names that a
human reviewer expects to see.

Right now the language is strongest at either:

- one static contract
- or one locally generic review surface

There is a missing middle: one real typed multi-mode critic with exact gate
projection and low duplication.

### What it would allow

- Keep exact shared-contract gate identities in emitted review prose even when
  the contract changes by mode.
- Avoid generic gates like `Metadata Review Basis` when the real failing gates
  already live in shared contract owners.
- Reduce duplicated review law in large critic families without weakening
  readable runtime output.

### Boundaries

- Do not silently merge different contracts into one flattened anonymous gate set.
- Keep exact gate ownership with the original contract.
- Fail loudly if the selected contract is ambiguous or the gate projection is
  not total.

## 4. Add a first-class typed artifact-set surface for invalidation readback

### Current limitation

Doctrine already renders one invalidated artifact title honestly. The problem
shows up when one upstream change invalidates a real downstream cluster, not
just one file.

Today authors tend to fall into one of two weak shapes:

- abstract bucket titles such as `Downstream Lesson Build Work`
- repeated hand-authored prose lists of concrete files

The first is too vague. The second is repetitive and easy to drift.

### What we want

Add one typed way to name a downstream artifact set and let invalidation
readback expand it into an explicit, readable restart surface.

Illustrative shape:

```prompt
artifact_set DownstreamLessonBuildSet: "Downstream Lesson Build Surfaces"
    members:
        lessons.contracts.lesson_situations.LessonSituationsContract
        lessons.contracts.materialization.LessonManifestContract

workflow LessonPlanWorkflow: "Lesson Plan Workflow"
    law:
        invalidates DownstreamLessonBuildSet via coordination_handoff.invalidations when lesson_plan_changed
```

Illustrative emitted readback:

```text
### Invalidations

- `lesson_root/_authoring/LESSON_SITUATIONS.md` is no longer current.
- `lesson_root/_authoring/lesson_manifest.json` is no longer current.
```

### Why we want it

Real authoring pipelines often have downstream rebuild boundaries that are
larger than one file but still smaller than a vague bucket.

Typed artifact sets would let the language keep those restart boundaries:

- explicit
- structured
- readable
- non-duplicative

### What it would allow

- Express downstream rebuild surfaces without vague bucket names.
- Keep invalidation readback concrete without repeating the same file list in
  multiple local owners.
- Make multi-artifact restart boundaries more honest in emitted `AGENTS.md`.

### Boundaries

- Do not replace simple one-artifact invalidation when one artifact is enough.
- Keep artifact-set members explicit and addressable.
- Fail loudly if a set contains unsupported or non-addressable members.

# Suggested order

If Doctrine only takes one follow-up feature from this list soon, it should be
the concrete agent display surface. That is the most general readability gap
for large prompt families and the one most likely to reduce hard-coded owner
strings without changing shipped `:name` semantics.

After that:

1. concrete agent display surface
2. enum member display surface
3. selected-contract review gate export
4. artifact-set invalidation surface

# What this would change for Lessons

If all four features existed, Lessons could do all of this cleanly:

- keep shared owner mentions structured and readable
- keep route-only facts machine-safe without schema-looking emitted prose
- emit exact review gates from one typed multi-mode critic
- express downstream rebuild boundaries as concrete typed sets instead of
  abstract invalidation buckets

That would not remove the need for good local prompt design. But it would make
the best local design easier to write and easier to keep readable at scale.

# Checks

No code or examples changed in this pass. I did not run `make verify-examples`.
This document is a docs-only proposal built from existing shipped behavior,
existing bug analysis, and the current Lessons port evidence.
