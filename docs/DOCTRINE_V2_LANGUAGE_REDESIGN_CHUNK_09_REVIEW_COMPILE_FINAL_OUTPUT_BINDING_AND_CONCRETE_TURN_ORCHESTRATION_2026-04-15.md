---
title: "Doctrine - V2 Language Redesign - Chunk 09 - Review Compile Final Output Binding And Concrete Turn Orchestration"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
source_plan: docs/DOCTRINE_V2_LANGUAGE_REDESIGN_PLAN_2026-04-15.md
chunk_order: 9
depends_on:
  - docs/DOCTRINE_V2_LANGUAGE_REDESIGN_CHUNK_08_REVIEW_FAMILY_REMOVAL_AND_REVIEW_DECLARATION_LOWERING_2026-04-15.md
primary_phases:
  - 9
shared_sections:
  - TLDR through Section 6
  - Section 7 intro
  - Backlog after 2.0.0
  - Sections 8 through 10
related:
  - docs/DOCTRINE_V2_LANGUAGE_REDESIGN_PLAN_2026-04-15.md
  - docs/LANGUAGE_REDESIGN_SPEC.md
  - docs/LANGUAGE_REDESIGN_EXT_SPEC.md
---
# TL;DR

## Outcome

Ship Doctrine v2 as one clean, breaking language cutover. The repo should end with one accepted v2 grammar, one typed semantic model, one compiler story, one proof corpus, and one public doc story. The base redesign should become the first stable v2 release. No extension-spec surface is part of this plan's `2.0.0` cut. Any extension work needs a later plan after `2.0.0`.

## Problem

`docs/LANGUAGE_REDESIGN_SPEC.md` and `docs/LANGUAGE_REDESIGN_EXT_SPEC.md` started from conflicting redesign drafts. This plan now closes the core contradiction set around semantic ownership, `review_family`, review grammar, schema naming, selector binding, decisions identity, and the extension cut line so implementation can proceed without inventing the language in compiler code.

## Approach

Treat this as a full v2 redesign, not an additive cleanup. The contradiction set is now locked in the plan: producer-local semantic ownership, `abstract review` replacing `review_family`, one accepted review grammar, `payload_schema:` plus `json schema`, explicit `where(...)` binders, keyed `decisions:` blocks, and no extension-spec features in core v2. Rebuild the language depth-first through grammar, parser, model, compiler, emitters, proof corpus, docs, editor support, and release guidance on one in-place owner path.

## Plan

1. Freeze the accepted v2 contract and close the contradiction set.
2. Build a shared v2 syntax, AST, patch, and identity foundation.
3. Rebuild refs, selectors, binds, and semantic ownership on top of that foundation.
4. Rebuild the high-risk control-plane surfaces: review, final output, route semantics, `route_only`, and `grounding`.
5. Rewrite proofs, emitted public surfaces, docs, editor support, and release guidance as one cutover for the first stable v2 release.
6. Limit planned follow-on work to niceties first and structured or library surfaces second. Keep heavier abstraction systems out until a later plan reopens them.

## Non-negotiables

- This is Doctrine v2. Breaking change is the default posture, not an edge case.
- No long-lived dual v1/v2 code paths in `main`.
- No owner-sensitive keyword overload if v2 says one keyword means one thing.
- No silent spec contradictions. Each one must be resolved in the plan before implementation claims readiness.
- Code, examples, docs, editor grammar, and release guidance must move together.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
external_research_grounding: not needed 2026-04-15
deep_dive_pass_2: done 2026-04-15
consistency_pass: done 2026-04-15
recommended_flow: deep dive -> external research grounding if needed -> deep dive again -> phase plan -> consistency-pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If we implement Doctrine v2 as one hard cutover around a single accepted language contract, then the repo will compile a v2-authored proof corpus end to end with no unresolved semantic collisions between grammar, model, compiler, emitted artifacts, examples, docs, and editor support. If a contradiction still requires local guesswork, the claim is false and the plan is not ready.

## 0.2 In scope

- Resolve the combined redesign specs into one decision-complete v2 contract, with every material contradiction accepted, rejected, narrowed, or deferred explicitly.
- Redesign the shipped language across grammar, parser, typed model, compiler resolution, compiler validation, rendering, emit surfaces, diagnostics, proof corpus, docs, and VS Code support.
- Cover both redesign docs in one canonical plan, but stage them honestly. This plan executes only the base redesign through `2.0.0`. Extension-spec features are backlog only here and require a later plan after `2.0.0`.
- Keep the implementation on the existing repo and Python module owner path unless a later explicit decision proves that impossible.
- Treat compatibility posture as a clean breaking cutover by default. Do not preserve v1 authored syntax or emitted layout through general shims unless a later Decision Log entry explicitly approves one narrow, timeboxed bridge with a removal plan.
- Update adjacent public surfaces that move with the same contract family: examples, emitted artifacts, docs, editor grammar, versioning guidance, changelog, and release flow notes.

## 0.3 Out of scope

- Supporting v1 and v2 as equal first-class languages in `main`.
- Pulling any extension-spec feature into this plan's `2.0.0` cut.
- New runtime, harness, memory, scheduling, or tool-orchestration features that are outside the redesign specs.
- Cosmetic repo cleanup that does not keep live truth aligned with v2.
- Performance work beyond what is needed to keep the v2 compiler path credible and maintainable.
- New package names, new repos, or speculative platform splits unless later repo evidence proves the current owner path cannot carry v2.

## 0.4 Definition of done (acceptance evidence)

- The contradiction set in Section 3.3 is closed and reflected in the target architecture and decision log.
- One accepted v2 grammar and typed model compile the v2 proof corpus through the shipped emit surfaces.
- Targeted unit tests cover the high-risk v2 pivots: inheritance and patch algebra, selectors and binds, review and final-output semantics, schema naming, route semantics, and normalized control-plane declarations.
- Public machine contracts stay explicit and versioned: emitted `schemas/<output-slug>.schema.json` files remain the payload wire contract, and emitted `final_output.contract.json` remains the host-facing final-output and review-control metadata artifact in its accepted v2 form.
- Public docs tell one truthful v2 story: `README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/EMIT_GUIDE.md`, `docs/VERSIONING.md`, and `CHANGELOG.md`.
- Editor support matches the shipped grammar and passes the repo's VS Code verification path if that surface changes.
- Breaking-change guidance is explicit and runnable. The release notes say what changed, who must act, what to change, and how to verify the upgrade.

## 0.5 Key invariants (fix immediately if violated)

- No parallel v1/v2 compiler or doc truth in `main`.
- No unresolved spec contradiction may be papered over with local implementation guesses.
- No hidden semantic ownership split across review, output, and agent surfaces without an explicit accepted model.
- No general fallback or shim layer. Fail loud when v2 behavior is not defined.
- No shipped syntax or emitted artifact change lands without matching proof, docs, and migration truth.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Semantic elegance and coherence across the whole language.
2. One source of truth across grammar, model, compiler, examples, and docs.
3. Honest breaking-change posture with explicit migration guidance.
4. Depth-first implementation order that avoids throwaway compatibility work.
5. Strong proof surfaces for the accepted v2 contract.

## 1.2 Constraints

- Doctrine 1.0 is already shipped and documented as a public language.
- Emitted Markdown, emitted schema files, and emitted final-output contracts are public surfaces.
- The proof ladder spans `examples/01_hello_world` through `examples/115_runtime_agent_packages`.
- The VS Code grammar and alignment tooling must move with syntax changes.
- Release and package docs already require explicit breaking-change guidance.

## 1.3 Architectural principles (rules we will enforce)

- One keyword means one thing.
- One semantic truth path per feature. No shadow contract in renderer-only or validator-only code.
- Keep v2 on the existing owner path. Do not create a `doctrine_v2` parallel compiler tree.
- Resolve semantics in the typed model and compiler core before rewriting emitted docs or examples.
- Prefer explicit deletes and hard cutover over compatibility shims.
- Keep Doctrine on the authoring side of the line. Do not turn v2 into a runtime state system.

## 1.4 Known tradeoffs (explicit)

