---
title: "Doctrine - Workflow Law Hard Cutover - Architecture Plan"
date: 2026-04-10
status: complete
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/COMPILER_ERRORS.md
  - examples/README.md
  - editors/vscode/README.md
---

> Historical note: this file is preserved as the 2026-04-10 implementation plan
> for the workflow-law cutover. For the live shipped reference, use
> [`../../WORKFLOW_LAW.md`](../../WORKFLOW_LAW.md).

# TL;DR

## Outcome

Doctrine ships the full workflow-law v1 surface from
`docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md` as the only live
language for this feature family: parser, model, compiler, renderer, corpus,
docs, and VS Code all agree on `law`, `trust_surface`, carriers, branch
currentness, preservation, invalidation, and law reuse.

## Problem

Before this cutover, the shipped language, compiler, renderer, corpus runner,
and VS Code extension still stopped at the pre-law world through
`examples/29_enums`, while `examples/30_*` through `examples/38_*` were only
planned review surfaces. That left Doctrine with a split between intended
language and shipped language, and the editor stack mirrored the old language
rather than the target one.

## Approach

Implement the spec as one end-to-end hard cutover inside the existing Doctrine
owner paths:
- extend `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, and
  `doctrine/model.py` with first-class workflow-law and trust-surface syntax
- add compiler-owned law semantics, diagnostics, and render ordering in
  `doctrine/compiler.py`, `doctrine/diagnostics.py`, and `doctrine/renderer.py`
- activate and repair the `30_*` through `38_*` examples as proof, using them
  as intent anchors instead of treating their current authored details as law
- update the VS Code syntax/resolver stack to track the shipped grammar and the
  new definition/navigation surfaces
- remove workflow-law split-brain documentation and proof rules in the same run

## Plan

1. Add the full syntax and AST for `law`, `trust_surface`, and the bounded law
   expression/path surfaces.
2. Implement normalized workflow-law compilation, branch validation, carrier
   invariants, rendering, and dedicated diagnostics.
3. Convert the workflow-law examples from planned review surfaces into active
   proof and regenerate their checked artifacts.
4. Bring the VS Code extension into parity for highlighting, indentation,
   navigation, and alignment checks.
5. Rewrite or delete stale live docs so the shipped truth exists in one place.

## Non-negotiables

- No scope cutting relative to the spec's v1 boundary.
- No runtime shims, fallback semantics, or compatibility layer for the old
  workflow-law-free model.
- No encoding the current `30_*` through `38_*` examples as if they were
  normative; the compiler must implement the spec and use the examples as
  illustrative receipts.
- No leaving workflow-law as planned-only corpus truth after implementation.
- No leaving the VS Code extension on the pre-law grammar after the compiler
  ships the new language.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-10
external_research_grounding: not needed for this repo-local language cutover
deep_dive_pass_2: done 2026-04-10
phase_plan: done 2026-04-10
recommended_flow: confirm or revise north star -> implement -> audit-implementation
note: This is a warn-first checklist only. It should not hard-block execution. Phase planning was completed against a still-draft North Star because the user explicitly requested the phase-plan pass before approval.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, a clean checkout can parse, compile,
render, verify, emit, and editor-navigate the full workflow-law v1 surface
defined in
`docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md`, with
`examples/30_*` through `examples/38_*` promoted from planned review examples
to active proof, and without leaving any live shipped docs or editor behavior
that still describe the old subset as the truth.

## 0.2 In scope

- Full v1 syntax from the spec:
  - `law` on `workflow`
  - `trust_surface` on `output`
  - `current artifact ... via ...`
  - `current none`
  - `invalidate ... via ...`
  - `active when`
  - `mode`
  - `must`
  - `when`
  - `match`
  - `own only`
  - `preserve exact`
  - `preserve structure`
  - `preserve decisions`
  - `preserve mapping`
  - `preserve vocabulary`
  - `support_only ... for comparison`
  - `ignore ... for truth|comparison|rewrite_evidence`
  - `forbid`
  - `stop`
  - explicit `route "..." -> Agent`
  - named law subsections plus `inherit` / `override` inside inherited
    workflows
- The bounded v1 law-expression and law-path surface needed by the spec.
- Compiler-owned branch analysis, carrier invariants, output coupling,
  ownership/preservation contradiction checks, invalidation checks, and
  rendering order.
- Dedicated diagnostics and updates to the canonical error catalog.
- Corpus activation and repair for `examples/30_*` through `examples/38_*`,
  including checked `ref/` and `build_ref/` artifacts where applicable.
- Emit pipeline changes required for newly active build-contract examples.
- VS Code highlighting, indentation, alignment validation, and navigation for
  the shipped workflow-law syntax and references.
- Live docs convergence: shipped language notes, error docs, examples docs, and
  extension docs must all describe the implemented language truth.

## 0.3 Out of scope

- Deferred features explicitly excluded by the spec:
  - `obligation`
  - `lens`
  - `concern`
  - `current status`
  - nominal artifact typing as a declaration family
  - basis roles beyond `truth`, `comparison`, and `rewrite_evidence`
  - targetless `route`
  - top-level reusable `law` declarations
  - `let`
  - packet-like or free-floating coordination tokens
- Any attempt to keep the old pre-law subset and the new law subset live as
  parallel authoring modes for the same feature family.
- New editor capabilities outside parity needs, such as hover, completion,
  rename, or a language server.
- Productizing proposal-only docs as additional live truth surfaces once the
  shipped docs absorb their final conclusions.

## 0.4 Definition of done (acceptance evidence)

- `make verify-examples` passes with `examples/30_*` through `examples/38_*`
  active.
- `make verify-diagnostics` passes with new workflow-law diagnostics and updated
  error normalization.
- `cd editors/vscode && make` passes with syntax, snapshot, integration, and
  Lark-alignment checks covering the new surface.
- The emitted/build-contract examples still compile and materialize their
  checked trees.
- The shipped docs no longer say the active corpus stops at `29`, and the
  extension docs no longer describe only the pre-law surface as shipped truth.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks.
- No dual sources of truth between shipped docs, examples, compiler behavior,
  and VS Code behavior.
- Compiler semantics own the language; examples demonstrate and verify them.
- Every active law leaf branch resolves exactly one current-subject form.
- Transferable currentness and invalidation require declared trusted carriers.
- Inherited workflow law patches are explicit, exhaustive, and fail loud.
- The editor stack may mirror the compiler, but it must not drift from the
  shipped grammar or supported reference semantics.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Semantic correctness against the spec's v1 boundary.
2. Hard cutover with no split-brain shipped truth.
3. Fail-loud diagnostics over permissive or inferred behavior.
4. Full corpus and editor parity in the same merge.
5. Maintainability of the new language surfaces inside the existing Doctrine
   owner paths.

## 1.2 Constraints

- The current parser, AST, compiler, renderer, and extension are all built
  around the pre-law workflow and record model.
- `editors/vscode/resolver.js` is effectively a second parser/indexer written
  in regexes and indentation heuristics; it must be kept in sync explicitly.
- `verify_corpus` currently distinguishes `active` from `planned`, so the
  workflow-law examples are not yet proof.
- The examples are useful but may encode mistakes; implementation must follow
  the spec intent and then repair the examples.
- The repo doctrine prefers live shipped truth in `doctrine/`, current docs,
  and manifest-backed examples, not sidecar planning or historical live docs.

## 1.3 Architectural principles (rules we will enforce)

- Extend existing declaration families instead of inventing a parallel
  coordination language.
- Keep `workflow` as the semantic home of law and `output` as the semantic home
  of downstream trust.
- Use dedicated AST and compiler structures for workflow law instead of
  smuggling it through generic record bodies or prose strings.
- Normalize law before rendering so diagnostics and output ordering do not
  depend on authored statement order beyond explicit branch structure.
- Prefer one compiler-owned semantic pass for law validation rather than
  distributing critical invariants across ad hoc render-time checks.
- Treat the VS Code extension as a mirror of shipped grammar and reference
  semantics, not as an independent language design surface.

## 1.4 Known tradeoffs (explicit)

- This is a large cutover touching grammar, AST, compiler, corpus, docs, and
  editor tooling at once, but that breadth is required to avoid two live
  languages.
- The current compiler is optimized for section-oriented rendering, so
  introducing workflow law will increase AST and normalization complexity.
- Keeping the VS Code extension regex/indexer instead of replacing it with a
  language server preserves the current editor architecture, but it means every
  grammar change must be mirrored carefully.
- Activating `30_*` through `38_*` may require substantial changes to authored
  prompts, refs, and diagnostic expectations because those examples are
  illustrative, not canonical.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Doctrine ships a grammar rooted in declarations such as `workflow`, `skills`,
  `inputs`, `outputs`, `input`, `output`, `skill`, `enum`, `agent`, and
  `abstract agent`.
- The parser and model (`doctrine/parser.py`, `doctrine/model.py`) materialize
  workflows as preamble prose plus keyed workflow items, records as prose plus
  keyed items, and outputs as ordinary record bodies.
- The compiler (`doctrine/compiler.py`) resolves inheritance, composition,
  addressable refs, typed I/O, and rendering surfaces through section-oriented
  structures such as `ResolvedWorkflowBody`, `ResolvedIoBody`, and
  `CompiledSection`.
- The renderer (`doctrine/renderer.py`) is a generic tree-to-Markdown renderer
  with no workflow-law-specific ordering or phrasing.
- The active corpus ends at `examples/29_enums`, while `examples/30_*` through
  `examples/38_*` are marked `planned` and only produce advisory diffs in
  `doctrine/verify_corpus.py`.
- The VS Code extension mirrors the old language using regex-driven syntax
  rules, indentation rules, and a resolver/indexer in
  `editors/vscode/resolver.js`.

## 2.2 What's broken / missing (concrete)

- The language described by the workflow-law spec does not exist in the shipped
  grammar.
- The AST has no first-class representation for law statements, law sections,
  trust surfaces, or bounded law expressions/paths.
- The compiler cannot validate or render:
  - branch-scoped currentness
  - carrier invariants
  - mode-gated exhaustiveness
  - ownership/preservation contradictions
  - basis-role contradictions
  - invalidation as a truth transition
  - law reuse through named subsections in inherited workflows
- The renderer cannot emit the human-first law ordering mandated by the spec.
- The corpus runner still treats the workflow-law example suite as review-only
  instead of proof.
- The extension cannot highlight or navigate the new keywords, law-section
  inheritance keys, carrier refs, or law-path-bearing surfaces.
- Multiple docs still state that the shipped corpus stops at `29`, which would
  become false the moment the compiler starts supporting the new language.

## 2.3 Constraints implied by the problem

- Implementation must change the full compiler pipeline, not just rendering or
  docs.
- The extension cannot be patched casually; its regex classifiers and
  navigation surfaces must be updated in lockstep with the grammar.
- Corpus activation must happen after compiler semantics are real, not before.
- Examples must be repaired against the compiler-owned truth rather than used
  to back-fill semantics the compiler does not yet define.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- None adopted for this plan. This is a repo-defined language cutover whose
  authoritative target is the local spec plus shipped code, and external prior
  art would not overrule that local contract.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` - the shipped grammar and keyword set.
    It currently has no `law`, `trust_surface`, `when`, `match`, or workflow-law
    expression surface.
  - `doctrine/parser.py` and `doctrine/indenter.py` - grammar-to-AST lowering,
    indentation ownership, body staging, and parse-stage structural failures.
    They currently have no typed law or trust-surface lowering.
  - `doctrine/model.py` - the frozen AST. It currently has `WorkflowBody`,
    `IoBody`, `RecordItem`, `RouteLine`, and explicit patch nodes, but no
    workflow-law, trust-surface, carrier, or bounded law-path nodes.
  - `doctrine/compiler.py` - shipped semantic resolution, inheritance, typed
    IO, addressable refs, diagnostics triggers, and compiled render model. It
    currently normalizes pre-law workflows into sections, refs, skills, and
    route lines only.
  - `doctrine/renderer.py` - current generic Markdown tree renderer. It has no
    workflow-law-specific ordering or phrasing.
  - `doctrine/diagnostics.py` and `doctrine/diagnostic_smoke.py` - canonical
    parse/compile/emit error shaping and stable-code smoke coverage. There is
    no workflow-law-specific diagnostic catalog yet.
  - `doctrine/verify_corpus.py` - current proof model, including the
    `planned`/`active` split. `planned` cases are not proof and do not run the
    normal render/build/failure contracts.
  - `doctrine/emit_docs.py` plus `pyproject.toml` - shipped emit pipeline and
    build-contract owner. `example_36_invalidation_and_rebuild` is already
    configured as an emit target even though the parser cannot yet admit its
    prompts.
  - `Makefile` - the repo-level verification gates remain `verify-examples` and
    `verify-diagnostics`.
  - `editors/vscode/package.json`, `editors/vscode/extension.js`,
    `editors/vscode/resolver.js`,
    `editors/vscode/language-configuration.json`,
    `editors/vscode/syntaxes/doctrine.tmLanguage.json`, and
    `editors/vscode/scripts/validate_lark_alignment.py` - the single shipped
    editor mirror path for highlighting, link-follow, definition resolution,
    indentation, and grammar drift checks.
