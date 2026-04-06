# 99 Port Directory Structure Proposal

Date: 2026-04-06

## Goal

Start a dedicated workspace for rebuilding `examples/99_not_clean_but_useful`
into the cleaner typed language direction without polluting the numbered
example ladder.

This proposal assumes one major porting rule:

- every agent owns exactly one output artifact
- that artifact uses the exact same name as the agent
- other files the lane reads or edits are inputs, support evidence, or product
  surfaces, not separate output artifacts

## What The 99 Read Actually Says

Reviewing all ten `99` role files shows a consistent outer shell and a messy
inner file-contract story.

Stable shared shell across all roles:

- `Read First`
- `Workflow Core`
- `How To Take A Turn`
- `Skills And Tools`
- `Your Job`
- `Files For This Role`
- `When To Use This Role`
- `Standards And Support`

What actually varies by role:

- the lane-local job
- the exact files or surfaces it depends on
- the packet or file contract it owns
- the stop line and reroute logic
- a few lane-local support standards

The biggest structural problems in `99` are:

- output ownership is inconsistent
- some roles own one packet
- some roles own two outputs
- some roles own one packet plus optional proof files
- `Lessons Acceptance Critic` has no named packet at all
- `Lessons Project Lead` has no single named packet at all
- several roles mix "primary output" with "support evidence" in the same
  section
- product files like `lesson_manifest.json` are treated half as live product
  state and half as role packet truth

That makes `99` hard to route, hard to review, and hard to model cleanly.

## Port Rule To Carry Forward

For the port, the cleanest rule is:

- each agent produces one agent-owned artifact
- the artifact name matches the agent name exactly
- the artifact is the handoff truth for that lane
- support evidence stays behind that artifact
- product files can still be edited, but they are not a second output artifact

This rule fixes two major `99` problems at once:

1. it gives `Lessons Acceptance Critic` and `Lessons Project Lead` a real
   first-class output artifact
2. it stops lanes like `LessonsSituationSynthesizer`,
   `LessonsPlayableMaterializer`, and `LessonsCopywriter` from pretending that
   a mix of packet files and live product files are all co-equal outputs

## Proposed Top-Level Home

Do not put this under `examples/`.

Reason:

- numbered `examples/` are the language teaching ladder
- `99` itself is requirement fodder, not a canonical design target
- this port is a migration workspace, not a settled example

The proposed home is:

- `ports/99_port/`

## Proposed Directory Tree

```text
ports/99_port/
  README.md
  prompts/
    _shared/
      README.md
    section/
      README.md
    lesson/
      README.md
    review/
      README.md
    coordination/
      README.md
```

Planned concern split inside that tree:

- `_shared/`
  - shared role-home workflow pieces
  - shared routing and ownership doctrine
  - shared skills
  - shared source and target declarations
  - cross-cutting input surfaces like issue state, attached checkout truth,
    and reusable output shapes
- `section/`
  - section-scoped agents and contracts
  - `SectionDossierEngineer`
  - `SectionConceptsTermsCurator`
  - `LessonsSectionArchitect`
  - `LessonsPlayableStrategist`
- `lesson/`
  - lesson-scoped agents and contracts
  - `LessonsLessonArchitect`
  - `LessonsSituationSynthesizer`
  - `LessonsPlayableMaterializer`
  - `LessonsCopywriter`
- `review/`
  - critic and review routing
  - `LessonsAcceptanceCritic`
- `coordination/`
  - routing, publish, and issue-state ownership
  - `LessonsProjectLead`

## Why This Split Is Cleaner

This split separates concerns in the way `99` actually behaves:

- section shaping happens before lesson shaping
- lesson shaping happens before build and copy lanes
- critic review is cross-cutting and should not live inside one production lane
- project lead work is orchestration, not content production
- shared role-home material should be modeled once, not repeated ten times

It also avoids the two bad extremes:

- one giant folder with all ten roles mixed together
- one folder per primitive with no domain grouping at all

