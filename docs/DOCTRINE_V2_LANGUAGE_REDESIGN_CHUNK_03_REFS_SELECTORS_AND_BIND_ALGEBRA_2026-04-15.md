---
title: "Doctrine - V2 Language Redesign - Chunk 03 - Refs Selectors And Bind Algebra"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
source_plan: docs/DOCTRINE_V2_LANGUAGE_REDESIGN_PLAN_2026-04-15.md
chunk_order: 3
depends_on:
  - docs/DOCTRINE_V2_LANGUAGE_REDESIGN_CHUNK_02_INHERITANCE_AND_PAYLOAD_CONTRACT_CLEANUP_2026-04-15.md
primary_phases:
  - 6
shared_ship_phases:
  - 11
  - 12
  - 13
  - 14
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

## Phase 6 - Rebuild refs, selectors, binds, and canonical identity

### Goal

Ship one identity, path, selector, and bind story for v2.

### Work

- Rework name resolution for the accepted v2 declaration set.
- Implement the final bound-root identity model, including normalization for identity and overlap checks, diagnostics that show `alias -> CanonicalDecl`, and rendered markdown that keeps the local bound title.
- Implement selector parsing, explicit-binder semantics, ordered `many` descendants, and evaluation exactly for `first`, `last`, `only`, `nth`, and `where(item => expr)`.
- Preserve left-to-right selector execution and the compile-time versus runtime failure split.

### Checklist (must all be done)

- [ ] Canonical identity rules are explicit in the resolver.
- [ ] Selector grammar and `many` descendants ship together.
- [ ] Selector and bind semantics are implemented.
- [ ] Left-to-right selector execution and explicit `where(item => expr)` binding rules are implemented.
- [ ] Compile-time selector failures and runtime contract failures are distinct and documented.
- [ ] Diagnostics explain ambiguous or invalid selector usage, including canonical alias display.
- [ ] Bound-root behavior is consistent across law, review, and emitted surfaces.
- [ ] The base-spec selector non-goals are preserved: no `before(...)`, no `after(...)`, and no selectors over unmodeled trees.

### Verification (required proof)

- `tests/test_compiler_boundary.py`
- `tests/test_review_imported_outputs.py`
- `tests/test_route_output_semantics.py`

### Docs/comments (propagation; only if needed)

- Add succinct comments only at the canonical alias-normalization and selector-evaluation boundaries if the final rules are not obvious from the code.

### Exit criteria (all required)

- Path, selector, and identity semantics are stable enough that higher-level control-plane features no longer need local resolver exceptions.

### Rollback

- None beyond branch-local revert. Do not ship partial selector semantics.

## Phase 11 - Rebuild emitters, diagnostics, helper CLIs, and smoke fixtures

### Goal

Make public emitted artifacts, diagnostics, helper CLIs, and smoke fixtures truthful to the v2 compiler semantics.

### Work

- Rewrite Markdown, flow, skill, and `final_output.contract.json` emission on top of the v2 review and route semantics.
- Rework diagnostics, error docs, and message builders for v2 names and migration behavior.
- Rewrite `_package_release.py`, `validate_output_schema.py`, `prove_output_schema_openai.py`, and `_diagnostic_smoke/*.py` to the accepted v2 language.

### Checklist (must all be done)

- [ ] Emit surfaces describe v2 truth.
- [ ] `final_output.contract.json` emits the accepted v2 host-facing metadata contract with `contract_version: 2`.
- [ ] Diagnostics are updated and documented, including alias normalization and migration-warning families.
- [ ] Example warning messages and docs match the accepted migration story.
- [ ] Package scaffolds, schema proof helpers, and smoke fixtures stop teaching retired public nouns.
- [ ] Emitted flow matches the route truth already established earlier in the plan.

### Verification (required proof)

- `tests/test_emit_docs.py`
- `tests/test_emit_flow.py`
- `tests/test_emit_skill.py`
- `tests/test_validate_output_schema.py`
- `tests/test_prove_output_schema_openai.py`
- `make verify-diagnostics`

### Docs/comments (propagation; only if needed)

- Update `docs/COMPILER_ERRORS.md` in the same phase as the error-surface change.

### Exit criteria (all required)

- Public emitted artifacts, diagnostics, package helpers, and smoke fixtures no longer describe v1 behavior.
- No shipped helper output silently reintroduces retired public family names.

### Rollback

- None. Public output drift is not acceptable at this stage.

## Phase 12 - Rewrite the corpus, focused proof, and emitted refs

### Goal

Move the proof ladder to v2 so the compiler, emitted refs, and examples all prove the same language.

### Work

- Rewrite the numbered corpus to the accepted v2 language.
- Replace or delete the flagship v1 examples and their invalid cases that freeze `review_family`, repeated `decision:`, `output schema`, or old review/final-output nouns.
- Regenerate emitted refs and build refs that are part of the shipped proof story.

### Checklist (must all be done)

- [ ] The numbered examples and manifests reflect v2.
- [ ] High-priority example families listed in Section 6.2 are replaced or rewritten.
- [ ] Invalid-case proof still exists for the same contract boundaries after the rewrite.
- [ ] Emitted refs and build refs match the accepted language.
- [ ] Focused proof files no longer freeze retired public family names as expected truth.

### Verification (required proof)

- `make verify-examples`
- `tests/test_verify_corpus.py`
- `tests/test_emit_docs.py`
- `tests/test_emit_flow.py`

### Docs/comments (propagation; only if needed)

- Update example-local notes only when they explain real surviving v2 behavior.

### Exit criteria (all required)

- The proof ladder now proves v2 instead of silently snapshotting v1.
- Example refs, build refs, and focused tests agree with emitted v2 behavior.

### Rollback

- None. Proof has to move with the language.

## Phase 13 - Rewrite live docs and editor support

### Goal

Move every live teaching, authoring, and editor surface to v2.

### Work

- Rewrite live docs and authoring notes to the v2 contract.
- Rewrite VS Code syntax, resolver behavior, tests, snapshots, and alignment tooling to the v2 grammar.
- Delete dead live explanations instead of archiving them.

### Checklist (must all be done)

- [ ] `README.md`, `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/WORKFLOW_LAW.md`, `docs/EMIT_GUIDE.md`, `docs/COMPILER_ERRORS.md`, `docs/AUTHORING_PATTERNS.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `examples/README.md`, and `editors/vscode/README.md` are rewritten or deleted so they no longer teach v1.
- [ ] `docs/EMIT_GUIDE.md` and `docs/VERSIONING.md` state plainly that `final_output.contract.json` stays public in v2, moves to `contract_version: 2`, and is the host-facing machine contract for review-control metadata.
- [ ] VS Code support reflects v2.
- [ ] No live doc, authoring note, example guide, or editor surface in the Section 6.2 list still teaches v1.
- [ ] VS Code prompt fixtures and snapshots that mirror rewritten examples are updated in the same cutover.

### Verification (required proof)

- `cd editors/vscode && make`
- `make verify-examples`

### Docs/comments (propagation; only if needed)

- Delete dead live explanations instead of archiving them. Rewrite surviving docs and editor surfaces to present truth.

### Exit criteria (all required)

- A reader who starts from the repo docs, examples, or editor docs sees one coherent v2 language.
- No live authoring surface is a shadow v1 reference.

### Rollback

- None. Live v1 docs must not survive a v2 cutover.

## Phase 14 - Finish the breaking-release cutover

### Goal

Ship the repo truth as Doctrine v2 with honest breaking-change guidance.

### Work

- Update language version and release-version guidance around the explicit `2.0.0` cutover target.
- Write exact upgrade steps, before or after examples, and surface-by-surface migration notes for alias behavior, selector runtime-failure behavior, review-surface replacement, and any surviving helper migration.
- Update `pyproject.toml`, package metadata, and release tests where needed.

### Checklist (must all be done)

- [ ] `docs/VERSIONING.md` reflects v2 breaking posture.
- [ ] `CHANGELOG.md` carries the v2 breaking-change payload.
- [ ] `pyproject.toml`, package metadata, and release-flow surfaces are aligned on `2.0.0`.
- [ ] Upgrade guidance is explicit and verifiable.
- [ ] Upgrade guidance includes the `final_output.contract.json` break: `contract_version: 2`, removed v1 review keys, and the new `review.carrier` plus `review.final_output_projection` contract.
- [ ] The release notes state plainly that no rewrite tool is required for `2.0.0`, and explain any optional helper honestly if one ships.
- [ ] Release helper output matches the same public language names used everywhere else.

### Verification (required proof)

- `make verify-package` when package or public install surfaces change
- `uv run --locked python -m unittest tests.test_release_flow` when release flow or release policy changes

### Docs/comments (propagation; only if needed)

- Keep release notes, upgrade guidance, and any release helper output aligned in the same phase.

### Exit criteria (all required)

- The repo can truthfully publish Doctrine v2 without silent breakage.
- The package surface, release-flow proof, and public install truth all match the v2 breaking-release story.

### Rollback

- Fix forward with plan and docs truth. Do not hide breakage in release notes.

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
# Reference Pack (folded materials; phase-aligned)
Updated: 2026-04-15

## Inventory
- R1 — Doctrine redesign full spec — docs/LANGUAGE_REDESIGN_SPEC.md
- R2 — Doctrine redesign extension spec — docs/LANGUAGE_REDESIGN_EXT_SPEC.md

The folded R1 and R2 blocks below preserve source text exactly, including draft syntax that the accepted plan later rejects. They are reference inputs, not executable v2 truth. When they differ from Sections 3.3, 7, or 10, the owned plan sections win.

## Binding obligations (distilled; must satisfy)
- Resolve the base-spec contradiction set before code starts: semantic ownership, `review_family`, compatibility posture, schema naming, selector binder semantics, and normative example drift. (From: R1)
- Treat Doctrine v2 as a clean, coherent language contract with one patch algebra, one path algebra, and one semantic ownership story. (From: R1)
- Do not let compatibility-cycle sugar or aliases survive by default just because they are written in the base spec. This plan must choose the final cutover posture explicitly. (From: R1)
- Rebuild review, final-output, and route semantics only after one full replacement grammar exists for the shipped review pipeline. (From: R1)
- Stage extension features honestly. Do not force parameterization, mixins, package barrels, protocols, or bounded-history surfaces into this plan's first stable v2 cut. They require a later plan after `2.0.0`. (From: R2 as narrowed by Section 3.3 and the Decision Log)
- Keep extension waves ordered by architectural risk: expression conveniences first, data and paths next, import and package composition after that, name-registry-heavy abstractions last. (From: R2)

## Instruction-bearing structure (only when present; preserve exact or equivalent operational form)
### R1 — Doctrine redesign full spec
1. Freeze phase choice and compatibility posture.
2. Add rich inheritance parity and shared patch rules.
3. Add selectors, `binds`, and collection descendants.
4. Rebuild review semantics through `semantic` and `projection`.
5. Remove `review_family` or replace it coherently.
6. Normalize `route_only`, `grounding`, `decision`, and payload-schema naming.
7. Finish canonical alias semantics, diagnostics, migration guidance, and the worked example.
- Hard negatives:
  - No owner-sensitive keyword overload.
  - No implicit merge or append semantics in the shared patch law.
  - No hidden readiness inference when control-readiness is claimed.
### R2 — Doctrine redesign extension spec
1. Keep the base redesign authoritative.
2. Add later abstractions only on top of the accepted base semantics.
3. Introduce expression conveniences before heavier library and name-registry features.
4. Keep protocols and bounded history as late, skeptical surfaces.
- Hard negatives:
  - Do not reopen base redesign choices from the extension doc.
  - Do not treat additive extensions as justification for a second inheritance or routing system.

## Phase alignment guidance (advisory; core planning commands adopt into Section 7 if needed)
### Global (applies across phases)
- Keep the base redesign and extension doc folded into the canonical plan so contradictions stay visible. (From: R1, R2)
- Prefer hard cutover and explicit deletes over runtime shims. (From: R1)
- Keep extension work out of the executable core cut in this plan. Any later adoption needs a new post-`2.0.0` plan. (From: R2 as narrowed by Section 3.3 and the Decision Log)

### Phase 1 — Freeze the accepted Doctrine v2 contract
- Potentially relevant obligations (advisory):
  - Close the contradiction set and choose the extension cut line. (From: R1, R2)
- References:
  - R1, R2

### Phase 2 through Phase 14 — Core v2 cutover
- Potentially relevant obligations (advisory):
  - Implement the accepted base redesign without reopening later extension debates. (From: R1)
- References:
  - R1

### Backlog after Phase 14 — Later extension work only
- Potentially relevant obligations (advisory):
  - Land extension features in risk order and only after the core language is stable. (From: R2)
- References:
  - R2

## Exhaustive adoption ledger (every numbered section and subsection)

This ledger is exhaustive for the numbered sections and numbered subsections in `R1` and `R2`.
The verbatim source text still follows below.
Rendered sample headings such as `## Inputs`, `## Outputs`, and other example-only nested headings stay preserved verbatim under their owning example sections. They are not omitted from the artifact. They are treated as subordinate to the numbered example subsection that contains them.