- Canonical path / owner to reuse:
  - `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, and
    `doctrine/model.py` must own the syntax and AST boundary for law and trust
    surfaces. Do not encode workflow law as generic record or prose nodes.
  - `doctrine/compiler.py` must own normalized workflow-law semantics, branch
    validation, carrier invariants, currentness and invalidation analysis, and
    render-ready law ordering. Do not push semantic ownership into examples,
    docs, or the renderer.
  - `doctrine/verify_corpus.py` must remain the proof boundary. Activate
    workflow-law proof by moving the manifests onto the existing runner, not by
    inventing a second verifier surface.
  - `doctrine/emit_docs.py` must remain the emitted-tree owner. Keep the
    current `pyproject.toml` target path and repair the parser/compiler beneath
    it rather than introducing a workflow-law-specific emit path.
  - `editors/vscode/resolver.js` must remain the single editor navigation owner
    unless the repo chooses a language-server architecture later. This cutover
    should enrich the existing mirror path, not replace it.
- Existing patterns to reuse:
  - explicit keyed-body plus `inherit` / `override` accounting in `workflow`,
    `skills`, `inputs`, and `outputs` already exists and should be extended to
    law reuse rather than replaced with a parallel coordination model.
  - parse-time body staging already separates prose from typed items and fails
    loud on mixed ordering. A future `LawBody` should follow that same
    structure.
  - `route` is the current example of a typed workflow statement with grammar,
    AST, parser lowering, compile-time validation, and renderer integration.
    Reuse that end-to-end pattern for law statements instead of inventing a
    second workflow parser.
  - `_split_record_items` in `doctrine/compiler.py` is the current seam for
    peeling reserved output keys away from generic record extras. If
    `trust_surface` can live as a reserved output child without corrupting the
    record model, this is the existing place to do it.
  - typed declaration validation and humanized diagnostics already exist and
    should be widened with new dedicated codes instead of falling back to
    generic `E299`.
  - addressable path traversal already exists for record, workflow, skills, and
    enum surfaces and may inform law-path resolution, but law paths are a
    distinct semantic surface and should not be collapsed into authored
    readable refs by default.
  - the VS Code extension already has reusable seams:
    TextMate keyword repositories, regex-based site collection in
    `resolver.js`, and three proof layers under `tests/unit`, `tests/snap`, and
    `tests/integration`.
- Prompt surfaces / agent contract to reuse:
  - `examples/30_*` through `examples/38_*` - illustrative authoring and
    failure-shape intent for the workflow-law family
  - `examples/README.md` - corpus sequencing and activation policy
- Current hard-cut blockers already confirmed by repo evidence:
  - sampled workflow-law prompts under `examples/30_*`, `examples/31_*`,
    `examples/36_*`, and `examples/38_*` currently fail at parse time on
    `law:` or `trust_surface:` rather than reaching compiler semantics.
  - `doctrine/verify_corpus.py` currently skips `examples/30_*` through
    `examples/38_*` because every case is still marked `planned`.
  - `uv run --locked python -m doctrine.emit_docs --target example_36_invalidation_and_rebuild`
    fails at the same parse boundary, so the configured build target exists but
    is not yet executable proof.
- Native model or agent capabilities to lean on:
  - not applicable; this is a deterministic compiler/editor change, not an
    agent-runtime capability problem.
- Existing grounding / tool / file exposure:
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
  - `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  - `uv run --locked python -m doctrine.emit_docs --target ...`
