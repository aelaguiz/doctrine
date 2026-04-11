---
title: "Doctrine - Metadata Binding Model And Mini Ladder - Architecture Plan"
date: 2026-04-10
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/archive/LESSONS_METADATA_PORT_BLOCKER_NOTE_2026-04-10.md
  - docs/PRO_PROPOSAL.md
  - docs/WORKFLOW_LAW.md
  - docs/REVIEW_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - editors/vscode/README.md
  - examples/24_io_block_inheritance/cases.toml
  - examples/31_currentness_and_trust_surface/cases.toml
  - examples/33_scope_and_exact_preservation/cases.toml
  - examples/38_metadata_polish_capstone/cases.toml
---

# TL;DR

## Outcome

Doctrine ships a first-class metadata binding model that lets workflow law and
review law bind mode, current artifact, owned scope, and preserved truth
through shared and inherited I/O surfaces without forcing duplicate local I/O
owners or role-specific shims, and the shipped corpus teaches that model with a
small progressive example ladder while the VS Code extension fully colorizes
and Ctrl/Cmd-follows the new authored shape.

## Problem

The current shipped language is strong enough to express portable currentness,
narrow scope, preservation, route-only turns, and review-owned current truth,
but it still requires `current artifact` and `own only` roots to resolve
directly against input or output artifacts visible to the concrete turn. That
blocks the richer metadata shape implied by `docs/PRO_PROPOSAL.md` and named in
`docs/archive/LESSONS_METADATA_PORT_BLOCKER_NOTE_2026-04-10.md`: shared
contracts plus inherited role-home outputs can carry the real truth, but the
compiler cannot yet bind that truth as first-class workflow law without either
duplicating local I/O ownership or weakening the shared model.

## Approach

Treat this as a full language feature, not a Lessons-specific patch. Deepen the
existing concrete-turn I/O binding model instead of inventing a second metadata
surface: keyed `inputs:` and `outputs:` entries become first-class law roots,
while the compiler, docs, examples, diagnostics, and VS Code adapter all learn
the same bound-artifact semantics. The feature must stay aligned with
Doctrine's existing design: explicit declarations, compiler-owned semantics,
one output truth model, fail-loud validation, and no shadow carrier or
repo-specific exception path.

## Plan

1. Define the full metadata binding model Doctrine should ship, including the
   authored shape, binding resolution rules, currentness/scope semantics, and
   how it composes with `law`, `review`, `trust_surface`, outputs blocks, and
   inherited I/O.
2. Add a compact but complete example ladder that teaches the feature from
   basic bound current-file law through shared/inherited metadata binding and
   review carryover.
3. Implement the feature end to end in compiler contract resolution,
   diagnostics, live docs, examples, and the VS Code grammar/resolver/test
   surface, touching grammar, parser, or model only if the final authored shape
   exposes a real gap in the shipped syntax.
4. Verify with manifest-backed examples, diagnostics when needed, and the VS
   Code package tests so the authored language, emitted readback, and editor
   behavior all agree.

## Non-negotiables

- No Lessons-only special case and no metadata-only compiler exception.
- No second carrier model, packet model, shadow route payload, or prose-only
  alias.
- No weakening of current `current artifact`, `own only`, `trust_surface`, or
  review invariants just to permit shared-I/O binding.
- No MVP slice that teaches a larger authored model than the compiler really
  ships.
- No VS Code support gap where the language compiles but the extension cannot
  colorize or navigate the new binding refs.
- Keep the solution elegant enough that it feels like Doctrine, not like a
  bolted-on metadata plugin.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-10
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None. The planned compiler, corpus, docs, and VS Code cutover is present.
  - Evidence anchors:
    - `doctrine/compiler.py:224`
    - `doctrine/compiler.py:363`
    - `doctrine/compiler.py:9535`
    - `doctrine/diagnostics.py:1123`
    - `doctrine/diagnostics.py:1234`
    - `doctrine/diagnostics.py:1538`
    - `examples/38_metadata_polish_capstone/prompts/AGENTS.prompt:195`
    - `examples/38_metadata_polish_capstone/prompts/AGENTS.prompt:244`
    - `docs/REVIEW_SPEC.md:15`
    - `docs/PRO_PROPOSAL.md:1`
    - `editors/vscode/README.md:24`
    - `editors/vscode/README.md:131`
    - `editors/vscode/tests/unit/workflow-law.test.prompt:18`
    - `editors/vscode/tests/unit/review.test.prompt:60`
    - `editors/vscode/tests/integration/suite/index.js:382`
    - `editors/vscode/tests/integration/suite/index.js:551`
  - Plan expects:
    - `Phase 1` through `Phase 4` land one bound-root compiler path, rewrite
      the metadata capstone, clean up live review/proposal truth, and close VS
      Code parity on the same authored surface.
  - Code reality:
    - `AgentContract` now preserves concrete-turn binding maps and
      `ResolvedLawPath` preserves binding provenance; workflow-law resolution
      searches bound roots before direct declaration lookup; diagnostics now
      name declared-or-bound concrete-turn roots; `38_metadata_polish_capstone`
      teaches lower-case bound roots directly; `docs/REVIEW_SPEC.md` and
      `docs/PRO_PROPOSAL.md` now reflect shipped truth instead of the old live
      proposal story; and the VS Code README, unit fixtures, and integration
      suite all include bound workflow and review roots.
  - Fix:
    - None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Optional desktop rerun of `cd editors/vscode && make` if you want another
  fresh package confirmation outside this sandbox. This audit pass re-ran the
  full corpus plus diagnostics from `.venv`, and re-ran VS Code unit, snapshot,
  and alignment checks locally, but the Electron integration host still
  aborted with `SIGABRT` after locating the cached VS Code runtime.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-10
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-10
recommended_flow: implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

We can extend Doctrine with a first-class metadata binding model that preserves
the elegance and enforcement strength of the shipped language while letting
workflow and review semantics bind through shared and inherited I/O truth.

This claim is false if any of these happen:

- the feature only works for Lessons-style metadata and does not generalize to
  the underlying shared-I/O pattern
- the authored surface compiles only by duplicating local I/O ownership that
  the shared model was supposed to replace
- portable currentness or owned-scope enforcement gets weaker, more magical, or
  less diagnosable than the current shipped rules
- the example ladder teaches a shape that the VS Code extension cannot fully
  colorize or navigate
