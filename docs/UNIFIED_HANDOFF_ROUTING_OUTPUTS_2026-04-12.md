---
title: "Doctrine - Universal Route Semantics For Outputs - Architecture Plan"
date: 2026-04-12
status: complete
fallback_policy: forbidden
owners:
  - doctrine maintainers
reviewers:
  - doctrine maintainers
doc_type: phased_refactor
related:
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
  - docs/COMPILER_ERRORS.md
  - docs/EMIT_GUIDE.md
  - docs/LANGUAGE_REFERENCE.md
  - examples/10_routing_and_stop_rules/prompts/AGENTS.prompt
  - examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt
  - examples/84_review_split_final_output_prose/prompts/AGENTS.prompt
  - docs/UNIFIED_HANDOFF_ROUTING_OUTPUTS_2026-04-12_WORKLOG.md
---

# TL;DR

- Outcome: Add one compiler-owned `route.*` semantic root that any emitted output, including `final_output`, may read or bind from, while keeping `final_output` free to remain a special machine-facing control surface.
- Problem: Doctrine already has real routing truth, but it is split across workflow law, review-only semantic bindings, and `route_only`-specific validation. Arbitrary outputs cannot consume routed-owner truth through one generic path today.
- Approach: Reuse existing authored `route "..." -> Agent` syntax as the only route source, lower all routed-owner semantics onto a shared `route.*` substrate, and replace bespoke review-only and `route_only`-only owner alignment checks with one route-aware validator.
- Plan: Implement the substrate and validator first, then land the example ladder, diagnostics, docs, and manifest-backed proof corpus updates as one coherent follow-through.
- Non-negotiables: No new route authoring syntax, no fake route object on non-route branches, no runner-facing change that forces `final_output` to become ordinary, no dual routing truth paths, and no silent fallback when `route.*` is read where no route exists.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: not started
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: mini-plan -> implement -> arch-docs
note: This doc is intentionally a one-pass mini-plan. It is already grounded enough to implement without a staged deep-dive sequence.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can expose routed-owner truth through one compiler-owned `route.*`
semantic root that any output may consume, without collapsing all turn-ending
outcomes into one universal handoff object and without breaking existing
authored route syntax.

## 0.2 In scope

- Add one shared compiler-owned route semantic surface for emitted outputs:
  `route.exists`, `route.next_owner`, `route.next_owner.key`,
  `route.next_owner.title`, `route.label`, and `route.summary`.
- Extend generic output field binding and interpolation so ordinary outputs,
  review comments, split review `final_output`, and schema-backed final outputs
  may all consume `route.*`.
- Lower current review-owned routed-owner semantics and `route_only`
  routed-owner validation onto one shared route-aware validation path.
- Add targeted diagnostics, tests, and manifest-backed examples that teach the
  feature in increasing complexity.
- Update live docs so shipped behavior, examples, and the implementation plan
  converge on the same story.

## 0.3 Out of scope

- Introducing a new authored route syntax family such as `handoff route`.
- Defining a universal turn-result ontology for `done`, `blocker`, `sleep`, or
  non-route terminal outcomes.
- Forcing machine control contracts and human pickup artifacts to merge into one
  emitted output.
- Changing runner or adapter behavior outside the compiler and rendered docs.
- Non-routing semantic unification outside the route-owner problem.

## 0.4 Definition of done (acceptance evidence)

- A normal workflow-owned output can bind `next_owner` from `route.next_owner`
  and render successfully on a routed branch.
- A review-driven agent can keep review-owned fields on `review.*` while reading
  routed-owner truth from `route.*`, including when `final_output` is separate
  from `comment_output`.
- `route_only` uses the same routed-owner alignment validator as the shared
  route substrate instead of its own bespoke next-owner rule.
- Reading or binding `route.*` on a non-route branch fails loudly unless the
  output section is properly guarded by route existence.
- The shipped proof corpus contains a four-step example ladder covering ordinary
  workflow routing, review reuse, `route_only` reuse, and split durable handoff
  plus machine `final_output`.
- `make verify-examples` and `make verify-diagnostics` pass after the feature
  lands.

## 0.5 Key invariants (fix immediately if violated)

- No new parallel source of route truth. Authored `route "..." -> Agent` stays
  the source; `route.*` is compiler-owned derived semantics.