- Duplicate or drifting paths relevant to this change:
  - `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md` and
    `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_AUDIT_2026-04-10.md` currently hold the
    intended truth while shipped docs still describe the old subset.
  - `examples/README.md` currently says the active shipped corpus stops at `29`.
  - `editors/vscode/resolver.js`,
    `editors/vscode/language-configuration.json`,
    `editors/vscode/syntaxes/doctrine.tmLanguage.json`, and
    `editors/vscode/README.md` mirror the old grammar explicitly.
  - `editors/vscode/scripts/validate_lark_alignment.py` currently only harvests
    quoted lowercase alpha keywords, so underscore keywords such as
    `trust_surface` and `support_only` would drift unless that validator is
    widened.
- Capability-first opportunities before new tooling:
  - none; the work is to extend the existing compiler/editor owners, not to add
    wrappers, parsers, or sidecars around them.
- Behavior-preservation signals already available:
  - active manifest-backed examples through `29`
  - diagnostic smoke checks in `doctrine/diagnostic_smoke.py`
  - configured emit targets in `pyproject.toml` for `example_07_handoffs`,
    `example_14_handoff_truth`, and `example_36_invalidation_and_rebuild`
  - VS Code unit, snapshot, integration, and Lark-alignment checks under
    `editors/vscode/`

## 3.3 Open questions from research

- Whether `law` should become a reserved `WorkflowItem` with its own typed
  `LawBody` or be special-cased through existing section machinery. Evidence
  needed: inherited law patch accounting, AST clarity, and whether typed law
  semantics stay explicit without parallel paths.
- Whether `trust_surface` should remain implemented as a reserved output child
  surface inside the generic output/record split or get a dedicated output-AST
  field/body type. Evidence needed: parse complexity, diagnostic clarity, and
  VS Code parity cost.
- How much of the bounded law-path surface can safely reuse the current
  addressable-path engine without collapsing the semantic distinction between
  law paths and readable refs. Evidence needed: wildcard, set, `except`, and
  conditional trust-surface cases from `examples/33_*` through `examples/38_*`.
- Which parts of the current `planned`-case machinery in `verify_corpus.py`
  remain justified after `30_*` through `38_*` become active? Evidence needed:
  whether any other manifests still intentionally rely on `planned`, or whether
  the feature now mainly hides drift.