- the implementation introduces a second truth path instead of deepening the
  existing `output` plus `trust_surface` contract

## 0.2 In scope

- A first-class Doctrine language feature for metadata binding through shared
  and inherited I/O surfaces.
- The full authored syntax and semantic model needed to express the richer
  metadata shape implied by [docs/PRO_PROPOSAL.md](/Users/aelaguiz/workspace/doctrine/docs/PRO_PROPOSAL.md).
- Compiler resolution and validation for current artifact, owned scope, mode,
  preservation, and review-owned current truth when the live artifact truth is
  exposed through shared or inherited I/O.
- A mini example ladder that teaches the feature progressively and lands as
  manifest-backed shipped proof.
- Live docs, diagnostics, and the VS Code extension surface required to make
  the feature feel fully shipped.

Allowed architectural convergence scope:

- widen grammar, parser, model, compiler, renderer, examples, docs, and VS Code
  support together so the feature is one coherent shipped surface
- refactor existing currentness or I/O-resolution logic if needed to create one
  canonical binding path instead of piling exceptions onto the current path
- consolidate overlapping example or doc truth where the new feature would
  otherwise leave stale stories alive

## 0.3 Out of scope

- A Paperclip-only fix or any repo-specific Lessons doctrine patch
- Runtime fallbacks, compatibility shims, or silent dual semantics
- A generic metadata product or schema library outside Doctrine's prompt
  language
- Shipping a partial ladder that leaves the most important shared-I/O binding
  semantics in prose
- Editing `paperclip_agents` as part of this plan's requested behavior

## 0.4 Definition of done (acceptance evidence)

This plan is done when all of this is true:

- Doctrine has one explicit first-class metadata binding model that can express
  the blocked shared-I/O metadata seam without duplicated local I/O owners.
- The grammar, parser, AST, compiler, renderer, diagnostics, live docs, and VS
  Code extension all describe and support the same authored shape.
- The shipped example corpus includes a compact metadata-binding ladder that
  proves the feature progressively, not only a capstone.
- The extension colorizes the new binding syntax and supports Ctrl/Cmd-follow
  navigation for the new clickable references.
- Existing workflow-law and review semantics stay correct and fail loud on old
  invalid cases.

Smallest credible acceptance evidence:

- targeted manifests for the new ladder plus regression coverage for the
  existing currentness, scope, and metadata capstone examples
- `make verify-examples`
- `make verify-diagnostics` if diagnostics change
- `cd editors/vscode && make`

Smallest credible behavior-preservation evidence:

- existing `31`, `33`, `38`, and `49` example behavior still passes after the
  feature lands
- current diagnostics for invalid currentness and owned-scope roots stay
  meaningful rather than collapsing into generic failures

## 0.5 Key invariants (fix immediately if violated)

- No new parallel truth model for currentness or scope.
- No hidden metadata special case inside compiler resolution.
- No silent weakening of `trust_surface` or emitted-output coupling.
- No feature story that depends on prose aliases the compiler cannot see.
- No VS Code grammar drift from the shipped language.
- No example ladder that teaches less than the actual architectural problem.
- No fallbacks.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Ship an elegant first-class language feature rather than a narrow unblock.
2. Preserve and deepen the existing Doctrine architecture: explicit
   declarations, compiler-owned semantics, and one output truth model.
3. Make the feature teachable through a compact ladder instead of only a
   capstone or one repo-specific motivating example.
4. Keep diagnostics and editor support as first-class deliverables, not cleanup
   work.
5. Preserve current workflow-law and review behavior without accidental
   regressions.

## 1.2 Constraints

- The language already treats `output` plus `trust_surface` as the portable
  truth contract.
- The shipped compiler currently resolves `current artifact` and `own only`
  against declared input or output roots on the concrete turn.
- IO inheritance already exists and is part of the language surface.
- The extension already supports current workflow-law, review, and inherited
  I/O shapes, so the new feature must fit that mental model instead of opening
  a second editor grammar story.

## 1.3 Architectural principles (rules we will enforce)

- Solve this at the language and compiler contract boundary, not in repo-local
  doctrine.
- Prefer one general metadata binding model over one-off allowances.
- Reuse existing typed surfaces where they can honestly own the behavior.
- If a new surface is needed, make it feel native to Doctrine's declaration
  style and explicit binding conventions.
- Keep fail-loud behavior and exact diagnostics.

## 1.4 Known tradeoffs (explicit)

- A truly elegant solution may require widening core resolution logic rather
  than adding a tiny local patch.
- A small teaching ladder is in scope even if the core implementation is the
  largest cost, because the feature is not done if users cannot learn it.
- VS Code support may force authored-shape clarity earlier than the compiler
  work alone would.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already ships:

- workflow-law currentness via `current artifact ... via Output.field`
- `current none`
- `own only` rooted in the current artifact
- `trust_surface` as the portable output truth boundary
- inherited I/O blocks
- first-class `review` with its own currentness and carry semantics

## 2.2 What’s broken / missing (concrete)

- Shared and inherited I/O truth cannot yet serve as a first-class binding root
  for metadata current-file and owned-scope law.
- The motivating metadata shape in `docs/PRO_PROPOSAL.md` is still more elegant
  than the shipped language can express honestly.
- The current example set proves the edges separately, but it does not yet
  teach the full shared-I/O metadata binding story as its own ladder.
- The VS Code extension cannot colorize or navigate an authored metadata
  binding shape that is not yet specified and shipped.

## 2.3 Constraints implied by the problem