- No silent fallbacks. If an output reads `route.*` where no route exists, the
  compiler must reject it unless that read is guarded away.
- No fake route object for local or terminal non-route branches.
- No shadow trust channel. Output trust still lives on ordinary outputs and
  existing review/final-output surfaces.
- No requirement that `final_output` become architecturally ordinary.
- No second routed-owner validator once the shared route path exists.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Expose route truth through one reusable output-facing semantic interface.
2. Preserve the current split between machine-facing `final_output` contracts
   and human-facing handoff artifacts when a repo wants both.
3. Keep authored source compatibility clean by reusing existing route syntax.
4. Replace bespoke routed-owner validation branches with one honest validator.
5. Teach the feature through examples and rendered output, not prose alone.

## 1.2 Constraints

- The authored surface already has generic dotted refs and interpolation on
  ordinary outputs. This change must reuse that shipped syntax instead of
  inventing a new `from route.*` grammar.
- Review already has a large semantic-resolution path in `doctrine/compiler.py`;
  the implementation should reuse that machinery shape instead of inventing an
  unrelated binding system.
- `route_only` already lowers through workflow-law facts and has a dedicated
  next-owner validation path; that behavior must converge without losing the
  current fail-loud guarantees.
- `final_output` already has dedicated compile and rendering behavior, including
  split review-final-output cases that must continue to work.
- The repo is example-driven. Docs that cannot be taught through manifest-backed
  examples will drift.

## 1.3 Architectural principles (rules we will enforce)

- Reuse the canonical route authoring path; do not add a second route language.
- Unify route semantics, not all end-of-turn control semantics.
- Keep review semantics on `review.*` and route semantics on `route.*`.
- Let any output read compiler-owned route truth through one generic binding and
  interpolation path.
- Fail loudly when an output claims route truth that the active branch did not
  resolve.
- Converge onto shared compiler helpers instead of growing more surface-specific
  validation code.

## 1.4 Known tradeoffs (explicit)

- This plan prefers a smaller, cleaner route substrate now over a broader
  turn-result abstraction that would overfit one downstream use case.
- The compatibility path keeps old review-authored `next_owner` behavior
  working, but the conceptual model shifts toward generic output binding from
  `route.*`.
- The implementation will likely touch compiler addressability and validation in
  multiple places, but that is still less risky than maintaining three distinct
  routed-owner paths forever.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Workflow law owns real routing truth through authored route edges.
- Review owns routed-owner semantics through typed review `fields:` and review
  semantic refs.
- `route_only` enforces routed-owner honesty through a dedicated next-owner
  contract path.
- `final_output` already supports separate prose and JSON control surfaces,
  including split review `comment_output` plus dedicated final output.
- `emit_flow` already renders routing structure, so the compiler clearly knows
  the route graph.

## 2.2 What this change addressed (concrete)

- Ordinary outputs now bind or interpolate routed-owner truth through one
  shared compiler-owned `route.*` semantic surface.
- Review and `route_only` now reuse the same routed-owner alignment path
  instead of maintaining separate honesty rules.
- Split review `final_output` contracts may now consume `route.*` through the
  same generic output-facing semantics non-review outputs use.
- The implementation keeps that gain scoped to routed-owner semantics instead
  of flattening all end-of-turn control into one universal handoff object.

## 2.3 Constraints implied by the problem

- The feature must solve route truth exposure without forcing all branches to
  look like a route.
- Any compatibility layer must preserve current authored prompts and existing
  shipped examples while allowing new examples to teach the generic path.
