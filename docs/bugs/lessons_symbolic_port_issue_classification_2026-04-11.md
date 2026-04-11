---
title: "Lessons symbolic port issue classification"
date: 2026-04-11
status: fix-ready
owners: [aelaguiz]
reviewers: []
related:
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

<!-- bugs:block:tldr:start -->
- Symptom: the Lessons symbolic port audit bundled several emitted-output problems under "Doctrine bugs or gaps," but they do not share one cause or one owner.
- Impact: we risk fixing the wrong layer. Only one audited item is a concrete Doctrine bug; one is a real shipped capability gap; the rest are Lessons prompt or output-design regressions in `paperclip_agents`.
- Most likely cause: the audit mixed compiler behavior, documented language limits, and local prompt authoring choices into one reopened defect bucket.
- Next action: fix the Doctrine workflow-law route-label interpolation bug in this repo, and treat the remaining items as either a documented language-gap decision or Paperclip prompt work.
- Status: `fix-ready` for the Doctrine bug split.
<!-- bugs:block:tldr:end -->

# Bug North Star

Only fix Doctrine when shipped Doctrine behavior is wrong or unsupported.
Do not mutate Doctrine to absorb Lessons prompt decisions that the language
already models honestly today.

# Bug Summary

The 2026-04-11 Lessons audit does surface one real Doctrine defect, but the
bundle is mixed:

- Doctrine bug: raw `{{Agent:name}}` tokens leak in readable markdown for
  workflow-law route lines.
- Doctrine capability gap: agent refs render declaration names, not
  human-facing `role:` prose.
- Lessons prompt or design gaps: critic review-basis collapse, dual next-owner
  readback, wording-only rewrite shift, route enum leakage, widened shared
  metadata handoff text, and abstract invalidation bucket names.

# Evidence

## Gathered First-Party Evidence

- Loaded the repo env and confirmed repo memory reachability with
  `gbrain doctor --json`.
- Read the reopened audit and plan in `paperclip_agents` plus the affected
  Lessons prompt owners.
- Ran these shipped verification surfaces:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/17_agent_mentions/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/20_authored_prose_interpolation/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/39_guarded_output_sections/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/42_route_only_handoff_capstone/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/47_review_multi_subject_mode_and_trigger_carry/cases.toml`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/49_review_capstone/cases.toml`
- Ran one minimal local compile under `uv run --locked python - <<'PY' ...`
  to isolate workflow-law route-label interpolation from the Lessons repo.

# Investigation

<!-- bugs:block:analysis:start -->
## 1. Raw `{{...:name}}` leakage in emitted workflow-law route lines

Verdict: Doctrine bug.

Why:

- `examples/20_authored_prose_interpolation` passes and proves ordinary route
  labels interpolate `{{...}}` correctly on shipped authored-prose surfaces.
- A minimal local prompt rendered this workflow-law branch literally:

  ```text
  If Facts.flag:
  - There is no current artifact for this turn.
  - Stop: Flag is set.
  - Route back to {{RoutingOwner:name}}.
  ```

- The code paths disagree:
  - ordinary route labels are interpolated in `doctrine/compiler.py`
    before they become `ResolvedRouteLine`
  - readable workflow-law rendering later prints `stmt.label` directly in
    `_render_law_stmt_lines()` instead of using an interpolated value

Code anchors:

- `doctrine/compiler.py` ordinary route interpolation near
  `_resolve_section_body_items()`
- `doctrine/compiler.py` workflow-law readable rendering near
  `_render_law_stmt_lines()`

Blast radius:

- readable markdown for workflow-law branches
- emitted `AGENTS.md` output from workflows that use law route labels

This matches the leaked raw tokens in the Lessons emitted homes and is fix-ready
as a Doctrine issue.

## 2. Human-readable owner prose vs raw declaration names

Verdict: Doctrine capability gap, not a bug.

Why:

- `examples/17_agent_mentions/prompts/AGENTS.prompt` explicitly says
  `{{AgentRef}}` and `{{AgentRef:name}}` render the raw agent declaration name.
- `examples/17_agent_mentions/cases.toml` passes with `ProjectLead` and
  `AcceptanceCritic`, not with human-facing `role:` text.
- `docs/LANGUAGE_REFERENCE.md` documents `{{AgentRef:name}}` as authored
  interpolation, but it does not claim that this resolves to role prose.

Implication:

- If Lessons needs human-facing owner names from structured refs, that needs a
  new explicit Doctrine surface such as a dedicated display label field.
- Reinterpreting `:name` to mean `role:` text would break shipped behavior.

## 3. Critic review criteria collapsed into generic review-basis buckets

Verdict: Lessons prompt gap, with a possible future Doctrine ergonomics gap if
the desired end state is one review declaration that can inline different
contract bodies per mode.

Why:

- `paperclip_agents/doctrine/prompts/lessons/agents/lessons_acceptance_critic/AGENTS.prompt`
  defines a single `LessonsCriticReviewContract` with generic gates such as
  `Dossier Review Basis`, `Copy Review Basis`, and `Metadata Review Basis`.
- The same prompt keys those gates off `ReviewState.selected_review_basis_failed`
  rather than directly emitting the detailed per-mode contract checks.