- The fix must generalize beyond one prompt family.
- The existing output truth model must remain the single source of truth.
- The feature must compose cleanly with both `law` and `review`.
- The extension work is part of the feature contract, not optional polish.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- None adopted in this pass. Reject broad prior-art fishing for now because the
  repo already exposes the exact semantic pressure, style constraints, and
  editor-surface obligations. Use explicit `external-research` only if deep-dive
  leaves two or more internally plausible binding designs alive.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/compiler.py` — canonical owner for workflow-law and review
    currentness, carrier validation, owned-scope validation, and concrete-turn
    output coupling. The sharp current constraints live in
    `_validate_current_artifact_stmt()`, `_validate_carrier_path()`, and
    `_validate_owned_scope()`.
  - `doctrine/parser.py` and `doctrine/model.py` — canonical owner for what the
    authored language can currently declare around `law`, `output`,
    `trust_surface`, inherited I/O, and `review`.
  - `docs/WORKFLOW_LAW.md` — live shipped workflow-law contract for currentness,
    `trust_surface`, scope, preservation, and route-only turns.
  - `docs/REVIEW_SPEC.md` — live shipped review contract proving that review
    currentness already reuses the same carrier model instead of inventing a
    second truth path.
  - `docs/AGENT_IO_DESIGN_NOTES.md` — live I/O contract stating that agent
    outputs should describe what the concrete turn produces and that portable
    truth moves only through emitted trusted outputs.
- Canonical path / owner to reuse:
  - `doctrine/compiler.py` — this feature should deepen the existing contract
    resolution path for `law` and `review`, not bolt on a metadata-only side
    resolver.
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json` plus
    `editors/vscode/resolver.js` — canonical editor owners for syntax coloring
    and Ctrl/Cmd-follow behavior once the authored shape is real.
- Existing patterns to reuse:
  - `examples/24_io_block_inheritance/**` — proves inherited `inputs` and
    `outputs` blocks are already first-class language structure.
  - `examples/31_currentness_and_trust_surface/**` — proves portable currentness
    and carrier coupling on emitted outputs.
  - `examples/33_scope_and_exact_preservation/**` — proves narrow owned scope
    and preservation behavior.
  - `examples/38_metadata_polish_capstone/**` — current integrated metadata
    capstone and strongest existing pressure test for this feature family.
  - `examples/49_review_capstone/**` — proves modern review inheritance,
    carried state, and review-owned current truth, which this feature must
    compose with.
- Prompt surfaces / authored doctrine to reuse:
  - `docs/PRO_PROPOSAL.md` — motivating authored-shape pressure, especially the
    richer metadata example that wants first-class mode, current-file, and
    narrow-scope law through shared truth.
  - `docs/archive/LESSONS_METADATA_PORT_BLOCKER_NOTE_2026-04-10.md` — precise
    evidence for what the shipped compiler cannot yet express honestly.
- Native model or agent capabilities to lean on:
  - Not the main lever here. This is primarily a language, compiler, and editor
    feature, not a runtime-model capability gap.
- Existing grounding / tool / file exposure:
  - repo-local docs and numbered manifests already expose the exact semantic
    seams and proof style this feature must fit
  - VS Code extension tests, resolver, and grammar fixtures already expose the
    clickable-surface and tokenization model the new feature must match
- Duplicate or drifting paths relevant to this change:
  - `docs/PRO_PROPOSAL.md` currently lives in root docs and still implies a
    richer metadata binding story than the shipped compiler can support.
  - `docs/archive/LESSONS_METADATA_PORT_BLOCKER_NOTE_2026-04-10.md` records the
    current implementation gap; once this feature lands, that blocker note
    becomes historical rather than current pressure.
  - `examples/38_metadata_polish_capstone/**` currently carries the metadata
    family as a capstone without a preceding shipped mini ladder for the shared
    binding model.
- Capability-first opportunities before new tooling:
  - deepen existing language and compiler surfaces before inventing wrappers,
    metadata-specific preprocessors, or repo-local binders
  - reuse the current VS Code resolver categories and clickable-ref model before
    inventing a separate metadata navigation subsystem
- Behavior-preservation signals already available:
  - `examples/24_io_block_inheritance/cases.toml` — protects inherited I/O
    behavior
  - `examples/31_currentness_and_trust_surface/cases.toml` — protects current
    artifact and carrier validation
  - `examples/33_scope_and_exact_preservation/cases.toml` — protects owned-scope
    and preservation validation
  - `examples/38_metadata_polish_capstone/cases.toml` — protects the current
    integrated metadata teaching surface
  - `examples/49_review_capstone/cases.toml` — protects review composition
    around currentness and carried state
  - `editors/vscode/README.md` plus existing unit, snapshot, and alignment tests
    — protect the extension's shipped clickable and colorized surface

## 3.3 Resolved questions and remaining risks

Resolved in deep-dive:

- The Doctrine-native authored shape is semantic deepening of existing `law`
  paths through concrete-turn keyed `inputs:` and `outputs:` bindings, not a
  new `bindings:` declaration family and not a metadata-only exception path.
- Shared-I/O binding resolution belongs in the existing compiler owner path:
  `AgentContract` extraction plus `_resolve_law_path()`, reused by both
  workflow law and review currentness.
- The portable-truth boundary stays unchanged: bound roots normalize to
  declared concrete-turn artifacts first, then the existing emitted-output and
  `trust_surface` checks run on those canonical artifacts.
- The shipped mini ladder should be explicit and progressive rather than hiding
  the feature inside `38_metadata_polish_capstone`.
- The VS Code extension must learn lower-case bound roots as first-class
  references on the same navigation and colorization family as the existing
  shipped law surface.

Remaining risks to settle during phase planning:

- Decide whether bound-root ambiguity and non-bindable-root failures deserve new
  stable diagnostic codes or only tightened wording on existing errors.
- Confirm the exact implementation split between compiler changes first versus
  example/doc/editor updates, while preserving one coherent shipped cutover.
- Use external research only if phase planning reopens multiple plausible
  architectures; it is not currently required to choose the owner path.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark` already accepts lower- or mixed-case dotted
  law paths. There is no dedicated metadata-binding syntax today, and nothing
  in the grammar distinguishes a concrete-turn I/O key from a declaration root.
- `doctrine/parser.py` and `doctrine/model.py` keep workflow-law targets as
  generic `LawPath` values and review currentness carriers as
  `ReviewOutputFieldRef`. The AST does not preserve any notion of "this law
  root came from an agent I/O binding."
- `doctrine/compiler.py` already has two relevant halves:
  - I/O inheritance and concrete-turn resolution live in `_resolve_inputs_decl()`,
    `_resolve_outputs_decl()`, `_resolve_io_body()`, and
    `_resolve_agent_contract()`.
  - workflow-law and review currentness validation live in
    `_validate_current_artifact_stmt()`, `_validate_invalidation_stmt()`,
    `_validate_carrier_path()`, `_validate_owned_scope()`,
    `_validate_law_path_root()`, and `_resolve_law_path()`.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` and
  `editors/vscode/resolver.js` mirror only the shipped clickable and keyword
  surface. The resolver's law-path collector is intentionally shallow and keys
  off uppercase declaration-looking tokens.