- The rendered Markdown in compiled agents should become more expressive where
  route truth is present, but should not invent semantics that the branch did
  not resolve.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- None required. This change is constrained by shipped Doctrine semantics more
  than outside prior art.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` - existing dotted output refs and
    interpolation syntax are already sufficient for output-facing `route.*`
    reads; no new route-binding grammar is required.
  - `doctrine/compiler.py` - review semantic resolution, output addressability,
    and routed-owner validation already exist and are the canonical substrate to
    extend rather than replace.
  - `doctrine/compiler.py` - `route_only` lowering and next-owner enforcement
    already prove that workflow-derived route truth can drive output honesty.
  - `doctrine/compiler.py` and `doctrine/renderer.py` - `final_output` compile
    and rendering paths already support prose and schema-backed split-final
    behavior and must stay intact.
  - `doctrine/diagnostic_smoke.py` - current diagnostics cover final-output and
    review-routed-owner behavior and provide the smallest high-signal regression
    guard for new semantics.
- Canonical path / owner to reuse:
  - `doctrine/compiler.py` - shared semantic-root addressability and output-path
    resolution should own `route.*`, not docs, examples, or ad hoc rendering
    shortcuts.
- Existing patterns to reuse:
  - `doctrine/compiler.py` - review semantic context and addressable-root logic
    are the existing compiler pattern for output-readable semantic fields.
  - `tests/test_final_output.py` - existing split `final_output` tests show the
    right preservation bar for machine-facing output contracts.
  - `tests/test_review_imported_outputs.py` - imported review outputs already
    prove that separate output carriers can inherit semantics from a routed
    review context.
- Prompt surfaces / agent contract to reuse:
  - `examples/10_routing_and_stop_rules/prompts/AGENTS.prompt` - smallest
    workflow-law routed-owner teaching surface.
  - `examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt` - route-only
    owner alignment surface worth converging onto the shared path.
  - `examples/84_review_split_final_output_prose/prompts/AGENTS.prompt` -
    concrete split review `comment_output` plus `final_output` teaching surface.
- Native model or agent capabilities to lean on:
  - Compiler/rendered Markdown only - the feature is declarative and does not
    require new harnesses, OCR, or external tooling.
- Existing grounding / tool / file exposure:
  - `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`,
    `docs/WORKFLOW_LAW.md`, and manifest-backed examples already describe the
    existing semantics that the new surface must preserve.
- Duplicate or drifting paths relevant to this change:
  - Review-only routed-owner binding and `route_only`-only next-owner
    validation are currently parallel implementations of adjacent truth.
- Capability-first opportunities before new tooling:
  - Extend compiler-owned semantic resolution and existing output-binding
    machinery before inventing any wrapper packet or synthetic handoff object.
- Behavior-preservation signals already available:
  - `tests/test_final_output.py` - preserves prose and JSON `final_output`
    rendering behavior.
  - `tests/test_review_imported_outputs.py` - preserves imported review comment
    and split-final-output inheritance behavior.
  - `doctrine/diagnostic_smoke.py` - preserves diagnostic quality for
    review/final-output routes.
  - `make verify-examples` - preserves manifest-backed shipped corpus behavior.

## 3.3 Decision gaps that must be resolved before implementation

- None blocking. The doc now fixes the earlier overreach: unify `route.*`
  semantics only, not all turn outcomes.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark` defines review-specific `fields:`
  semantics, ordinary dotted refs, and route-related authored surfaces.
- `doctrine/compiler.py` owns semantic resolution, output-path addressability,
  route-only lowering, routed-owner validation, and final-output lowering.
- `doctrine/renderer.py` renders agent Markdown, including `## Final Output`
  sections.
- `doctrine/diagnostic_smoke.py` exercises compiler-facing diagnostics and
  rendered-output expectations.
- `tests/` holds focused unit coverage for final output, review outputs, and
  corpus verification helpers.
- `examples/` is the teaching and proof corpus; it is the public-facing surface
  that must explain new semantics without product-specific jargon.

## 4.2 Control paths (runtime)

1. Authored workflow law resolves a route edge for a branch.
2. Review can additionally resolve typed review semantic fields such as
   `next_owner` through review-owned output bindings.
3. `route_only` resolves route truth through facts, feeds the shared `route.*`
   output surface, and validates routed-owner honesty through the same shared
   alignment path.
4. `final_output` points at one emitted output and gets special compile/render
   treatment, including split review-final-output behavior.
5. Ordinary non-review outputs, review comments, and split `final_output`
   contracts may all read compiler-owned routed truth directly through
   `route.*`.

## 4.3 Object model + key abstractions

- Review semantic context is the existing model for compiler-owned semantic data
  that becomes addressable from outputs.
- Route semantic context now extends that same compiler-owned semantic pattern
  for ordinary outputs, review comments, `route_only`, and split
  `final_output`.
- Output field paths and interpolation refs now validate review semantics and
  route semantics through the same shared compiler helpers.
- Final-output metadata is separate from ordinary outputs and must remain able
  to carry repo-specific control-plane meaning.