### R1 — Doctrine redesign full spec

| Section | Disposition | Phase | Note |
| --- | --- | --- | --- |
| `0. Phase choice and compatibility` | Accept with rewrite before v2.0 | Phase 1 | Keep the hard v2 cutover. Remove the compatibility-cycle alias story. |
| `1. Rich declaration inheritance parity` | Accept for v2.0 | Phase 2 / Phase 5 | This is core to the v2 language shape. |
| `1.1 Problem` | Accept for v2.0 | Phase 1 | Keep as justification for parity. |
| `1.2 General syntax` | Accept with rewrite before v2.0 | Phase 2 | Final syntax must match the accepted family inventory and declaration headers. |
| `1.3 Patch algebra` | Accept for v2.0 | Phase 2 | This is one of the main architectural anchors. |
| `1.4 Input inheritance` | Accept with rewrite before v2.0 | Phase 5 | The current normative example violates the stated patch law. |
| `1.5 Output inheritance` | Accept for v2.0 | Phase 5 | Keep, but make it agree with the final semantic-ownership model. |
| `1.6 Skill inheritance` | Accept for v2.0 | Phase 5 | Keep on the shared patch engine. |
| `1.7 Decision inheritance` | Accept for v2.0 | Phase 10 | Keep, but resolve local identity and attachment rules. |
| `1.8 Route-only inheritance` | Accept with rewrite before v2.0 | Phase 10 | Keep inheritance parity, but do not let this section pre-decide `route_only emits`. |
| `1.9 Grounding inheritance` | Accept with rewrite before v2.0 | Phase 10 | Keep inheritance parity, but only after the grounding normalization contract is closed. |
| `2. Decisions blocks` | Accept with rewrite before v2.0 | Phase 10 | Keep the block, but resolve unnamed-sugar identity first. |
| `2.1 Problem` | Accept for v2.0 | Phase 1 | Valid motivation. |
| `2.2 New surface` | Accept with rewrite before v2.0 | Phase 10 | Keep only if every attached decision gets a real stable local key. |
| `2.3 Example usage` | Accept as illustrative only after parent semantics are closed | Phase 10 | Rewrite once the identity rule is fixed. |
| `2.4 How it works` | Accept with rewrite before v2.0 | Phase 10 | The sugar story must not contradict the stable-key claim. |
| `2.5 Best-case rendered markdown` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Render output must follow the final attachment model. |
| `3. Selector algebra and collection descendants` | Accept for v2.0 | Phase 6 | This is core to the redesign. |
| `3.1 Problem` | Accept for v2.0 | Phase 1 | Valid motivation. |
| `3.2 New path syntax` | Accept with rewrite before v2.0 | Phase 6 | Freeze the required `where(item => expr)` binder syntax. |
| `3.3 Ordered collection descendants` | Accept for v2.0 | Phase 6 | Keep if the typed path model can own it cleanly. |
| `3.4 Selector semantics` | Accept with rewrite before v2.0 | Phase 6 | Item-local name resolution must be explicit. |
| `3.5 Static and runtime validation` | Accept for v2.0 | Phase 6 | Keep, with concrete diagnostics. |
| `3.6 General binds block` | Accept for v2.0 | Phase 6 | Core to the base redesign. |
| `3.7 Example usage: bind a review to the latest rejected review in a file` | Accept as illustrative only after parent semantics are closed | Phase 6 / Phase 12 | Rewrite after selector and review semantics are final. |
| `3.8 Example usage inside a review` | Accept as illustrative only after parent semantics are closed | Phase 6 / Phase 12 | Rewrite after review grammar closes. |
| `3.9 Best-case rendered markdown` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Output must come from the final resolver and renderer. |
| `3.10 Non-goals in this phase` | Accept for v2.0 | Phase 1 | Keep as scope guard unless later explicitly reopened. |
| `4. Semantic records and projections` | Accept with rewrite before v2.0 | Phase 7 | Core idea is accepted. Use producer-local binding and the locked review grammar. |
| `4.1 Problem` | Accept for v2.0 | Phase 1 | Valid motivation. |
| `4.2 New declarations` | Accept with rewrite before v2.0 | Phase 7 | Keep if `semantic` and `projection` remain the accepted abstraction. |
| `4.3 Producer binding: carrier plus emits` | Accept with rewrite before v2.0 | Phase 7 | Keep `carrier` plus `emits` in the locked core review grammar. |
| `4.4 Output projection: project` | Accept with rewrite before v2.0 | Phase 7 | Keep producer-local binding in `agent.final_output`. Do not let reusable outputs own projection binding. |
| `4.5 Review example` | Accept as illustrative only after parent semantics are closed | Phase 12 | Rewrite after the replacement review grammar is final. |
| `4.6 Partial projection` | Accept with rewrite before v2.0 | Phase 7 | Keep only if projection remains the chosen split-final mechanism. |
| `4.7 Control readiness` | Accept with rewrite before v2.0 | Phase 7 | Keep explicit control-readiness only if it survives as a real validator contract. |
| `4.8 Best-case rendered markdown: control-ready projection` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Renderer output depends on the final semantic ownership model. |
| `4.9 Best-case rendered markdown: partial projection` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Same dependency as `4.8`. |
| `5. Remove review_family` | Accept for v2.0 | Phase 8 | Replace it with `abstract review` as the only incomplete reusable review surface. |
| `5.1 Problem` | Accept for v2.0 | Phase 1 | Valid motivation. |
| `5.2 New rule` | Accept for v2.0 | Phase 1 | Only `abstract review` may be incomplete. |
| `5.3 Direct replacement: shared review scaffold` | Reject as written; replace with cleaner rule | Phase 1 | The example uses an incomplete plain `review` in conflict with the stated rule. |
| `5.4 Direct replacement: case-selected scaffold` | Accept with rewrite before v2.0 | Phase 8 / Phase 9 | Keep only after the final review grammar is closed. |
| `5.5 How it works` | Accept with rewrite before v2.0 | Phase 9 | The "purely linguistic cleanup" claim is too strong until the compiler and model path are proven. |
| `5.6 Best-case rendered markdown` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Keep only after replacement semantics are implemented. |
| `6. Route-only and grounding normalization` | Accept with rewrite before v2.0 | Phase 10 | Normalization is in scope. The semantic-producer story must be narrowed. |
| `6.1 Route-only semantic projection` | Defer the `emits` part to later wave unless Phase 1 chooses otherwise | Phase 10 or later | Default recommendation: keep `route_only` normalization in v2.0 and defer route-only semantic emission until after core review semantic cutover. |
| `6.2 Grounding mapping remains a preservation target` | Accept for v2.0 | Phase 10 | Fits the normalization story. |
| `6.3 Best-case rendered markdown: route-only` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Must reflect the final route-only contract, not the current contradictory one. |
| `6.4 Best-case rendered markdown: grounding` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Same dependency as `6.3`. |
| `6.5 Phase-2 note` | Accept for later wave consideration | Phase 1 / later | Keep as a non-binding later possibility only. |
| `7. Schema naming cleanup` | Accept with rewrite before v2.0 | Phase 5 | Use `payload_schema:` plus `json schema` and ordinary `schema`. |
| `7.1 Problem` | Accept for v2.0 | Phase 1 | Valid motivation. |
| `7.2 New rule` | Accept for v2.0 | Phase 1 | The naming rule is closed in the decision log. |
| `7.3 Syntax` | Accept for v2.0 | Phase 1 | Remove `output schema` and use `json schema` plus `payload_schema:`. |
| `7.4 Rendering rules` | Accept with rewrite before v2.0 | Phase 11 | Renderer labels follow the final schema-family decision. |
| `7.5 Best-case rendered markdown` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Keep only after the final naming rule is chosen. |
| `8. Canonical alias semantics for bound roots` | Accept for v2.0 | Phase 6 | Matches the repo owner-path direction. |
| `8.1 Problem` | Accept for v2.0 | Phase 1 | Valid motivation. |
| `8.2 New rule` | Accept for v2.0 | Phase 6 | Keep in the resolver and diagnostics core. |
| `8.3 Example` | Accept as illustrative only after parent semantics are closed | Phase 6 / Phase 12 | Rewrite after the final identity and law-path model is implemented. |
| `8.4 Best-case rendered markdown` | Accept as illustrative only after parent semantics are closed | Phase 11 / Phase 12 | Renderer output follows the final alias model. |
| `9. Diagnostics and migration` | Accept with rewrite before v2.0 | Phase 11 / Phase 14 | Keep the structure, but rewrite it for the actual accepted cutover story. |
| `9.1 Phase boundaries` | Accept for v2.0 | Phase 11 | Keep as compiler hygiene. |
| `9.2 New or revised compile diagnostics` | Accept with rewrite before v2.0 | Phase 11 | Final families depend on the closed v2 contract. |
| `9.3 Required new diagnostics` | Accept with rewrite before v2.0 | Phase 11 | Keep, but only for features that survive the cut line. |
| `9.4 Example migration messages` | Accept with rewrite before v2.0 | Phase 14 | Messages must reflect the real cutover posture, not speculative compatibility shims. |
| `10. Full worked example` | Accept as illustrative only after parent semantics are closed | Phase 12 | Rewrite only after the accepted v2 language is implemented. |
| `10.1 Doctrine source` | Accept as illustrative only after parent semantics are closed | Phase 12 | Same dependency as `10`. |
| `10.2 Best-case rendered markdown` | Accept as illustrative only after parent semantics are closed | Phase 12 | Same dependency as `10`. |
| `11. Summary of what changes materially` | Accept with rewrite before v2.0 | Phase 14 | Keep as the final migration summary once every contradiction is closed. |

### R2 — Doctrine redesign extension spec

The `Phase` column for `R2` rows names backlog buckets after `2.0.0`, not executable Section 7 phases in this plan.