- Whether the VS Code resolver's current regex-plus-indentation context stack
  can represent nested `active when`, `when`, and `match` bodies cleanly enough
  for parity. Evidence needed: a prototype editor pass once the grammar exists,
  especially for law-section `inherit` / `override` keys and nested branch
  containers.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark`
  - the single shipped grammar for declarations, record bodies, route lines,
    typed fields, readable refs, addressable dotted paths, and enums
  - workflow and output syntax still stop at the pre-law subset; there is no
    reserved `law` or `trust_surface` surface
- `doctrine/parser.py` plus `doctrine/indenter.py`
  - `parse_text()` / `parse_file()` run Lark and `ToAst`
  - workflow and IO body staging split prose from existing typed items only;
    there are no transform hooks for workflow law or downstream trust
- `doctrine/model.py`
  - frozen AST for `WorkflowBody`, `OutputDecl`, `RecordItem`,
    `AddressableRef`, `RouteLine`, and the current explicit patching nodes
  - there are no law sections, guarded branches, carriers, invalidations,
    trust-surface items, or law-path nodes
- `doctrine/compiler.py`
  - `CompilationContext` indexes declarations and imports, resolves inherited
    workflow/skills/IO structure, compiles outputs and workflows, and provides
    addressable traversal
  - the dominant abstractions are `ResolvedWorkflowBody`, `ResolvedIoSection`,
    `ResolvedIoRef`, and `CompiledSection`
- `doctrine/renderer.py`
  - generic serializer of `CompiledAgent` and `CompiledSection`
- `doctrine/verify_corpus.py`
  - manifest loader and proof runner with explicit `active` versus `planned`
    behavior
- `doctrine/emit_docs.py` plus `pyproject.toml`
  - configured emitted-tree pipeline using the same parse -> compile -> render
    path as ordinary prompt compilation
  - `example_36_invalidation_and_rebuild` is already wired as an emit target
    and has checked `build_ref/` receipts even though the parser cannot admit
    its workflow-law syntax yet
- `doctrine/diagnostics.py` plus `doctrine/diagnostic_smoke.py`
  - parse/compile/emit error normalization and stable-code smoke coverage for
    the shipped subset
- `examples/01_*` through `examples/29_*`
  - active shipped proof corpus
- `examples/30_*` through `examples/38_*`
  - illustrative workflow-law authoring and manifests, still marked `planned`
  - each example already carries prompts, refs, and negative cases; `36` also
    carries a checked build tree
- `docs/*.md` and `editors/vscode/README.md`
  - live documentation still describes the pre-law shipped subset and therefore
    acts as split-brain truth relative to the workflow-law spec and examples
- `editors/vscode/*`
  - repo-local editor mirror using tmLanguage regexes, indentation config,
    resolver/index logic, alignment checks, and extension-host tests
  - it mirrors only the pre-law language surface today

## 4.2 Control paths (runtime)

1. `parse_file()` calls `parse_text()`, which runs the Lark parser and then
   `ToAst` to build `model.PromptFile`.
2. `compile_prompt()` creates `CompilationContext`, indexes declarations and
   imports into `IndexedUnit`, and then compiles one concrete agent.
3. `_compile_agent_decl()` compiles role, inputs, outputs, workflow, and skills
   as mostly separate field-local surfaces before assembling a `CompiledAgent`.
4. `_resolve_io_body()` resolves IO blocks into `ResolvedIoSection` and
   `ResolvedIoRef`, which already contain render-ready `CompiledSection`
   objects. Output semantics therefore collapse before the renderer runs.
5. `_resolve_workflow_body()` and `_resolve_workflow_addressable_body()` are the
   two explicit workflow patch engines. They know sections, `use`, workflow
   skills, `inherit`, and `override`, but nothing about workflow law.
6. `_compile_resolved_workflow()` turns the resolved workflow into generic
   `CompiledSection` trees, and `render_markdown()` simply serializes that
   compiled tree.
7. `verify_corpus()` wraps the same parse -> compile -> render or emit path for
   `active` cases, while `planned` cases are surfaced only as advisory review.
8. `emit_target()` reparses the entrypoint, recompiles each root concrete
   agent, and renders build output. There is no separate emit semantics lane.
9. The VS Code extension performs a separate regex and indentation driven mirror
   for syntax and navigation through `resolver.js`; it does not call the Python
   parser or compiler.

## 4.3 Object model + key abstractions

- `WorkflowBody` owns authored preamble prose plus ordinary keyed workflow
  items. Those items are limited to titled sections, workflow `use`, workflow
  skills, and explicit `inherit` / `override`.
- `OutputDecl` owns an ordinary record body whose typed keys are still
  `target`, `shape`, `requirement`, and optional `files`; everything else falls
  through generic record handling.
- `AddressableRef` is the current typed path surface. It models authored
  readable/addressable descent such as `Decl:path.to.child`; it is not a law
  path algebra.
- The compiler currently keeps two related but separate workflow resolution
  lanes:
  one for fully rendered semantics and one for addressable traversal. Both are
  keyed by the current pre-law workflow item families.
- `RouteLine` is the only dedicated workflow statement today. It proves the
  pipeline can carry typed workflow statements, but it is still section-local
  and not a general workflow-law system.
- There is no agent-level contract context that joins workflow semantics to the
  concrete outputs an agent emits. That is why currentness, carrier membership,
  invalidation, and trust-surface coupling cannot be expressed or validated.

## 4.4 Observability + failure behavior today

- The first hard stop is the grammar boundary:
  `law:` in workflow examples and `trust_surface:` in output examples currently
  fail as parse-stage `E101` before any workflow-law semantics run.
- The second hard stop is proof activation:
  `verify_corpus()` intentionally prevents `examples/30_*` through `examples/38_*`
  from becoming shipped truth because their manifests are still `planned`.
- Diagnostics are structured and code-based, but workflow-law-specific failures
  have no dedicated code family yet; once the syntax lands, they would either
  need new mappings or fall back to overly generic compile errors.
- Emit inherits the same failure surface as ordinary compilation because it
  reparses and recompiles the prompt entrypoint. Example `36` therefore fails
  before build-tree comparison, not during build emission.
- VS Code drift prevention exists, but only for the current language subset:
  `validate_lark_alignment.py` mirrors old keyword coverage and currently misses
  underscore workflow-law keywords such as `trust_surface` and `support_only`.

## 4.5 UI surfaces (ASCII mockups, if UI work)

- VS Code navigation surface:
  - import Cmd-click
  - Go to Definition for shipped refs and addressable paths
  - syntax highlighting via tmLanguage regexes
  - indentation/folding via language configuration
- There is no editor affordance today for workflow-law keywords, carrier refs,
  trust-surface field paths, enum-backed mode refs, or law-section structural
  `inherit` / `override` keys because those tokens and containers are not
  shipped.
- Editor proof is also pre-law:
  tmgrammar unit tests, snapshot fixtures, and integration tests still exercise
  examples up through the old subset rather than `30-38`.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/grammars/doctrine.lark`
  - grows reserved `law` syntax inside workflow bodies and reserved
    `trust_surface` syntax inside outputs, plus the bounded workflow-law
    expression and path-set surface required by the spec
- `doctrine/parser.py`
  - lowers those reserved surfaces into typed AST rather than generic record or
    prose fallback
- `doctrine/model.py`
  - keeps one declaration family per shipped concept, but extends the existing
    workflow and output models with explicit law and trust ownership:
    `WorkflowBody` owns authored prose plus optional typed `law`;
    `OutputDecl` owns ordinary output items plus optional typed `trust_surface`
- `doctrine/compiler.py`
  - remains the single semantic owner and grows private normalized law and agent
    contract structures under the existing `CompilationContext` entry point
  - if the file needs internal factoring for size, any helper modules stay
    private to the same compiler entry path rather than becoming a second
    semantics surface
- `doctrine/renderer.py`
  - remains a generic serializer of compiled trees
  - any renderer change is mechanical shape support only, not semantic policy
- `doctrine/verify_corpus.py` and `doctrine/emit_docs.py`
  - stay the only proof and emit consumers; workflow law rides the ordinary
    parse -> compile -> render path instead of gaining special runners
- `editors/vscode/*`
  - stays on the existing `package.json -> extension.js -> resolver.js` mirror
    architecture while adding workflow-law syntax, indentation, classification,
    and navigation parity
- `docs/*.md` plus `examples/README.md` and `editors/vscode/README.md`
  - converge onto one live shipped truth after the cutover; proposal and audit
    notes are folded in, deleted, or clearly demoted rather than left as
    competing active doctrine

## 5.2 Control paths (future)

1. Parse prompt source into typed AST that distinguishes:
   authored workflow prose, ordinary workflow items, typed `law`,
   ordinary output fields, and typed `trust_surface`.
2. Resolve inherited authored workflow, skills, and IO structure using the
   existing explicit patching model, then resolve inherited law subsections
   inside the typed `law` surface with the same fail-loud explicitness.
3. After agent slots and typed fields resolve, build one compiler-owned
   agent contract context that knows:
   available inputs, concrete emitted outputs, trust surfaces, enums, and route
   targets for that agent.
4. Normalize workflow law into guarded leaf branches that carry predicates,
   mode bindings, currentness, scope, preservation, basis-role policy,
   invalidations, and stop or route semantics.
   The compiler validates branch contradictions and coverage; it does not
   pretend to evaluate runtime truth.
5. Validate carrier invariants and output coupling against the concrete agent
   contract context:
   current roots, `via` carrier refs, trust-surface membership, invalidation
   carriers, and output emission obligations all fail loud here.
6. Compile workflows and outputs into generic `CompiledSection` trees with the
   human-first wording and ordering already chosen by compiler semantics.
7. Render Markdown mechanically from those compiled sections. The renderer does
   not reorder law or infer trust policy.
8. Verify and emit through the same shipped compiler path, then mirror the
   shipped syntax and reference semantics into VS Code without inventing
   editor-only meaning.

## 5.3 Object model + abstractions (future)

- `WorkflowBody` becomes a two-surface owner:
  authored workflow prose and ordinary keyed items stay as they are, while
  typed `law` is attached as a reserved workflow child surface rather than
  smuggled through `WorkflowItem`.
- `OutputDecl` becomes a two-surface owner:
  ordinary output keys still describe the output contract, while typed
  `trust_surface` explicitly lists what downstream truth rides with that output.
- The public AST stays explicit and typed:
  law sections, law statements, carrier refs, trust-surface entries, law paths,
  path sets, and bounded expressions get first-class nodes instead of generic
  `RecordSection` or prose fallback.
- The compiler grows private normalized structures for:
  inherited law subsection accounting, guarded leaf branches, path-set algebra,
  and agent contract validation. Those are compiler internals, not new public
  declaration families.
- The missing join point becomes explicit:
  agent compilation builds one contract context that combines the agent's
  resolved outputs and trust surfaces with its workflow law so carrier
  invariants can be validated in one place.
- Law paths stay intentionally separate from authored readable refs:
  authored readable refs remain `Decl:path.to.child`;
  workflow-law paths use a distinct typed algebra rooted in declared input or
  output artifacts and carrier fields.

## 5.4 Invariants and boundaries

- `law` exists only inside `workflow`, and `trust_surface` exists only inside
  `output`. There is no top-level reusable `law` declaration in this cutover.
- `doctrine/compiler.py` is the only semantic owner.
  `doctrine/renderer.py`, `doctrine/verify_corpus.py`, `doctrine/emit_docs.py`,
  and `editors/vscode/*` consume that truth; they do not define alternative
  semantics.
- There is no runtime fallback, shim, or dual-language mode.
  The compiler either admits the workflow-law surface end to end or fails loud.
- The compiler normalizes guarded branches; it does not evaluate arbitrary
  runtime truth. Predicates remain bounded expressions carried through semantic
  validation rather than executed during compilation.
- Every active law leaf branch resolves exactly one current-subject form.
  `current none` cannot coexist with `current artifact`, and transferable
  currentness or invalidation always requires declared carrier fields on an
  emitted output.
- Carrier output emission, trust-surface membership, and current-output
  emission are compile-time invariants, not renderer advice.
- Named law subsections are structural compiler identities for inherited patch
  accounting. They do not become public render headings.
- Law paths are not authored readable refs and must not be collapsed into
  `AddressableRef` semantics even if compiler traversal helpers are reused
  internally.
- Verify, emit, docs, and VS Code must all describe the same shipped subset in
  the same merge. No split-brain truth surfaces survive the cutover.

## 5.5 UI surfaces (ASCII mockups, if UI work)

- Syntax scopes and indentation:
  - block starters for `law`, `trust_surface`, `active when`, `when`, and
    `match`
  - keyword scopes for `current artifact`, `current none`, `invalidate`,
    `own only`, `preserve`, `support_only`, `ignore`, `forbid`, `mode`,
    `must`, `stop`, and `route`
  - dedicated classification for carrier refs and trust-surface field paths
- Go to Definition and click targets:
  - current artifact roots
  - carrier output roots and trust-surface fields
  - enum refs used by `mode` and `match`
  - agent refs used by `route`
  - law-section structural keys for `inherit` and `override`
- The extension mirrors only shipped syntax and reference semantics.
  It does not evaluate law predicates, invent synthetic destinations, or add a
  second language design surface.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | `workflow_decl`, `workflow_body`, `workflow_item`, `record_keyed_item`, `route_stmt`, `PATH_REF` | Only pre-law workflow and output syntax exists | Add reserved `law` inside workflow bodies, reserved `trust_surface` inside outputs, and bounded workflow-law expression and path-set grammar | The spec is unrepresentable otherwise | First-class workflow-law grammar | `30-38`, VS Code alignment, parser negatives |
| Parser | `doctrine/parser.py` | `ToAst`, workflow and IO body staging, `parse_text()`, `parse_file()` | Lowers prose, sections, refs, `use`, skills, and generic record items only | Add dedicated lowering for law blocks, named law subsections, law statements, carriers, trust-surface items, law paths, path sets, and bounded expressions | Grammar must lower into typed semantics, not prose fallback | Reserved-surface AST lowering | Positive and negative `30-38`, parse-fail coverage |
| AST | `doctrine/model.py` | `WorkflowBody`, `OutputDecl`, `RecordItem`, `AddressableRef` | No law or trust node families exist | Extend workflow and output models with typed law and trust ownership plus dedicated law/trust node families | Generic record and prose nodes would erase semantics | Public AST for workflow law and downstream trust | Compiler, VS Code mirror, diagnostics |
| Compiler agent join point | `doctrine/compiler.py` | `_compile_agent_decl()` | Compiles workflow and outputs as mostly separate field-local surfaces | Build one agent contract context after agent fields resolve so workflow law can validate against concrete outputs, trust surfaces, enums, and routes | Carrier invariants and emitted-output coupling need one validation boundary | Compiler-owned agent contract context | `31`, `36`, `38` |
| Compiler workflow resolution | `doctrine/compiler.py` | `_resolve_workflow_body()` | Explicit patching only for sections, `use`, and workflow skills | Add typed law ownership and inherited law-subsection accounting without creating a second workflow semantics path | Law must patch like other compiler-owned structure | Resolved workflow plus resolved law | `37`, `38` |
| Compiler workflow addressability | `doctrine/compiler.py` | `_resolve_workflow_addressable_body()` | Mirrors pre-law workflow structure for addressable traversal | Extend only as needed for law-section structural keys and workflow-law reference surfaces while keeping readable refs separate | VS Code and compiler need structural parity without collapsing semantics | Addressable mirror for shipped law structure | VS Code integration tests |
| Compiler IO resolution | `doctrine/compiler.py` | `_resolve_io_body()` | Resolves IO blocks directly into `CompiledSection` backed sections/refs | Reserve `trust_surface` before the render-ready collapse point and validate it semantically in compiler space | Output trust cannot be deferred to the renderer | Typed output trust resolution | `31`, `36`, `38` |
| Compiler output compilation | `doctrine/compiler.py` | `_compile_output_decl()`, `_split_record_items()` | Reserves only `target`, `shape`, `requirement`, and `files` | Reserve and compile `trust_surface`, validate membership, and project downstream truth into compiled sections | Portable truth must be typed and emitted from compiler semantics | Output contract plus trust contract | `31`, `36`, `38` render and compile cases |
| Compiler branch normalization | `doctrine/compiler.py` | workflow semantic path after authored resolution | No guarded branches, mode handling, or leaf currentness analysis exist | Normalize `active when`, `when`, `match`, `mode`, `must`, `stop`, `route`, and currentness into guarded leaf branches | Hard rules require one current-subject form per active leaf | Private normalized law branches | `30`, `32`, `38` |
| Compiler scope algebra | `doctrine/compiler.py` | `_resolve_addressable_path_value()`, `_get_addressable_children()` | Traverses only authored dotted child paths | Add law-path and path-set resolution, overlap checks, and carrier field rooting without collapsing into `AddressableRef` semantics | `own only`, `preserve`, `ignore`, and `forbid` depend on typed scope algebra | Law-path and path-set contract | `33`, `34`, `35`, `38` |
| Compiler inheritance parity | `doctrine/compiler.py` | workflow inheritance and missing-parent checks | Explicit patching exists only for current workflow item families | Add named law-subsection `inherit` / `override` accounting with the same fail-loud explicitness as workflow/skills/IO patching | `37` and `38` require inherited law parity | Inherited law patch contract | `37`, `38` |
| Compiler render shaping | `doctrine/compiler.py` | `_compile_resolved_workflow()`, output compile path | Compiler already shapes human-facing sections but only for pre-law content | Keep law ordering, trust-surface projection, and plain-English phrasing in compiler space | Renderer must stay dumb and generic | Compiler-owned law and trust narration | `30-38` render contracts |
| Renderer | `doctrine/renderer.py` | `render_markdown()` | Serializes generic compiled sections | Keep generic serializer behavior; change only if mechanical shape support is needed | Avoid a second semantic policy lane | No new renderer-owned semantics | Full corpus preservation |
| Diagnostics | `doctrine/diagnostics.py` | compile and parse normalization tables | No workflow-law-specific code family or wording exists | Add stable summaries and codes for workflow-law parse and compile failures without changing reserved existing code meanings | Fail-loud diagnostics are shipped truth | New law-specific diagnostic contract | `30-38`, `docs/COMPILER_ERRORS.md`, `make verify-diagnostics` |
| Diagnostic smoke | `doctrine/diagnostic_smoke.py` | stable-code smoke assertions | No workflow-law smoke coverage | Add narrow checks where corpus coverage is insufficient or too indirect | Preserve error-code stability | Law diagnostic smoke | `make verify-diagnostics` |
| Corpus verifier | `doctrine/verify_corpus.py` | `_load_manifest()`, `verify_corpus()`, `format_report()` | `planned` cases are advisory only and never become proof | Promote `30-38` to `active`, keep or later re-evaluate generic `planned` support only if other repo cases still need it | Hard cut requires real proof | Active workflow-law manifests on the standard runner | `make verify-examples`, targeted manifests |
| Emit pipeline | `doctrine/emit_docs.py` | `emit_target()` | Reuses ordinary parse -> compile -> render | Keep same path, but make workflow-law build targets executable and truthful | No separate emit architecture is allowed | Emit proof rides shipped compiler | `example_36_invalidation_and_rebuild` target and any additional targets |
| Emit target config | `pyproject.toml` | `tool.doctrine.emit.targets` | `example_36_invalidation_and_rebuild` already configured | Preserve or expand targets only as needed once workflow law compiles | Build proof already exists and should be activated, not bypassed | Same emit-target mechanism | Emit checks, example `36` |
| Example 30 | `examples/30_law_route_only_turns/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair semantics, activate manifest, and keep route-only currentness and parse/compile negatives honest | Route-only turns are the minimal workflow-law proof | Active example 30 | Targeted manifest, full corpus |
| Example 31 | `examples/31_currentness_and_trust_surface/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair and activate current artifact plus `via` carrier proof | Establish portable currentness and trust carriers | Active example 31 | Targeted manifest, full corpus |
| Example 32 | `examples/32_modes_and_match/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair and activate enum-backed mode, `match`, and `must` proof | Establish guarded branch and exhaustiveness semantics | Active example 32 | Targeted manifest, full corpus |
| Example 33 | `examples/33_scope_and_exact_preservation/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair and activate `own only`, `preserve exact`, `preserve decisions`, and `forbid` proof | Establish typed ownership and overlap rules | Active example 33 | Targeted manifest, full corpus |
| Example 34 | `examples/34_structure_mapping_and_vocabulary_preservation/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair and activate non-exact preserve forms | Establish structure, mapping, and vocabulary semantics | Active example 34 | Targeted manifest, full corpus |
| Example 35 | `examples/35_basis_roles_and_rewrite_evidence/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair and activate `support_only` and `ignore ... for ...` proof | Establish basis-role and rewrite-evidence semantics | Active example 35 | Targeted manifest, full corpus |
| Example 36 | `examples/36_invalidation_and_rebuild/**` | prompts, manifest, refs, `build_ref/`, emit target | Illustrative only, status `planned` | Repair and activate invalidation and rebuild proof, including checked build tree parity | This is the capstone build-contract proof for downstream invalidation | Active example 36 plus emit proof | Targeted manifest, emit target, full corpus |
| Example 37 | `examples/37_law_reuse_and_patching/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair and activate named law-subsection inheritance and patching | Establish law reuse parity with existing patch systems | Active example 37 | Targeted manifest, full corpus |
| Example 38 | `examples/38_metadata_polish_capstone/**` | prompts, manifest, refs | Illustrative only, status `planned` | Repair and activate integrated capstone composition of all earlier contracts | Prove the whole model composes | Active example 38 | Targeted manifest, full corpus |
| Example docs | `examples/README.md` | corpus description and verify guidance | Still says shipped proof stops at `29` and `30-38` are planned review-only | Rewrite to describe the active shipped corpus and cutover-era verification guidance | Remove split-brain corpus truth | Current corpus documentation | Human review, repo verification |
| Language docs | `docs/LANGUAGE_DESIGN_NOTES.md` | shipped language notes | Still documents the pre-law shipped subset | Fold in shipped workflow-law truth and delete subset-only claims | Live docs must match compiler truth | Updated shipped language contract | Human review |
| IO docs | `docs/AGENT_IO_DESIGN_NOTES.md` | output and handoff model | Still describes pre-law I/O and no trust-surface carrier semantics | Update for `trust_surface`, carrier invariants, currentness, and invalidation | Output contract changes materially | Updated shipped IO contract | Human review |
| Error docs | `docs/COMPILER_ERRORS.md` | canonical error catalog | Stops at existing code families | Document new workflow-law parse and compile codes and wording bands | Docs must match shipped diagnostics | Updated diagnostic catalog | Diagnostic smoke, full verification |
| Docs index | `docs/README.md` | live docs map | Does not route readers to shipped workflow-law truth | Update docs map after cutover | Discoverability and SSOT | Updated docs map | Human review |
| Proposal and audit docs | `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md`, `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_AUDIT_2026-04-10.md`, related one-offs | Still act as live planning truth | Fold into shipped docs or clearly demote/delete so they do not compete post-cutover | Git should hold history, not live split-brain truth | One live doc set | Human review |
| VS Code syntax | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | keyword and surface regexes | Only pre-law keywords and containers are scoped | Add full shipped workflow-law keyword, block, and path-bearing surfaces | Highlighting parity | Updated grammar mirror | `npm test`, snapshots, alignment |
| VS Code indentation | `editors/vscode/language-configuration.json` | on-enter rules and block starters | Tuned for the old declaration and section set | Add block-start rules for `law`, `trust_surface`, `active when`, `when`, and `match` | Editing ergonomics must match shipped grammar | Updated indentation contract | Editor checks, manual smoke |
| VS Code navigation | `editors/vscode/resolver.js` | `provideDefinitionLinks()`, `getChildBodySpecForLine()`, site collection and body maps | Only knows pre-law containers, refs, and structural keys | Add law and trust contexts, carrier refs, enum-backed mode refs, trust-surface fields, and law-section structural `inherit` / `override` navigation | Link-follow and definition parity are in scope | Updated resolver semantics on same architecture | Integration tests, manual smoke |
| VS Code extension wiring | `editors/vscode/extension.js` | provider registration | Current providers are already the right shape | Keep same wiring unless provider types truly need to change | Avoid new editor architecture | Same provider surface, richer semantics | Integration tests |
| VS Code package boundary | `editors/vscode/package.json`, `editors/vscode/Makefile`, `editors/vscode/scripts/package_vsix.py` | test, alignment, and packaging entrypoints | Package and verify flow still targets the pre-law surface implicitly | Keep the same package boundary while updating test and packaging assumptions to the shipped workflow-law surface | `cd editors/vscode && make` is part of definition of done and must stay truthful | Same package flow, wider parity proof | `npm test`, `cd editors/vscode && make` |
| VS Code alignment validator | `editors/vscode/scripts/validate_lark_alignment.py` | keyword and sample harvesting | Mirrors only quoted lowercase alpha keywords and old samples | Extend keyword/sample coverage for underscores and workflow-law surfaces | Prevent grammar-editor drift | Updated alignment contract | `cd editors/vscode && make` |
| VS Code tests | `editors/vscode/tests/unit/**`, `tests/snap/**`, `tests/integration/suite/index.js`, `package.json` | Tests stop at pre-law examples | Add unit, snapshot, and integration coverage against `30-38` without changing the test architecture | Editor parity needs proof, not only docs | Workflow-law editor proof on current harness | `npm test`, `cd editors/vscode && make` |
| VS Code docs | `editors/vscode/README.md` | shipped editor capabilities | Documents only the old clickable surface | Update to describe workflow-law highlighting and navigation and any remaining unsupported surfaces | Live editor docs must match shipped behavior | Updated editor README | Human review |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/compiler.py` remains the one semantic owner for workflow-law
    truth, entered through `compile_prompt()` and `CompilationContext`.
  - `doctrine/grammars/doctrine.lark` plus `doctrine/parser.py` and
    `doctrine/model.py` remain the one syntax and AST owner.
  - `doctrine/verify_corpus.py` and `doctrine/emit_docs.py` remain the one
    proof and emit owners.
  - `editors/vscode/resolver.js` plus tmLanguage, language configuration, and
    current test harnesses remain the one editor mirror.
- Deprecated APIs (if any):
  - workflow-law-specific "planned review corpus" wording and behavior for
    `30-38`
  - any temporary acceptance path that would admit both old and new meanings at
    once
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - workflow-law manifests left as `planned`
  - docs that still claim the shipped corpus stops at `29`
  - proposal and audit docs that remain framed as live shipped truth after the
    cutover
  - any temporary compatibility code that accepts the old meaning and the new
    meaning simultaneously
  - stale editor regexes, samples, or docs that intentionally exclude the new
    syntax
- Capability-replacing harnesses to delete or justify:
  - none expected; extend the shipped compiler, verifier, emitter, and
    extension instead of adding sidecar parsers, emitters, or editor semantics
- Live docs/comments/instructions to update or delete:
  - `docs/README.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
  - `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md`
  - `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_AUDIT_2026-04-10.md`
  - `docs/ROUTE_ONLY_TURNS_NORMALIZATION_CASE_STUDY_2026-04-10.md`
  - `docs/ROUTE_ONLY_TURNS_OUTPUT_FIRST_REIMAGINING_2026-04-10.md`
  - `docs/ROUTE_ONLY_TURNS_RENDER_OWNED_REFACTOR_2026-04-10.md`
  - `docs/VSCODE_IMPORT_PATH_HIGHLIGHTING_AND_NAVIGATION_2026-04-07.md`
  - workflow-law and VS Code planning notes that would otherwise remain as
    competing live truth
- Behavior-preservation signals for refactors:
  - full active corpus through `make verify-examples`
  - targeted manifest runs while bringing up individual examples
  - `make verify-diagnostics`
  - direct emit check for `example_36_invalidation_and_rebuild`
  - existing active examples `01-29` to ensure the hard cut does not regress
    the shipped subset while adding workflow law
  - `cd editors/vscode && make`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Compiler | `doctrine/compiler.py` workflow and output handling | reserved-surface compilation plus agent contract validation in compiler space | prevents `law` and `trust_surface` from becoming ad hoc prose or record semantics | include |
| Compiler | `doctrine/compiler.py` normalized law branch path | guarded branch normalization rather than renderer inference | prevents semantic drift and duplicate ordering logic | include |
| Diagnostics | `doctrine/diagnostics.py` plus `docs/COMPILER_ERRORS.md` | stable dedicated workflow-law error codes and wording | prevents failures from hiding under generic bands | include |
| Corpus | `examples/30_*` through `examples/38_*` | active manifest-backed proof on the existing verifier | prevents review-only examples from drifting away from the compiler | include |
| Emit | `doctrine/emit_docs.py` plus `pyproject.toml` targets | same compiler path for build proof | prevents build-contract truth from becoming a side lane | include |
| Editor | `editors/vscode/*` | full shipped keyword, block, and reference parity with compiler grammar | prevents extension drift and false navigation or highlighting behavior | include |
| Docs | shipped docs set under `docs/`, `examples/README.md`, and `editors/vscode/README.md` | one live description of shipped workflow-law and trust semantics | prevents planning docs from remaining as live competing truth | include |
| Planned-manifest support | `doctrine/verify_corpus.py` generic `planned` pathway | retain only if still justified after `30-38` activation | prevents unnecessary parallel proof semantics | defer |
| Compiler file factoring | `doctrine/compiler.py` internal helper layout | factor privately only if file size becomes the blocker | avoids turning internal refactors into a second semantic entry point | defer |
| Extension wiring | `editors/vscode/extension.js` | keep the same provider wiring | avoids needless editor architecture churn | exclude |
| Indenter | `doctrine/indenter.py` | change only if new grammar actually requires it | avoids speculative parser churn | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria +
> explicit verification plan. Refactors, consolidations, and shared-path
> extractions must preserve behavior with the smallest credible signal. Prefer
> existing repo checks over new harnesses. No fallbacks/runtime shims. Delete
> or rewrite superseded live docs/comments in the phase that would otherwise
> leave stale truth behind. Do not encode the existing workflow-law examples as
> law; implement the spec and then repair the examples to match shipped
> semantics.

## Phase 1 - Grammar and AST foundation

Status: COMPLETE

Completed work:
- Added full shipped grammar, parser lowering, and typed AST ownership for
  `law`, `trust_surface`, workflow-law expressions, law paths, path sets, and
  inherited law section patching.
- Promoted `WorkflowBody.law` and `OutputDecl.trust_surface` into the shipped
  model so workflow law and downstream trust no longer ride on generic prose or
  generic record fallback nodes.

* Goal:
  Land a complete parseable syntax and AST for the workflow-law v1 surface.
* Work:
  Update `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, and
  `doctrine/model.py` to support `law`, `trust_surface`, bounded law
  expressions, law paths, path-set forms, carrier refs, law-section
  inheritance, and all v1 statements. Keep `law` owned by `WorkflowBody`,
  `trust_surface` owned by `OutputDecl`, and keep law-path nodes distinct from
  `AddressableRef` rather than routing through generic record items or prose.
* Verification (smallest signal):
  Targeted parse success for positive `30-38` prompts and parse-fail success for
  the explicit parse-negative cases, plus parse smoke on representative active
  shipped examples that exercise workflow and output syntax so the old subset
  does not regress at the grammar boundary.
* Docs/comments (propagation; only if needed):
  Add short boundary comments in parser/model around reserved law/trust surfaces
  and the separation between authored readable refs and law paths.
* Exit criteria:
  All spec syntax can be represented in AST form without generic fallback nodes
  for core law/trust semantics, and inherited law patching plus trust-surface
  ownership are expressible without parser-side ambiguity.
* Rollback:
  Revert to the pre-law grammar/model if the AST shape cannot represent
  inherited law reuse, trust-surface ownership, and the bounded law-path
  surface cleanly.

## Phase 2 - Compiler semantics, normalization, and diagnostics

Status: COMPLETE

Completed work:
- Implemented compiler-owned workflow-law normalization, branch validation,
  current-subject analysis, carrier/trust checks, preservation and invalidation
  semantics, and inherited law subsection patching in `doctrine/compiler.py`.
- Added workflow-law parse and compile diagnostic coverage, including dedicated
  currentness, mode/match, scope, invalidation, and inherited-law codes, and
  updated the shipped error catalog.

* Goal:
  Make the compiler understand workflow law as real semantics rather than parse
  trivia.
* Work:
  Implement normalized law resolution in `doctrine/compiler.py`:
  activation, modes, exhaustive matches, current-subject analysis, carrier
  invariants, owned scope, preservation kinds, basis roles, invalidation,
  stop/route semantics, and inherited law subsection patching. Create the
  single agent-contract join point that validates workflow law against concrete
  outputs and trusted carriers. Add dedicated diagnostic normalization and
  stable codes in `doctrine/diagnostics.py` and `docs/COMPILER_ERRORS.md`.
* Verification (smallest signal):
  Compile-fail and compile-success manifest cases for `30-38`, plus
  representative active examples that already cover workflow, output, and
  addressable-path behavior, plus `make verify-diagnostics`.
* Docs/comments (propagation; only if needed):
  Add high-leverage comments at the normalized law boundary and carrier
  validation boundary.
* Exit criteria:
  Positive workflow-law examples compile under the new semantics, negative cases
  fail for the right reasons with dedicated codes or canonical summaries, the
  active pre-law subset still compiles through the same compiler entry path,
  and no core workflow-law rule depends on renderer-side guesswork.
* Rollback:
  Revert the semantic layer if branch normalization or carrier invariants prove
  internally contradictory; do not ship partial semantics.

## Phase 3 - Rendering and emitted-tree parity

Status: COMPLETE

Completed work:
- Kept workflow-law render shaping in compiler space and limited renderer work
  to serializer parity, including the nested-section blank-line fix needed to
  restore the shipped corpus.
- Revalidated emitted tree targets for `example_07_handoffs`,
  `example_14_handoff_truth`, and `example_36_invalidation_and_rebuild`.

* Goal:
  Render the new semantics in the human-first form required by the spec and keep
  emit contracts truthful.
* Work:
  Keep law ordering, trust-surface projection, and plain-English phrasing in
  `doctrine/compiler.py` so workflows and outputs compile into the right
  `CompiledSection` shape. Touch `doctrine/renderer.py` only if that compiled
  shape needs mechanical serializer support. Update `doctrine/emit_docs.py`
  only as needed for active workflow-law emit/build cases, and keep the
  existing build-contract target lane aligned in `pyproject.toml` for
  `example_07_handoffs`, `example_14_handoff_truth`, and
  `example_36_invalidation_and_rebuild`.
* Verification (smallest signal):
  Render-contract cases for `30-38`; targeted emit checks for
  `example_07_handoffs`, `example_14_handoff_truth`, and
  `example_36_invalidation_and_rebuild`.
* Docs/comments (propagation; only if needed):
  Add one comment at the law-render ordering boundary if the normalization step
  is non-obvious.
* Exit criteria:
  Rendered Markdown matches the intended workflow-law reading model, emitted
  tree outputs are stable, and the generic renderer remains a serializer rather
  than a second semantic owner.
* Rollback:
  Revert render shaping if it introduces a second semantic path or breaks the
  generic section serializer for pre-law examples.

## Phase 4 - Corpus activation and example repair

Status: COMPLETE

Completed work:
- Activated `examples/30_*` through `examples/38_*` as shipped proof, repaired
  illustrative negative cases to fail for the intended reasons, and refreshed
  their checked render and build artifacts.
- Preserved the pre-law active subset while fixing older wrong-kind IO
  regression paths exposed by the new agent-contract join point.
- Removed the dead `planned` proof lane from `doctrine/verify_corpus.py` and
  rewrote the remaining corpus-facing wording so the shipped examples stay one
  active proof surface instead of a split active/advisory model.

* Goal:
  Turn the workflow-law example family into active proof and align illustrative
  prompts with the shipped compiler truth.
* Work:
  Update `examples/30_*` through `examples/38_*` prompts where needed, flip
  their manifest statuses to `active`, update expected lines, regenerate
  checked `ref/` and `build_ref/` artifacts, and remove workflow-law-specific
  planned-review wording from `examples/README.md`. Evaluate whether the generic
  `planned` pathway in `verify_corpus.py` still has a justified use after this
  cutover; delete it if it becomes dead machinery rather than keeping a second
  proof mode around without need.
* Verification (smallest signal):
  `make verify-examples`, plus targeted manifest runs while repairing each
  example family.
* Docs/comments (propagation; only if needed):
  Update example readme language and any checked error/reference docs generated
  from the new semantics.
* Exit criteria:
  `30-38` are active proof, their refs/builds are current, and the repo no
  longer describes workflow-law as review-only. Any surviving `planned`
  behavior in `verify_corpus.py` has an explicit remaining justification.
* Rollback:
  Revert example repairs only if the compiler semantics are still moving; do
  not freeze bad example authoring as a semantic source of truth.

## Phase 5 - VS Code parity

Status: COMPLETE

Completed work:
- Extended the tmLanguage, indentation rules, alignment validator, resolver,
  unit fixtures, integration checks, and snapshot corpus to cover the shipped
  workflow-law and trust-surface surface.
- Added definition coverage for law carriers, trust-surface items, enum-backed
  mode refs, law-section structural keys, and route targets inside law
  branches while keeping the existing extension architecture intact.

* Goal:
  Make highlighting, indentation, alignment validation, and go-to-definition
  track the shipped workflow-law surface.
* Work:
  Update `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
  `editors/vscode/language-configuration.json`,
  `editors/vscode/resolver.js`,
  `editors/vscode/scripts/validate_lark_alignment.py`, and any required tests,
  fixtures, or package-boundary files so the extension recognizes new keywords,
  law containers, carrier refs, law paths, trust-surface items, enum-backed
  mode refs, and law-section structural keys. Keep the extension architecture
  the same unless a concrete parity gap forces a wiring change.
* Verification (smallest signal):
  `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  Update `editors/vscode/README.md` and add a brief comment in `resolver.js`
  where law context classification becomes non-obvious.
* Exit criteria:
  The extension highlights the shipped workflow-law surface, follows the new
  definition/navigation targets correctly, and the Lark-alignment script covers
  the new keywords and underscore forms without drift.
* Rollback:
  Revert editor-side changes if they drift from the compiler grammar; never
  leave the extension describing a language the compiler does not ship.

## Phase 6 - Live docs hard cut and final verification

Status: COMPLETE

Completed work:
- Rewrote the shipped language, I/O, error, examples, and VS Code docs to
  describe workflow law as current shipped truth instead of planned future
  work.
- Deleted the superseded workflow-law planning notes named in this phase so
  the repo no longer leaves alternate live explanations of the feature family.
- Corrected the remaining stale live-truth surfaces in the root README,
  language notes, and docs index so the repo now consistently says the shipped
  corpus runs through `examples/38_*`.
- Final verification passed: `make verify-examples`,
  `make verify-diagnostics`, and `cd editors/vscode && make`.

* Goal:
  Remove split-brain live truth and prove the full cutover end to end.
* Work:
  Rewrite `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/COMPILER_ERRORS.md`, `docs/README.md`, `examples/README.md`, and
  `editors/vscode/README.md` to describe the shipped workflow-law language.
  Delete or clearly demote the now-superseded planning surfaces:
  `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_AUDIT_2026-04-10.md`,
  `docs/ROUTE_ONLY_TURNS_NORMALIZATION_CASE_STUDY_2026-04-10.md`,
  `docs/ROUTE_ONLY_TURNS_OUTPUT_FIRST_REIMAGINING_2026-04-10.md`,
  `docs/ROUTE_ONLY_TURNS_RENDER_OWNED_REFACTOR_2026-04-10.md`, and
  `docs/VSCODE_IMPORT_PATH_HIGHLIGHTING_AND_NAVIGATION_2026-04-07.md` if their
  conclusions have been absorbed into shipped docs. Keep
  `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md` only as the original
  proposal/spec reference, not as a competing live description of shipped
  truth. Run the full repo verification surface.
* Verification (smallest signal):
  `make verify-examples`
  `make verify-diagnostics`
  `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  This phase is the docs propagation phase; no stale live docs remain.
* Exit criteria:
  The repo has one live language story, all required checks pass, and the
  workflow-law feature family is no longer described as future or planned.
* Rollback:
  If full verification fails, revert the last incomplete convergence edits
  rather than shipping mixed docs/proof/editor/compiler truth.
<!-- arch_skill:block:phase_plan:end -->

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-10
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

Verification run:
- `make verify-examples` passed.
- `make verify-diagnostics` passed.
- `cd editors/vscode && make` passed.

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

# 8) Verification Strategy (common-sense; non-blocking)

- Foundation checks:
  - targeted manifest runs for the example family being brought up
  - direct parse/compile smoke while stabilizing grammar and AST
- Required repo checks before calling the cutover done:
  - `make verify-examples`
  - `make verify-diagnostics`
  - `cd editors/vscode && make`
- Targeted emitted-tree checks:
  - `uv run --locked python -m doctrine.emit_docs --target example_07_handoffs`
  - `uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth`
  - `uv run --locked python -m doctrine.emit_docs --target example_36_invalidation_and_rebuild`
  - any additional emit targets added for workflow-law proof if implementation
    makes them necessary
- Manual editor sanity check after packaging:
  - open representative `30-38` prompts
  - inspect syntax scopes for new keywords
  - use Go to Definition on current artifact roots, carrier refs, enum mode refs,
    route targets, and law-section `inherit` / `override` keys
- Negative-value checks to avoid:
  - snapshotting unstable rendered whitespace outside manifest-backed cases
  - deletion-only tests for removed planned semantics
  - custom harnesses that duplicate the compiler or extension parser

# 9) Rollout / Ops / Telemetry

- Rollout model:
  - single hard cut on the main shipped compiler/editor/docs path
  - no compatibility period and no dual-language support for this feature
    family
- Operational follow-through:
  - rebuild and reinstall the packaged VSIX after editor changes
  - ensure build targets in `pyproject.toml` still reflect the active example
    surfaces
- Telemetry:
  - none required; this is a local compiler/editor toolchain change, not a
    service rollout
- Failure policy:
  - if a phase cannot preserve repo-wide truth, stop and repair before moving
    on rather than carrying partial cutover state

# 10) Decision Log (append-only)

- 2026-04-10 - Adopt full workflow-law v1 cutover as one architecture change.
  We are not shipping a slice, compatibility layer, or review-only corpus.
- 2026-04-10 - Treat
  `docs/MODE_SCOPE_TRUTH_WORKFLOW_LAW_SPEC_2026-04-10.md` as the normative v1
  target and treat `examples/30_*` through `examples/38_*` as illustrative
  implementation receipts that may need repair.
- 2026-04-10 - Keep `workflow` as the semantic home of law and `output` as the
  semantic home of downstream trust. Do not invent a second coordination
  language.
- 2026-04-10 - Keep the VS Code extension on its current architecture, but
  require full parity with shipped grammar and reference semantics in the same
  cutover.
- 2026-04-10 - Prefer deleting obsolete workflow-law planning truth from the
  live docs set once the shipped docs absorb the final semantics; Git is the
  history surface.
- 2026-04-10 - Status corrected back to `draft` because the north star has not
  been explicitly approved yet. Research grounding can proceed against the
  draft artifact, but later planning should not pretend confirmation already
  happened.
- 2026-04-10 - Deep-dive locked the preferred architecture:
  typed `law` and `trust_surface` live on the existing workflow and output
  owners, `doctrine/compiler.py` remains the single semantic owner with an
  agent-level contract validation join point, and renderer, verifier, emitter,
  docs, and VS Code stay downstream mirrors rather than alternate semantics
  paths.
- 2026-04-10 - Phase planning tightened the execution contract: preservation
  checks must cover the shipped active subset and the existing emit targets,
  VS Code parity explicitly includes link-follow behavior and Lark-alignment
  underscore keywords, and stale workflow-law planning docs must be deleted or
  demoted during final convergence instead of lingering as live truth.
- 2026-04-10 - Implementation completed against the draft North Star because
  the user explicitly requested a hard-cut implementation run before north-star
  approval. The code, corpus, editor, and shipped docs now reflect the full
  workflow-law v1 cutover even though the planning artifact itself remained
  `draft` at the end of the first implementation pass.
- 2026-04-10 - A follow-up `arch-step implement` pass closed the audit-reopened
  Phase 4 and Phase 6 gaps by deleting the dead `planned` proof lane from
  `doctrine/verify_corpus.py` and repairing the remaining stale live docs.
  With the required repo verification green after those fixes, the canonical
  plan status returned to `complete`.