## 4.4 Observability + failure behavior today

- The compiler already fails loudly for review next-owner mismatches and for
  invalid `final_output` schemas or references.
- Diagnostics already render enough context to prove split review
  `final_output` behavior, review semantic addressability, unguarded route
  reads, and route-only rendered route semantics.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 Route semantics model

Every active branch resolves zero or one real route outcome. When a real route
exists, the compiler exposes:

```prompt
route.exists
route.next_owner
route.next_owner.key
route.next_owner.title
route.label
route.summary
```

`route.*` is derived compiler truth, not authored source. Authored
`route "..." -> Agent` remains the route source of truth.

## 5.2 Output access model

Any emitted output may consume `route.*` through:

- direct interpolation inside prose or rich Markdown sections
- field-level binding, including schema-backed final outputs
- guarded sections that only render when route truth exists

The critical distinction is:

| Concern | Shared route substrate | Still surface-specific |
| ---- | ---- | ---- |
| Routed owner | `route.next_owner` | none |
| Review verdict and review gates | not part of `route.*` | `review.*` |
| Human handoff artifact | may consume `route.*` | output-specific design |
| Machine final control JSON | may consume `route.*` | `final_output` contract |
| Non-route terminal outcomes | not modeled here | repo- or surface-specific |

## 5.3 Validation model

- One shared validator checks that any bound or interpolated owner-facing route
  field stays aligned with the actual routed target.
- Review lowers its routed-owner semantics onto that validator.
- `route_only` lowers onto the same validator for real routed branches.
- Non-route branches do not receive synthetic `local` or `terminal` route
  variants. They simply have no `route.*` data to read.

## 5.4 Edge-case behavior matrix

| Edge case | Expected behavior | Proof surface |
| ---- | ---- | ---- |
| Ordinary output binds `route.next_owner` on a routed branch | Compiles and renders resolved owner | new unit test + new manifest example |
| Ordinary output reads `route.*` on a non-route branch without a guard | Compile failure with route-specific diagnostic | new unit test + diagnostics |
| Guarded output section checks route existence before reading `route.*` | Legal and renders only on routed branches | new unit test |
| Review comment uses `review.verdict` and `route.next_owner` together | Legal; review semantics and route semantics remain distinct | review unit test + new example |
| Split review `final_output` reads `route.*` while `comment_output` remains the durable review carrier | Legal; existing split-final-output behavior preserved | `tests/test_final_output.py` expansion + example |
| `route_only` reroute comment binds `route.next_owner` | Legal on routed branch and checked by shared validator | route-only unit test + example |
| JSON `final_output` includes conditional `next_owner` field | Legal when routed; compile-time alignment enforced | JSON final-output test + diagnostics |
| Local or terminal non-route branch | No fake route object; route reads require guards or fail | unit test |

## 5.5 Example ladder to ship

| Step | Example shape | What it teaches | Ideal rendered result |
| ---- | ------------- | --------------- | --------------------- |
| 1 | ordinary workflow route binding | generic outputs can read `route.*` | prose clearly states who owns next and why |
| 2 | review reusing shared route semantics | review keeps `review.*` while route ownership moves to `route.*` | review comment shows verdict plus routed owner without bespoke review-only binding |
| 3 | `route_only` reroute comment | route-only owner honesty now uses the shared route substrate | reroute comment names the next owner through ordinary route semantics |
| 4 | split durable handoff plus machine `final_output` | one route substrate can feed two different output contracts without forcing them to merge | human pickup Markdown and JSON final result both stay honest about the same routed owner |

### Rendered Markdown standard for the new examples

Use expressive, cold-read-friendly Markdown rather than flat heading spam:

- lead with a short control summary sentence
- use tables where the output is contract-like
- use bullets for ordered reasons or next steps
- keep route truth visually explicit, for example `Next owner: ReviewLead`
- keep human-readable route summaries authored and compact

Illustrative rendered shape for the split-output example:

```md
## Final Output

### Acceptance Control

| Field | Value |
| ---- | ----- |
| verdict | changes_requested |
| next_owner | DraftAuthor |
| route_label | revise |

Keep `next_owner` aligned with the routed owner for this branch.

## Emitted Outputs

### Review Handoff

Draft needs another pass.

- Current artifact: outline_v2
- Next owner: DraftAuthor
- Reason: Completeness gate failed
```