| Section | Disposition | Phase | Note |
| --- | --- | --- | --- |
| `0. Extension scope` | Accept for later waves | Phase 1 | Keep as the staging contract for non-core surfaces. |
| `1. Parameterized declarations` | Defer to extension wave 4 | Phase 12 | High leverage, but too risky for the first stable v2 cut. |
| `1.1 Syntax` | Defer to extension wave 4 | Phase 12 | Depends on stable instantiated identity and indexing. |
| `1.2 How it works` | Defer to extension wave 4 | Phase 12 | Same dependency as `1.1`. |
| `1.3 Example usage` | Defer to extension wave 4 | Phase 12 | Keep verbatim below as future source material. |
| `1.4 Best-case rendered markdown` | Defer to extension wave 4 | Phase 12 | Renderer work belongs after the abstraction survives. |
| `2. Lexical let bindings` | Defer to extension wave 1 | Phase 9 | Low-risk convenience after selectors and binds are stable. |
| `2.1 Syntax` | Defer to extension wave 1 | Phase 9 | Depends on the accepted expression model. |
| `2.2 How it works` | Defer to extension wave 1 | Phase 9 | Same dependency as `2.1`. |
| `2.3 Example usage` | Defer to extension wave 1 | Phase 9 | Keep as future source text. |
| `2.4 Best-case rendered markdown` | Defer to extension wave 1 | Phase 9 | Renderer work follows the accepted expression model. |
| `3. Quantified collection expressions` | Defer to extension wave 1 | Phase 9 | Natural follow-on after selectors and `let`. |
| `3.1 Syntax` | Defer to extension wave 1 | Phase 9 | Depends on the accepted expression model. |
| `3.2 How it works` | Defer to extension wave 1 | Phase 9 | Same dependency as `3.1`. |
| `3.3 Example usage` | Defer to extension wave 1 | Phase 9 | Keep as future source text. |
| `3.4 Best-case rendered markdown` | Defer to extension wave 1 | Phase 9 | Renderer work follows the accepted expression model. |
| `4. Import aliasing and selective imports` | Defer to extension wave 3 | Phase 11 | Grammar and name-resolution collisions must be resolved first. |
| `4.1 Syntax` | Defer to extension wave 3 | Phase 11 | Qualified declaration-ref grammar is not closed yet. |
| `4.2 How it works` | Defer to extension wave 3 | Phase 11 | Same dependency as `4.1`. |
| `4.3 Example usage` | Defer to extension wave 3 | Phase 11 | Keep as future source text. |
| `4.4 Best-case rendered markdown` | Defer to extension wave 3 | Phase 11 | Renderer work follows the final qualified-name grammar. |
| `5. display_title for dynamic headings` | Defer to extension wave 1 | Phase 9 | Keep only after the render-only versus semantic-readback contradiction is fixed. |
| `5.1 Syntax` | Defer to extension wave 1 | Phase 9 | Depends on the closed title and projection semantics. |
| `5.2 How it works` | Needs explicit rewrite before adoption | Phase 9 | Must choose whether `display_title` is truly render-only or part of semantic readback. |
| `5.3 Example usage` | Defer to extension wave 1 | Phase 9 | Keep as future source text. |
| `5.4 Best-case rendered markdown` | Defer to extension wave 1 | Phase 9 | Renderer work follows the final semantics. |
| `6. Read-only mention semantics with @` | Defer to extension wave 1 | Phase 9 | Reasonable convenience, but only if it fits the final readable-ref model. |
| `6.1 Syntax` | Defer to extension wave 1 | Phase 9 | Depends on the accepted mention and projection grammar. |
| `6.2 How it works` | Defer to extension wave 1 | Phase 9 | Same dependency as `6.1`. |
| `6.3 Example usage` | Defer to extension wave 1 | Phase 9 | Keep as future source text. |
| `6.4 Best-case rendered markdown` | Defer to extension wave 1 | Phase 9 | Renderer work follows the final mention model. |
| `7. Typed local route selection` | Defer to extension wave 1 | Phase 9 | Route typing can follow the core route-semantics cutover. |
| `7.1 Syntax` | Defer to extension wave 1 | Phase 9 | Depends on the final typed-proof rule for route sources. |
| `7.2 How it works` | Needs explicit rewrite before adoption | Phase 9 | The current proof rule is weaker than the example claims. |
| `7.3 Example usage` | Defer to extension wave 1 | Phase 9 | Keep as future source text. |
| `7.4 Best-case rendered markdown` | Defer to extension wave 1 | Phase 9 | Renderer work follows the final typing rule. |
| `8. Native typed data contracts` | Defer to extension wave 2 | Phase 10 | Strong feature, but not needed to close core v2. |
| `8.1 Syntax` | Defer to extension wave 2 | Phase 10 | Depends on stable core declaration and payload semantics. |
| `8.2 How it works` | Defer to extension wave 2 | Phase 10 | Same dependency as `8.1`. |
| `8.3 Example usage` | Defer to extension wave 2 | Phase 10 | Keep as future source text. |
| `8.4 Best-case rendered markdown` | Defer to extension wave 2 | Phase 10 | Renderer work follows accepted structured-output ownership. |
| `9. Path roots and typed file paths` | Defer to extension wave 2 | Phase 10 | Useful, but host-bound and not core to the first break. |
| `9.1 Syntax` | Defer to extension wave 2 | Phase 10 | Depends on the authoring-boundary decision for path roots. |
| `9.2 How it works` | Defer to extension wave 2 | Phase 10 | Same dependency as `9.1`. |
| `9.3 Example usage` | Defer to extension wave 2 | Phase 10 | Keep as future source text. |
| `9.4 Best-case rendered markdown` | Defer to extension wave 2 | Phase 10 | Renderer work follows the final host-boundary rule. |
| `10. Package exports and public library barrels` | Defer to extension wave 3 | Phase 11 | Useful only after core import and identity rules are stable. |
| `10.1 Syntax` | Defer to extension wave 3 | Phase 11 | Depends on the final package and qualified-name grammar. |
| `10.2 How it works` | Defer to extension wave 3 | Phase 11 | Same dependency as `10.1`. |
| `10.3 Example usage` | Defer to extension wave 3 | Phase 11 | Keep as future source text. |
| `10.4 Best-case rendered markdown` | Defer to extension wave 3 | Phase 11 | Renderer work follows the final package model. |
| `11. Mixins without multiple inheritance` | Defer to extension wave 4 | Phase 12 | High-risk abstraction. Only worth adding after the core patch engine is proven. |
| `11.1 Syntax` | Defer to extension wave 4 | Phase 12 | Depends on stable family-local include semantics. |
| `11.2 How it works` | Defer to extension wave 4 | Phase 12 | Same dependency as `11.1`. |
| `11.3 Example usage` | Defer to extension wave 4 | Phase 12 | Keep as future source text. |
| `11.4 Best-case rendered markdown` | Defer to extension wave 4 | Phase 12 | Renderer work follows the final mixin model. |
| `12. Later-phase protocols and structural conformance` | Defer to extension wave 5 | Phase 13 | The spec already treats this as a later-phase feature. |
| `12.1 Syntax` | Defer to extension wave 5 | Phase 13 | Keep as future source text only. |
| `12.2 How it works` | Defer to extension wave 5 | Phase 13 | Same dependency as `12.1`. |
| `12.3 Example usage` | Defer to extension wave 5 | Phase 13 | Keep as future source text. |
| `12.4 Best-case rendered markdown` | Defer to extension wave 5 | Phase 13 | Renderer work follows the final protocol model if accepted. |
| `13. Minimal historical state as a host-bound input` | Defer to extension wave 5 | Phase 13 | Highest boundary risk. Must be re-justified against Doctrine's authoring boundary. |
| `13.1 Syntax` | Defer to extension wave 5 | Phase 13 | Keep as future source text only. |
| `13.2 How it works` | Defer to extension wave 5 | Phase 13 | Must be re-evaluated against the harness boundary. |
| `13.3 Example usage` | Defer to extension wave 5 | Phase 13 | Keep as future source text. |
| `13.4 Best-case rendered markdown` | Defer to extension wave 5 | Phase 13 | Renderer work follows the final boundary decision if accepted. |
| `14. Summary` | Accept as extension-wave backlog summary | Phase 8 / later | Keep once the staged-wave plan is locked. |

## Folded sources (verbatim; inlined so they cannot be missed)
The only added wrapper is the Markdown fence around each folded source.
The inner source text is preserved as-is.

### R1 — Doctrine redesign full spec — docs/LANGUAGE_REDESIGN_SPEC.md
~~~~markdown
# Doctrine redesign full spec

This document specifies a coherent language redesign that addresses the gaps identified in the repo review:

1. rich declaration inheritance parity
2. selector algebra for `first` / `last` / `nth` / `only` / `where`
3. review semantics as authored semantic records plus reusable projections
4. removal of `review_family` as a separate primitive
5. normalization of `decision`, `route_only`, and `grounding`
6. schema naming cleanup so one keyword means one thing
7. canonical alias semantics for bound roots
8. migration and diagnostics

This is a **shipped-surface spec**, not an implementation sketch. It chooses one consistent Doctrine direction.

The design goal is simple:

- one patch algebra everywhere
- one path algebra everywhere
- one semantics/projection algebra everywhere
- no owner-sensitive keyword overload
- no magic repeated single-use fields where a first-class block should exist
- explicitness preserved; implicit merge stays out

---

## 0. Phase choice and compatibility

This spec makes four decisive choices.

1. `review_family` is removed as a separate primitive. Its job is absorbed by `review` and `abstract review`.
2. `decision` stays first-class, but becomes inheritable and block-attachable through a new `decisions` block.
3. `route_only` and `grounding` stay first-class in this phase, but are normalized onto the same keyed-body and inheritance algebra as the rest of Doctrine.
4. `output shape.schema` is renamed to `payload_schema` so `schema` means the Doctrine schema family everywhere else.

Backwards compatibility rules:

- `review_family` is accepted for one compatibility cycle as a deprecated alias for `review`.
- repeated `decision:` fields are accepted for one compatibility cycle but render a deprecation warning that recommends `decisions:`.
- `schema:` inside `output shape` is accepted for one compatibility cycle as a deprecated alias for `payload_schema:`.
- legacy unkeyed `decision`, `route_only`, and `grounding` item forms are accepted as sugar and lower into the normalized keyed forms below.

---

## 1. Rich declaration inheritance parity

### 1.1 Problem

Today the language lets many container declarations inherit while some leaf declarations remain non-inheritable. The asymmetry is visible in the current model:

- `InputsDecl` and `OutputsDecl` carry `parent_ref`
- `InputDecl`, `OutputDecl`, and `SkillDecl` do not
- `AnalysisDecl` carries `parent_ref`
- `DecisionDecl`, `RouteOnlyDecl`, and `GroundingDecl` do not

The redesigned rule is:

> Every semantically rich declaration with keyed authored content is inheritable.

That means the following declarations all support `inheritance?`:

- `input`
- `output`
- `skill`
- `decision`
- `route_only`
- `grounding`

`analysis`, `workflow`, `schema`, `document`, `review`, `skills`, `inputs`, and `outputs` already follow the same family.

### 1.2 General syntax

```ebnf
input_decl      := "input"      CNAME inheritance? ":" string NL INDENT input_body      DEDENT
output_decl     := "output"     CNAME inheritance? ":" string NL INDENT output_body     DEDENT
skill_decl      := "skill"      CNAME inheritance? ":" string NL INDENT record_body     DEDENT
decision_decl   := "decision"   CNAME inheritance? ":" string NL INDENT decision_body   DEDENT
route_only_decl := "route_only" CNAME inheritance? ":" string NL INDENT route_only_body DEDENT
grounding_decl  := "grounding"  CNAME inheritance? ":" string NL INDENT grounding_body  DEDENT

inheritance     := "[" name_ref "]"
```

### 1.3 Patch algebra

All inheritable declarations use the same doctrine patch rules:

- child title is always child-owned
- child preamble prose is always child-owned
- inherited keyed entries must be accounted for exactly once
- `inherit key` keeps the inherited entry and places it exactly here
- `override key:` replaces the inherited entry, keeping the inherited title unless a new title is given
- `override key: "New Title"` replaces the inherited entry and its title
- `key: "Title"` introduces a new keyed entry
- no implicit merge
- no append semantics
- missing inherited entry is a compile error
- duplicate inherited accounting is a compile error
- overriding an unknown key is a compile error

This is the same law already used by workflows, schemas, documents, reviews, skills blocks, and I/O blocks. The point of this spec is to make leaf declarations obey it too.

### 1.4 Input inheritance

#### Syntax

```doctrine
input ReleasePlan: "Release Plan"
    source: File
        path: "release_root/PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    structure: ReleasePlanDocument
    "Read the current release plan before changing scope."

input RebuildAwareReleasePlan[ReleasePlan]: "Release Plan"
    inherit source
    inherit shape
    inherit requirement
    inherit structure

    override notes: "Notes"
        "Read the current release plan before changing scope."
        "If rebuild work is active, compare the current plan with the latest rebuild note."
```

#### How it works

`input` inheritance patches the top-level keyed contract surface. Fixed fields such as `source`, `shape`, `requirement`, and `structure` are ordinary inherited keys, not a special case.

Validation still runs after patching. A final concrete `input` must still have:

- exactly one `source`
- exactly one `shape`
- exactly one `requirement`
- at most one `structure`

#### Best-case rendered markdown

```markdown
## Inputs

### Release Plan

- Source: File
- Path: `release_root/PLAN.md`
- Shape: Markdown Document
- Requirement: Required
- Structure: Release Plan Document

Read the current release plan before changing scope.
If rebuild work is active, compare the current plan with the latest rebuild note.
```

### 1.5 Output inheritance

#### Syntax

```doctrine
output BaseReviewComment: "Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "State whether the work passed review."

    current_artifact: "Current Artifact"
        "Name the artifact that remains current after review."

    standalone_read: "Standalone Read"
        "This comment should stand on its own."

output ControlReadyReviewComment[BaseReviewComment]: "Review Comment"
    inherit target
    inherit shape
    inherit requirement
    inherit verdict
    inherit current_artifact

    next_owner: "Next Owner"
        "Name the next owner when the review routes."

    inherit standalone_read
```

#### How it works

`output` inheritance patches the entire authored output contract:

- ordinary contract fields such as `target`, `shape`, `requirement`
- titled sections such as `must_include`, `standalone_read`, `trust_surface`
- guarded sections
- nested titled bodies, which may themselves be patched when overridden

Final validation still applies. The patched output must still satisfy the normal output invariants.

#### Best-case rendered markdown

```markdown
## Outputs

### Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Verdict

State whether the work passed review.

#### Current Artifact

Name the artifact that remains current after review.

#### Next Owner

Name the next owner when the review routes.

#### Standalone Read

This comment should stand on its own.
```

### 1.6 Skill inheritance

#### Syntax

```doctrine
skill BaseGroundingSkill: "Grounding Skill"
    purpose: "Ground reader-facing wording against current source truth."

    use_when: "Use When"
        "Use this when wording must be re-earned from primary evidence."

skill ReleaseGroundingSkill[BaseGroundingSkill]: "Grounding Skill"
    inherit purpose

    override use_when: "Use When"
        "Use this when wording must be re-earned from release evidence."

    provides: "Provides"
        "A release-specific route for collecting the evidence this lane needs."
```

#### How it works

`skill` inheritance is a leaf-level version of the existing `skills` block inheritance story. It patches the skill contract itself, not merely the block that references the skill.

#### Best-case rendered markdown

```markdown
## Skills

### Can Run

#### Grounding Skill

##### Purpose

Ground reader-facing wording against current source truth.

##### Use When

Use this when wording must be re-earned from release evidence.

##### Provides

A release-specific route for collecting the evidence this lane needs.
```

### 1.7 Decision inheritance

#### Normalized keyed syntax

Legacy decision items become keyed fields.

```doctrine
decision PlayableStrategyChoice: "Playable Strategy Choice"
    minimum_candidates: 3
    rank: Required
    rejects: Required
    winner: Required

    rank_by: "Rank By"
        teaching_fit
        product_reality
        capstone_coherence
        downstream_preservability

decision PlatformAwareStrategyChoice[PlayableStrategyChoice]: "Playable Strategy Choice"
    inherit minimum_candidates
    inherit rank
    inherit rejects
    inherit winner

    override rank_by: "Rank By"
        teaching_fit
        product_reality
        capstone_coherence
        downstream_preservability
        platform_fit
```