- The current teaching surface is split:
  - `examples/24_io_block_inheritance/**` proves inherited typed I/O blocks.
  - `examples/31_*`, `33_*`, and `38_*` prove workflow-law currentness, scope,
    and the metadata capstone.
  - `examples/46_*` through `49_*` prove review currentness and carried review
    semantics.
  - no example family teaches "bound concrete-turn I/O keys as law roots."

## 4.2 Control paths (runtime)

1. Concrete workflow agents resolve `inputs:` and `outputs:` through inherited
   blocks or inline bodies. `_resolve_agent_contract()` then collects only the
   concrete input and output declarations that survive that process.
2. Workflow-law validation later uses that `AgentContract` only as an emitted
   decl set. `_resolve_law_path()` still searches readable declaration names,
   not the bound keys that got the decls onto the concrete turn.
3. `current artifact ... via ...`, `invalidate ... via ...`, and `own only`
   all depend on that direct declaration search. The binding key path that the
   author actually wrote in `inputs:` or `outputs:` never participates.
4. `review` already has its own compiler-owned semantic binding layer:
   `subject`, `subject_map`, `comment_output`, and `fields:`. When review
   currentness is validated, `_resolve_review_agreement_branch()` synthesizes a
   workflow-style `CurrentArtifactStmt` and reuses `_validate_current_artifact_stmt()`.
5. The VS Code extension mirrors the current shipped law surface by scanning
   candidate law tokens with `collectShippedLawRefSites()`, splitting them at
   the first uppercase segment, and resolving those refs against declarations or
   addressable fields. Lower-case local binding roots are invisible to that
   strategy.

## 4.3 Object model + key abstractions

- `AgentContract` is the real seam. Today it stores only:
  - `inputs[(module_parts, decl_name)] -> (unit, InputDecl)`
  - `outputs[(module_parts, decl_name)] -> (unit, OutputDecl)`
- The contract collectors walk inherited and inline I/O surfaces correctly, but
  they discard authored binding keys on the floor. Once collection finishes,
  the compiler knows which decls are concrete, but not which keyed path on the
  concrete turn exposed them.
- `ResolvedLawPath` stores only `unit`, `decl`, `remainder`, and `wildcard`.
  It has no field for binding origin, bound key path, or local-vs-global root
  provenance.
- `ResolvedIoBody` and `ResolvedIoSection` preserve keys for rendering and
  inheritance patching, but that keyed structure never becomes part of workflow
  law semantics.
- `ReviewFieldsConfig` and `ReviewSemanticContext` show the strongest existing
  precedent for a Doctrine-native binding surface: compiler-owned, explicit,
  inherited, and semantically meaningful, but still routed through ordinary
  `output` truth rather than a second carrier primitive.

## 4.4 Observability + failure behavior today

- The shipped compiler is honest and fail-loud on the current model:
  - `E333`/`E334` enforce that currentness carriers and current output roots are
    emitted by the concrete turn.
  - `E335`/`E352` enforce that currentness and owned scope resolve to declared
    input/output roots.
  - `E336`/`E337` and `E372` enforce `trust_surface` and field addressability.
  - review carries the same carrier discipline through `E487`/`E488`.
- What the compiler cannot express today is not "shared I/O exists" but "shared
  I/O bindings are semantic law roots." There is no error class for
  "this keyed I/O path does not bind exactly one artifact" because that concept
  is not modeled yet.
- The live docs tell the same story:
  - `docs/WORKFLOW_LAW.md` and `docs/AGENT_IO_DESIGN_NOTES.md` describe direct
    declared input/output roots plus emitted `trust_surface` carriers.
  - `docs/REVIEW_SPEC.md` describes review binding surfaces, but not bound
    concrete-turn I/O keys for workflow law.
  - `docs/PRO_PROPOSAL.md` still carries stronger metadata-binding pressure than
    the shipped implementation.

## 4.5 UI surfaces (ASCII mockups, if UI work)

There is no end-user UI. The only in-scope UI is editor behavior, and today it
has one important ceiling: lower-case bound artifact roots inside `law` or
carrier paths do not colorize or navigate as first-class refs because the
extension only recognizes the shipped declaration-shaped law surface.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Do not add a new metadata-only declaration family. The first-class feature is
  a deeper meaning for existing concrete-turn `inputs:` and `outputs:` bindings.
- `doctrine/compiler.py` becomes the canonical owner of a new internal binding
  layer:
  - `AgentContract` keeps its current emitted-decl sets.
  - `AgentContract` also gains bound input and output maps keyed by authored
    binding path, not only by declaration identity.
  - each binding entry records the concrete binding path, underlying decl, kind
    (`input` or `output`), and enough authored origin to drive diagnostics and
    editor navigation.