- Maximum elegance likely rules out most compatibility-cycle aliases proposed in the base spec. That improves clarity but increases rewrite cost.
- Folding both redesign specs into this plan doc makes the artifact large, but it prevents missed obligations and keeps contradictions reviewable in one place.
- A hard in-place cutover is cleaner than a parallel package path, but it means grammar, compiler, corpus, docs, and editor support must converge before release.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine v1 ships a real public language through `doctrine/grammars/doctrine.lark`, the family-specific parser lowerers in `doctrine/_parser/`, the typed model families in `doctrine/_model/`, the resolution and validation pipeline in `doctrine/_compiler/`, the emitters in `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, and `doctrine/emit_skill.py`, the numbered proof corpus under `examples/`, the public docs under `docs/`, and the VS Code support under `editors/vscode/`.

## 2.2 What’s broken / missing (concrete)

- The redesign specs started from a cleaner future language idea, but they left several core choices open until this plan closed them.
- The extension spec is additive in spirit, but several of its later surfaces would stress the current flat name registry and owner-path assumptions if pulled into the first break.
- Current Doctrine still has family asymmetry: some declarations inherit richly and others do not.
- Review semantics, route semantics, final-output semantics, and output bindings are partly compiler-owned and partly surfaced through family-specific config.
- Public naming is still owner-sensitive in places like `schema` versus `output schema`.
- There is no canonical repo plan that tells the implementation in what order to make this break without growing parallel paths or stale truth.

## 2.3 Constraints implied by the problem

- This work must touch grammar, parser, typed model, resolution, validation, rendering, emitters, examples, tests, docs, editor support, and release guidance together.
- Breaking changes must be explicit in `docs/VERSIONING.md` and `CHANGELOG.md`.
- Generated reference artifacts under `examples/*/ref` and `build_ref/` are proof surfaces, not disposable afterthoughts.
- The plan cannot pretend the specs are already consistent. Contradictions must be handled as first-class blockers.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

This pass is repo-first.
No external anchor is authoritative enough to override the shipped repo truth or the redesign specs.
If later passes need parser or DSL migration prior art, add it then with explicit adopt-or-reject reasoning.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors:
  - `doctrine/grammars/doctrine.lark` - shipped grammar boundary.
  - `doctrine/_parser/reviews.py` and `doctrine/_parser/analysis_decisions.py` - current syntax lowering for review and decision surfaces that v2 will replace.
  - `doctrine/_model/review.py` - current review object model, including the `family` flag on `ReviewDecl`.
  - `doctrine/_model/analysis.py` and `doctrine/_model/workflow.py` - current dedicated `decision`, `route_only`, and `grounding` leaf models.
  - `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/review_cases.py`, and `doctrine/_compiler/compile/final_output.py` - the current split review and final-output semantic pipeline.
  - `doctrine/_compiler/resolve/reviews.py` and `doctrine/_compiler/resolve/route_semantics.py` - current resolution ownership for review and route semantics.
  - `doctrine/_compiler/validate/reviews.py`, `doctrine/_compiler/validate/review_semantics.py`, `doctrine/_compiler/validate/review_branches.py`, `doctrine/_compiler/validate/route_semantics.py`, and `doctrine/_compiler/validate/routes.py` - current fail-loud validation boundary.
  - `doctrine/_renderer/`, `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, and `doctrine/emit_skill.py` - public emitted contract surfaces.
  - `doctrine/verify_corpus.py` and `tests/test_verify_corpus.py` - manifest-backed corpus proof entrypoints.
- Canonical owner path or boundary to reuse:
  - `doctrine/` - the existing package is still the canonical owner path for grammar, model, compiler, renderer, and emit logic. The plan should replace the shipped language in place instead of creating a parallel `doctrine_v2` tree.
- Adjacent surfaces tied to the same contract family or migration boundary:
  - `examples/**` and `examples/*/ref/**` - proof inputs and expected public artifacts must move with the language cutover.
  - `tests/test_review_imported_outputs.py`, `tests/test_final_output.py`, `tests/test_route_output_semantics.py`, and `tests/test_decision_attachment.py` - focused proof for the semantic fronts most likely to break.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/EMIT_GUIDE.md`, `docs/VERSIONING.md`, and `CHANGELOG.md` - live public truth that cannot drift behind the compiler.
  - `editors/vscode/extension.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, and `editors/vscode/scripts/validate_lark_alignment.py` - editor grammar and alignment boundary.
  - `tests/test_release_flow.py` and `tests/test_package_release.py` - public release guidance and package truth.
- Compatibility posture:
  - Clean breaking cutover - this matches the approved North Star, the user's stated v2 intent, and the plan doctrine against long-lived dual paths or general shims.
- Existing patterns to reuse:
  - `doctrine/verify_corpus.py` and `make verify-examples` - the main integration-proof ladder already exists and should stay the top proof surface for the language cutover.
  - `make verify-diagnostics` - existing diagnostics proof path for warning and error-surface changes.
  - `editors/vscode/scripts/validate_lark_alignment.py` and `cd editors/vscode && make` - the existing editor-alignment pattern should stay the source of truth for syntax support.
- Duplicate or drifting paths relevant to this change:
  - Review truth is currently split across parser, model, compile, resolve, validate, and final-output modules instead of one accepted semantic package.
  - `ReviewDecl.family` in `doctrine/_model/review.py` preserves `review_family` as a real model split that the redesign wants to remove or replace.
  - `DecisionDecl`, `RouteOnlyDecl`, and `GroundingDecl` still live in dedicated family models and validation paths, which creates the asymmetry the redesign is trying to normalize.
  - Public docs and emitted refs still teach v1 semantics and naming, so they will become stale immediately if the compiler changes first.
- Behavior-preservation signals already available:
  - `make verify-examples`
  - `make verify-diagnostics`
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `make verify-package`
  - `cd editors/vscode && make`

## 3.3 Accepted design decisions that close the contradiction set

- Semantic ownership: keep semantic and final-output truth producer-local at the concrete review or agent edge. Reusable `output` declarations own payload contract, target, requirement, and trust surface. They do not own semantic projection binding.
- Semantic and projection declarations: `semantic` declares one reusable semantic record type. `projection` declares one reusable subset of exactly one `semantic`. `role: Control` may appear only on `projection`.
- Final-output projection surface: producer-local binding lives in the agent-local `final_output` block, not on reusable `output` declarations. Core v2 canonical form is:

  ```doctrine
  final_output:
      output: AcceptanceControlFinalResponse
      project AcceptanceReview as AcceptanceControl:
          verdict: verdict
          current_artifact: current_artifact
          next_owner: next_owner
          blocked_gate: blocked_gate
  ```

  Plain non-review final outputs use the same block with `output:` only:

  ```doctrine
  final_output:
      output: AcceptanceControlFinalResponse
  ```

  `output:` must name one emitted `TurnResponse` output. `project <ReviewName> as <ProjectionName>:` is optional and legal only for review-bound semantic readback. Reusable `output` declarations never contain `project` state, no shorthand `final_output: OutputName` survives in core v2, and `final_output.review_fields` is removed.
- Host-facing emitted metadata: keep `final_output.contract.json` as a public machine-readable peer artifact in `2.0.0`; do not force hosts to scrape Markdown. Because the review metadata shape changes, bump `contract_version` to `2`. The v2 file keeps top-level `agent` and `final_output` blocks and, for review-driven agents, emits a v2 `review` block with review identity, `carrier`, `final_output_projection`, and `outcomes`. Canonical review metadata shape is:

  ```json
  {
    "review": {
      "exists": true,
      "declaration_key": "AcceptanceReview",
      "declaration_name": "Acceptance Review",
      "carrier": {
        "declaration_key": "AcceptanceReviewComment",
        "declaration_name": "Acceptance Review Comment",
        "field_paths": {
          "verdict": "verdict",
          "blocked_gate": "failure_detail.blocked_gate"
        }
      },
      "final_output_projection": {
        "mode": "carrier",
        "projection_key": null,
        "projection_name": null,
        "field_paths": {},
        "control_ready": true
      },
      "outcomes": {}
    }
  }
  ```

  `final_output_projection.mode` is `carrier` or `projected`. When it is `carrier`, `final_output.declaration_key` must equal `review.carrier.declaration_key` and `final_output_projection.field_paths` stays empty. When it is `projected`, `field_paths` maps stable semantic field names to final-output JSON paths, and `projection_key` plus `projection_name` must name the accepted reusable `projection`. Stable host-readable semantic keys are `verdict`, `reviewed_artifact`, `analysis`, `readback`, `current_artifact`, `next_owner`, `blocked_gate`, and `failing_gates`.
- `review_family`: remove it completely in v2. `abstract review` is the only incomplete reusable review surface. Complete `review` declarations may attach directly to agents. No compatibility alias survives in core v2.
- Compatibility posture: keep the hard v2 break. Migration help, if any, comes from diagnostics or a rewrite tool, not a surviving grammar alias.
- Migration-tool policy: `2.0.0` does not require a source rewrite tool. The release bar is explicit upgrade guidance plus fail-loud diagnostics. If a rewrite helper ships, it is optional, repo-local, version-scoped to `1.0.x -> 2.0.0`, and limited to source edits or warnings. It must not add compiler aliases, runtime bridges, or silent lowering.
- Schema naming: use `payload_schema:` as the attachment name for machine JSON payload contracts. Keep `json schema` as the machine declaration family and ordinary `schema` as the Doctrine-readable declaration family. Do not keep `output schema` as a declaration family.
- Selector semantics: `where(...)` requires an explicit item binder with the form `where(<item> => <expr>)`. The binder is in scope only inside that `where` clause. Bare item-local names such as `where(verdict == ...)` are invalid. Canonical example:

  ```doctrine
  ReviewHistoryFile:entries[where(entry => entry.verdict == ReviewVerdict.changes_requested)][last]
  ```

  Preserve left-to-right selector execution and the compile-time versus runtime failure split.
- Normative examples: rewrite contradictory examples before treating them as binding source truth. In particular, inheritance examples must obey the shared patch law.
- Review completeness and producer scope: only `abstract review` may be incomplete. `review` is the only semantic producer in first-release v2. `route_only emits` is deferred beyond the core cutover.
- Core review grammar: use `carrier`, `emits`, optional `selector`, optional `handoff_first`, `checks`, `on_accept`, `on_reject`, and optional `cases`. Remove `contract_checks` and `basis_checks` as separate authored sections. `carrier` and `emits` are review-level only. `handoff_first` is review-level only, reserved for producer handoff completeness, and runs before case selection and before ordinary `checks`. `checks` is the only ordinary review gate surface, runs in authored order, and may contain `block`, `reject`, and `accept`. Basis-first blockers that previously lived in `basis_checks` move to the top of `checks`. A matched `block` produces a blocked branch, not a reject branch. `selector` and `cases` must appear together. Non-case reviews own top-level `subject`, `contract`, `checks`, `on_accept`, and `on_reject`. Case-selected reviews move `subject`, `contract`, `checks`, `on_accept`, and `on_reject` into each case.
- Control readiness: `control_ready` is explicit compiler proof, not inference. A final output is control-ready only when its chosen `projection` carries `role: Control` and every required control field is available on every live branch of the bound review. Core v2 requires `verdict` always, `next_owner` on any branch that routes, and `blocked_gate` on any blocked branch. Compilation fails if any required field is absent on any live branch.
- Core route-selection model: keep direct `route_from <route_ref> as <Enum>:` as the only route-selection form in core v2. `<route_ref>` must be a declared field path or selector path rooted in an input, emitted output, or readable bind that the compiler can prove is enum-typed on the existing law surfaces. `let` names, computed expressions, projection aliases, and typed local `route_from` are not legal core route sources.
- Decisions identity: core v2 uses keyed `decisions:` blocks only. Remove `decision:` sugar from the core cutover.
- Keyed control-family inventories: core v2 keeps keyed inventories end to end for `decisions:`, `route_only`, and `grounding`. Canonical `route_only` top-level keys are `facts`, `select`, `when`, `current`, `handoff_output`, optional `guarded`, and `routes`. Canonical `grounding` top-level keys are `source`, `target`, and keyed `policy`. Every control item must have a stable local key in authored, resolved, validated, and emitted form. Compiler registries and resolved types must store these as keyed maps, not lists plus compatibility lowering.
- Public Python model API: `doctrine/model.py` is the only supported typed-model import surface in v2. `doctrine/_model/**` stays internal. The `2.0.0` cut may remove or rename v1 exports that encode retired surfaces, including `ReviewDecl.family`, review `comment_output` or `fields` helpers, `FinalOutputField.review_fields`, repeated decision-attachment helpers, and `OutputSchema*` names. Core v2 adds public `semantic` and `projection` model exports and renames machine payload exports to the final `json schema` or `payload_schema` vocabulary. After `2.0.0`, every export from `doctrine/model.py` is part of the supported Python contract and must carry direct import-surface tests plus migration notes when it changes.
- Release target: the first public Doctrine v2 cutover ships as `2.0.0`. Do not ship this redesign as a `1.x` patch or minor release.
- Extension read surfaces: `display_title` is not in core v2. If it lands later, it stays render-only and does not become a semantic readback field.
- Deferred extension grammar: import aliasing, typed local `route_from`, and other extension-only ref rules are deferred beyond core v2. They must be designed in their later wave, not assumed during the core cutover.
- Extension cut line: no extension-spec features are in core v2. Earliest follow-on candidates are `let`, quantifiers, read-only `@` mentions, and possibly typed local `route_from` only after its proof rules are closed. Structured data, typed paths, import aliasing, and package barrels are later follow-on work. Parameterization, mixins, protocols, and bounded history stay out until a later plan reopens them.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark` is the shipped language boundary. It still owns v1 declaration headers such as `comment_output`, `final_output.review_fields`, `output schema`, and the current `route_from` surface.
- `doctrine/_parser/` lowers grammar rules into family-local dataclasses. `doctrine/_parser/reviews.py` and `doctrine/_parser/analysis_decisions.py` show that review and decision syntax still take special lowering paths instead of one shared v2 declaration algebra.
- `doctrine/_model/` keeps family-specific types. `doctrine/_model/review.py` still preserves `review_family` through `ReviewDecl.family`, still uses `ReviewCommentOutputConfig` and `ReviewFieldsConfig`, and therefore leaks old review nouns directly into the typed model even though case-selected review branches already use `checks`.
- `doctrine/_model/analysis.py` and `doctrine/_model/workflow.py` keep separate `DecisionDecl`, `RouteOnlyDecl`, and `GroundingDecl` shapes, so the leaf-family normalization work is still real.
- `doctrine/model.py` is the public Python export surface for the typed model. Any v2 model rewrite has to keep that export story honest instead of treating `_model/` as purely internal.
- `doctrine/_compiler/indexing.py`, `doctrine/_compiler/session.py`, `doctrine/_compiler/context.py`, and `doctrine/_compiler/resolved_types.py` are the shared compiler spine today. They already own module loading, family registries, caches, and many resolved runtime-agnostic structures.
- Review semantics are split twice. `doctrine/_compiler/compile/reviews.py` still compiles authored review sections around `comment_output` and `fields`, while `doctrine/_compiler/compile/review_contract.py` separately compiles review-bound final-response semantics and `control_ready`.
- Final-output and structured-response semantics are split across `doctrine/_compiler/compile/final_output.py`, `doctrine/_compiler/output_schema_validation.py`, `doctrine/_compiler/resolve/refs.py`, the dedicated machine-schema subsystem in `doctrine/_compiler/resolve/output_schemas.py`, and the concrete-turn compile path in `doctrine/_compiler/compile/agent.py`.
- `doctrine/_compiler/compile/agent.py` is the live coupling seam where review output contexts, route output contexts, review contracts, and final-output compilation all meet for one concrete agent.
- Route semantics and emitted turn-flow truth are spread across `doctrine/_compiler/resolve/route_semantics.py`, `doctrine/_compiler/validate/routes.py`, `doctrine/_compiler/validate/route_semantics.py`, `doctrine/_compiler/validate/route_semantics_context.py`, `doctrine/_compiler/validate/route_semantics_reads.py`, and `doctrine/_compiler/flow.py`.
- Public diagnostics are not just thrown strings in compiler code. `doctrine/_diagnostics/_message_builders_agents.py` and `doctrine/_diagnostics/_message_builders_reviews.py` freeze user-facing names like `output schema`, `comment_output`, and `final_output.review_fields`.
- Package, smoke, and proof helpers also carry public language truth. `doctrine/_package_release.py`, `doctrine/validate_output_schema.py`, `doctrine/prove_output_schema_openai.py`, and `doctrine/_diagnostic_smoke/*.py` still scaffold or verify the shipped v1 language.
- Public output surfaces live in `doctrine/_renderer/`, `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, and `doctrine/emit_skill.py`.
- Proof and public truth live outside the package too: `examples/**`, `tests/**`, `docs/**`, and `editors/vscode/**`.
- `docs/COMPILER_ERRORS.md`, `docs/AUTHORING_PATTERNS.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/README.md`, and `editors/vscode/README.md` are not side notes. They are live public descriptions of the shipped language and authoring model today.

## 4.2 Control paths (runtime)

1. Parse `.prompt` source through `doctrine/grammars/doctrine.lark`.
2. Index declarations into `IndexedUnit` registries in `doctrine/_compiler/indexing.py`, including one dictionary per family such as `reviews_by_name`, `route_onlys_by_name`, `groundings_by_name`, and `output_schemas_by_name`.
3. Resolve imports, inheritance, slots, refs, and family bodies through `doctrine/_compiler/context.py` caches and the `doctrine/_compiler/resolve/` modules.
4. Compile authored review sections through `doctrine/_compiler/compile/reviews.py`, then separately compile review-bound final-response semantics through `doctrine/_compiler/compile/review_contract.py` and `doctrine/_compiler/compile/final_output.py`, with `doctrine/_compiler/compile/agent.py` acting as the current concrete-turn coupling point.
5. Resolve and lower machine payload contracts through `doctrine/_compiler/resolve/output_schemas.py`, then validate lowered schemas through `doctrine/_compiler/output_schema_validation.py`.
6. Validate semantic invariants, route truth, review truth, and law-path safety through `doctrine/_compiler/validate/`.
7. Render Markdown, flow graphs, and skill packages through the renderer and emit modules.
8. Prove behavior through manifest-backed corpus verification, targeted unit tests, diagnostic smoke fixtures, release-flow tests, package tests, package scaffolds, and VS Code alignment tests.

## 4.3 Object model + key abstractions

- The registry spine is already centralized, but the language model is not. `IndexedUnit` is one shared compiler object, while declaration families still express very different authored and resolved shapes.
- Rich inheritance already exists for several high-level families such as workflows, schemas, documents, skills, and I/O blocks. The redesign pressure comes from bringing leaf declarations onto that same algebra.
- Review truth is currently explicit but fragmented. `ReviewDecl` still centers `comment_output`, `fields`, selector cases, and carrier-relative bindings, while the agent model separately owns `final_output` and optional `review_fields`.
- `ResolvedReviewBody` still carries `comment_output` and `fields` as review-local truth. `CompileReviewsMixin` renders review sections from that body, then `CompileReviewContractMixin` and `CompileFinalOutputMixin` coordinate a second-stage semantic split for split final responses and control readiness.
- `DecisionDecl`, `RouteOnlyDecl`, and `GroundingDecl` are each still first-class dedicated leaf families with their own indexing, resolution, validation, and display logic.
- `output schema` is still subordinate to `output shape`, and `ResolveOutputSchemasMixin` treats it as a dedicated compiler subsystem with its own inheritance, rebinding, lowering, example materialization, and owner-label diagnostics.
- `doctrine/model.py` currently re-exports these typed families directly, which means the v2 model rewrite also has a Python API surface to keep aligned.

## 4.4 Observability + failure behavior today

- Parse and compile errors already fail loud. The redesign should preserve that posture instead of hiding unresolved v2 behavior behind compatibility shims.
- `make verify-examples` is the main integration-proof surface. It exercises the numbered example corpus plus the emitted refs that public docs implicitly rely on.
- `make verify-diagnostics` is the current diagnostics proof path and will matter once v2 warning families and migration messages land.
- `uv run --locked python -m unittest tests.test_release_flow` and `make verify-package` are the public release and package truth surfaces for a breaking cutover.
- `cd editors/vscode && make` plus `editors/vscode/scripts/validate_lark_alignment.py` are the syntax-support proof path for the editor boundary.
- `docs/COMPILER_ERRORS.md` already freezes large parts of the current stable error contract, including review-specific `E469` through `E500` semantics and final-output `E211` through `E218` semantics.
- `doctrine/_diagnostic_smoke/*.py` and `doctrine/_package_release.py` already assume public language labels such as `output schema`, so they will drift immediately if the cutover changes syntax first.
- `editors/vscode/README.md` already documents the shipped review, `final_output`, `output schema`, and `route_from` clickable surface, so it will drift immediately if the cutover changes syntax first.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No product UI is in scope.
The only user-facing UI-like surfaces here are emitted Markdown and the VS Code extension.

The highest-risk semantic migration front is the current review plus split-final package:

- `doctrine/_model/review.py`
- `doctrine/_compiler/resolve/reviews.py`
- `doctrine/_compiler/compile/review_contract.py`
- `doctrine/_compiler/compile/final_output.py`
- `doctrine/_compiler/validate/review_*.py`
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep the implementation on the existing `doctrine/` owner path. No `doctrine_v2` package, no second grammar file, and no long-lived parallel compiler tree.
- Replace the shipped grammar in `doctrine/grammars/doctrine.lark` with the accepted v2 grammar in place.
- Reuse the existing compiler spine in `doctrine/_compiler/indexing.py`, `session.py`, `context.py`, and `resolved_types.py` as the canonical owner path for registry, loading, and resolved-shape work. Refactor it as needed, but do not bypass it with a sidecar v2 pipeline.
- Rebuild `doctrine/_model/` around one accepted v2 declaration inventory with shared patch, inheritance, identity, and semantic abstractions.
- Keep `doctrine/model.py` aligned as the public Python export surface for that accepted v2 declaration model.
- Thin `doctrine/_parser/` so syntax lowering targets the shared v2 model instead of repeating family-local one-offs.
- Concentrate the accepted review, projection, final-output, route, and payload semantics in the compiler core instead of letting renderer-only or family-local special cases own public truth.
- Rewrite `docs/`, `examples/`, `tests/`, and `editors/vscode/` in the same cutover so live truth stays single-source.

## 5.2 Control paths (future)

1. Parse v2 source into one accepted syntax tree and one accepted declaration inventory.
2. Index that inventory through the existing compiler spine, but with the v2 family set and identity rules instead of the v1 family split.
3. Resolve imports, refs, inheritance, selectors, `many` descendants, binds, and canonical aliases through one v2 resolver story, including left-to-right selector execution and the compile-time versus runtime failure split.
4. Lower the accepted `semantic`, `projection`, agent-local `final_output.project`, review package, route semantics, and payload semantics once in the compiler core, so `doctrine/_compiler/compile/agent.py` becomes an orchestration seam instead of a hidden semantic fork.
5. Validate invariants once from that resolved v2 model: alias normalization, selector legality, review package validity, route truth, schema ownership, and migration warnings where approved.
6. Emit Markdown, flow output, structured-output schemas, `final_output.contract.json`, and editor-facing syntax truth from the same accepted v2 model.
7. Prove the cutover through the corpus, targeted tests, diagnostics proof, release-flow proof, package proof, and editor-alignment proof.

## 5.3 Object model + abstractions (future)

- One shared patch and inheritance algebra for every accepted rich declaration family.
- One registry and identity story through the existing `IndexedUnit` and compiler-context spine.
- One accepted semantic package for review and split-final truth: producer-local binding at the concrete review or agent edge, reusable `semantic` and `projection` declarations, reusable `output` payload contracts, `abstract review` as the only incomplete reusable review surface, and no second-stage review/final-output owner split between `compile/reviews.py`, `compile/review_contract.py`, and `compile/agent.py`.
- One accepted final-output binding surface: inside `agent.final_output`, `output:` names one emitted `TurnResponse` output and `project <ReviewName> as <ProjectionName>:` optionally binds that output to one concrete review plus one reusable projection. Plain non-review final outputs use the same block with `output:` only. Reusable `output` declarations never contain `project` blocks, and shorthand `final_output: OutputName` does not survive core v2.
- One accepted host-facing metadata artifact: `final_output.contract.json` remains the compiler-owned machine-readable peer artifact. In `2.0.0` it becomes `contract_version: 2`, keeps top-level `agent` and `final_output`, and uses `review.declaration_*`, `review.carrier`, `review.final_output_projection`, and `review.outcomes` for review-native turns. Hosts version-gate on that file; they do not scrape Markdown.
- One accepted case-review rule set: `carrier` and `emits` are review-level only, `handoff_first` is only for producer handoff completeness and runs before case selection, `checks` is the only ordinary review gate surface and may contain ordered `block`, `reject`, and `accept`, `selector` and `cases` must appear together, non-case reviews keep top-level `subject` or `contract` or `checks` or outcome blocks, and case-selected reviews move `subject`, `contract`, `checks`, `on_accept`, and `on_reject` into each case.
- One path algebra and selector model, including explicit item binders in `where(<item> => <expr>)`, canonical alias normalization in identity, overlap checks, diagnostics, and emitted readable titles.
- One payload-shape story with `payload_schema:` as the JSON attachment name, `json schema` as the machine contract family, and ordinary `schema` as the Doctrine-readable contract family.
- One accepted core route-selection surface: direct `route_from <route_ref> as <Enum>:` survives on the existing law surfaces in core v2. Typed local `route_from` is deferred.
- One public Python model-export story through `doctrine/model.py`, kept aligned with the accepted v2 declaration set instead of lagging behind `_model/`.
- Review is the only semantic producer in core v2. `route_only emits` is deferred beyond the first release.
- Core v2 uses keyed `decisions:` blocks only. `decision:` sugar does not survive the core cutover.
- Core v2 keeps keyed control inventories end to end for `decisions:`, `route_only`, and `grounding`, and those keyed identities survive authored, resolved, validated, and emitted form.
- Package scaffolds, schema proof CLIs, diagnostic smoke fixtures, and emitted refs must tell the same v2 story as the compiler. They are part of the shipped contract, not optional helpers.
- Dedicated primitives stay only where they still earn their keep after the accepted v2 decisions. No leaf family survives just because v1 had a dedicated type for it.
- Extension waves must reuse the same registry, patch, path, and identity foundations. Later waves must not open a second inheritance, import, or namespace system.

## 5.4 Invariants and boundaries

- Compatibility posture is a clean breaking v2 cutover. No general bridge is approved.
- The existing `doctrine/` package is the canonical owner path. Convergence work should refactor into that path, not around it.
- Code is shipped truth once implementation starts. The folded specs remain reference inputs, not a competing runtime contract.
- Reusable `output` declarations do not own semantic projection binding.
- No emitted public artifact change lands without matching proof, docs, release truth, and editor truth when syntax changes.
- No package scaffold, smoke fixture, CLI proof helper, or diagnostic builder may keep a retired public family name after the cutover.
- Ambiguous semantics fail loud.
- No migration wrappers, prompt-like sidecars, or harness replacements should be invented for this redesign. This is a compiler and language refactor, not an agent-capability workaround.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No product UI is planned.
VS Code support and emitted Markdown remain part of the shipped language surface and must track the accepted grammar and emit model exactly.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | declaration headers, review syntax, `final_output`, `output schema`, `route_from` | Ships the public v1 grammar and family inventory | Replace with the accepted v2 grammar in place | Grammar is the public language boundary | One v2 grammar contract | parser tests, corpus, VS Code alignment |
| Parser lowering | `doctrine/_parser/reviews.py`, `doctrine/_parser/analysis_decisions.py`, sibling parser modules | Lowers v1 family-specific syntax into family-specific dataclasses | Rebuild around the accepted v2 declaration inventory and shared lowering shapes | Avoid family-local drift | One v2 lowering story | parser tests, compiler tests, corpus |
| Compiler spine | `doctrine/_compiler/indexing.py`, `doctrine/_compiler/session.py`, `doctrine/_compiler/context.py`, `doctrine/_compiler/resolved_types.py` | Centralizes loading, caches, and family registries for v1 | Keep this as the canonical owner path, but refactor the registries and resolved types for v2 families and identities | Prevent a sidecar v2 compiler path | One v2 registry and context story | compiler unit tests, corpus |
| Public model export surface | `doctrine/model.py` | Re-exports the shipped typed model publicly | Update the export set and names to match the accepted v2 model | The model rewrite has a Python API surface too | One honest v2 model-export surface | unit tests, importers, docs |
| Review model | `doctrine/_model/review.py` | `ReviewDecl`, `ReviewBody`, `family` flag, `comment_output`, `fields` | Encodes v1 review-family and carrier semantics directly in the model | Replace with the accepted v2 review package and remove or replace the `family` split | Review is the highest-risk semantic front | One accepted v2 review model | review unit tests, corpus |
| Review compile split | `doctrine/_compiler/compile/reviews.py`, `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/final_output.py`, `doctrine/_compiler/compile/agent.py` | Compiles authored review sections, review-bound final response semantics, and concrete-turn output binding in separate stages with different public nouns | Collapse onto one accepted v2 owner path where only `review` emits semantics, `agent.final_output.project` binds the final readback, and `compile/agent.py` is orchestration-only | Prevent the compiler from re-inventing the language through split staging | One owner path for review, projection, final output, and control readiness | review tests, final-output tests, flow tests |
| Decision and control leaf models | `doctrine/_model/analysis.py`, `doctrine/_model/workflow.py`, `doctrine/_model/agent.py` | Keeps dedicated `decision`, `route_only`, `grounding`, and agent `final_output.review_fields` shapes | Normalize these onto the accepted v2 family and semantic model, or defer them explicitly by phase | Remove v1 family asymmetry | One accepted v2 declaration model | unit tests, route and decision tests |
| Review resolution and validation | `doctrine/_compiler/resolve/reviews.py`, `doctrine/_compiler/validate/reviews.py`, `doctrine/_compiler/validate/review_semantics.py`, `doctrine/_compiler/validate/review_branches.py`, `doctrine/_compiler/validate/review_agreement.py`, `doctrine/_compiler/validate/review_gate_observation.py`, `doctrine/_compiler/validate/review_preflight.py` | Resolves and validates v1 review semantics, gates, branches, and carrier truth | Rebuild for the accepted v2 review grammar, ordered `checks`, blocked pre-contract review behavior, and semantic package | This is where hidden semantic splits become compiler truth | One v2 review validation contract | review tests, imported-output tests, corpus |
| Concrete-turn coupling seam | `doctrine/_compiler/compile/agent.py` | Joins review output contexts, route output contexts, review contracts, and final-output compile for one agent | Refactor this seam so it orchestrates resolved v2 artifacts plus agent-local `final_output.project` binding instead of preserving the v1 semantic split | This is where hidden divergence can survive even after family rewrites | One orchestration seam, not a second semantics owner | review tests, final-output tests, route tests |
| Final output and payload semantics | `doctrine/_compiler/compile/final_output.py`, `doctrine/_compiler/output_schema_validation.py`, `doctrine/_compiler/resolve/refs.py`, `doctrine/_compiler/resolve/output_schemas.py` | Owns split final-output semantics, lowered schemas, payload-schema refs, and machine-JSON lowering under the v1 `output schema` family | Rebuild around the accepted v2 agent-local `final_output.project` surface, explicit `control_ready`, `payload_schema:`, and `json schema` story | Public structured-output truth depends on it | One v2 final-output and machine-payload contract | final-output tests, schema tests, schema CLI proof, corpus |
| Host-facing final-output metadata | `doctrine/emit_docs.py`, `tests/test_emit_docs.py`, `docs/EMIT_GUIDE.md`, `docs/VERSIONING.md` | `final_output.contract.json` | Emits v1 final-output and review-control metadata under review nouns such as `comment_output` and `review_fields` | Keep the filename, bump `contract_version` to `2`, and replace the review metadata with accepted v2 `carrier` and `final_output_projection` contract keys | External hosts load this file directly and must not scrape Markdown | One versioned v2 host metadata contract | emit tests, docs, external consumers |
| Route semantics and flow | `doctrine/_compiler/resolve/route_semantics.py`, `doctrine/_compiler/validate/routes.py`, `doctrine/_compiler/validate/route_semantics.py`, `doctrine/_compiler/validate/route_semantics_context.py`, `doctrine/_compiler/validate/route_semantics_reads.py`, `doctrine/_compiler/flow.py` | Owns route truth for workflow law, handoff routing, and emitted flow | Rebuild to match the accepted v2 route semantics, selector truth, and any chosen `route_only` role | Route and final-output truth must stay coherent | One v2 route and flow contract | route tests, flow tests, corpus |
| Diagnostics builders and error catalog | `doctrine/_diagnostics/_message_builders_agents.py`, `doctrine/_diagnostics/_message_builders_reviews.py`, `docs/COMPILER_ERRORS.md` | User-facing error messages still name v1 concepts such as `output schema`, `comment_output`, and `final_output.review_fields` | Rewrite names, examples, and migration hints to the accepted v2 surface | Public diagnostics are part of the language contract | One v2 diagnostics story | `make verify-diagnostics`, diagnostics smoke, docs |
| Render and emit | `doctrine/_renderer/*.py`, `doctrine/emit_docs.py`, `doctrine/emit_flow.py`, `doctrine/emit_skill.py` | Emits v1 public artifacts and layout contracts | Update emitted surfaces to the accepted v2 contract | Emitted artifacts are public surface | One v2 emitted contract story | emit tests, corpus |
| Package, scaffold, and smoke helpers | `doctrine/_package_release.py`, `doctrine/validate_output_schema.py`, `doctrine/prove_output_schema_openai.py`, `doctrine/_diagnostic_smoke/*.py` | Public helper output and smoke fixtures still scaffold or verify v1 names such as `output schema` | Rewrite helper output and smoke fixtures to the accepted v2 language | Package helpers and proof CLIs are shipped behavior too | One v2 helper and smoke story | package tests, schema CLI tests, smoke checks |
| Corpus and focused proof | `examples/**`, `doctrine/verify_corpus.py`, `tests/test_verify_corpus.py`, `tests/test_review_imported_outputs.py`, `tests/test_final_output.py`, `tests/test_route_output_semantics.py`, `tests/test_decision_attachment.py`, `tests/test_output_schema_surface.py`, `tests/test_output_schema_lowering.py`, `tests/test_output_schema_validation.py`, `tests/test_emit_flow.py`, `tests/test_emit_docs.py` | Proves v1 language and key semantic edges | Rewrite and expand proof for v2 semantics, migration fronts, and emitted truth | Proof must move with the language | One v2 proof ladder | verify-corpus, named unit tests, emit tests |
| Live docs and authoring notes | `README.md`, `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/EMIT_GUIDE.md`, `docs/COMPILER_ERRORS.md`, `docs/AUTHORING_PATTERNS.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `examples/README.md`, `editors/vscode/README.md` | Teaches v1 syntax, review semantics, route semantics, current error codes, editor behavior, and release truth | Rewrite or delete stale v1 truth in the same cutover | Live docs are public surface | One v2 doc and migration story | docs consistency, diagnostics verification, release/package proof |
| VS Code support | `editors/vscode/extension.js`, `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/scripts/validate_lark_alignment.py`, `editors/vscode/tests/**` | Supports and snapshots the shipped v1 grammar | Rewrite to the accepted v2 grammar and keep alignment proof honest | Editor support is shipped surface | One v2 editor story | `cd editors/vscode && make` |
| Release and packaging | `pyproject.toml`, `tests/test_release_flow.py`, `tests/test_package_release.py` | Carries current public release assumptions | Update to the explicit v2 breaking-release story where needed | Silent breakage is forbidden | Explicit v2 release and package contract | release-flow and package tests |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - Stay in the existing `doctrine/` package and compiler spine. Refactor into `indexing.py`, `session.py`, `context.py`, and the surrounding compiler modules instead of creating a second v2 execution path.
- Deprecated APIs (if any):
  - No compatibility aliases or deprecated grammar bridges are approved for core v2. Migration help, if any, must come from diagnostics or rewrite tooling, not a surviving alias surface.
- Public Python API contract:
  - `doctrine/model.py` is the only supported typed-model import surface in v2. `doctrine/_model/**` stays internal.
  - The `2.0.0` cut may remove or rename v1 exports that encode retired surfaces. The upgrade guide must map those old names to the accepted v2 export set.
  - After `2.0.0`, every export from `doctrine/model.py` is public contract and needs direct import-surface tests plus migration notes when it changes.
- Public emitted machine contract:
  - `final_output.contract.json` remains the shipped host-facing metadata file in `2.0.0`.
  - The v2 cut bumps that file to `contract_version: 2`.
  - Review-native metadata must move from v1 `comment_output` plus `final_response.review_fields` naming to v2 `review.carrier` plus `review.final_output_projection`.
  - External consumers must version-gate on that file instead of scraping emitted Markdown.
- Rewrite-tool posture:
  - No source rewrite tool is required for `2.0.0`.
  - If a rewrite helper ships, it is optional, repo-local, version-scoped to `1.0.x -> 2.0.0`, and limited to source edits or warnings. It must not add compiler aliases, runtime bridges, or silent lowering.
- Delete list (what must be removed; include superseded shims or parallel paths if any):
  - Surviving v1-only grammar rules once the accepted v2 grammar lands.
  - `ReviewDecl.family` and all `review_family`-specific parser, model, compiler, and validation branches.
  - `comment_output`, `fields`, `basis_checks`, `contract_checks`, and `final_output.review_fields` split paths once the accepted v2 review package replaces them.
  - Any owner-sensitive `output schema` declaration branches, registry names that leak retired public nouns, or payload-schema special cases that conflict with the accepted v2 naming rule.
  - Core `decision:` sugar once keyed `decisions:` blocks replace it.
  - Stale `doctrine/model.py` exports that no longer describe the accepted declaration set.
  - Retired v1-only error descriptions, package scaffold snippets, schema proof helper examples, and VS Code README claims once the shipped language boundary changes.
  - Stale v1 examples, emitted refs, docs, and VS Code snapshot expectations.
- Adjacent surfaces tied to the same contract family:
  - Examples, emitted refs, focused tests, public docs, authoring notes, error docs, diagnostic smoke fixtures, schema proof CLIs, package scaffolds, release tests, package tests, VS Code syntax, and VS Code snapshots all move with the same language boundary.
- Compatibility posture / cutover plan:
  - Clean breaking cutover for the public language. No general runtime shim, no dual grammar, and no long-lived parallel docs story.
  - Ship the first public breaking release as `2.0.0`.
- Capability-replacing harnesses to delete or justify:
  - None should be added. This redesign should not invent migration wrappers or extra harness layers to avoid real compiler convergence work.
- High-priority example and snapshot replacements:
  - Replace or rewrite the legacy family and sugar examples first: `examples/68_review_family_shared_scaffold`, `examples/69_case_selected_review_family`, and `examples/74_decision_attachment`.
  - Replace or rewrite the machine-payload and split-final examples that currently freeze `output schema`, `comment_output`, or `review_fields`: `examples/79_final_output_output_schema`, `examples/82_review_final_output_prose_basic` through `examples/86_imported_review_comment_local_routes`, `examples/90_split_handoff_and_final_output_shared_route_semantics`, `examples/91_handoff_routing_route_output_binding`, and `examples/104_review_final_output_output_schema_blocked_control_ready` through `examples/106_review_split_final_output_output_schema_partial`.
  - Replace matching VS Code prompt fixtures and snapshots that mirror those examples.
- Live docs, comments, and instructions to update or delete:
  - `README.md`
  - `docs/README.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/REVIEW_SPEC.md`
  - `docs/WORKFLOW_LAW.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - `make verify-diagnostics`
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `make verify-package`
  - `cd editors/vscode && make`

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Review and split-final semantics | `doctrine/_model/review.py`, `doctrine/_compiler/resolve/reviews.py`, `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/final_output.py`, `tests/test_review_imported_outputs.py`, `tests/test_final_output.py`, `docs/REVIEW_SPEC.md` | One accepted v2 semantic package | Prevent another split truth between review carriers, final output, and public docs | include |
| Shared registry and identity | `doctrine/_compiler/indexing.py`, `session.py`, `context.py`, `resolved_types.py` | Reuse the existing compiler spine as the canonical owner path | Prevent a sidecar v2 compiler and duplicate identity logic | include |
| Payload naming and schema truth | `doctrine/grammars/doctrine.lark`, `doctrine/_compiler/resolve/refs.py`, `doctrine/_compiler/output_schema_validation.py`, `doctrine/emit_docs.py`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, `editors/vscode/syntaxes/doctrine.tmLanguage.json` | One final payload naming rule across compiler, emitters, docs, and editor support | Prevent owner-sensitive drift around `schema`, `output schema`, and `payload_schema` | include |
| Diagnostics and migration messaging | `doctrine/_compiler/validate/*.py`, `docs/COMPILER_ERRORS.md`, `make verify-diagnostics`, VS Code snapshots | One explicit warning and error story for v2 migration | Prevent compiler, docs, and editor drift on the public diagnostics surface | include |
| Package and smoke truth | `doctrine/_package_release.py`, `doctrine/validate_output_schema.py`, `doctrine/prove_output_schema_openai.py`, `doctrine/_diagnostic_smoke/*.py` | One v2 package scaffold and proof-helper story | Prevent public helpers from quietly teaching retired syntax after the compiler changes | include |
| Authoring docs and numbered examples | `docs/README.md`, `docs/AUTHORING_PATTERNS.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `examples/68_*`, `69_*`, `74_*`, `79_*`, `82_*` through `86_*`, `90_*`, `91_*`, `104_*` through `106_*` | Rewrite or delete stale live truth in the same cutover | Prevent the docs index and flagship examples from becoming a shadow v1 language | include |
| Public release truth | `docs/VERSIONING.md`, `CHANGELOG.md`, `tests/test_release_flow.py`, `tests/test_package_release.py` | One honest breaking-release story | Prevent a compiler cutover with stale release guidance | include |
| Import aliasing and package barrels | future import and package surfaces | Extension-wave namespace work only after the core identity model is stable | Prevent the core cutover from reopening namespace design too early | defer |
| Parameterization and mixins | future param and mixin surfaces | Extension-wave abstraction work only after registry and patch stability | Prevent a second inheritance or identity system from sneaking into core v2 | defer |
| Protocols and bounded history | future protocol and history surfaces | Keep these outside the first breaking cut unless later evidence justifies them | Prevent runtime-bound or speculative scope creep | defer |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: build the redesign foundation first, keep Section 7 as the one execution checklist, and bias toward smaller coherent phases instead of blended ones. `Work` explains the unit. `Checklist (must all be done)` is the authoritative must-do list. `Exit criteria (all required)` names the concrete done state. No phase may hide unresolved branch choices, soft shims, or stale live-truth cleanup. A phase is not ready to start or finish until its `Verification (required proof)` block names exact repo commands, exact test modules, or exact example manifests. Phrases like targeted tests, focused cases, representative commands, minimal slice, and spot-check do not count by themselves.

Core phases 1 through 14 are the implementation contract for the first public Doctrine v2 release. They are implementation-ready only because this section now freezes exact selector syntax, review and final-output syntax, core route-selection syntax, keyed control-family inventories, public Python API rules, migration-tool policy, release target, and hard proof bars. Implementation starts at Phase 2, not Phase 1. Phase 1 remains as the closed contract-freeze record that implementation must preserve. The material below Phase 14 is backlog only. It is not approved implementation work in this plan and must not quietly slide into the core cutover.

## Phase 9 - Rebuild review compile, final-output binding, and concrete-turn orchestration

### Goal

Collapse the current split review owner path into one accepted v2 review semantic package.

### Work

- Rebuild `doctrine/_compiler/compile/reviews.py`, `doctrine/_compiler/resolve/reviews.py`, and `doctrine/_compiler/validate/review_*` around the locked v2 review grammar plus the frozen semantic contract.
- Rebuild projected final outputs so they read from agent-local named projections instead of hidden review-only special cases.
- Rebuild blocked pre-contract review behavior so ordered `checks` can produce first-class blocked branches with stable `blocked_gate` semantics instead of fake rejects.
- Compile the resolved v2 review-control metadata that Phase 11 will emit through `final_output.contract.json`.
- Refactor `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/final_output.py`, and `doctrine/_compiler/compile/agent.py` so `compile/agent.py` becomes orchestration-only.

### Checklist (must all be done)

- [ ] Review compilation uses the accepted v2 review grammar exactly.
- [ ] Review validation enforces the accepted producer-local semantic model.
- [ ] Case-selected reviews, `handoff_first`, and ordered `checks` compile and validate under one rule set.
- [ ] Blocked pre-contract reviews remain first-class compiler truth and produce stable `blocked_gate` semantics instead of reject semantics.
- [ ] Split final outputs bind through agent-local named projections, not reusable output-owned projection state.
- [ ] `control_ready` is explicit and validated from projected semantic fields across live branches.
- [ ] `compile/review_contract.py`, `compile/final_output.py`, and `compile/agent.py` no longer preserve a second hidden semantic fork.
- [ ] No review-driven final-output path still depends on `final_output.review_fields`.
- [ ] Review remains the only core semantic producer.
- [ ] Resolved review artifacts expose enough carrier and projected-final metadata for the accepted versioned `final_output.contract.json` contract.

### Verification (required proof)

- `tests/test_final_output.py`
- `tests/test_review_imported_outputs.py`
- `tests/test_emit_flow.py`

### Docs/comments (propagation; only if needed)

- Add one high-leverage comment at the review or concrete-turn orchestration seam if the new ownership line would otherwise be easy to regress.

### Exit criteria (all required)

- Review compilation and validation no longer depend on a hidden v1 semantic split.
- No split-final feature depends on hidden v1 ownership.
- Concrete-turn orchestration consumes resolved v2 artifacts instead of reconstructing semantic truth.

### Rollback

- None. This is part of the core cutover.

## Backlog after `2.0.0` (not execution-ready in this plan)

These notes preserve the accepted follow-on order, but they are not approved implementation phases in this plan. Reopen any of them only after the first public `2.0.0` release, with a new plan doc and a new Section 10 decision entry.

### Backlog note A - expression conveniences

- Candidate surfaces: `let`, quantifiers, read-only `@` mentions, and `display_title` only if it stays render-only.
- Reopen rule: these surfaces must reuse the shipped v2 expression, path, and identity model exactly. They must not reopen core selector, route, title, or semantic-readback rules.

### Backlog note B - native data and typed file roots

- Candidate surfaces: native `data`, `type:` integration, `path_root`, and typed file paths.
- Reopen rule: keep the extension-spec rules intact for closed objects, required fields by default, field-order preservation, `type:` versus `payload_schema:` exclusivity, host-bound resolution, and the ban on `..`.

### Backlog note C - import aliasing and package barrels

- Candidate surfaces: import aliasing, selective imports, and package barrels.
- Reopen rule: no wildcard imports, no alias collisions, no declaration-identity drift, and barrels become the stable public namespace only when a later plan closes the grammar.

### Backlog note D - parameterization and mixins

- Candidate surfaces: parameterized declarations and family-local mixins.
- Reopen rule: keep stable instantiated identity, named-only args, no concrete parameterized `agent` declarations in the first shipped form, and no second inheritance system.

### Backlog note E - protocols and bounded history

- Candidate surfaces: `protocol` and `source: History`.
- Reopen rule: only if a later plan proves they still fit Doctrine's authoring boundary and do not reopen runtime-state ownership.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

This section is a shared verification summary only. It does not relax any phase-gated proof or acceptance rule from Sections 0 or 7.

- Use targeted unit tests for parser, model, resolver, validation, review semantics, route semantics, final output, and payload schema work as the code changes land.
- Keep the manifest-backed corpus as the main integration proof and run `make verify-examples` for the full cutover.
- Run `make verify-diagnostics` when diagnostics or error docs change.
- Run the schema proof-helper tests and package smoke checks when machine-payload contracts or helper CLIs change.
- Run `cd editors/vscode && make` when the editor surface changes.
- Run `make verify-package` for package metadata, publish-flow, or public-install changes.
- Run `uv run --locked python -m unittest tests.test_release_flow` if release flow or release policy changes.
- When a phase needs direct emit or docs sanity checks, use the rewritten flagship example families from Section 6.2: `68_*`, `69_*`, `74_*`, `79_*`, `82_*` through `86_*`, `90_*`, `91_*`, and `104_*` through `106_*`.
- Do not add ceremony-only repo-policing checks to prove elegance.

# 9) Rollout / Ops / Telemetry

- Rollout shape: land v2 as one coordinated breaking cutover, not as a long-lived mixed-language mainline.
- Ops burden is repo-local, not production runtime telemetry. The key signals are corpus proof, targeted tests, editor alignment, and package-release proof.
- If a narrow bridge is later approved, it must be timeboxed, logged in Section 10, and deleted before the final v2 stable release.
- If a later phase uncovers a contradiction large enough to change scope or compatibility posture, update this plan and the decision log before more code lands.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, helper blocks, `# TL;DR`, and Sections `0` through `10`
  - cross-section agreement on scope, owner path, compatibility posture, migrations, deletes, verification burden, and execution order
- Findings summary:
  - the pass first found an open contradiction set in Section 3.3 while Section 7 still looked close to implementation-ready
  - route semantics, review semantics, and split-final ownership were still blended across multiple compiler stages instead of one owned execution sequence
  - doc, release, and package obligations were weaker in the phase plan than in the call-site audit
  - the helper-block stage order had drifted from the actual planning flow
- Integrated repairs:
  - marked external research as not needed for this pass, added `consistency_pass: done`, and updated the recommended stage order
  - folded in accepted decisions on semantic ownership, `review_family`, review grammar, schema naming, selector binding, decisions identity, `route_only emits`, and the extension cut line
  - made Section 7 say plainly that only Phases 1 through 14 are executable in this plan, and that implementation starts at Phase 2
  - split the core cutover into smaller owned phases for grammar and parser, typed model, compiler inventories, machine payload contracts, selectors and identity, semantic or projection contract freeze, review lowering, review compile plus final-output binding, route or control normalization, emitters and helpers, proof, docs and editor, then release
  - made the doc list from Section 6.2, package helper truth, and release truth explicit must-do work in the later core phases
  - clarified that Section 8 is a shared proof summary, not a way around phase-gated verification
  - locked exact selector binder syntax, exact agent-local `final_output.project` syntax, the explicit `control_ready` field-totality rule, the direct core `route_from` surface, keyed control-family inventories, the `doctrine/model.py` public API policy, optional rewrite-tool policy, the `2.0.0` release target, and the rule that backlog notes after Phase 14 are not executable in this plan
- Remaining inconsistencies:
  - none in owned Sections 0 through 10 for core Phases 1 through 14; verbatim folded source blocks later in the file intentionally preserve superseded draft syntax and are not executable truth
- Unresolved decisions:
  - none in core Phases 1 through 14
- Unauthorized scope cuts:
  - none
- Decision-complete:
  - yes
- Decision: proceed to implement? yes, for core Phases 2 through 14 only
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

- 2026-04-15: Treat this work as Doctrine v2, a breaking major language cutover. Default compatibility posture is a clean cutover, not a soft bridge.
- 2026-04-15: Keep the implementation on the existing `doctrine/` owner path unless later repo evidence proves that impossible.
- 2026-04-15: Fold `docs/LANGUAGE_REDESIGN_SPEC.md` and `docs/LANGUAGE_REDESIGN_EXT_SPEC.md` into this plan doc so the redesign source cannot be missed.
- 2026-04-15: The contradiction set in Section 3.3 is a readiness blocker. No implementation phase may claim completion by coding around those decisions.
- 2026-04-15: The first stable v2 release is the base redesign only. Extension-spec features are out of scope for `2.0.0` and require a later plan after `2.0.0`.
- 2026-04-15: Superseding the earlier softer staging note, no extension-spec surface may be pulled into this plan's `2.0.0` core cut. Any extension work requires a later plan after `2.0.0`.
- 2026-04-15: North Star approved. The canonical plan doc is now active and may drive `auto-plan`.
- 2026-04-15: Deep-dive pass 1 locked the existing `doctrine/_compiler` spine as the canonical v2 owner path and named the review plus split-final package as the first major semantic migration front.
- 2026-04-15: Deep-dive pass 2 hardened the architecture around three extra public seams: `doctrine/_compiler/compile/agent.py` as the concrete-turn orchestration seam, `doctrine/model.py` as the public model export surface, and `docs/COMPILER_ERRORS.md` plus `editors/vscode/README.md` as live truth that must cut over with the compiler.
- 2026-04-15: Phase-plan locked Section 7 as the owned execution checklist, made Phase 1 the gate for all contradiction decisions, and pulled route semantics plus emitted flow truth into an explicit core delivery phase instead of leaving that work smeared across review and docs phases.
- 2026-04-15: Semantic ownership is producer-local. Reusable `output` declarations do not own semantic projection binding.
- 2026-04-15: `review_family` is removed. `abstract review` is the only incomplete reusable review surface.
- 2026-04-15: Core review grammar is `carrier`, `emits`, optional `selector`, optional `handoff_first`, `checks`, `on_accept`, `on_reject`, and optional `cases`. Separate `basis_checks` and `contract_checks` sections are removed.
- 2026-04-15: `payload_schema:` is the only JSON payload attachment name. `json schema` remains the machine declaration family, and ordinary `schema` remains the Doctrine-readable declaration family.
- 2026-04-15: `where(...)` requires an explicit item binder. Bare item-local names are not legal.
- 2026-04-15: Core v2 uses keyed `decisions:` blocks only. `decision:` sugar is removed from the core cutover.
- 2026-04-15: `route_only emits` is deferred beyond first-release v2. Review remains the only core semantic producer.
- 2026-04-15: No extension-spec features are in core v2. The first follow-on candidates are niceties like `let` and quantifiers. Parameterization, mixins, protocols, and bounded history are deferred until a later plan reopens them.
- 2026-04-15: Consistency-pass repaired stage-order drift, folded the accepted decision set into Sections 3.3, 5, 7, and 10, forced route, review, and split-final ownership into explicit core phases, and tightened the doc, package, helper, and release obligations in later core phases. The artifact is now decision-complete and may proceed to implementation at Phase 2.
- 2026-04-15: Additional deep-dive hardening widened the owned architecture to include `compile/reviews.py`, `resolve/output_schemas.py`, diagnostics message builders, package scaffolds, schema proof helpers, diagnostic smoke fixtures, and live authoring notes as part of the same contract family.
- 2026-04-15: Additional phase-plan hardening split the core cutover into smaller enforceable units: grammar and parser, typed model, compiler inventories, machine payload contracts, selectors and identity, review declaration lowering, review compile core, projection and final-output binding, route or control normalization, emitters and helpers, proof, docs and editor, then release cutover. Only two follow-on passes are approved by default.
- 2026-04-15: Hardening pass locked exact selector binder syntax, exact agent-local `final_output.project` syntax, the explicit `control_ready` field-totality rule, the direct core `route_from` surface, keyed control-family inventories, the `doctrine/model.py` public API policy, the optional rewrite-tool policy, and the `2.0.0` release target.
- 2026-04-15: Section 7 is executable only through Phase 14. Material after Phase 14 is backlog only and requires a new plan after the first public `2.0.0` release.
- 2026-04-15: Rally compatibility hardening locked `final_output.contract.json` as a surviving public machine-readable artifact in `2.0.0`, bumped it to `contract_version: 2`, and froze the v2 review metadata around `review.carrier` plus `review.final_output_projection`.
- 2026-04-15: Rally compatibility hardening also closed blocked pre-contract review behavior: ordered `checks` absorbs former `basis_checks`, `block` remains a first-class blocked branch, and `blocked_gate` stays explicit compiler and host-facing truth.

<!-- arch_skill:block:reference_pack:start -->