## 5.6 Compatibility and migration

- Existing authored `route "..." -> Agent` syntax continues to work unchanged.
- Existing review-authored `next_owner` behavior remains supported during the
  migration, but the canonical teaching story becomes generic output binding
  from `route.*`.
- Existing review and split-final-output examples continue to compile; they are
  updated only where the shared route substrate should be made visible.
- No migration is required for repos that do not use the new `route.*` output
  semantics.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | ordinary dotted refs and interpolation syntax | shipped grammar already accepts the authored surface the feature needs | no grammar change; reuse existing output ref syntax | avoid inventing a second route-binding language | plain dotted `route.*` refs and interpolations stay the authored surface | new compiler tests |
| Model | `doctrine/model.py` | semantic ref / output binding structures | existing `NameRef`, `AddressableRef`, and `RecordRef` shapes already carry routed refs | no model change; add compiler-owned route context only | compiler needs route addressability without widening the authored model | shared `route.*` context stays compiler-resolved | new unit tests |
| Compiler substrate | `doctrine/compiler.py` | review semantic root resolution and output addressability | review-only semantic roots are special-cased | add shared route semantic root resolution and addressable children | any output must read route truth | `route.*` resolves like compiler-owned semantics, not authored outputs | new route semantics tests |
| Compiler validation | `doctrine/compiler.py` | review next-owner validation | review has bespoke routed-owner validation | converge onto one shared route-aware owner-alignment validator | remove duplicate honesty rules | one validator for review, route_only, and ordinary outputs | review tests, route-only tests, diagnostics |
| Route-only lowering | `doctrine/compiler.py` | `_resolve_route_only_decl_as_workflow` and route-only contract validation | route_only lowers via facts and validates its own next_owner surface | populate shared route semantics for real routed branches and reuse shared validator | route_only should not remain a separate routed-owner island | route-only routes feed `route.*` | route-only tests, new example |
| Final output | `doctrine/compiler.py`, `doctrine/renderer.py` | final-output lowering and rendering | final output already supports prose/json plus split review cases | allow `final_output` to consume `route.*` without changing its special role | keep elegance without collapsing control plane | final output may bind `route.*` while staying machine-special | `tests/test_final_output.py`, diagnostics |
| Diagnostics | `doctrine/diagnostic_smoke.py`, `docs/COMPILER_ERRORS.md` | review next-owner alignment and final-output diagnostics | no route-specific ordinary-output diagnostic exists yet | add route-semantic misuse diagnostics and update catalog if codes/messages change | fail loudly and teach the feature | explicit route diagnostic language | `make verify-diagnostics` |
| Docs | `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md` | live docs | docs describe shipped split semantics but not shared `route.*` output binding | update to present truth and remove review-only implication where no longer true | examples and docs must converge | shared route substrate documented once, then referenced | full corpus + docs read |
| Examples | `examples/87_*` through `examples/90_*` | new manifest-backed ladder | no generic route-output example ladder exists | add four numbered examples with refs/manifests | teach one new idea per example | generic route binding, review reuse, route_only reuse, split outputs | `make verify-examples` |
| Existing examples | `examples/84_*`, possibly `examples/42_*` | existing routed-owner teaching surfaces | teach current behavior but not shared route substrate | update only where shared route semantics should now be visible | preserve continuity while teaching new path | existing example comments may mention `route.*` | targeted manifest verification |

## Migration notes

- Canonical owner path / shared code path:
  - `doctrine/compiler.py` route semantic resolution and output-path validation.
- Deprecated APIs (if any):
  - none immediately; legacy review-authored `next_owner` remains compatibility
    sugar until follow-through chooses to de-emphasize it in docs.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - bespoke route-only next-owner validator path once the shared route validator
    fully replaces it
  - any new helper branch that duplicates review semantic-root resolution instead
    of extending the existing pattern
- Capability-replacing harnesses to delete or justify:
  - none; the feature should land entirely through compiler, renderer, tests,
    examples, and docs