#### Legacy sugar

The following legacy surface remains valid for one compatibility cycle:

```doctrine
decision PlayableStrategyChoice: "Playable Strategy Choice"
    candidates minimum 3
    rank required
    rejects required
    winner required
    rank_by {teaching_fit, product_reality, capstone_coherence, downstream_preservability}
```

It lowers internally to the keyed form above.

#### How it works

A `decision` declaration is now a first-class patchable scaffold. That means:

- it can inherit
- it is addressable
- it can be reused in blocks
- it can be rendered consistently
- later protocol families can project from it if desired

#### Best-case rendered markdown

```markdown
## Playable Strategy Choice

Build at least 3 candidates.
You must rank the candidates.
You must name clear rejects.
Choose exactly one winner.

### Rank By

- Teaching Fit
- Product Reality
- Capstone Coherence
- Downstream Preservability
- Platform Fit
```

### 1.8 Route-only inheritance

#### Normalized keyed syntax

```doctrine
enum RouteRepairMode: "Route Repair Mode"
    draft_owner: "Draft Owner"
    routing_owner: "Routing Owner"

route_only BaseRouteRepair: "Route Repair"
    facts: RouteFacts
    select: RouteFacts.next_owner_mode as RouteRepairMode

    when:
        live_job: live_job == "route_repair"

    current: none
    handoff_output: RouteRepairComment

    routes:
        draft_owner: DraftAuthor
        routing_owner: RoutingOwner
        else: RoutingOwner

route_only RewriteAwareRouteRepair[BaseRouteRepair]: "Route Repair"
    inherit facts
    inherit select
    inherit current
    inherit handoff_output

    override when:
        live_job: live_job == "route_repair"
        missing_output: current_specialist_output_missing

    guarded:
        rewrite_mode: section_status in {"new", "full_rewrite"}

    inherit routes
```

#### How it works

`route_only` becomes a normal keyed declaration:

- `facts` supplies the expression root
- `select` names the selector source and its enum
- `when` is a keyed block of AND-ed activation conditions
- `current` is a keyed field, currently only allowing `none`
- `handoff_output` names the emitted route handoff
- `guarded` names optional output sections keyed by guard name
- `routes` maps selector members to concrete agents; `else` is optional fallback

Inheritance patches those top-level keys exactly like every other keyed declaration.

#### Best-case rendered markdown

```markdown
## Route Repair

Run this only when Route Facts says route repair is live and the current specialist output is missing.

No artifact is current for this turn.

Use Route Repair Mode to choose the next owner:
- Draft Owner -> Draft Author
- Routing Owner -> Routing Owner
- Else -> Routing Owner

#### Rewrite Mode

Show this only when section status is new or full rewrite.

Say plainly that later metadata must be rewritten instead of inherited.
```

### 1.9 Grounding inheritance

#### Normalized keyed syntax

```doctrine
grounding ClaimGrounding: "Claim Grounding"
    source: RepoFacts
    target: wording_claim

    policy:
        base_claim: start_from accepted_claim unless stale_claim
        rejects_unchecked: forbid unchecked_claim
        cited_support: allow cited_fact
        review_gate: route ReviewLead when needs_review

grounding ReleaseClaimGrounding[ClaimGrounding]: "Claim Grounding"
    inherit source
    inherit target

    override policy:
        inherit base_claim
        inherit rejects_unchecked
        inherit cited_support
        release_review_gate: route ReleaseReviewLead when needs_release_review
```

#### How it works

`grounding` remains first-class in this phase, but its internal policy becomes keyed so it can be patched explicitly.

`policy` entries are ordered and addressable. They are not hidden compiler strings.

#### Best-case rendered markdown

```markdown
## Claim Grounding

Ground this pass against Repo Facts.
Target: wording_claim.

### Policy

- Start from accepted_claim unless stale_claim.
- Do not use unchecked_claim.
- Allow cited_fact.
- If needs_release_review, route to Release Review Lead.
```

---

## 2. Decisions blocks

### 2.1 Problem

A single `decision:` attachment works, but repeated `decision:` attachments are keyless and have no local identity. That means:

- no local names
- no block inheritance
- no clean reordering
- no clean selective override

### 2.2 New surface

Doctrine adds first-class `decisions` blocks, parallel to `skills`, `inputs`, and `outputs`.

#### Grammar

```ebnf
decisions_decl  := "decisions" CNAME inheritance? ":" string NL INDENT decisions_body DEDENT
decisions_field := "decisions" ":" name_ref NL?
                 | "decisions" ":" string NL INDENT decisions_body DEDENT

decisions_body  := decision_entry+
decision_entry  := CNAME ":" name_ref NL?
                 | "inherit" CNAME NL?
                 | "override" CNAME ":" name_ref NL?
```

### 2.3 Example usage

```doctrine
decisions ReleaseChoices: "Decisions"
    strategy: PlayableStrategyChoice
    reps: RepChoice

agent MultiDecisionDemo:
    role: "Follow the attached decisions before you lock the plan."
    workflow: "Choose"
        "Use both attached decision scaffolds before you freeze the route and reps."
    decisions: ReleaseChoices
```

Inline form:

```doctrine
agent MultiDecisionInlineDemo:
    role: "Follow the attached decisions before you lock the plan."
    workflow: "Choose"
        "Use both attached decision scaffolds before you freeze the route and reps."

    decisions: "Decisions"
        strategy: PlayableStrategyChoice
        reps: RepChoice
```

Inherited form:

```doctrine
decisions BaseChoices: "Decisions"
    strategy: PlayableStrategyChoice

decisions ReleaseChoices[BaseChoices]: "Decisions"
    inherit strategy
    reps: RepChoice
```

### 2.4 How it works

- each attached decision gets a stable local key
- the key is structural, not display identity
- the referenced decision declaration still owns the rendered decision scaffold
- `decision: X` remains valid sugar for a single unnamed `decisions` block entry for one compatibility cycle
- repeated `decision:` fields become deprecated

### 2.5 Best-case rendered markdown

```markdown
## Decisions

### Strategy

#### Playable Strategy Choice

Build at least 3 candidates.
You must rank the candidates.
You must name clear rejects.
Choose exactly one winner.

### Rank By

- Teaching Fit
- Product Reality
- Capstone Coherence
- Downstream Preservability

### Reps

#### Rep Choice

You must define the candidate pool.
You must say which reps are kept.
You must say which reps are rejected.
You must provide sequencing proof.
You must justify the winner.
```

---

## 3. Selector algebra and collection descendants

### 3.1 Problem

Current Doctrine addressability is excellent for named static structure but weak for discovered or positional structure.

The missing class is:

- first / last / nth
- only
- filtered selection
- binding a review or workflow to the most recent matching item inside a modeled artifact

### 3.2 New path syntax

Doctrine extends path expressions with selector suffixes.

#### Grammar

```ebnf
path_expr       := root_ref ":" path_segment ("." path_segment)*
path_segment    := CNAME selector*
selector        := "[" "first" "]"
                 | "[" "last" "]"
                 | "[" "only" "]"
                 | "[" "nth(" INT ")" "]"
                 | "[" "where(" expr ")" "]"
```

Examples:

```doctrine
ReviewHistoryFile:entries[last]
ReviewHistoryFile:entries[where(verdict == ReviewVerdict.changes_requested)][last]
LessonPlan:step_arc.rows[first].coaching_level
```

### 3.3 Ordered collection descendants

Selectors only become genuinely useful when an addressable surface exposes an ordered collection. Doctrine adds `many` descendants for that purpose.

#### Document syntax

```ebnf
many_block := "many" CNAME ":" string NL INDENT "item" ":" name_ref NL? DEDENT
```

#### Example

```doctrine
document ReviewEntry: "Review Entry"
    definitions fields: "Fields" required
        reviewer: "Reviewer"
            "Name the reviewer."

        verdict: "Verdict"
            "State the verdict."

        summary: "Summary"
            "Summarize the review."

document ReviewHistory: "Review History"
    many entries: "Entries"
        item: ReviewEntry
```

This declares an ordered repeated collection of `ReviewEntry` items.

### 3.4 Selector semantics

Evaluation is left-to-right.

1. Resolve the root.
2. Walk to the named descendant family.
3. Apply zero or more selectors in order.
4. Continue descending from the selected item if more path segments remain.

Rules:

- `where(expr)` filters the current ordered collection and preserves order.
- `first` selects the first surviving item.
- `last` selects the last surviving item.
- `nth(n)` is 1-based.
- `only` asserts that exactly one item survives.

### 3.5 Static and runtime validation

Doctrine distinguishes two cases.

#### Statically authored collections

When the collection is fully declared in the source model, the compiler may fully validate selector use.

#### Runtime collections

When the collection is instance-shaped at runtime, selector cardinality is a runtime contract check.

Examples:

- `nth(3)` fails at runtime if fewer than three items exist.
- `only` fails at runtime if zero or more than one item survives.
- `last` fails at runtime if the filtered set is empty.

These are **contract failures**, not parse failures.

### 3.6 General binds block

Selectors become much more useful with local names. Doctrine adds a general `binds:` block.

#### Grammar

```ebnf
binds_block  := "binds" ":" NL INDENT bind_stmt+ DEDENT
bind_stmt    := CNAME ":" path_expr NL?
```

Shipped surfaces:

- `workflow`
- `review`
- `analysis`
- `route_only`
- `grounding`

Bindings are lexical aliases to resolved addressable nodes. They do not copy data.

### 3.7 Example usage: bind a review to the latest rejected review in a file

```doctrine
document ReviewEntry: "Review Entry"
    definitions fields: "Fields" required
        reviewer: "Reviewer"
            "Name the reviewer."
        verdict: "Verdict"
            "State the verdict."
        summary: "Summary"
            "Summarize the review."

document ReviewHistory: "Review History"
    many entries: "Entries"
        item: ReviewEntry

input ReviewHistoryFile: "Review History File"
    source: File
        path: "unit_root/REVIEW_HISTORY.md"
    shape: MarkdownDocument
    structure: ReviewHistory
    requirement: Required

workflow ReadFirst: "Read First"
    binds:
        last_rejected_review: ReviewHistoryFile:entries[where(verdict == ReviewVerdict.changes_requested)][last]

    prior_review: "Prior Review"
        "Read {{last_rejected_review:title}} before you reopen the draft."
        "Start with {{last_rejected_review.summary}}."
```

### 3.8 Example usage inside a review

```doctrine
review LatestFollowUpReview: "Latest Follow-Up Review"
    subject: DraftPlan
    contract: PlanReviewContract
    carrier: LatestReviewComment

    binds:
        last_rejected_review: ReviewHistoryFile:entries[where(verdict == ReviewVerdict.changes_requested)][last]

    contract_checks: "Contract Checks"
        reject "The latest rejected review still lacks closure." when last_rejected_review.summary_missing
        accept "The latest rejected review is fully addressed." when contract.passes
```

### 3.9 Best-case rendered markdown

```markdown
## Read First

### Prior Review

Read Review Entry before you reopen the draft.
Start with Summary.
```

And for a review that uses the same bind:

```markdown
## Latest Follow-Up Review

### Contract Checks

Reject: The latest rejected review still lacks closure.
Accept only if The latest rejected review is fully addressed.
```

### 3.10 Non-goals in this phase

Not shipped in this phase:

- `before(...)`
- `after(...)`
- free-text parsing of arbitrary raw markdown with no declared structure
- cross-file selectors over unmodeled trees

Selectors require declared addressable structure.

---

## 4. Semantic records and projections

### 4.1 Problem

Current review semantics are compiler-owned and split across:

- `comment_output`
- `fields`
- `final_output.review_fields`
- hidden control-readiness inference

That makes review feel like a partially separate language.

### 4.2 New declarations

Doctrine adds two top-level declaration families:

- `semantic`
- `projection`

#### Semantic declaration

A semantic declaration defines a named semantic record type.

```ebnf
semantic_decl       := "semantic" CNAME ":" string NL INDENT semantic_field_decl+ DEDENT
semantic_field_decl := CNAME optional? ":" semantic_type NL?
optional            := "?"
semantic_type       := CNAME
                     | "List" "<" semantic_type ">"
```

Built-in semantic atom types shipped in this phase:

- `Text`
- `Artifact`
- `Agent`
- `Bool`
- `Enum<EnumName>`

#### Projection declaration

A projection declaration defines a reusable subset of a semantic record and optionally names its host role.

```ebnf
projection_decl := "projection" CNAME ":" string NL INDENT projection_body DEDENT
projection_body := "from" ":" name_ref NL
                   ("role" ":" CNAME NL)?
                   "include" ":" NL INDENT projection_field_ref+ DEDENT

projection_field_ref := CNAME NL?
```

Shipped projection roles in this phase:

- `Control`

### 4.3 Producer binding: `carrier` plus `emits`

Any declaration that emits semantic output may bind a carrier and emit a semantic record. In this phase the shipped producer surface is `review`, though the design is intentionally reusable.