- `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, and
  `doctrine/model.py` stay unchanged unless implementation exposes a real parse
  gap. The preferred architecture is semantic deepening, not syntax growth.
- The docs and example ladder are part of the shipped architecture:
  - workflow-law docs must define bound concrete-turn I/O roots explicitly
  - review docs must explain how review keeps its own reserved binding surfaces
    while reusing the same canonical output truth model
  - the example corpus must teach the new bound-root model directly
- The VS Code extension must mirror the same bound-root surface in grammar,
  navigation, tests, and README wording.

## 5.2 Control paths (future)

1. Resolve the concrete agent's `inputs:` and `outputs:` exactly as today,
   including inheritance, explicit `inherit`, `override`, and inline bodies.
2. During contract collection, walk keyed I/O sections recursively and extract
   every leaf binding path that resolves to exactly one concrete input or output
   declaration on that turn.
3. Expose those bound paths to workflow law as first-class local roots:
   - longest bound-path prefix wins among bound-path candidates
   - any remaining path segments are interpreted as fields on the underlying
     input/output declaration
   - if a bound-path candidate and a direct declaration candidate would both
     match the same authored root text and normalize to different canonical
     identities, fail loud instead of shadowing
   - if no bound path matches, fall back to the shipped declaration-root and
     enum-root search
4. Apply that same canonical resolution helper everywhere workflow law currently
   resolves roots:
   - `current artifact`
   - `invalidate`
   - `own only`
   - `forbid`
   - `support_only`
   - `ignore`
   - `preserve exact`, `preserve structure`, `preserve decisions`,
     `preserve mapping`, and `preserve vocabulary`
5. Keep carrier rules unchanged at the truth boundary:
   - `via` may now root at a bound output path or a direct output decl
   - after resolution, the carrier still has to be an emitted concrete-turn
     `output`
   - the carried field still has to exist and be listed in `trust_surface`
6. Keep review semantically coherent without inventing a second review alias
   family:
   - `subject`, `subject_map`, `comment_output`, and `fields:` remain the
     authored review binding surfaces
   - review currentness continues to reuse the shared workflow currentness
     validator under the hood
   - review-specific subject and comment-output agreement checks still run after
     the shared root resolver succeeds
7. Keep the renderer generic. Bound roots are compiler semantics, not a new
   emitted markdown format.
8. Mirror the same resolution model in VS Code:
   - recognize lower-case or mixed-case bound law roots in law/trust surfaces
   - resolve the root segment to the local binding site
   - resolve descendant segments to the underlying typed declaration fields
   - preserve existing uppercase declaration-root behavior unchanged

## 5.3 Object model + abstractions (future)

The key abstraction is a compiler-owned contract binding, not a new authored
primitive.

Proposed internal shape:

- `ContractBinding`
  - `binding_path: tuple[str, ...]`
  - `kind: "input" | "output"`
  - `unit: IndexedUnit`
  - `decl: model.InputDecl | model.OutputDecl`
  - `origin_label: str`
- `AgentContract`
  - keep the current canonical emitted-decl maps
  - add `input_bindings_by_path`
  - add `output_bindings_by_path`
- `ResolvedLawPath`
  - keep `unit`, `decl`, `remainder`, `wildcard`
  - add optional binding metadata so diagnostics and editor parity can say
    whether a path resolved through a local binding or a direct declaration

Binding rules:

- A bindable path is a keyed leaf path in concrete-turn `inputs:` or `outputs:`
  that resolves to exactly one typed declaration after inheritance and patching.
- Nested keyed paths are legal. If a parent section groups child artifact
  bindings, the child leaf path is the bindable root.
- Unkeyed refs remain usable by direct declaration name only; they do not gain a
  synthetic alias.
- A keyed section that expands to multiple artifact refs is structural only; it
  does not become a bindable artifact root.
- Local bound roots are unqualified. Module-qualified names remain direct
  declaration refs, not binding refs.
- If two distinct bound or direct roots would resolve the same authored path,
  the compiler must fail loud unless they normalize to the same canonical
  declaration identity and remainder.
- Carrier paths follow the same root-resolution rule as other workflow-law
  paths, but they still must normalize to `output`, never `input`.

Exact example-ladder shape:

- `50_bound_currentness_roots`: smallest proof that keyed concrete-turn output
  bindings can root `current artifact ... via ...`
- `51_inherited_bound_io_roots`: inherited `outputs:` or `inputs:` blocks feed
  the same bound-root semantics without local duplication
- `52_bound_scope_and_preservation`: `own only`, `preserve exact`, and
  non-current preservation bind through concrete-turn keys
- `53_review_bound_carrier_roots`: review currentness and carried review state
  prove that bound output roots compose with `review` without a second carrier
  story

Direct-root preservation:

- `31_currentness_and_trust_surface` stays the smallest direct declaration-root
  currentness sentinel
- `33_scope_and_exact_preservation` stays the smallest direct declaration-root
  scope sentinel
- `49_review_capstone` stays the strongest review composition sentinel

Concrete authored effect:

```prompt
agent MetadataCopywriter:
    inputs: MetadataInputs
    outputs: MetadataOutputs
    workflow: MetadataPolish

workflow MetadataPolish: "Metadata Polish"
    law:
        match pass_mode:
            MetadataPassMode.lesson_title:
                current artifact lesson_title_manifest via coordination_handoff.current_artifact
                own only lesson_title_manifest.title
                preserve exact lesson_title_manifest.* except lesson_title_manifest.title

            MetadataPassMode.section:
                current artifact section_metadata via coordination_handoff.current_artifact
                own only {section_metadata.name, section_metadata.description}
                preserve decisions approved_structure
```

That authored surface stays fully Doctrine-native:

- no packet primitive
- no metadata-only alias
- no hidden carrier channel
- no second trust model
- no workflow-local free variable story

## 5.4 Invariants and boundaries

- The one binding surface for workflow law is the concrete turn's existing
  `inputs:` and `outputs:` structure.
- Bound roots never weaken the underlying truth model. The portable truth still
  lives on declared `output` plus `trust_surface`.
- Bound roots are legal only where the concrete agent actually binds exactly one
  artifact. Structural grouping sections, prose-only keys, or unkeyed refs do
  not silently become law-visible aliases.
- The compiler must compare canonical declaration identity, not authored text,
  when checking "same current artifact," owned scope, invalidation conflicts,
  and preservation overlaps.
- New ambiguity or non-bindable-root failures must be specific. If the final
  implementation would otherwise collapse these cases into generic `E299`, add a
  narrow stable compile code in the open `E343`-`E350` band.
- `review` keeps its current authored binding surfaces. This feature must not
  turn `fields:` into a hidden currentness alias or add a review-only shadow
  carrier syntax.
- Ambiguity is never resolved by silent precedence. Distinct matches fail loud.
- The editor mirrors compiler truth only. No extension-only metadata heuristics,
  fake destinations, or second ref taxonomy.
- If implementation discovers that a new authored surface is truly required,
  phase planning must justify why the existing concrete-turn binding path could
  not own the feature. That is an exception path, not the default design.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Editor behavior after the feature lands:

```text
current artifact section_metadata via coordination_handoff.current_artifact
                 ^^^^^^^^^^^^^^^      ^^^^^^^^^^^^^^^^^^^^
                 local bound root     local bound carrier root
                                  ^^^^^^^^^^^^^^^
                                  bound carrier field path