- Live docs/comments/instructions to update or delete:
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/COMPILER_ERRORS.md` if diagnostic text changes
  - `examples/README.md` if new example numbering or reading order matters
- Behavior-preservation signals for refactors:
  - existing final-output tests
  - existing imported-review-output tests
  - diagnostic smoke checks
  - full manifest-backed corpus

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Compiler | `doctrine/compiler.py` review semantic root helpers | shared compiler-owned semantic-root resolution pattern | prevents a second semantic-binding subsystem | include |
| Compiler | `doctrine/compiler.py` route-only validation helpers | shared route-aware validator | prevents review/route-only drift | include |
| Tests | `tests/test_final_output.py`, `tests/test_review_imported_outputs.py` | split-output preservation bar | prevents route work from regressing final-output behavior | include |
| Diagnostics | `doctrine/diagnostic_smoke.py` | route misuse smoke coverage | keeps fail-loud contracts visible | include |
| Docs | route and review design docs | one canonical route-substrate explanation | prevents docs from teaching review-only semantics as the only path | include |
| Emit flow | `doctrine/emit_flow.py` | no change unless route-substrate docs reveal drift | avoid widening scope without evidence | defer |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Shared route substrate and validator

Status: COMPLETE

Completed work:

- Added compiler-owned `RouteSemanticContext` / `RouteSemanticBranch`
  resolution across workflow law, review, and `route_only`.
- Reused existing dotted refs and interpolation syntax for output-facing
  `route.*` reads instead of adding new grammar.
- Extended scalar rendering, prose interpolation, guard validation, readable
  blocks, and final-output lowering to understand `route.*`.
- Replaced the bespoke review/route-only owner-alignment split with one shared
  route-aware alignment helper.
- Fixed two implementation gaps discovered during the pass:
  conditional workflow-law routes now keep unrouted-branch liveness honest, and
  bare `RecordRef` route reads inside output sections now participate in the
  shared validator path.

* Goal: make route truth addressable from any emitted output without changing
  authored route syntax or flattening non-route outcomes.
* Work:
  - run repo preflight: `uv sync` and `npm ci`
  - add compiler-owned `route.*` semantic resolution for routed branches
  - extend generic output interpolation and field binding so ordinary outputs and
    `final_output` can read `route.*`
  - preserve existing review semantics on `review.*` while letting routed-owner
    consumers move to `route.*`
  - replace bespoke review/route-only owner-alignment checks with one shared
    route-aware validator
  - add fail-loud handling for unguarded `route.*` access on non-route branches
* Verification (smallest signal):
  - targeted unit tests for new route semantics, likely in a new
    `tests/test_route_output_semantics.py`
  - targeted preservation runs for
    `tests/test_final_output.py` and `tests/test_review_imported_outputs.py`
  - `make verify-diagnostics`
* Docs/comments (propagation; only if needed):
  - add short compiler comments only at the shared semantic-root / validator
    boundary if the ownership would otherwise be hard to recover later
* Exit criteria:
  - ordinary outputs compile with plain `route.*` refs on routed branches
  - split `final_output` still works and may read `route.*`
  - one shared validator covers routed-owner honesty
  - misuse of `route.*` on non-route branches fails loudly
* Rollback:
  - revert to current review-only and route-only-specific routed-owner handling
    while keeping authored route syntax untouched

## Phase 2 — Proof corpus, docs, and teaching surfaces

Status: COMPLETE

Completed work:

- Added manifest-backed examples `87` through `90` for ordinary workflow-law
  binding, review reuse, dedicated `route_only`, and split review JSON
  `final_output:`.
- Added targeted unit coverage in `tests/test_route_output_semantics.py` plus
  final-output expansions in `tests/test_final_output.py`.
- Added diagnostic smoke coverage for unguarded route reads and route-only
  rendered route semantics.
- Updated the evergreen docs to teach plain dotted `route.*` refs,
  `when route.exists:` guards, and split durable comment plus machine final
  output routing truth.

* Goal: make the feature teachable, auditable, and aligned across examples,
  docs, and rendered output.
* Work:
  - add a new four-step manifest-backed example ladder after example `86`
  - update existing review and route-only teaching examples only where the
    shared route substrate should become visible
  - update live docs to describe `route.*` as the generic routed-owner output
    surface and clarify that `final_output` may consume route truth while
    remaining special
  - add or update diagnostics catalog entries if messages or codes change
* Verification (smallest signal):
  - targeted manifest verification for each new example
  - `make verify-examples`
  - `make verify-diagnostics`
* Docs/comments (propagation; only if needed):
  - reality-sync `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/REVIEW_SPEC.md`,
    `docs/WORKFLOW_LAW.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`,
    and `examples/README.md`
* Exit criteria:
  - the example ladder teaches the feature in increasing complexity
  - live docs no longer imply that routed-owner output binding is review-only
  - full shipped verification passes
* Rollback:
  - drop the example and doc changes together if the implementation cannot be
    taught honestly yet; do not leave the feature half-documented
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy

## 8.1 Unit tests (contracts)

| Contract | File | Expected assertion |
| ---- | ---- | ------------------ |
| ordinary output field binding from `route.next_owner` | `tests/test_route_output_semantics.py` | compiler resolves bound field path on routed branch |
| prose interpolation of `route.summary` | `tests/test_route_output_semantics.py` | rendered output contains route summary text |
| unguarded `route.*` access on non-route branch | `tests/test_route_output_semantics.py` | compile failure with specific diagnostic |
| guarded route-aware section | `tests/test_route_output_semantics.py` | legal and only renders on routed branch |
| review output combining `review.*` and `route.*` | `tests/test_route_output_semantics.py` or existing review test file | both semantic roots resolve without conflict |
| `route_only` shared validator path | `tests/test_route_output_semantics.py` or existing route-only coverage | owner mismatch fails through shared validator |
| split prose `final_output` consuming `route.*` | `tests/test_final_output.py` | final output renders routed owner while comment output stays separate |
| split JSON `final_output` consuming `route.*` | `tests/test_final_output.py` | schema example stays aligned with routed owner |

## 8.2 Integration tests (flows)

- New manifest-backed examples:
  - `examples/87_workflow_route_output_binding`
  - `examples/88_review_route_semantics_shared_binding`
  - `examples/89_route_only_shared_route_semantics`
  - `examples/90_split_handoff_and_final_output_shared_route_semantics`
- Existing example regressions to keep green:
  - `examples/10_routing_and_stop_rules`
  - `examples/42_route_only_handoff_capstone`
  - `examples/84_review_split_final_output_prose`
  - `examples/85_review_split_final_output_json`
  - `examples/86_imported_review_comment_local_routes`

## 8.3 E2E / device tests (realistic)

Not applicable as a separate class. For this compiler-first repo, the realistic
end-to-end signal is:

- targeted unit coverage for semantic resolution
- diagnostic smoke checks
- manifest-backed example verification

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship as one coherent compiler/doc/example change set.
- Do not hide behind a runtime flag. The feature is declarative compiler
  behavior and must either compile honestly or fail loudly.
- Land docs and examples in the same branch as the compiler change so the public
  language story never advertises a half-shipped feature.

## 9.2 Telemetry changes

- None. This repo has no telemetry surface for the compiler itself.

## 9.3 Operational runbook

1. `uv sync`
2. `npm ci`
3. Implement Phase 1
4. Run targeted unit tests and `make verify-diagnostics`
5. Implement Phase 2
6. Run targeted new example manifests, then `make verify-examples`
7. Reality-check compiled Markdown in the new example refs before closeout

# 10) Decision Log (append-only)

## 2026-04-12 - Unify route semantics, not all turn outcomes

Context

The earlier version of this document overreached by collapsing turn-ending
control into one universal handoff root. That created unnecessary constraints
for systems that want route semantics to be shared while keeping richer final
result contracts separate.

Options

- Option A: unify everything under one `handoff.*` object
- Option B: unify only routed-owner semantics under `route.*`

Decision

Choose Option B. The compiler should share route truth broadly, but it should
not pretend all terminal control-plane states are the same thing.

Consequences

- `final_output` may consume shared route semantics without losing its special
  role
- human handoff artifacts and machine control artifacts may stay separate
- the implementation converges review and `route_only` logic without imposing a
  broader ontology

Follow-ups

- implement the shared route semantic root
- add the new example ladder
- update live docs to teach the narrower model directly

# 11) Ready Verdict

This plan is ready for implementation. The architecture choice that mattered
most is now settled: shared `route.*` semantics with no universal handoff
object.

Exact next move: `arch-step implement docs/UNIFIED_HANDOFF_ROUTING_OUTPUTS_2026-04-12.md`