- `docs/REVIEW_SPEC.md` says review contracts export gate identities and titles.
  Shipped examples `47_review_multi_subject_mode_and_trigger_carry` and
  `49_review_capstone` pass with exactly that readable shape.

Doctrine is doing what the current review surface promises. The Lessons port
chose generic gate identities, so the emitted runtime brief is generic.

## 4. Accepted `metadata-lesson-title` branch reads like two next owners at once

Verdict: Lessons prompt readability bug or gap, not a Doctrine bug.

Why:

- The affected prompt branch in the Lessons critic uses:
  - one guarded route to `LessonsMetadataCopywriter` when
    `ReviewState.section_metadata_owed`
  - followed by one unconditional fallback route to `LessonsProjectLead`
- Shipped review examples `47` and `49` show the readable renderer preserves
  exclusivity clearly when the author uses explicit `match` or guarded branch
  structure.
- Runtime route semantics are still compiler-owned; the confusing readback comes
  from flattening two mutually exclusive routes into one readable branch body.

This is a local review-authoring problem, not a core Doctrine defect.

## 5. Section rewrite narrowed to wording-only rewrite

Verdict: Lessons port behavior change or requirements drift, not a Doctrine bug
or gap.

Why:

- `paperclip_agents/doctrine/prompts/lessons/contracts/metadata_wording.prompt`
  explicitly scopes section-mode work to `name` and `description` and preserves
  `sectionId`, `order`, and `status`.
- That narrowing was authored directly into the Lessons contract. Nothing in the
  shipped Doctrine surfaces forced it.

If the old Lessons doctrine needs broader rewrite ownership, Paperclip needs to
change the prompt or update the plan to justify the new behavior.

## 6. Project-lead route enum leakage such as `section-dossier-engineer`

Verdict: Lessons prompt readability gap, not a Doctrine bug.

Why:

- `paperclip_agents/doctrine/prompts/lessons/agents/lessons_project_lead/AGENTS.prompt`
  defines `ProjectLeadRouteOnlyNextOwner` with kebab-case machine values.
- Shipped route and review examples already show readable markdown rendering enum
  values in conditions and matches.

Doctrine is faithfully rendering the authored enum values. If the conditions
look schema-like, the enum values are the source of that look.

## 7. Shared `Metadata State When Current` block widened into non-metadata lanes

Verdict: Lessons shared-output design gap, not a Doctrine bug.

Why:

- `paperclip_agents/doctrine/prompts/lessons/outputs/outputs.prompt` adds
  `metadata_state_when_current` directly to the generic `HandoffOutput`.
- Shipped `examples/39_guarded_output_sections` passes and proves Doctrine can
  keep optional output sections narrow with guards.

Doctrine did not force this metadata block onto every producer lane. The shared
output contract did.

## 8. Typed invalidation still renders abstract buckets

Verdict: Lessons naming and design gap, not a Doctrine bug.

Why:

- `paperclip_agents/doctrine/prompts/lessons/contracts/lesson_plan.prompt` and
  `materialization.prompt` name the invalidated inputs as
  `Downstream Lesson Build Work` and `Downstream Copy And Metadata Work`.
- Shipped `examples/36_invalidation_and_rebuild` passes and shows invalidation
  readback renders the invalidated artifact title exactly.

Doctrine is honestly emitting the chosen bucket titles. If the restart boundary
needs to be more explicit, the Lessons invalidation targets need more explicit
names or narrower split inputs.

## Rejected Theories

- "All reopened items are one Doctrine rendering regression."
  False. Only workflow-law route-label interpolation reproduced as a Doctrine bug.
- "The owner-name readability regression is a Doctrine bug."
  False. That behavior is already documented and covered by shipped example 17.
- "Doctrine forced shared metadata text and abstract invalidation buckets into
  the emitted homes."
  False. Shipped guarded outputs and invalidation examples show those are prompt
  design choices.
<!-- bugs:block:analysis:end -->

# Fix Plan

<!-- bugs:block:fix_plan:start -->
## Doctrine fix-ready item

1. Interpolate workflow-law route labels before readable markdown renders them.
2. Add one manifest-backed example that places `{{AgentRef:name}}` inside a
   workflow-law route label and proves the emitted markdown resolves it.
3. Re-run the targeted proof surfaces for authored interpolation and route-only
   law after the patch.

## Non-Doctrine follow-through

1. Treat human-facing owner names from structured refs as a future Doctrine
   feature request, not a bug fix.
2. Rewrite the Lessons critic metadata accept branch into explicit mutually
   exclusive readable branches if the runtime brief must name only one next
   owner at a time.
3. Narrow the shared Lessons output contract and rename invalidation targets if
   the emitted homes need more concrete restart surfaces.
<!-- bugs:block:fix_plan:end -->

# Implementation

<!-- bugs:block:implementation:start -->
No code changes landed in this analyze pass.

Checks run:

- `gbrain doctor --json`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/17_agent_mentions/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/20_authored_prose_interpolation/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/39_guarded_output_sections/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/42_route_only_handoff_capstone/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/47_review_multi_subject_mode_and_trigger_carry/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/49_review_capstone/cases.toml`
- one minimal local compile under `uv run --locked python - <<'PY' ...` to
  reproduce workflow-law route-label interpolation leakage
<!-- bugs:block:implementation:end -->