#### Review syntax

```ebnf
carrier_stmt := "carrier" ":" output_ref NL?
emits_block  := "emits" name_ref ":" NL INDENT semantic_binding+ DEDENT
semantic_binding := CNAME ":" field_path NL?
```

### 4.4 Output projection: `project`

Any output may project a producer's semantic record onto its own output fields.

#### Syntax

```ebnf
project_block := "project" name_ref "as" name_ref ":" NL INDENT projection_binding+ DEDENT
projection_binding := CNAME ":" field_path NL?
```

Interpretation:

- left side is the semantic field from the named projection
- right side is the output field path that carries it

### 4.5 Review example

#### Semantic type

```doctrine
semantic ReviewOutcome: "Review Outcome"
    verdict: Text
    reviewed_artifact: Artifact
    analysis: Text
    readback: Text
    current_artifact?: Artifact
    next_owner?: Agent
    blocked_gate?: Text
    failing_gates?: List<Text>
```

#### Control projection

```doctrine
projection AcceptanceControl: "Acceptance Control"
    from: ReviewOutcome
    role: Control

    include:
        verdict
        current_artifact
        next_owner
        blocked_gate
```

#### Review carrier

```doctrine
review AcceptanceReview: "Acceptance Review"
    subject: DraftPlan
    contract: PlanReviewContract
    carrier: AcceptanceReviewComment

    emits ReviewOutcome:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        next_owner: next_owner
        blocked_gate: failure_detail.blocked_gate
        failing_gates: failure_detail.failing_gates

    contract_checks: "Contract Checks"
        reject contract.outline_complete when ReviewFacts.outline_missing
        accept "The acceptance review contract passes." when contract.passes

    on_accept:
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Accepted plan goes to ReviewLead." -> ReviewLead

    on_reject:
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Rejected plan goes to PlanAuthor." -> PlanAuthor
```

#### Split final response

```doctrine
output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
    target: TurnResponse
    shape: AcceptanceControlJson
    requirement: Required

    project AcceptanceReview as AcceptanceControl:
        verdict: verdict
        current_artifact: current_artifact
        next_owner: next_owner
        blocked_gate: blocked_gate
```

#### Agent

```doctrine
agent AcceptanceReviewSplitControlReadyDemo:
    role: "Emit the review comment and end with a control-ready JSON result."
    review: AcceptanceReview

    inputs: "Inputs"
        DraftPlan

    outputs: "Outputs"
        AcceptanceReviewComment
        AcceptanceControlFinalResponse

    final_output: AcceptanceControlFinalResponse
```

### 4.6 Partial projection

A non-control final readback is just a different projection.

```doctrine
projection AcceptanceSnapshot: "Acceptance Snapshot"
    from: ReviewOutcome

    include:
        current_artifact
        next_owner

output AcceptanceSnapshotFinalResponse: "Acceptance Snapshot Final Response"
    target: TurnResponse
    shape: AcceptanceControlJson
    requirement: Required

    project AcceptanceReview as AcceptanceSnapshot:
        current_artifact: current_artifact
        next_owner: next_owner
```

Because this projection has no `role: Control`, it is explicitly not control-ready.

### 4.7 Control readiness

`role: Control` makes readiness explicit instead of guessed.

Validation rule:

- if a projected output claims `role: Control`, Doctrine proves that the included semantic fields are sufficient for control on every live branch of the producer

In this phase, `Control` requires:

- `verdict` always
- `next_owner` when any branch routes
- `blocked_gate` when any blocked branch exists

If those conditions fail, compilation fails. No hidden readiness inference remains.

### 4.8 Best-case rendered markdown: control-ready projection

```markdown
## Final Output

### Acceptance Control Final Response

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Acceptance Control JSON |
| Projection | Acceptance Control |
| Projection role | Control |
| Requirement | Required |

#### Semantic Projection

This final response projects review semantics from Acceptance Review.

| Semantic Field | Output Field |
| --- | --- |
| Verdict | `verdict` |
| Current Artifact | `current_artifact` |
| Next Owner | `next_owner` |
| Blocked Gate | `blocked_gate` |

This final response is control-ready.

#### Read on Its Own

This final JSON should be enough for a host to read the review outcome.
```

### 4.9 Best-case rendered markdown: partial projection

```markdown
## Final Output

### Acceptance Snapshot Final Response

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Acceptance Control JSON |
| Projection | Acceptance Snapshot |
| Requirement | Required |

#### Semantic Projection

This final response projects review semantics from Acceptance Review.

| Semantic Field | Output Field |
| --- | --- |
| Current Artifact | `current_artifact` |
| Next Owner | `next_owner` |

This final response is not control-ready.

#### Read on Its Own

This final JSON is a small semantic readback, not the full review outcome.
```

---

## 5. Remove `review_family`

### 5.1 Problem

`review_family` exists because reusable review scaffolds escaped past the original review inheritance boundary. But the current review engine already supports selector blocks, cases, and inheritance.

A separate keyword is unnecessary.

### 5.2 New rule

- `review_family` is removed from the grammar
- `review` may use `selector`, `cases`, `carrier`, and `emits`
- `abstract review` remains the only incomplete reusable review surface
- a complete `review` may be attached directly to an agent
- case-selected reusable reviews are ordinary `review` declarations

### 5.3 Direct replacement: shared review scaffold

#### Old

```doctrine
review_family SharedDraftReviewFamily: "Shared Draft Review"
    ...
```

#### New

```doctrine
review SharedDraftReview: "Shared Draft Review"
    carrier: SharedReviewComment

    emits ReviewOutcome:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    handoff_first:
        reject "Producer handoff is incomplete." when DraftSpec.handoff_incomplete
```

Child review:

```doctrine
review DraftReview[SharedDraftReview]: "Shared Draft Review"
    subject: DraftSpec
    contract: SharedDraftReviewContract

    inherit emits ReviewOutcome
    inherit handoff_first

    contract_checks: "Contract Checks"
        accept "The shared draft review contract passes." when contract.passes

    on_accept:
        current none
        route "Accepted draft goes to ReviewLead." -> ReviewLead

    on_reject:
        current none
        route "Rejected draft goes to DraftAuthor." -> DraftAuthor
```

### 5.4 Direct replacement: case-selected scaffold

```doctrine
review SelectedReview: "Selected Review"
    carrier: SelectedReviewComment

    emits ReviewOutcome:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        next_owner: next_owner
        current_artifact: current_artifact
        failing_gates: failure_detail.failing_gates

    selector:
        mode selected_mode = ReviewFacts.selected_mode as ReviewMode

    handoff_first:
        reject "Shared review handoff is incomplete." when ReviewFacts.handoff_incomplete

    cases:
        draft_path: "Draft Path"
            when ReviewMode.draft_rewrite
            subject: DraftSpec
            contract: DraftReviewContract
            checks:
                accept "The draft review contract passes." when contract.passes
            on_accept:
                current artifact DraftSpec via SelectedReviewComment.current_artifact
                route "Accepted draft rewrite goes to RevisionOwner." -> RevisionOwner
            on_reject:
                current artifact DraftSpec via SelectedReviewComment.current_artifact
                route "Rejected draft rewrite goes to RevisionOwner." -> RevisionOwner

        metadata_path: "Metadata Path"
            when ReviewMode.metadata_refresh
            subject: MetadataRecord
            contract: MetadataReviewContract
            checks:
                accept "The metadata review contract passes." when contract.passes
            on_accept:
                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                route "Accepted metadata refresh goes to RevisionOwner." -> RevisionOwner
            on_reject:
                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                route "Rejected metadata refresh goes to RevisionOwner." -> RevisionOwner
```

### 5.5 How it works

Nothing about the runtime review engine changes. The cleanup is purely linguistic:

- one primitive instead of two
- no special family branch in the user model
- ordinary review inheritance is the only reuse story

### 5.6 Best-case rendered markdown

Rendered output is unchanged except the authored keyword is now `review` instead of `review_family`.

---

## 6. Route-only and grounding normalization

This section answers the “reevaluate primitive count” concern without introducing a new protocol meta-language in the same release.

The phase-1 rule is:

- keep `route_only` and `grounding`
- normalize them onto the same keyed-body, inheritance, selector, bind, and semantic machinery as everything else

### 6.1 Route-only semantic projection

A route-only declaration may emit semantics exactly like a review.

#### Semantic type

```doctrine
semantic RouteOutcome: "Route Outcome"
    next_owner: Agent
    current_route: Text
    next_step: Text
    rewrite_mode?: Bool
```

#### Route-only declaration

```doctrine
route_only RouteRepair: "Route Repair"
    facts: RouteFacts
    select: RouteFacts.next_owner_mode as RouteRepairMode

    when:
        live_job: live_job == "route_repair"
        missing_output: current_specialist_output_missing

    current: none
    handoff_output: RouteRepairComment

    emits RouteOutcome:
        next_owner: next_owner
        current_route: current_route
        next_step: next_step
        rewrite_mode: rewrite_mode

    guarded:
        rewrite_mode: section_status in {"new", "full_rewrite"}

    routes:
        draft_owner: DraftAuthor
        routing_owner: RoutingOwner
        else: RoutingOwner
```

This makes route-only outputs projectable and host-readable without special-case route semantics.

### 6.2 Grounding mapping remains a preservation target

`preserve mapping ClaimGrounding` remains valid, but because `grounding` is now keyed and inheritable, mapping preservation becomes more reusable.

#### Example

```doctrine
workflow PreserveGroundingMapping: "Preserve Grounding Mapping"
    law:
        current artifact RepoFacts via CoordinationHandoff.current_artifact
        preserve mapping ClaimGrounding
```

### 6.3 Best-case rendered markdown: route-only

```markdown
## Route Repair

Run this only when route repair is live and the current specialist output is missing.

No artifact is current for this turn.

### Current Route

Use Route Repair Mode to choose the live route:
- Draft Owner -> Draft Author
- Routing Owner -> Routing Owner
- Else -> Routing Owner

### Next Step

Say the next concrete step now.

### Rewrite Mode

Show this only when section status is new or full rewrite.

Say plainly that later metadata must be rewritten instead of inherited.
```

### 6.4 Best-case rendered markdown: grounding

```markdown
## Claim Grounding

Ground this pass against Repo Facts.
Target: wording_claim.

### Policy

- Start from accepted_claim unless stale_claim.
- Do not use unchecked_claim.
- Allow cited_fact.
- If needs_review, route to Review Lead.
```

### 6.5 Phase-2 note

A later Doctrine phase may demote these surfaces into standard-library protocol declarations. This spec does not depend on that demotion. It only removes the current asymmetry and hidden lowering seams.

---

## 7. Schema naming cleanup

### 7.1 Problem

Current authored guidance has to explain that:

- `output shape.schema` means JSON schema
- `output.schema` means Doctrine schema

That is owner-sensitive overloading.

### 7.2 New rule

- `schema` means Doctrine schema
- `payload_schema` means JSON payload schema

### 7.3 Syntax

#### Old

```doctrine
json schema DeliveryJsonSchema: "Delivery JSON Schema"
    profile: OpenAIStructuredOutput
    file: "schemas/delivery.schema.json"

output shape DeliveryPayload: "Delivery Payload"
    kind: JsonObject
    schema: DeliveryJsonSchema
```

#### New

```doctrine
json schema DeliveryJsonSchema: "Delivery JSON Schema"
    profile: OpenAIStructuredOutput
    file: "schemas/delivery.schema.json"

output shape DeliveryPayload: "Delivery Payload"
    kind: JsonObject
    payload_schema: DeliveryJsonSchema
```

Normal Doctrine schema stays unchanged:

```doctrine
schema DeliveryInventory: "Delivery Inventory"
    sections:
        summary: "Summary"
            "Include a short summary."

output DeliveryPlan: "Delivery Plan"
    target: File
        path: "unit_root/DELIVERY_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    schema: DeliveryInventory
```

### 7.4 Rendering rules

When a shape carries a JSON schema:

- render `Payload Schema`
- render `Payload Schema File`
- render `Payload Schema Profile`

When an artifact carries a Doctrine schema:

- render `Schema`
- render `Required Sections`
- render `Contract Gates`
- render `Artifact Inventory`
- render `Surface Groups`

### 7.5 Best-case rendered markdown

```markdown
## Outputs

### Delivery Plan

- Target: File
- Path: `unit_root/DELIVERY_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
- Schema: Delivery Inventory

#### Required Sections

##### Summary

Include a short summary.
```

And for the payload shape:

```markdown
### Delivery Payload

- Kind: Json Object
- Payload Schema: Delivery JSON Schema
- Payload Schema Profile: OpenAIStructuredOutput
- Payload Schema File: `schemas/delivery.schema.json`
```

---

## 8. Canonical alias semantics for bound roots

### 8.1 Problem

Bound roots are useful, but they create aliasing pressure.

### 8.2 New rule

A bound root is a canonical alias, not a distinct artifact identity.

Semantics:

- identity checks normalize bound names to canonical declaration identities
- overlap checks normalize bound names to canonical declaration identities
- diagnostics show the first alias mention as `alias -> CanonicalDecl`
- rendered markdown keeps the local bound title, not the canonical declaration name

### 8.3 Example

```doctrine
agent BoundCurrentTruthDemo:
    role: "Carry portable current truth through named concrete-turn bindings."
    workflow: CarryBoundCurrentTruth

    inputs: "Inputs"
        approved_plan: "Approved Plan Binding"
            ApprovedPlan

    outputs: "Outputs"
        coordination_handoff: "Coordination Handoff Binding"
            CoordinationHandoff