Pure primitive-first layout would bury the actual workflow order. Pure
role-first layout would duplicate too much shared structure. Domain-first with
shared primitives above it is the better compromise.

## Agent To Artifact Mapping

This is the core port rule translated onto the current `99` roles.

| Current role | Current 99 output story | Proposed single artifact |
|---|---|---|
| `SectionDossierEngineer` | `SECTION_DOSSIER.md` plus scratch concept evidence | `SectionDossierEngineer` |
| `SectionConceptsTermsCurator` | `SECTION_CONCEPTS_AND_TERMS.md` plus support evidence | `SectionConceptsTermsCurator` |
| `LessonsSectionArchitect` | `SECTION_LESSON_MAP.md` plus `SECTION_FLOW_AUDIT.md` | `LessonsSectionArchitect` |
| `LessonsPlayableStrategist` | `SECTION_PLAYABLE_STRATEGY.md` | `LessonsPlayableStrategist` |
| `LessonsLessonArchitect` | `LESSON_PLAN.md` | `LessonsLessonArchitect` |
| `LessonsSituationSynthesizer` | `LESSON_SITUATIONS.md` plus optional `ACTION_AUTHORITY.md` | `LessonsSituationSynthesizer` |
| `LessonsPlayableMaterializer` | `lesson_manifest.json` plus `MANIFEST_VALIDATION.md` | `LessonsPlayableMaterializer` |
| `LessonsCopywriter` | `COPY_GROUNDING.md` plus edited `lesson_manifest.json` | `LessonsCopywriter` |
| `LessonsAcceptanceCritic` | explicit verdict and reroute, but no named packet | `LessonsAcceptanceCritic` |
| `LessonsProjectLead` | route state, issue plan, publish state, but no named packet | `LessonsProjectLead` |

## What Stops Being A Separate Output

These should move out of "role output artifact" status and become support or
product surfaces:

- `CONCEPTS.md`
- `TERM_DECISIONS.md`
- `LEARNING_JOBS.md`
- `SECTION_FLOW_AUDIT.md`
- `STRAWMAN_LESSON_CONTAINERS.md`
- `TEMPLATE_DECISION.md`
- `ARCHITECTURE_LOCK.md`
- `ACTION_AUTHORITY.md`
- `MANIFEST_VALIDATION.md`
- `lesson_manifest.json`

That does not mean those files disappear.

It means they should no longer define lane identity. The lane-owned artifact
does that job. These other files become one of:

- an input surface
- support evidence
- a live product file
- a generated or updated file referenced by the artifact

## File Layout Direction Inside Each Domain

As the port grows, each domain should separate:

- shared input and surface declarations
- artifact declarations
- concrete agents

A likely next step after this scaffold is:

```text
ports/99_port/prompts/section/
  inputs.prompt
  artifacts.prompt
  agents/
    section_dossier_engineer.prompt
    section_concepts_terms_curator.prompt
    lessons_section_architect.prompt
    lessons_playable_strategist.prompt
```

And the same pattern for `lesson/`, `review/`, and `coordination/`.

This keeps:

- agent declarations small
- artifact rules centralized by domain
- reusable input surfaces grouped by the work they support

## Key Modeling Consequence

The port should model "edited product file" separately from "owned output
artifact."

That is especially important for:

- `LessonsPlayableMaterializer`
- `LessonsCopywriter`
- `LessonsSituationSynthesizer`
- `LessonsProjectLead`

Without that distinction, the new one-artifact rule will collapse back into the
same `99` ambiguity under different names.

## First Authoring Order

Suggested order for the port workspace:

1. `_shared/` role-home and routing pieces
2. `section/` agents and artifacts
3. `lesson/` agents and artifacts
4. `review/` critic artifact and routes
5. `coordination/` project-lead artifact and routes

That matches the real dependency order in `99`:

- section truth before lesson truth
- lesson truth before build and copy
- review after specialist work
- project lead across routing and publish state