```

Navigation expectations:

- Ctrl/Cmd-click `section_metadata` opens the local binding site under the
  concrete agent's `outputs:` or inherited outputs block.
- Ctrl/Cmd-click `coordination_handoff` opens that bound output entry.
- Ctrl/Cmd-click `current_artifact` opens the underlying output field declared
  on the bound output contract.
- TextMate coloring treats these as real Doctrine refs, not plain prose.
- Lower-case bound roots should use the same reference-family scopes as other
  clickable Doctrine refs rather than inventing a metadata-only token class.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Compiler contract extraction | `doctrine/compiler.py` | `AgentContract`, `_resolve_agent_contract()`, `_collect_input_decls_from_io_value()`, `_collect_output_decls_from_io_value()`, `_collect_*_record_items()` | Collects only canonical input/output decl identity and drops authored binding keys | Preserve keyed binding paths for every concrete-turn leaf artifact, including inherited and overridden I/O | The blocked metadata seam needs law to resolve through shared/inherited concrete-turn bindings, not only raw decl names | `AgentContract` grows bound input/output path maps | `examples/24_*`, new bound ladder, full `make verify-examples` |
| I/O inheritance seam | `doctrine/compiler.py` | `_resolve_inputs_decl()`, `_resolve_outputs_decl()`, `_resolve_io_body()` | Correctly resolves inherited I/O shape for rendering, but the resolved keyed structure never becomes law-visible | Reuse the resolved inherited keyed structure as the source of bindable leaf paths | The new feature must treat inherited blocks as first-class, not as a local-only implementation detail | Bindable paths are derived after inheritance/override resolution | `examples/24_*`, `examples/38_*`, new bound ladder |
| Law root resolution | `doctrine/compiler.py` | `ResolvedLawPath`, `_resolve_law_path()`, `_validate_law_path_root()`, `_display_law_path_root()` | Searches only readable declared input/output/enum names | Add longest-prefix bound-path resolution before direct decl lookup; preserve fail-loud ambiguity | Existing law paths already provide the right syntax; the missing piece is semantic root resolution | `ResolvedLawPath` carries optional binding provenance | `examples/31_*`, `33_*`, new bound ladder |
| Workflow-law validation | `doctrine/compiler.py` | `_validate_current_artifact_stmt()`, `_validate_carrier_path()`, `_validate_invalidation_stmt()`, `_validate_owned_scope()`, `_validate_path_set_roots()` | Enforces emitted-output and `trust_surface` rules only after direct-decl resolution | Apply the exact same output/trust rules after bound-path normalization; compare canonical decl identity for scope and invalidation checks | Bound roots must deepen the same invariants, not create a new semantics lane | Shared normalized law-path helper across all law statements | `examples/31_*`, `33_*`, `36_*`, `38_*`, full corpus |
| Review currentness reuse | `doctrine/compiler.py` | `_resolve_review_agreement_branch()`, `_validate_review_output_agreement_branch()` | Review synthesizes workflow currentness validation but still assumes direct authored review roots | Keep review authored surfaces unchanged while reusing the upgraded currentness resolver and preserving subject/comment-output agreement checks | Prevent workflow and review from diverging at the carrier boundary | No new review-only alias surface; currentness still normalizes through one helper | `examples/46_*` through `49_*` |
| Diagnostics and error catalog | `doctrine/diagnostics.py`, `docs/COMPILER_ERRORS.md` | `E333`-`E337`, `E351`-`E355`, `E371`-`E372`, `E487`-`E488`, generic law-path ambiguity | Wording assumes only declared roots and lacks a narrow concept for non-bindable or ambiguous bound paths | Tighten wording to "declared or bound concrete-turn input/output" where needed; add a narrow ambiguity/non-bindable binding error only if the final surface would otherwise fall back to generic compile failure | The feature must stay teachable and fail loud | Stable code meanings preserved unless a new narrow code is necessary | `make verify-diagnostics` if changed |
| Live workflow and I/O docs | `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/README.md` | Current live docs describe direct declared roots only | Document concrete-turn I/O bindings as first-class workflow-law roots and name their limits clearly | Live docs cannot keep the old ceiling once the compiler ships the deeper model | One live shipped story for workflow law and I/O | Doc review plus example read-through |
| Repo instructions and corpus ceiling | `AGENTS.md`, `docs/README.md`, `examples/README.md` | Repo instructions and docs say the shipped numbered corpus ends at `49_review_capstone` | Raise the declared corpus ceiling and teach where the new bound-root ladder fits relative to the workflow-law and review ladders | The repo instructions must stay aligned with the shipped proof surface | Instructions and docs acknowledge the extended manifest-backed corpus | Doc review |
| Proposal and blocker cleanup | `docs/PRO_PROPOSAL.md`, `docs/archive/LESSONS_METADATA_PORT_BLOCKER_NOTE_2026-04-10.md` | Proposal still sits in live docs root and blocker note reads as a current constraint | Move the proposal to historical framing or archive it; rewrite the blocker note as historical-after-ship context | Prevent stale proposal pressure from reading like a live spec | One live truth, one historical trail | Doc review |
| Example teaching surface | `examples/README.md`, `examples/38_metadata_polish_capstone/**`, new `examples/50_*` through `examples/53_*` | No dedicated metadata-binding ladder exists; `38` proves metadata behavior without teaching the shared binding model | Add a compact bound-root ladder and rewrite `38` to the new concrete-turn binding idiom while keeping `31` and `33` as direct-root sentries | Users need a progressive proof, not only a capstone | New ladder for bound currentness, scope, inheritance, and review carryover; metadata capstone adopts the feature | `make verify-examples` |
| VS Code navigation and coloring | `editors/vscode/resolver.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/README.md` | Law refs are discovered by uppercase declaration heuristics; lower-case bound roots are plain text | Add contract-aware bound-root site collection in law/trust surfaces, local-binding navigation, and matching color scopes | The extension must ship the same authored shape the compiler accepts | Bound root click -> binding site; descendant segment click -> underlying decl field | `cd editors/vscode && make` |
| VS Code tests and alignment | `editors/vscode/tests/unit/workflow-law.test.prompt`, `editors/vscode/tests/unit/io-blocks.test.prompt`, `editors/vscode/tests/unit/review.test.prompt`, `editors/vscode/tests/unit/standalone-reference-bodies.test.prompt`, `editors/vscode/scripts/validate_lark_alignment.py` | No fixture covers lower-case bound roots in law or carrier refs | Add fixtures for bound currentness, bound carrier roots, inherited binding navigation, and review parity; keep alignment validator honest if token rules move | Prevent editor drift and half-shipped support | Extension tests prove compiler/editor parity on the new surface | `cd editors/vscode && make` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  `AgentContract` binding extraction plus `_resolve_law_path()` is the one
  canonical compiler path. Workflow law and review currentness both depend on
  that path after this feature lands.
- Deprecated APIs (if any):
  none at the grammar level. The change is semantic deepening of existing
  authored law paths.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - any temptation to add a metadata-only binder, packet wrapper, or root-binding
    side syntax during implementation
  - stale live-doc wording that says workflow law can only root at directly
    declared inputs/outputs
  - proposal phrasing in `docs/PRO_PROPOSAL.md` that still reads like a live
    spec after the real bound-root model ships
- Capability-replacing harnesses to delete or justify:
  none in Doctrine today. The main rule is to avoid adding repo-local examples,
  wrappers, or editor heuristics that bypass the canonical compiler path.
- Live docs/comments/instructions to update or delete:
  - `AGENTS.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md` if diagnostic wording changes
  - `docs/README.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
- Behavior-preservation signals for refactors:
  - keep `examples/24_*` as the inheritance sentinel
  - keep `examples/31_*` and `examples/33_*` as direct-root workflow-law
    sentries
  - keep `examples/49_*` as the strongest review composition sentinel
  - add new bound-root manifests instead of weakening the old ones

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Metadata teaching path | `examples/38_metadata_polish_capstone/**`, new `examples/50_*` through `examples/53_*`, `examples/README.md` | Bound concrete-turn I/O roots as the metadata workflow idiom | Prevents the metadata seam from staying capstone-only or proposal-only | include |
| Workflow-law live docs | `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md` | One canonical explanation that workflow law can root through concrete-turn bindings | Prevents docs from preserving the old semantic ceiling | include |
| Review boundary docs | `docs/REVIEW_SPEC.md` | Clarify that review keeps `subject` / `comment_output` / `fields` as its authored binding surfaces while reusing the same canonical output-truth boundary | Prevents readers from inferring a second review alias family or missing parity | include |
| Existing direct-root workflow examples | `examples/31_*`, `examples/33_*` | Keep direct declaration roots as explicit regression sentries alongside the new bound-root ladder | Prevents the new feature from accidentally narrowing the older direct-root model | include |
| Repo instruction surfaces | `AGENTS.md`, `docs/README.md` | Update the declared shipped corpus ceiling and example-ladder story when new manifests land | Prevents the repo instructions from immediately lying about shipped proof coverage | include |
| Route-only ladder | `examples/40_*` through `examples/42_*` | Adopt bound roots only if it clarifies the examples without diluting the route-only story | Prevents unrelated churn inside the route-only capstones | defer |
| External Paperclip doctrine | `../paperclip_agents/**` | Port the new feature into the Lessons family | Prevents scope bleed from this Doctrine architecture plan into another repo | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria and
> explicit verification with the smallest credible signal. Preserve existing
> workflow-law and review behavior while deepening the canonical compiler path.
> No metadata-only binders, packet wrappers, shadow carrier syntax, editor-only
> interpretations, or repo-local workaround lanes are allowed. Keep `output`
> plus `trust_surface` as the one downstream-truth boundary, keep Section 7 as
> the one execution checklist, and document only the high-leverage boundary
> comments needed to prevent future drift.

## Phase 1 — Canonical compiler binding substrate

Status: DONE

Goal:
- Land one compiler-owned bound-root resolution path through concrete-turn
  `inputs:` and `outputs:` bindings without introducing a new authored
  primitive or weakening existing direct-root semantics.

Work:
- Extend `AgentContract` to preserve bound input/output leaf paths alongside the
  current canonical decl maps.
- Derive bindable leaf paths from resolved inherited and inline I/O structure
  after `inherit` / `override` application, not from raw authored text alone.
- Teach `ResolvedLawPath` and `_resolve_law_path()` to normalize through bound
  roots first, then fall back to the shipped direct declaration/enum lookup.
- Enforce fail-loud collision behavior when a bound root and a direct
  declaration candidate normalize to different canonical identities.
- Reuse the same normalized root-resolution path in
  `_validate_current_artifact_stmt()`, `_validate_carrier_path()`,
  `_validate_invalidation_stmt()`, `_validate_owned_scope()`, and review
  currentness reuse through `_resolve_review_agreement_branch()`.
- Tighten diagnostics only where the final implementation would otherwise fall
  back to generic compile failure; if a new stable code is needed, keep it in
  the open `E343`-`E350` band.
- Add only the compiler boundary comments needed to explain why concrete-turn
  binding extraction, not rendered IO or examples, owns the feature.

Verification (smallest signal):
- Add the first narrow proof example `50_bound_currentness_roots` and run its
  manifest directly.
- Re-run existing preservation sentries:
  - `examples/24_io_block_inheritance/cases.toml`
  - `examples/31_currentness_and_trust_surface/cases.toml`
  - `examples/33_scope_and_exact_preservation/cases.toml`
  - `examples/49_review_capstone/cases.toml`
- Run `make verify-diagnostics` only if stable code mappings or wording change.

Docs/comments (propagation; only if needed):
- Update only touched compiler comments in this phase. Leave live docs for the
  next phase when the workflow-facing proof ladder is real.

Exit criteria:
- One minimal bound-root workflow example compiles and proves currentness
  through a concrete-turn binding.
- Existing direct-root workflow-law and review sentries still pass unchanged.
- No new authored syntax is required to express the minimal bound-root story.

Rollback:
- If bound-root extraction cannot stay coherent on the existing compiler owner
  path, revert the binding substrate and the first bound-root example together
  rather than leaving a partially active semantic surface behind.

## Phase 2 — Workflow-law ladder and metadata capstone cutover

Goal:
- Ship the workflow-facing proof ladder and make metadata binding a taught
  Doctrine feature instead of a proposal-only or capstone-only story.

Work:
- Add `51_inherited_bound_io_roots` to prove inherited I/O blocks feed the same
  bound-root semantics without local duplication.
- Add `52_bound_scope_and_preservation` to prove `own only`, `preserve exact`,
  and preserved upstream truth through bound roots.
- Rewrite `38_metadata_polish_capstone` onto the bound-root idiom where it
  honestly improves the metadata story, while keeping `31` and `33` as direct-
  root sentries.
- Update checked-in refs, build refs, and manifests for the new ladder and the
  rewritten metadata capstone.
- Cut over the live workflow-law story:
  - `docs/WORKFLOW_LAW.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `examples/README.md`

Verification (smallest signal):
- Run targeted manifests for:
  - `examples/38_metadata_polish_capstone/cases.toml`
  - `examples/50_bound_currentness_roots/cases.toml`
  - `examples/51_inherited_bound_io_roots/cases.toml`
  - `examples/52_bound_scope_and_preservation/cases.toml`
- Run `make verify-examples` before leaving the phase because the shipped
  workflow-law ladder and metadata teaching path changed.

Docs/comments (propagation; only if needed):
- Update the live workflow-law and I/O docs in the same phase so the repo no
  longer claims the old direct-root-only ceiling once the examples ship.

Exit criteria:
- The bound-root workflow-law ladder teaches the feature progressively in the
  shipped corpus.
- `38_metadata_polish_capstone` no longer depends on a proposal-only metadata
  binding story.
- Live workflow-law docs match the shipped compiler and examples.

Rollback:
- If the ladder or metadata capstone cannot teach the feature honestly, revert
  the ladder additions and metadata-capstone rewrite together rather than
  leaving the feature as hidden compiler behavior with stale docs.

## Phase 3 — Review parity and live-truth cleanup

Goal:
- Prove bound roots compose with `review` and remove stale live truth from repo
  docs and instructions.

Work:
- Add `53_review_bound_carrier_roots` to prove review currentness and carried
  review state compose with bound output roots without a second carrier story.
- Keep `49_review_capstone` as the strongest direct-root review sentinel while
  deciding whether `53` needs any additional review-specific diagnostics.
- Update live review and repo-truth surfaces:
  - `docs/REVIEW_SPEC.md`
  - `docs/COMPILER_ERRORS.md` if diagnostics changed
  - `docs/README.md`
  - `AGENTS.md`
- Move `docs/PRO_PROPOSAL.md` into historical framing or archive status and
  rewrite `docs/archive/LESSONS_METADATA_PORT_BLOCKER_NOTE_2026-04-10.md` as a
  historical resolved blocker once the shipped feature exists.

Verification (smallest signal):
- Run targeted manifests for:
  - `examples/49_review_capstone/cases.toml`
  - `examples/53_review_bound_carrier_roots/cases.toml`
- Run `make verify-diagnostics` if review or workflow-law diagnostics changed.
- Re-run `make verify-examples` if review composition work changes shared
  semantics beyond the targeted manifests.

Docs/comments (propagation; only if needed):
- Update every touched live doc or instruction in this phase. Do not leave the
  old corpus ceiling, proposal status, or blocker note as live truth once the
  feature is shipped.

Exit criteria:
- Review bound-root composition is proven in the shipped corpus.
- Repo instructions, live docs, and historical notes tell one current story
  about the feature and its proof coverage.

Rollback:
- If review composition reveals an unresolved semantic conflict, revert the
  review-bound example and live-truth doc cutover together rather than shipping
  a workflow-only feature with misleading review docs.

## Phase 4 — VS Code parity and final full verification

Goal:
- Ship editor parity for the final authored shape and close the feature with
  full repo verification.

Work:
- Teach `editors/vscode/resolver.js` to discover lower-case or mixed-case bound
  roots in workflow-law and trust-surface surfaces, navigate them to the local
  binding site, and resolve descendant segments onto the underlying typed
  declaration fields.
- Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` so bound roots use
  the same reference-family scopes as other clickable Doctrine refs instead of
  a metadata-only token class.
- Add or update extension fixtures in:
  - `editors/vscode/tests/unit/workflow-law.test.prompt`
  - `editors/vscode/tests/unit/io-blocks.test.prompt`
  - `editors/vscode/tests/unit/review.test.prompt`
  - any additional unit file strictly required for bound carrier/readback parity
- Update `editors/vscode/README.md` to reflect the shipped clickable surface.
- Run the final repo-wide verification pass and fix any residual drift in docs,
  comments, examples, or instructions that the final checks expose.

Verification (smallest signal):
- Run `cd editors/vscode && make`.
- Run `make verify-examples`.
- Run `make verify-diagnostics` if diagnostics changed in earlier phases and
  were not already fully verified after the last edits.

Docs/comments (propagation; only if needed):
- Keep only the extension README and any high-leverage resolver/compiler
  comments that explain the canonical bound-root navigation contract.

Exit criteria:
- Compiler, examples, live docs, repo instructions, and VS Code all support the
  same bound-root language surface.
- The full shipped corpus passes, and the extension packages cleanly with the
  new navigation and colorization behavior.

Rollback:
- If the extension cannot mirror the shipped compiler surface without heuristic
  drift, do not ship a split feature. Revert the editor-facing feature cutover
  or reopen the architecture only if the compiler truth itself is in doubt.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

- Use manifest-backed example proof first.
- Preserve current currentness, scope, and review signals before adding new
  harnesses.
- Run `make verify-diagnostics` only if the diagnostic surface changes.
- Treat `cd editors/vscode && make` as part of the feature, not optional polish.

# 9) Rollout / Ops / Telemetry

- No runtime rollout surface is expected.
- Live docs, examples, and editor support must cut over together so the repo
  does not carry a proposal-only metadata binding story after implementation.

# 10) Decision Log (append-only)

- 2026-04-10: Started canonical full-arch planning from the metadata binding
  blocker and the richer feature shape implied by `docs/PRO_PROPOSAL.md`.
- 2026-04-10: Locked the scope to a first-class Doctrine language feature plus
  example ladder and VS Code support, not a Paperclip-only workaround.
- 2026-04-10: North Star approved; the canonical plan is now active and may
  enter the bounded planning controller.
- 2026-04-10: Chose concrete-turn `inputs:` and `outputs:` bindings as the one
  first-class metadata-binding surface for workflow law, and rejected both a
  metadata-only compiler exception and a new `bindings:` declaration family.
- 2026-04-10: Tightened the design so bound roots fail loud on collisions with
  different canonical identities, kept direct declaration roots as permanent
  sentries, and required repo instructions plus the VS Code extension to ship
  the same corpus and binding story.
- 2026-04-10: Sequenced implementation as compiler substrate first, then the
  workflow ladder and metadata capstone cutover, then review and live-truth
  cleanup, and finally VS Code parity plus full verification.
- 2026-04-10: Entered implementation on branch
  `feature/metadata-binding-model-20260410-215227`; Phase 1 is now in progress
  under `implement-loop`.