```

Law:

```doctrine
law:
    current artifact approved_plan via coordination_handoff.current_artifact
```

Normalization treats `approved_plan` as an alias to `ApprovedPlan`.

### 8.4 Best-case rendered markdown

```markdown
## Inputs

### Approved Plan Binding

#### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
```

No authored syntax change is required in this phase. This is a semantic cleanup.

---

## 9. Diagnostics and migration

### 9.1 Phase boundaries

Diagnostics become strictly phase-scoped:

- parse: grammar and transform only
- compile: name resolution, inheritance, semantic validation
- emit: rendering/build/export only

### 9.2 New or revised compile diagnostics

Recommended families:

- `E24x`: rich declaration inheritance and patching
- `E27x`: selector and path resolution
- `E47x`: review declaration validity
- `E50x`: semantic emission and projection validity
- `E53x`: bound-root identity and overlap
- `E54x`: deprecation / migration guidance

### 9.3 Required new diagnostics

#### Selector diagnostics

- selector target is not a collection
- `where(...)` reads a non-addressable field
- `nth(n)` uses zero or negative index
- projection or inline prose ends on a multi-valued collection with no collapsing selector
- `only` proved impossible statically

#### Projection diagnostics

- producer emits no semantic record of the required type
- projection includes a field not present on the source semantic type
- output mapping omits an included field
- output mapping points at a missing output field
- `role: Control` is declared but required control fields are not total across branches

#### Migration diagnostics

- `review_family` is deprecated; use `review`
- repeated `decision:` is deprecated; use `decisions:`
- `output shape.schema` is deprecated; use `payload_schema:`
- legacy unkeyed `decision` items are deprecated; use keyed form
- legacy unkeyed `route_only` policy-like items are deprecated; use keyed form
- legacy unkeyed `grounding` policy items are deprecated; use keyed form

### 9.4 Example migration messages

```text
E542 compile warning: `review_family` is deprecated
Detail:
- `review_family SharedDraftReviewFamily` lowers to `review SharedDraftReviewFamily`
Hint:
- Replace `review_family` with `review`. Use `abstract review` only when the declaration is intentionally incomplete.
```

```text
E544 compile warning: repeated `decision:` fields are deprecated
Detail:
- agent `MultiDecisionDemo` attaches more than one `decision:` field
Hint:
- Replace repeated `decision:` fields with one `decisions:` block so each attached decision has a stable local key.
```

---

## 10. Full worked example

This final example combines the major changes into one coherent authored surface.

### 10.1 Doctrine source

```doctrine
semantic ReviewOutcome: "Review Outcome"
    verdict: Text
    reviewed_artifact: Artifact
    analysis: Text
    readback: Text
    current_artifact?: Artifact
    next_owner?: Agent
    blocked_gate?: Text
    failing_gates?: List<Text>

projection AcceptanceControl: "Acceptance Control"
    from: ReviewOutcome
    role: Control
    include:
        verdict
        current_artifact
        next_owner
        blocked_gate

enum ReviewMode: "Review Mode"
    draft_rewrite: "Draft Rewrite"
    metadata_refresh: "Metadata Refresh"

document ReviewEntry: "Review Entry"
    definitions fields: "Fields" required
        reviewer: "Reviewer"
            "Name the reviewer."
        verdict: "Verdict"
            "State the verdict."
        summary: "Summary"
            "Summarize the review."

document ReviewHistory: "Review History"
    many entries: "Entries"
        item: ReviewEntry

input DraftPlan: "Draft Plan"
    source: File
        path: "unit_root/DRAFT_PLAN.md"
    shape: MarkdownDocument
    requirement: Required

input ReviewHistoryFile: "Review History File"
    source: File
        path: "unit_root/REVIEW_HISTORY.md"
    shape: MarkdownDocument
    structure: ReviewHistory
    requirement: Required

output AcceptanceReviewComment: "Acceptance Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "State whether the plan passed review or asked for changes."

    reviewed_artifact: "Reviewed Artifact"
        "Name the reviewed artifact."

    analysis_performed: "Analysis Performed"
        "Summarize the review analysis."

    output_contents_that_matter: "Output Contents That Matter"
        "State what the next owner should read first."

    current_artifact: "Current Artifact"
        "Name the artifact that remains current after review."

    next_owner: "Next Owner"
        "Name the next owner when the review routes."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        blocked_gate: "Blocked Gate"
            "Name the blocking gate when review stopped early."
        failing_gates: "Failing Gates"
            "List exact failing gates in authored order."

output AcceptanceControlFinalResponse: "Acceptance Control Final Response"
    target: TurnResponse
    shape: AcceptanceControlJson
    requirement: Required

    project AcceptanceReview as AcceptanceControl:
        verdict: verdict
        current_artifact: current_artifact
        next_owner: next_owner
        blocked_gate: blocked_gate

review AcceptanceReview: "Acceptance Review"
    subject: DraftPlan
    contract: PlanReviewContract
    carrier: AcceptanceReviewComment

    emits ReviewOutcome:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        current_artifact: current_artifact
        next_owner: next_owner
        blocked_gate: failure_detail.blocked_gate
        failing_gates: failure_detail.failing_gates

    binds:
        last_rejected_review: ReviewHistoryFile:entries[where(verdict == ReviewVerdict.changes_requested)][last]

    contract_checks: "Contract Checks"
        reject "The latest rejected review still lacks closure." when last_rejected_review.summary_missing
        accept "The acceptance review contract passes." when contract.passes

    on_accept:
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Accepted plan goes to ReviewLead." -> ReviewLead

    on_reject:
        current artifact DraftPlan via AcceptanceReviewComment.current_artifact
        route "Rejected plan goes to PlanAuthor." -> PlanAuthor

agent AcceptanceReviewDemo:
    role: "Emit the review comment and end with a control-ready JSON result."
    review: AcceptanceReview

    inputs: "Inputs"
        DraftPlan
        ReviewHistoryFile

    outputs: "Outputs"
        AcceptanceReviewComment
        AcceptanceControlFinalResponse

    final_output: AcceptanceControlFinalResponse
```

### 10.2 Best-case rendered markdown

```markdown
Emit the review comment and end with a control-ready JSON result.

## Acceptance Review

Review subject: Draft Plan.
Shared review contract: Plan Review Contract.

### Contract Checks

Reject: The latest rejected review still lacks closure.
Accept only if The acceptance review contract passes.

### If Accepted

Current artifact: Draft Plan.

Accepted plan goes to Review Lead.

### If Rejected

Current artifact: Draft Plan.

Rejected plan goes to Plan Author.

#### Carrier

Carrier output: Acceptance Review Comment.

#### Emits Semantics

| Semantic | Carrier Field |
| --- | --- |
| Verdict | `verdict` |
| Reviewed Artifact | `reviewed_artifact` |
| Analysis | `analysis_performed` |
| Readback | `output_contents_that_matter` |
| Current Artifact | `current_artifact` |
| Next Owner | `next_owner` |
| Blocked Gate | `failure_detail.blocked_gate` |
| Failing Gates | `failure_detail.failing_gates` |

## Inputs

### Draft Plan

- Source: File
- Path: `unit_root/DRAFT_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

### Review History File

- Source: File
- Path: `unit_root/REVIEW_HISTORY.md`
- Shape: Markdown Document
- Requirement: Required
- Structure: Review History

#### Structure: Review History

##### Entries

Ordered collection of Review Entry items.

## Outputs

### Acceptance Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Verdict

State whether the plan passed review or asked for changes.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.

#### Current Artifact

Name the artifact that remains current after review.

#### Next Owner

Name the next owner when the review routes.

#### Failure Detail

Show this only when verdict is changes requested.

##### Blocked Gate

Name the blocking gate when review stopped early.

##### Failing Gates

List exact failing gates in authored order.

### Acceptance Control Final Response

> **Final answer contract**
> End the turn with one final assistant message that follows this schema.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Acceptance Control JSON |
| Projection | Acceptance Control |
| Projection role | Control |
| Requirement | Required |

#### Semantic Projection

This final response projects review semantics from Acceptance Review.

| Semantic Field | Output Field |
| --- | --- |
| Verdict | `verdict` |
| Current Artifact | `current_artifact` |
| Next Owner | `next_owner` |
| Blocked Gate | `blocked_gate` |

This final response is control-ready.

#### Read on Its Own

This final JSON should be enough for a host to read the review outcome.
```

---

## 11. Summary of what changes materially

If you only care about the architectural delta, it is this:

- `input`, `output`, `skill`, `decision`, `route_only`, and `grounding` all become inheritable
- `decision` gets a keyed normalized body and a first-class `decisions` block
- Doctrine gets selectors and collection descendants, so “the last matching thing in a file” becomes modelable
- Doctrine gets `semantic` and `projection`, so review semantics become authored and reusable
- `review_family` disappears
- `payload_schema` removes owner-sensitive `schema` overload
- bound roots become canonical aliases rather than textually special cases

That package is internally consistent. It makes Doctrine smaller in concept even though it adds a few declarations, because it replaces special rules with shared algebras.
~~~~

### R2 — Doctrine redesign extension spec — docs/LANGUAGE_REDESIGN_EXT_SPEC.md
~~~~markdown
# Doctrine redesign extension spec

This document extends `docs/LANGUAGE_REDESIGN_SPEC.md`.

That base spec is the canonical redesign source.

If the two docs disagree:

- `docs/LANGUAGE_REDESIGN_SPEC.md` wins
- this doc must be read as a later-phase extension
- this doc may add new surfaces, but it does not reopen base redesign choices

This doc does not restate the base redesign package.
It assumes the shipped redesign already includes:

- rich inheritance parity
- selector and `binds` support
- semantic records and projections
- removal of `review_family` as a real primitive
- normalization of `decision`, `route_only`, and `grounding`
- `payload_schema` as the JSON payload schema field
- canonical alias semantics for bound roots

This doc keeps those choices intact.

In particular:

- `review_family` stays removed as a first-class primitive
- the base inheritance and patch algebra stays authoritative
- `binds:` remains the base addressable alias feature
- `payload_schema:` stays the canonical JSON payload schema field
- `route_only` and `grounding` stay first-class in the base phase

The goal here is simple:

- add meta-abstractions that the base redesign does not yet cover
- keep explicitness, determinism, and readable rendered output
- avoid new overlaps with the base spec

---

## 0. Extension scope

This doc only covers additive surfaces that can sit on top of the base redesign.

It does not define:

- an alternate patch system
- an alternate removal plan for `review_family`
- an alternate JSON schema naming rule
- an alternate replacement for `binds`

The extension set in this document is:

1. parameterized declarations and named instantiation
2. lexical `let` bindings for derived values
3. quantified collection expressions
4. import aliasing and selective imports
5. `display_title` for dynamic rendered headings
6. read-only mention semantics with `@`
7. typed local route selection over proven enum bindings
8. native typed data contracts
9. first-class path roots and typed file paths
10. package exports and public library barrels
11. mixins without multiple inheritance
12. later-phase protocols and structural conformance
13. minimal historical state as a host-bound input surface

---

## 1. Parameterized declarations

This is an additive extension.

It does not replace inheritance.
It makes reusable declarations easier to specialize.

### 1.1 Syntax

```ebnf
decl_header      := DECL_KW CNAME param_list? inheritance? ":" string
param_list       := "(" param ("," param)* ")"
param            := CNAME ":" type_ref ("=" expr)?

instantiated_ref := name_ref arg_list?
arg_list         := "(" named_arg ("," named_arg)* ")"
named_arg        := CNAME "=" expr
```

Legal parameter kinds in this phase include:

- scalar types such as `string`, `integer`, `number`, and `bool`
- enum types
- declaration-family refs such as `agent`, `workflow`, `route_only`, `grounding`, `schema`, `document`, `skill`, `skills`, `inputs`, `outputs`, `input`, `output`, `analysis`, `decision`, `review`, `semantic`, `projection`, and `data`

### 1.2 How it works

A parameterized declaration is a compile-time template.

Instantiating it produces a specialized declaration value with stable identity.
That identity is based on the declaration plus its fully resolved named arguments.

Rules:

- parameters are immutable
- arguments are always named
- positional arguments are not supported
- defaults are compile-time expressions
- a parameter without a default is required
- a parameterized declaration may inherit from an instantiated parent
- unknown parameters are compile errors
- duplicate arguments are compile errors
- missing required arguments are compile errors
- type mismatches are compile errors

Parameters may be used in:

- prose interpolation
- guards and conditions
- route targets, when the parameter type is `agent`
- `display_title`
- ref-bearing sites such as `use`, `include`, `schema`, `structure`, `type`, and `carrier`

Concrete `agent` declarations do not take parameters in the first shipped form of this feature.
Reusable declarations carry the abstraction.

### 1.3 Example usage

```doctrine
enum EditMode: "Edit Mode"
    polish: "Polish"
    rewrite: "Rewrite"

agent ReviewLead: "Review Lead"
    role: "Own review."

workflow Delivery(mode: EditMode, next_owner: agent): "Delivery"
    display_title: "{{mode}} Delivery"
    "Do the {{mode}} pass."

    next_step: "Next Step"
        route "When ready" -> next_owner

agent PolishDeliveryAgent: "Polish Delivery Agent"
    role: "Deliver one parameterized workflow instance."

    workflow: Delivery(mode=EditMode.polish, next_owner=ReviewLead)
```

### 1.4 Best-case rendered markdown

```markdown
# Polish Delivery Agent

Deliver one parameterized workflow instance.

## Polish Delivery

Do the Polish pass.

### Next Step

- When ready -> Review Lead
```

---

## 2. Lexical `let` bindings

This is an additive extension on top of the base `binds:` feature.

`binds:` still names addressable nodes and selected paths.
`let` names derived values, computed scalars, and reusable refs inside a local scope.

### 2.1 Syntax

```ebnf
let_stmt   := "let" CNAME type_annot? "=" expr NL
type_annot := ":" type_ref
```

### 2.2 How it works

`let` introduces a local immutable binding.

Rules:

- bindings are lexical
- a name is visible from the next line onward
- nested bodies may read outer bindings
- shadowing is not allowed in the first shipped form
- `let` bindings are not rendered by themselves
- type annotation is optional when the type is clear
- type annotation is required when inference would be ambiguous

`let` does not widen what a surface may read.
It only names values that are already legal in that surface.

In this phase, `let` is legal in declaration bodies that already allow expressions or interpolation, including:

- `workflow`
- `review`
- `analysis`
- `route_only`
- `grounding`
- titled prose bodies that already support interpolation

### 2.3 Example usage

```doctrine
input CurrentPlan: "Current Plan"
    source: File
        path: "track_root/current-plan.md"
    shape: MarkdownDocument
    requirement: Required
    "Use this as the current plan truth."

workflow ReadFirst: "Read First"
    let plan = CurrentPlan
    let plan_path = CurrentPlan:source.path

    "Read {{plan}} at `{{plan_path}}` before you act."

agent LocalBindingAgent: "Local Binding Agent"
    role: "Use local bindings to keep prose dry."

    workflow: ReadFirst

    inputs: "Inputs"
        CurrentPlan
```

### 2.4 Best-case rendered markdown

```markdown
# Local Binding Agent

Use local bindings to keep prose dry.

## Read First

Read Current Plan at `track_root/current-plan.md` before you act.

## Inputs

### Current Plan

- Source: File
- Path: `track_root/current-plan.md`
- Shape: Markdown Document
- Requirement: Required

Use this as the current plan truth.
```

---

## 3. Quantified collection expressions

This is an additive extension.

Selectors from the base redesign still choose items from ordered collections.
Quantifiers summarize whole collections.

### 3.1 Syntax

```ebnf
expr := ...
     | "all" CNAME "in" expr ":" expr
     | "any" CNAME "in" expr ":" expr
     | "count" CNAME "in" expr
     | "count" CNAME "in" expr ":" expr
```

### 3.2 How it works

Collections may come from:

- selector-driven collection paths from the base redesign
- list-valued host inputs
- native data list fields from this extension
- future collection-bearing declaration families

Semantics:

- `all x in c: p` is true when every member satisfies `p`
- `any x in c: p` is true when at least one member satisfies `p`
- `count x in c` returns the member count
- `count x in c: p` returns the count of members that satisfy `p`

Empty collection behavior:

- `all` over empty is true
- `any` over empty is false
- `count` over empty is `0`

The binder name exists only inside the quantified expression.

Quantifiers are legal in:

- guards
- `must` checks
- `stop when`
- `match when`
- `let`
- interpolated scalar expressions that reduce to a number or boolean

### 3.3 Example usage

```doctrine
input GateFacts: "Gate Facts"
    source: Prompt
    shape: JsonObject
    requirement: Required
    failing_gates: "Failing Gates"

workflow ReviewMath: "Review Math"
    let failing_count = count gate in GateFacts.failing_gates
    "Do not accept while {{failing_count}} failing gates remain."

agent QuantifierAgent: "Quantifier Agent"
    role: "Use quantified expressions over list-valued inputs."

    workflow: ReviewMath

    inputs: "Inputs"
        GateFacts
```

### 3.4 Best-case rendered markdown

```markdown
# Quantifier Agent

Use quantified expressions over list-valued inputs.

## Review Math

Do not accept while 2 failing gates remain.

## Inputs

### Gate Facts

- Source: Prompt
- Shape: Json Object
- Requirement: Required

- Failing Gates: `Failing Gates`
```

---

## 4. Import aliasing and selective imports

This is an additive extension.

It does not change canonical identity.
It only changes how names are spelled in a local module.

### 4.1 Syntax

```ebnf
import_decl := "import" import_path ("as" CNAME)? NL
             | "from" import_path "import" import_item ("," import_item)* NL

import_item := CNAME ("as" CNAME)?
```

Examples:

```doctrine
import shared.contracts as contracts
from shared.owners import ProjectLead as Lead
from ..library.workflows import Delivery, Closing as FinalStep
```

### 4.2 How it works

Two new forms exist:

`import module as alias`
Creates a module alias namespace.

`from module import Name as Alias`
Brings one or more declarations into local scope.

Rules:

- wildcard imports are forbidden
- aliases may not collide with local declarations
- aliases may not collide with other imported names
- selective imports do not change declaration identity
- before package barrels exist, `from module import Name` may target that module's exported local names
- once package barrels exist, cross-package selective import should prefer the package barrel

### 4.3 Example usage

```doctrine
import shared.contracts as contracts
from shared.owners import ProjectLead as Lead

workflow ReadFirst: "Read First"
    "Read {{contracts.CurrentPlan}} before you escalate."

    routing: "Routing"
        route "Escalate when blocked" -> Lead

agent ImportAliasAgent: "Import Alias Agent"
    role: "Use module aliases and selective imports."

    workflow: ReadFirst

    inputs: "Inputs"
        contracts.CurrentPlan
```

### 4.4 Best-case rendered markdown

```markdown
# Import Alias Agent

Use module aliases and selective imports.

## Read First

Read Current Plan before you escalate.

### Routing

- Escalate when blocked -> Project Lead

## Inputs

### Current Plan

- Source: Prompt
- Shape: Markdown Document
- Requirement: Required
```

---

## 5. `display_title` for dynamic headings

This is an additive extension.

It preserves the base redesign rule that literal titles stay structural.

### 5.1 Syntax

```ebnf
display_title_field := "display_title" ":" string NL
```

It is legal on any declaration or titled keyed item that already has a literal title.

### 5.2 How it works

Rules:

- the literal title stays structural
- `display_title` is optional and render-only
- `display_title` may interpolate parameters, `let` bindings, bind names, and addressable refs
- rendered headings use `display_title` when present
- default read-only mentions use `display_title` when present
- explicit `:title` reads the literal title
- explicit `:display_title` reads the rendered title

This keeps identity stable while allowing dynamic output.

### 5.3 Example usage

```doctrine
enum EditMode: "Edit Mode"
    polish: "Polish"
    rewrite: "Rewrite"

workflow Delivery(mode: EditMode): "Delivery"
    display_title: "{{mode}} Delivery"
    "Run the {{mode}} pass."

agent DisplayTitleAgent: "Display Title Agent"
    role: "Show dynamic headings without making titles unstable."

    workflow: Delivery(mode=EditMode.polish)
```

### 5.4 Best-case rendered markdown

```markdown
# Display Title Agent

Show dynamic headings without making titles unstable.

## Polish Delivery

Run the Polish pass.
```

---

## 6. Read-only mention semantics with `@`

This is an additive extension.

It does not change structural composition.
`use` still means "compose this surface into the current one."
`@` means "mention this surface without composing it."

### 6.1 Syntax

```ebnf
mention_ref    := "@" instantiated_ref
mention_interp := "{{" "@" instantiated_ref projection? "}}"
projection     := ":" projection_path
```

### 6.2 How it works

Rules:

- `use SomeWorkflow` is structural composition
- `@SomeWorkflow` is a read-only mention
- a mention in a readable body renders as a bullet item
- an inline mention renders as a scalar string
- mentions never inline the target body
- mention targets may use named arguments
- `@` is required when the target family is not readable by default

### 6.3 Example usage

```doctrine
workflow SharedRead: "Shared Read"
    first: "First"
        "Read this first."

workflow MentionDemo: "Mention Demo"
    references: "References"
        @SharedRead
        "Return to {{@SharedRead}} if the issue changes."

agent MentionAgent: "Mention Agent"
    role: "Mention workflows without composing them."

    workflow: MentionDemo
```

### 6.4 Best-case rendered markdown

```markdown
# Mention Agent

Mention workflows without composing them.

## Mention Demo

### References

- Shared Read

Return to Shared Read if the issue changes.
```

---

## 7. Typed local route selection

This is a narrow later-phase extension.

The base redesign keeps direct selector routing as the canonical form.
This extension only adds one extra legal source: an enum-typed local binding.

### 7.1 Syntax

```ebnf
route_from_stmt := "route_from" selector_expr ("as" enum_ref)? ":" NL INDENT route_from_arm+ DEDENT
selector_expr   := direct_field_ref | let_name
```

### 7.2 How it works

`route_from` may now accept either:

- a direct declared input or output field ref
- a `let` binding whose type is provably that enum

Rules:

- direct computed expressions are still forbidden
- the bound value must be provably enum-valued
- route arms must stay exhaustive
- duplicate arms are still compile errors
- rendered guidance should preserve the underlying route source when it can

This is a typing convenience.
It is not a general routing language.

### 7.3 Example usage

```doctrine
enum ProofRoute: "Proof Route"
    accept: "Accept"
    change: "Change"

output ProofResult: "Proof Result"
    target: TurnResponse
    shape: Comment
    requirement: Required
    route_choice: "Route Choice"

agent AcceptanceCritic: "Acceptance Critic"
    role: "Accept routed work."

agent ChangeEngineer: "Change Engineer"
    role: "Handle requested changes."

workflow RoutedTurn: "Routed Turn"
    law:
        current none
        let chosen_route: ProofRoute = ProofResult.route_choice

        route_from chosen_route:
            ProofRoute.accept:
                route "Send to Acceptance Critic." -> AcceptanceCritic
            ProofRoute.change:
                route "Send to Change Engineer." -> ChangeEngineer

agent TypedRouteFromAgent: "Typed Route-From Agent"
    role: "Use typed local routing selectors."

    workflow: RoutedTurn

    outputs: "Outputs"
        ProofResult
```

### 7.4 Best-case rendered markdown

```markdown
# Typed Route-From Agent

Use typed local routing selectors.

## Routed Turn

No artifact is current for this turn.

Select one route from Proof Result.Route Choice.
Use exactly one route choice:
- Accept
- Change

If the route choice is Accept:
- Send to Acceptance Critic.

If the route choice is Change:
- Send to Change Engineer.

## Outputs

### Proof Result

- Target: Turn Response
- Shape: Comment
- Requirement: Required

- Route Choice: `Route Choice`
```

---

## 8. Native typed data contracts

This is an additive extension.

It does not change the base redesign naming cleanup.
If a shape still uses external JSON Schema, the field name stays `payload_schema:`.

### 8.1 Syntax

```ebnf
data_decl := "data" CNAME inheritance? ":" string NL INDENT data_body DEDENT
data_body := data_field+

data_field := CNAME ":" string? data_type NL data_field_body?
data_type  := "string"
            | "integer"
            | "number"
            | "bool"
            | "[" data_type "]"
            | "map" "<" "string" "," data_type ">"
            | name_ref
            | data_type "?"
            | data_type "|" data_type
            | "object" NL INDENT data_field+ DEDENT
```

Additional typed machine-structure fields:

```ebnf
input_body        := ... | "type" ":" name_ref NL
output_shape_body := ... | "type" ":" name_ref NL
```

### 8.2 How it works

A `data` declaration is a native machine-structured contract.

Rules:

- the root kind is an object
- fields are required unless marked `?`
- objects are closed by default
- field order is preserved
- enum refs serialize by their wire value when present, else by their member literal
- `type:` may be attached to machine-structured `input` and `output shape` declarations
- `type:` and `payload_schema:` are mutually exclusive on the same shape
- build tools may lower native data declarations to JSON Schema

This makes Doctrine the source of truth for structured payload shapes when a project wants that model.

### 8.3 Example usage

```doctrine
enum BuildStatus: "Build Status"
    ok: "ok"
    action_required: "action_required"

data RepoStatus: "Repo Status"
    summary: "Summary" string
        "Short natural-language status."

    status: "Status" BuildStatus
        "Current repo outcome."

    next_step: "Next Step" string?
        "Omit only when no follow-up is needed."

output shape RepoStatusJson: "Repo Status JSON"
    kind: JsonObject
    type: RepoStatus

output RepoStatusFinalResponse: "Repo Status Final Response"
    target: TurnResponse
    shape: RepoStatusJson
    requirement: Required

agent NativeDataAgent: "Native Data Agent"
    role: "End the turn with a Doctrine-native JSON contract."

    outputs: "Outputs"
        RepoStatusFinalResponse

    final_output: RepoStatusFinalResponse
```

### 8.4 Best-case rendered markdown

```markdown
# Native Data Agent

End the turn with a Doctrine-native JSON contract.

## Final Output

### Repo Status Final Response

> **Final answer contract**
> End the turn with one final assistant message that follows this contract.

| Contract | Value |
| --- | --- |
| Message type | Final assistant message |
| Format | Structured JSON |
| Shape | Repo Status JSON |
| Requirement | Required |

#### Payload Fields

| Field | Type | Notes |
| --- | --- | --- |
| `summary` | string | Short natural-language status. |
| `status` | Build Status | Current repo outcome. |
| `next_step` | string? | Omit only when no follow-up is needed. |
```

---

## 9. Path roots and typed file paths

This is an additive extension for host-bound file locations.

It does not replace the base redesign selector path algebra.
Selector paths still use the base `Root:field.segment[selector]` form.

This feature only adds typed values for filesystem-like paths in path-bearing fields.

### 9.1 Syntax

```ebnf
path_root_decl := "path_root" CNAME ":" string NL INDENT path_root_body DEDENT
path_root_body := "source" ":" path_root_source NL
                  ("key" ":" string NL)?
                  ("env" ":" string NL)?

path_root_source := "HostMount"
                  | "EnvVar"
                  | "PromptRoot"
                  | "PackageRoot"

file_path_expr := CNAME ("/" string)+
```

Usage in path-bearing fields:

```doctrine
path: section_root / "_authoring" / "SECTION_PLAN.md"
```

### 9.2 How it works

A `path_root` is a symbolic mount declared in Doctrine.

A typed file path value is made from:

- one declared root
- one or more literal path segments

Rules:

- parent traversal such as `..` is forbidden in the first shipped form
- path-bearing fields may accept either legacy string paths or typed file path values
- when both are allowed, render should preserve the symbolic form
- roots resolve at the host boundary, not inside Doctrine source text

### 9.3 Example usage

```doctrine
path_root section_root: "Section Root"
    source: HostMount
    key: "section_root"

input SectionPlan: "Section Plan"
    source: File
        path: section_root / "_authoring" / "SECTION_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    "Read the current section plan."

agent PathRootAgent: "Path Root Agent"
    role: "Use modeled path roots instead of prose-only path notes."

    inputs: "Inputs"
        SectionPlan
```

### 9.4 Best-case rendered markdown

```markdown
# Path Root Agent

Use modeled path roots instead of prose-only path notes.

## Inputs

### Section Plan

- Source: File
- Path Root: Section Root
- Path: `section_root/_authoring/SECTION_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

Read the current section plan.
```

---

## 10. Package exports and public library barrels

This is an additive extension for library-scale Doctrine use.

It is distinct from skill package bundling.
This section is about authored public APIs, not build artifacts.

### 10.1 Syntax

Module-level exports:

```ebnf
export_decl := "export" export_item ("," export_item)* NL
export_item := CNAME ("as" CNAME)?
```

Package barrel:

```ebnf
package_decl := "package" CNAME ":" string NL INDENT package_body DEDENT
package_body := package_metadata? exports_block

package_metadata := "metadata" ":" NL INDENT package_metadata_field+ DEDENT
package_metadata_field := CNAME ":" string NL

exports_block := "exports" ":" string NL INDENT package_export+ DEDENT
package_export := decl_kind CNAME "from" dotted_name ("as" CNAME)? NL
decl_kind := "workflow" | "schema" | "document" | "data" | "protocol"
           | "skill" | "skills" | "inputs" | "outputs" | "review"
           | "route_only" | "grounding" | "analysis" | "decision"
           | "semantic" | "projection"
```

Selective import from a package barrel:

```doctrine
from LessonsCore import Delivery, Inventory
```

### 10.2 How it works

There are two public API layers.

Module export:
marks local names as public from that module.

Package barrel:
defines a stable package namespace that can outlive file layout changes.

Rules:

- package barrels are the stable public namespace for cross-package use
- internal modules may move without breaking consumers if the barrel stays stable
- `from PackageName import Name` may import only package-exported names
- wildcard exports are forbidden
- package barrels may rename exports with `as`

### 10.3 Example usage

```doctrine
workflow Delivery: "Delivery"
    "Deliver the shared workflow."

export Delivery
```

```doctrine
schema LessonInventory: "Lesson Inventory"
    sections:
        summary: "Summary"
            "Summarize the lesson inventory."

export LessonInventory
```

```doctrine
package LessonsCore: "Lessons Core"
    metadata:
        name: "lessons-core"
        version: "1.0.0"
        description: "Stable public Doctrine library for lesson workflows."

    exports: "Exports"
        workflow Delivery from workflows.delivery.Delivery
        schema LessonInventory from schemas.inventory.LessonInventory as Inventory
```

Consumer:

```doctrine
from LessonsCore import Delivery, Inventory
```

### 10.4 Best-case rendered markdown

```markdown
---
name: "lessons-core"
version: "1.0.0"
description: "Stable public Doctrine library for lesson workflows."
---

# Lessons Core

## Exports

- Delivery — workflow
- Inventory — schema
```

---

## 11. Mixins without multiple inheritance

This is an additive extension.

It keeps single-parent inheritance as the only parent model.
Mixins are reusable fragments, not parents.

### 11.1 Syntax

```ebnf
workflow_mixin_decl := "workflow" "mixin" CNAME inheritance? ":" string NL INDENT workflow_body DEDENT
skills_mixin_decl   := "skills" "mixin" CNAME inheritance? ":" string NL INDENT skills_body DEDENT
inputs_mixin_decl   := "inputs" "mixin" CNAME inheritance? ":" string NL INDENT io_body DEDENT
outputs_mixin_decl  := "outputs" "mixin" CNAME inheritance? ":" string NL INDENT io_body DEDENT
document_mixin_decl := "document" "mixin" CNAME inheritance? ":" string NL INDENT document_body DEDENT
review_mixin_decl   := "review" "mixin" CNAME inheritance? ":" string NL INDENT review_body DEDENT

include_stmt := "include" instantiated_ref NL
```

### 11.2 How it works

A mixin is a non-rendering fragment declaration for one family.

Rules:

- a mixin is not a render root
- a mixin may be parameterized
- a mixin may inherit from mixins of the same family
- a declaration may include any number of mixins in authored order
- include expansion happens before ordinary family validation
- after expansion, the family follows the same ordinary rules it would use for inline authored content
- mixins do not create a second inheritance system

This keeps the base redesign patch and inheritance rules intact.

### 11.3 Example usage

```doctrine
skill GroundingSkill: "Grounding Skill"
    purpose: "Ground the current claim before you write."

skill CopyRewriteSkill: "Copy Rewrite Skill"
    purpose: "Rewrite reader-facing text."

skills mixin CommonSupport: "Common Support"
    support: "Support"
        skill grounding: GroundingSkill
            requirement: Advisory

skills CopywriterSkills: "Skills"
    can_run: "Can Run"
        skill rewrite: CopyRewriteSkill
            requirement: Required

    include CommonSupport

agent MixinAgent: "Mixin Agent"
    role: "Use mixin-composed skills without multiple inheritance."

    skills: CopywriterSkills
```

### 11.4 Best-case rendered markdown

```markdown
# Mixin Agent

Use mixin-composed skills without multiple inheritance.

## Skills

### Can Run

#### Copy Rewrite Skill

##### Purpose

Rewrite reader-facing text.

This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.

### Support

#### Grounding Skill

##### Purpose

Ground the current claim before you write.
```

---

## 12. Later-phase protocols and structural conformance

This is a later-phase extension.

It is not part of the base redesign phase.
It does not demote or replace `route_only`, `grounding`, `review`, `semantic`, or `projection`.

Protocols are structural constraints only.
They are not reusable content blocks.

### 12.1 Syntax

```ebnf
protocol_decl := "protocol" CNAME inheritance? ":" string NL INDENT protocol_body DEDENT
protocol_body := "kind" ":" CNAME NL
                 protocol_clause+

protocol_clause := fields_clause
                 | trust_surface_clause
                 | slot_clause
                 | property_clause

fields_clause := "fields" ":" NL INDENT protocol_field+ DEDENT
protocol_field := CNAME ":" string? protocol_field_kind NL
protocol_field_kind := "scalar"
                     | "scalar" "optional"
                     | name_ref
                     | "readable"

trust_surface_clause := "trust_surface" ":" NL INDENT CNAME+ DEDENT
slot_clause := "requires_slot" ":" CNAME NL
property_clause := "requires_property" ":" CNAME NL

conforms_field := "conforms_to" ":" name_ref ("," name_ref)* NL
```

### 12.2 How it works

A protocol is a compile-time structural contract.

Rules:

- `kind` states the target family, such as `output`, `input`, `agent`, `workflow`, or `document`
- a declaration may `conforms_to` one or more protocols of its own kind
- protocols may inherit other protocols
- conformance is compile-time only
- protocols do not inject fields or prose
- protocols may be exported and published through package barrels

### 12.3 Example usage

```doctrine
protocol RouteCarrier: "Route Carrier"
    kind: output

    fields:
        next_owner: "Next Owner" scalar
        current_artifact: "Current Artifact" scalar optional

    trust_surface:
        next_owner

output HandoffComment: "Handoff Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required
    conforms_to: RouteCarrier

    next_owner: "Next Owner"
        "Name the honest next owner."

    trust_surface:
        next_owner

agent ProtocolAgent: "Protocol Agent"
    role: "Emit an output that conforms to a reusable protocol."

    outputs: "Outputs"
        HandoffComment
```

### 12.4 Best-case rendered markdown

```markdown
# Protocol Agent

Emit an output that conforms to a reusable protocol.

## Outputs

### Handoff Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required
- Protocols: Route Carrier

#### Next Owner

Name the honest next owner.
```

---

## 13. Minimal historical state as a host-bound input

This is an optional host surface.

It is not a general state-machine DSL.
It is a small previous-turn snapshot for retry and reroute sanity.

### 13.1 Syntax

Built-in input source:

```doctrine
source: History
```

Optional history field map:

```ebnf
input_body := ... | history_fields_clause

history_fields_clause := "history_fields" ":" NL INDENT history_field+ DEDENT
history_field := CNAME ":" string NL
```

### 13.2 How it works

The host provides a bounded history snapshot.

Recommended first-phase field set:

- `previous_current_artifact`
- `previous_next_owner`
- `turn_index`
- `retry_count`
- `previous_invalidations`

Rules:

- this input is read-only
- it is advisory by default
- it is intentionally shallow
- absent host support behaves like any other missing input source
- this surface is for immediate retry and reroute checks, not long-term memory

When native data contracts are used, a history input may also declare `type:`.

### 13.3 Example usage

```doctrine
data TurnState: "Turn State"
    previous_current_artifact: "Previous Current Artifact" string?
    previous_next_owner: "Previous Next Owner" string?
    turn_index: "Turn Index" integer
    retry_count: "Retry Count" integer

input TurnHistory: "Turn History"
    source: History
    shape: JsonObject
    type: TurnState
    requirement: Advisory

    history_fields:
        previous_current_artifact: "Previous Current Artifact"
        previous_next_owner: "Previous Next Owner"
        turn_index: "Turn Index"
        retry_count: "Retry Count"

    "Use this only to detect immediate retries or stale reroutes."

agent HistoryAwareAgent: "History-Aware Agent"
    role: "Use one bounded history snapshot without turning Doctrine into a state machine."

    inputs: "Inputs"
        TurnHistory
```

### 13.4 Best-case rendered markdown

```markdown
# History-Aware Agent

Use one bounded history snapshot without turning Doctrine into a state machine.

## Inputs

### Turn History

- Source: History
- Shape: Json Object
- Type: Turn State
- Requirement: Advisory

#### History Fields

- Previous Current Artifact
- Previous Next Owner
- Turn Index
- Retry Count

Use this only to detect immediate retries or stale reroutes.
```

---

## 14. Summary

If the base redesign is the hard cutover:

- `docs/LANGUAGE_REDESIGN_SPEC.md` defines the canonical core language
- this extension doc adds later surfaces without reopening that core

The clean extension set is:

- parameters for reusable declarations
- lexical `let` bindings
- quantifiers for collections
- import aliasing
- render-only dynamic titles
- read-only mentions
- typed local route selection
- native data contracts
- typed file path roots
- public package barrels
- mixins
- optional later-phase protocols
- one bounded history input

That keeps the redesign consistent.
The base spec stays small and decisive.
This doc carries only the extra abstractions that can be layered on top.

~~~~
<!-- arch_skill:block:reference_pack:end -->
