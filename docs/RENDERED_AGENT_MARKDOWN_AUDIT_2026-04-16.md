---
title: "Doctrine - Rendered Agent Markdown Formatting - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: phased_refactor
related:
  - doctrine/_compiler/compile/outputs.py
  - doctrine/_compiler/compile/final_output.py
  - doctrine/_compiler/compile/records.py
  - doctrine/_compiler/compile/workflows.py
  - doctrine/_compiler/display.py
  - doctrine/_compiler/resolve/outputs.py
  - doctrine/_renderer/blocks.py
  - doctrine/_renderer/semantic.py
  - docs/EMIT_GUIDE.md
  - examples/README.md
  - examples/09_outputs/ref/turn_response_output_agent/AGENTS.md
  - examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md
  - examples/51_inherited_bound_io_roots/ref/inherited_bound_current_truth_demo/AGENTS.md
  - examples/56_document_structure_attachments/ref/lesson_plan_structure_demo/AGENTS.md
  - examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md
  - examples/84_review_split_final_output_prose/ref/draft_review_split_final_output_demo/AGENTS.md
  - examples/85_review_split_final_output_output_schema/ref/acceptance_review_split_json_demo/AGENTS.md
  - examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md
  - examples/119_route_only_final_output_contract/build_ref/route_only_final_output_contract_demo/AGENTS.md
---

# TL;DR

- Outcome: turn this audit into the one Doctrine plan for making rendered agent markdown tighter, clearer, and more human without changing Doctrine syntax or runtime semantics.
- Problem: current rendered examples still mirror too much of the typed source tree, so they repeat the same contract, build heading ladders, dump structure too eagerly, leak raw guard and route syntax, and overuse tables for tiny scalar surfaces.
- Approach: treat this as a Doctrine compile, display, lowering, and render-presentation refactor inside the canonical owner paths, then prove it on the shipped example corpus.
- Plan: lock the exact owner paths and compaction rules, then implement in phases starting with split review and final-output deduplication, wrapper lowering, artifact-structure compaction, and broader humanizing of guard, mode, and route text.
- Non-negotiables: no new Doctrine syntax, no payload-shape changes, no review or route semantic changes, no `../psflows` or `../rally` cleanup in this plan, and no content loss from the original audit.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can render much tighter agent markdown by changing presentation logic
only. A good implementation will make the rendered outputs for the current
problem examples smaller, clearer, and less repetitive while preserving the
same Doctrine language, payload contracts, review semantics, and route
semantics.

## 0.2 In scope

- Requested behavior scope:
  - make rendered Doctrine markdown feel markdown-first instead of compiler-first
  - fix the current Doctrine-owned bloat fronts in rendered outputs:
    - split review and final-output duplication
    - single-child wrapper headings and binding shells
    - eager artifact-structure expansion
    - raw guard, mode, and route syntax in human markdown
    - tiny scalar contracts that still default to tables
- Allowed architectural convergence scope:
  - `doctrine/_compiler/compile/final_output.py`
  - `doctrine/_compiler/compile/outputs.py`
  - `doctrine/_compiler/compile/records.py`
  - `doctrine/_compiler/compile/workflows.py`
  - `doctrine/_compiler/display.py`
  - `doctrine/_compiler/resolve/outputs.py` if existing omitted-title lowering
    must be reused directly
  - `doctrine/_renderer/blocks.py`
  - `doctrine/_renderer/semantic.py`
  - impacted example `ref/` and `build_ref/` outputs under `examples/`
  - Doctrine docs and instructions that would become stale if the emitted
    markdown story changes in a public way
- Adjacent-surface scope:
  - include now: impacted example refs, build refs, and manifest-backed proof
    inputs in this repo
  - include now if they become stale: `docs/EMIT_GUIDE.md` and
    `examples/README.md`
  - explicit out of scope: `../psflows` and `../rally`
- Compatibility posture:
  - preserve the existing public Doctrine language
  - preserve review semantics, route semantics, and output payload shapes
  - allow a clean cutover only for Doctrine-owned generated markdown wording and
    layout in example artifacts

## 0.3 Out of scope

- new Doctrine syntax
- new declarations or authored semantic features
- changing wire payload shape
- changing review semantics
- changing route semantics
- repo-local prompt cleanup outside this repo
- sibling repo cleanup in `../psflows` or `../rally`

## 0.4 Definition of done (acceptance evidence)

- The plan names one canonical owner path for each current markdown-bloat front.
- The target render rules are concrete enough to implement without guessing.
- The representative Doctrine examples in this doc have a clear "today" and
  "best case" story for the intended cleanup.
- After implementation, impacted examples render closer to the best-case forms
  in this doc without changing the underlying contract meaning.
- After implementation, `make verify-examples` passes.
- If diagnostics change, `make verify-diagnostics` also passes.
- If public render guidance changes, the touched Doctrine docs update in the
  same change.
- This `reformat` pass is docs-only. I did not run verify commands here.

## 0.5 Key invariants (fix immediately if violated)

- No new Doctrine syntax.
- No payload-shape changes.
- No review or route semantic changes.
- No sidecar formatter or second render system.
- No runtime fallback or shim for old rendered wording.
- Tables must earn their space.
- One concept should render once.
- Wrapper headings should earn their space.
- Guard and route logic should read like human instructions, not compiler IR.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Remove repeated contract explanation from rendered markdown.
2. Make the markdown read like plain instructions, not compiler output.
3. Keep Doctrine language and runtime meaning stable.
4. Fix the problem in canonical Doctrine owner paths, not with repo-local hacks.
5. Keep tables for real schema, comparison, or columns only.

## 1.2 Constraints

- Shipped truth lives in `doctrine/`, not in docs or example prose alone.
- The corpus is the proof surface. Example refs will need to move with the
  code.
- Shipped bundled markdown prose should stay at about a 7th grade reading
  level.
- This plan is Doctrine-only. It must not absorb sibling repo cleanup work.
- This `reformat` command is docs-only and must not change code.

## 1.3 Architectural principles (rules we will enforce)

- Treat this as a formatting and presentation problem first, not a
  language-design project.
- Lower extra shells earlier when structure is the real problem. Do not only
  swap punctuation at the end.
- Extend the current humanizing machinery before inventing a second render
  stack.
- Keep payload semantics in one clear place when review and final output both
  render.
- Prefer bullets or short prose for tiny scalar contracts.
- Prefer fail-loud rendering boundaries over silent semantic drift.

## 1.4 Known tradeoffs (explicit)

- Some "formatting-only" wins will still require compiler-side edits because the
  shape is decided before the final markdown renderer runs.
- Cleaner emitted markdown will cause expected churn in example refs and build
  refs.
- A more compact render may hide some typed structure that is visible today, but
  that typed structure still exists in shipped Doctrine truth and does not need
  to be restated in full human markdown.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already has a strong shipped corpus and some compact render behavior,
but many rendered agent examples still expose the internal typed tree too
directly. The result is correct enough, but larger and less clear than it needs
to be.

The current repeated patterns are:

- split review and final-output sections that restate the same contract
- single-child wrappers that create heading ladders
- artifact outputs that explain every structure layer by default
- raw guard, mode, and route syntax in human markdown
- small scalar contracts that still render as mini tables

## 2.2 What's broken / missing (concrete)

### P1. Split review and final-output sections restate the same contract

This is the biggest Doctrine-owned presentation bloat front. Today, split
review examples often render a readable review carrier, then a payload table for
the final output, then a semantics table mapping meanings back to fields, then
another field-by-field outline. The same contract appears in three or four
forms.

### P1. Single-child wrapper headings and binding shells create heading ladders

Doctrine still emits a lot of wrapper structure that does not add meaning. The
clean fix is usually earlier lowering, not just changing punctuation at the
end.

### P1. Artifact-structure emission is still too eager

This is still a formatting and emit-presentation problem, even though the owner
path sits in compile code. The default pattern is often a contract table, a
structure row, a structure heading, a prose lead-in, and then a second table.
That scales badly once the structure gets larger.

### P1. Raw guard, mode, and route syntax is leaking into human markdown

Some rendered Doctrine examples still read like compiler IR. The problem is
coverage. The ugliest guard and route-heavy surfaces still fall through as raw
structure.

### P2. Small scalar contracts still default to table-heavy rendering too often

Doctrine already has proof that compact output can work. The gap is consistency.
Tiny scalar contracts should not get the same table-heavy treatment as a real
payload schema.

## 2.3 Constraints implied by the problem

- The fix must preserve meaning while removing restatement.
- The work may start in compiler lowering, not only in the final renderer.
- The solution should build on current concise and sentence rendering support.
- Tables still have a role for payload schema, real comparison, and real
  columns.

The core problem is still the same: Doctrine is rendering too much of the typed
source tree directly into markdown. This plan treats that as a formatting and
presentation problem, not a language-design project. The next win is better
lowering, simpler structure, and cleaner markdown.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- None yet. Reject outside prior art for now. Repo truth is closer, more
  specific, and already names the shipped contracts, examples, and proof
  surfaces this cleanup must preserve.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/_compiler/compile/final_output.py:28-154` - resolves the
    `final_output` owner, threads review and route semantics, and decides
    whether a dedicated `Final Output` section is built.
  - `doctrine/_compiler/compile/final_output.py:157-334` - assembles the final
    output markdown body. Today this path starts from a contract table and then
    layers payload, example, schema, structure, and support items.
  - `doctrine/_compiler/compile/final_output.py:335-382` - adds `Review
    Response Semantics` when `review_contract.final_response.mode == "split"`.
    This is the direct source of the review and final-output restatement in the
    split review examples.
  - `doctrine/_compiler/compile/outputs.py:90-210` - compiles ordinary outputs,
    including the contract-table-first path for non-final outputs.
  - `doctrine/_compiler/compile/outputs.py:350-383` -
    `_compile_ordinary_output_contract_rows` always materializes `Target`,
    `Shape`, `Requirement`, and optional `Schema` or `Structure` rows that later
    become the visible table.
  - `doctrine/_compiler/compile/outputs.py:563-666` and
    `doctrine/_compiler/compile/outputs.py:814-866` - record-table and
    flattening helpers already collapse some prose-only detail, so there is
    existing compaction logic to extend instead of replace.
  - `doctrine/_compiler/compile/outputs.py:867-947` -
    `_compile_output_structure_section` always emits the `This artifact must
    follow...` lead-in plus a required-section table and optional detail blocks.
    This is the direct source of the eager `Artifact Structure` shape in example
    `56`.
  - `doctrine/_compiler/compile/records.py:46-199` and
    `doctrine/_compiler/compile/records.py:201-233` - generic record-section and
    fallback-scalar lowering. Wrapper shells and titled nested sections stay
    alive here unless a caller lowers them sooner.
  - `doctrine/_compiler/compile/workflows.py:174-286` - workflow-law and
    handoff-routing compilation already emits fixed-mode and active-when prose
    before the renderer sees the text.
  - `doctrine/_compiler/display.py:215-274`,
    `doctrine/_compiler/display.py:393-459`,
    `doctrine/_compiler/display.py:621-677`, and
    `doctrine/_compiler/display.py:852-878` - current artifact, current none,
    own only, preserve exact, mode selection, route wording, and route-exists
    humanization all originate here.
  - `doctrine/_compiler/resolve/outputs.py:1998-2048` - existing omitted IO
    wrapper-title lowering. This is the nearest shipped pattern for safe
    single-child shell collapse.
  - `doctrine/_renderer/semantic.py:8-36` - built-in profile modes already
    support sentence and concise lowering for `ArtifactMarkdown` and
    `CommentMarkdown`.
  - `doctrine/_renderer/blocks.py:34-180` and
    `doctrine/_renderer/blocks.py:447-460` - renderer applies semantic lowering
    and the concise guard shell, but only after compiled shapes have already
    been chosen.
- Canonical path / owner to reuse:
  - `doctrine/_compiler/compile/final_output.py` - split review and final-output
    dedupe.
  - `doctrine/_compiler/compile/outputs.py` plus
    `doctrine/_compiler/compile/records.py` - ordinary output compaction,
    wrapper collapse, tiny scalar bullets, and artifact-structure compaction.
  - `doctrine/_compiler/compile/workflows.py` plus
    `doctrine/_compiler/display.py` - sentence-level wording for workflow-law
    mode, current artifact, own only, preserve, stop, and route text.
  - `doctrine/_renderer/semantic.py` plus `doctrine/_renderer/blocks.py` -
    final shell style for semantic sections and guard blocks after the compiler
    has already chosen the simpler shape.
- Adjacent surfaces tied to the same contract family:
  - `examples/83_review_final_output_output_schema`,
    `examples/84_review_split_final_output_prose`,
    `examples/85_review_split_final_output_output_schema`,
    `examples/90_split_handoff_and_final_output_shared_route_semantics`,
    `examples/104_review_final_output_output_schema_blocked_control_ready`,
    `examples/105_review_split_final_output_output_schema_control_ready`,
    `examples/106_review_split_final_output_output_schema_partial`, and
    `examples/119_route_only_final_output_contract` - the same final-output,
    review, and route contract family. Their `cases.toml`, `ref/`, `build_ref/`,
    and emitted `final_output.contract.json` files must stay in sync.
  - `examples/38_metadata_polish_capstone`,
    `examples/51_inherited_bound_io_roots`,
    `examples/56_document_structure_attachments`, and
    `examples/117_io_omitted_wrapper_titles` - the same wrapper, heading, and
    structure-compaction family.
  - `examples/64_render_profiles_and_properties` and
    `examples/67_semantic_profile_lowering` - existing render-profile and
    semantic-lowering proof that this plan should extend.
  - `examples/README.md` - live corpus map that already documents examples `64`,
    `67`, `83` through `85`, `105`, `117`, and `119`.
  - `docs/EMIT_GUIDE.md` - live emit guidance if generated markdown shape
    changes in a way users should read about.
- Compatibility posture (separate from `fallback_policy`):
  - Preserve the existing Doctrine language, payload schemas, review semantics,
    route semantics, and emitted contract metadata.
  - Allow a clean cutover only for generated markdown wording and layout plus
    refreshed checked-in example artifacts in this repo.
- Existing patterns to reuse:
  - `examples/117_io_omitted_wrapper_titles/cases.toml` - omitted wrapper
    titles already lower one direct declaration and fail loud on ambiguous
    collapse. This is the closest shipped proof for safe wrapper compaction.
  - `examples/64_render_profiles_and_properties/prompts/AGENTS.prompt` and
    `examples/67_semantic_profile_lowering/prompts/AGENTS.prompt` - existing
    `render_profile` modes for concise guards, sentence-like review checks, and
    natural ordered prose.
  - `doctrine/_compiler/compile/outputs.py:814-866` - existing flattening helper
    for prose-only record content.
- Prompt surfaces / agent contract to reuse:
  - `examples/*/prompts/AGENTS.prompt` - authored truth for the representative
    examples.
  - `examples/*/cases.toml` - manifest-backed proof inputs for the same
    examples.
- Native model or agent capabilities to lean on:
  - Not applicable. This is not a runtime-capability or prompt-authoring gap.
- Existing grounding / tool / file exposure:
  - `doctrine/verify_corpus.py` - shipped corpus verifier.
  - `Makefile` `verify-examples` and `verify-diagnostics` - shipped repo proof
    entry points.
  - Repo `AGENTS.md` instructions - single-manifest verify command for focused
    example passes.
- Duplicate or drifting paths relevant to this change:
  - `examples/README.md` says checked-in `ref/AGENTS.md` files render ordinary
    outputs as grouped contract tables. That text may drift if ordinary output
    compaction broadens beyond the current pattern.
  - Emitted `final_output.contract.json` files under `build_ref/` must stay
    aligned with any final-output cleanup that still preserves route and
    control-ready metadata.
- Capability-first opportunities before new tooling:
  - Extend the current compiler lowering and render-profile or semantic-lowering
    paths first.
  - Do not add a post-render formatter or a second markdown system.
- Behavior-preservation signals already available:
  - `make verify-examples`.
  - `uv run --locked python -m doctrine.verify_corpus --manifest <cases.toml>`
    for a focused example pass.
  - `tests/test_final_output.py` - split review and final-output coverage, route
    semantics coverage, and schema-backed final-output coverage.
  - `tests/test_emit_docs.py` - emitted contract and route-contract metadata
    coverage.
  - `tests/test_emit_flow.py` and `tests/test_review_imported_outputs.py` -
    flow and imported review-output truth coverage.
  - `tests/test_output_rendering.py:179` and
    `tests/test_output_inheritance.py:228` - current artifact-structure
    rendering coverage.

## 3.3 Decision gaps that must be resolved before implementation

- No user blocker is exposed by research.
- Deep-dive resolves the remaining design choices in Sections `4` through `6`.
- The remaining work is implementation detail, not plan shape:
  - exact helper names
  - exact touched examples inside the already approved adjacent-surface families
  - whether `docs/EMIT_GUIDE.md` also needs an update once the final rendered
    diffs are in hand

The next pass should build on those strengths instead of inventing a second
render system.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Parse, resolve, and compile surfaces:
  - `doctrine/_compiler/resolve/outputs.py` - resolves I/O buckets and already
    lowers omitted wrapper titles when there is exactly one direct declaration.
  - `doctrine/_compiler/compile/final_output.py` - builds the dedicated final
    output contract section.
  - `doctrine/_compiler/compile/outputs.py` - builds ordinary output contracts,
    file artifacts, record tables, and structure sections.
  - `doctrine/_compiler/compile/records.py` - lowers generic record sections,
    fallback scalars, and guarded output items.
  - `doctrine/_compiler/compile/workflows.py` - compiles workflow-law and
    handoff-routing prose before markdown render.
  - `doctrine/_compiler/display.py` - turns workflow-law statements and route
    conditions into the human-facing strings that appear in the rendered docs.
- Renderer surfaces:
  - `doctrine/_renderer/semantic.py` - built-in semantic lowering modes.
  - `doctrine/_renderer/blocks.py` - final markdown rendering for sections,
    guards, properties, tables, and other readable blocks.
- Proof and adjacent live surfaces:
  - `doctrine/verify_corpus.py`
  - `Makefile`
  - `examples/*/cases.toml`
  - `examples/*/ref/**`
  - `examples/*/build_ref/**`
  - `examples/README.md`
  - `docs/EMIT_GUIDE.md`

## 4.2 Control paths (runtime)

1. Doctrine parses prompts and resolves typed declarations, including I/O bucket
   structure and inherited declarations.
2. `resolve/outputs.py` lowers omitted wrapper titles only for one direct
   declaration and fails loud when that shape is ambiguous.
3. `compile/workflows.py` and `display.py` emit workflow-law sentences such as
   active mode, current artifact, own only, preserve exact, stop, and route
   wording before the markdown renderer sees the text.
4. `compile/outputs.py`, `compile/records.py`, and `compile/final_output.py`
   turn output declarations into `CompiledSection` trees, tables, guard blocks,
   and support sections.
5. `semantic.py` and `blocks.py` apply render-profile modes and shell style to
   the compiled shapes that already exist.
6. `verify_corpus` and the checked-in example artifacts prove the emitted
   markdown, emitted schemas, and route-contract metadata.

Today the bloat fronts are split across steps 3 through 5. Some wording is too
literal before render time, and some compiled shapes stay too large for the
small contracts they describe.

## 4.3 Object model + key abstractions

- `CompiledSection` and `CompiledBodyItem` are the main markdown-tree
  abstraction.
- `CompiledGuardBlock`, `CompiledPropertiesBlock`, and `CompiledTableBlock`
  already give the renderer distinct structural shapes.
- `CompiledReviewSpec` and `final_response.mode == "split"` drive the current
  review and final-output split behavior.
- `ResolvedContractBucket` and omitted-title lowering already capture the
  "single direct declaration may own the heading" rule for one shipped I/O path.
- `ResolvedRenderProfile` plus built-in profile modes already support
  sentence-like review checks and concise guard shells.

## 4.4 Observability + failure behavior today

- The most common failure mode here is not a compiler crash. It is a truthful
  but over-large or hard-to-scan rendered markdown shape.
- The strongest preservation signals already exist:
  - `tests/test_final_output.py:1061-1618`
  - `tests/test_emit_docs.py:194-269`
  - `tests/test_emit_flow.py:206-234`
  - `tests/test_review_imported_outputs.py:138-261`
  - `tests/test_output_rendering.py:179-239`
  - `tests/test_output_inheritance.py:211-233`
  - the manifest-backed example families named in Section `3.2`
- The fail-loud invariant for omitted wrapper-title lowering is already proven
  by `examples/117_io_omitted_wrapper_titles/cases.toml`.
- There is no telemetry or rollout instrumentation for this surface. The proof
  story is code-level tests plus the example corpus.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is emitted markdown and contract presentation, not UI.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/_compiler/compile/final_output.py` remains the single owner for
  split review and dedicated final-output presentation.
- `doctrine/_compiler/compile/outputs.py` plus
  `doctrine/_compiler/compile/records.py` remain the single owner for ordinary
  output contract compaction, compiler-generated binding-shell collapse, tiny
  scalar bullet rendering, and artifact-structure compaction.
- `doctrine/_compiler/compile/workflows.py` plus
  `doctrine/_compiler/display.py` become the explicit owner for cleaner
  workflow-law wording in route-heavy and mode-heavy sections.
- `doctrine/_compiler/resolve/outputs.py` stays the shipped precedent for safe
  single-child lowering. Reuse its rule shape instead of inventing a different
  ambiguity policy.
- `doctrine/_renderer/semantic.py` plus `doctrine/_renderer/blocks.py` stay the
  final style layer. They do not become a second decision system for dedupe,
  shell collapse, or contract-size selection.

## 5.2 Control paths (future)

1. Resolution still enforces fail-loud ambiguity rules for omitted wrapper
   titles.
2. Workflow-law compilation emits cleaner sentences earlier for fixed mode,
   current artifact, preserve, own-only, stop, and route statements.
3. Final-output compilation renders the review carrier once and the final-output
   contract once. Split review outputs stop emitting a standalone `Review
   Response Semantics` section when it only repeats payload meaning already
   shown elsewhere.
4. Ordinary output compilation chooses contract shape before render:
  - bullet form for tiny scalar turn-response outputs with only `Target`,
    `Shape`, and `Requirement` and no schema, structure, delivery-skill rows,
    config rows, or support tables
  - table form for files outputs, schema-backed JSON outputs, outputs with
    structure or schema rows, outputs with delivery-skill or target-config rows,
    and any output whose detail really benefits from columns
5. Artifact-structure compilation chooses between compact and full form using
   the existing summary and detail split:
  - compact form when the document has no preamble and produces no detail blocks
  - full `Artifact Structure` section when there is a preamble, a definitions
    contract, a table contract, or any other detail block that needs explicit
    follow-on rendering
6. Compiler-generated binding shells collapse when all of these are true:
  - the wrapper is compiler-owned, not a user-authored explicit wrapper title
  - the wrapper body contains exactly one direct compiled child section
  - the wrapper adds no authored prose, no extra siblings, and no extra metadata
  - the child title already carries the real meaning
7. Renderer semantic modes keep doing sentence and concise shell rendering for
   the simpler compiled shapes above. No new public `render_profile` target is
   required in this plan.
8. The corpus refreshes the impacted example artifacts and emitted contracts in
   one clean cutover.

## 5.3 Object model + abstractions (future)

- No new public Doctrine objects, declarations, or syntax.
- Internal helper boundaries should become explicit:
  - review and final-output dedupe helper in `final_output.py`
  - tiny scalar contract selector in `outputs.py`
  - simple-structure compact selector in `outputs.py`
  - compiler-generated binding-shell collapse helper in `outputs.py` or
    `records.py`
  - workflow-law sentence humanizers in `display.py` and their callers in
    `compile/workflows.py`
- Existing `CompiledSection`, `CompiledGuardBlock`, and semantic render-profile
  machinery stay in place. The change is about producing better shapes earlier,
  not replacing the readable model.

## 5.4 Invariants and boundaries

- One meaning renders once.
- Public Doctrine syntax stays stable.
- Payload schemas and emitted `final_output.contract.json` metadata stay stable.
- Review semantics and route semantics stay stable.
- Compiler and display code own structure-sensitive compaction and
  sentence-level wording.
- Renderer code owns shell style, not semantic dedupe.
- User-authored explicit wrapper titles keep their current long-form behavior.
- Omitted wrapper-title ambiguity stays fail loud.
- Tables are for real tables.
- No second formatter, no post-render cleanup layer, and no fallback shim for
  old wording.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Split review and final-output dedupe | `doctrine/_compiler/compile/final_output.py` | `_compile_final_output_section`, `_compile_final_output_review_response_semantics` | split review outputs render the review carrier, then a separate review-response semantics section that repeats payload meaning | remove standalone repeated semantics when split final output already shows the payload contract and support items | biggest markdown-bloat front | none public | `tests/test_final_output.py:1061-1618`, `tests/test_emit_docs.py:194-269`, `tests/test_emit_flow.py:206-234`, `tests/test_review_imported_outputs.py:138-261`, examples `83`, `84`, `85`, `90`, `104`, `105`, `106`, `119` |
| Tiny scalar ordinary-output compaction | `doctrine/_compiler/compile/outputs.py` | `_compile_output_decl`, `_compile_ordinary_output_contract_rows`, `_compile_ordinary_output_contract_table` | small turn-response contracts default to `Contract | Value` tables even when they only say target, shape, and requirement | select bullets for tiny scalar contracts and keep tables for complex contracts | tables should earn space | none public | `examples/09_outputs/cases.toml`, `examples/85_review_split_final_output_output_schema/cases.toml`, `tests/test_output_target_delivery_skill.py:75-140`, `make verify-examples` |
| Compiler-generated binding-shell collapse | `doctrine/_compiler/compile/outputs.py`, `doctrine/_compiler/compile/records.py` | ordinary output support-item lowering around `_compile_ordinary_output_support_item`, generic section lowering in `_compile_record_item` | compiler-generated binding shells create heading ladders even when one child section already owns the meaning | collapse compiler-owned single-child binding wrappers that add no prose or metadata | clearer structure without changing authored wrapper behavior | none public | `examples/38_metadata_polish_capstone/cases.toml`, `examples/51_inherited_bound_io_roots/cases.toml`, `examples/117_io_omitted_wrapper_titles/cases.toml`, `make verify-examples` |
| Simple artifact-structure compaction | `doctrine/_compiler/compile/outputs.py` | `_compile_output_structure_section`, `_compile_output_structure_summary_rows`, `_compile_output_structure_summary_row` | every structure attachment emits the same lead-in plus summary table and optional detail blocks | emit a compact required-structure summary when there is no preamble and no detail block; keep full structure sections otherwise | avoids eager structure dumps while preserving rich structure proofs | none public | `tests/test_output_rendering.py:179-239`, `tests/test_output_inheritance.py:211-233`, `examples/56_document_structure_attachments/cases.toml`, `make verify-examples` |
| Workflow-law sentence humanization | `doctrine/_compiler/compile/workflows.py`, `doctrine/_compiler/display.py` | `_compile_workflow_law`, `_compile_handoff_routing_law`, `_render_law_stmt_lines`, `_render_match_stmt`, `_render_condition_ref` | active mode, current artifact, own only, preserve exact, and route selection text still render as compiler-like statements in workflow-law sections | rewrite these sentence forms to be more human while preserving exact law meaning and route guards | examples `38` and `119` are owned here, not by final markdown rendering alone | none public | `examples/38_metadata_polish_capstone/cases.toml`, `examples/119_route_only_final_output_contract/cases.toml`, `make verify-examples` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `final_output.py` owns split review and final-output dedupe
  - `outputs.py` plus `records.py` own ordinary output compaction and simple
    artifact-structure compaction
  - `compile/workflows.py` plus `display.py` own cleaner workflow-law wording
  - `semantic.py` plus `blocks.py` stay the style layer and are not the planned
    primary change surface
- Deprecated APIs (if any):
  - none public
- Delete list (what must be removed; include superseded shims or parallel paths if any):
  - the generated `Review Response Semantics` section where it only repeats the
    payload contract
  - compiler-generated `* Binding` shells that meet the single-child collapse
    rule
  - eager simple `Artifact Structure` detail sections when the compact summary
    rule applies
- Adjacent surfaces tied to the same contract family:
  - include now:
    - examples `83`, `84`, `85`, `90`, `104`, `105`, `106`, and `119`
    - examples `38`, `51`, `56`, `64`, `67`, and `117`
    - their `cases.toml`, `ref/`, `build_ref/`, and emitted contract files
  - include now if stale after the code diff:
    - `examples/README.md`
    - `docs/EMIT_GUIDE.md`
  - exclude:
    - `../psflows`
    - `../rally`
- Compatibility posture / cutover plan:
  - preserve the public Doctrine language, payload contracts, review semantics,
    route semantics, and route-contract metadata
  - cleanly refresh the generated markdown and checked-in proof artifacts in the
    same repo change
- Capability-replacing harnesses to delete or justify:
  - none
  - do not add a post-render formatter, docs audit script, or grep-based proof
    gate
- Live docs/comments/instructions to update or delete:
  - update `examples/README.md` if its grouped-table story becomes stale
  - update `docs/EMIT_GUIDE.md` only if the public emitted-markdown guidance
    truly changes
  - add at most a short boundary comment where a compact-vs-full rule would be
    hard to infer from code
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - focused `doctrine.verify_corpus --manifest ...` runs for touched example
    families
  - `tests/test_final_output.py`
  - `tests/test_emit_docs.py`
  - `tests/test_emit_flow.py`
  - `tests/test_review_imported_outputs.py`
  - `tests/test_output_rendering.py`
  - `tests/test_output_inheritance.py`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Split review final outputs | `doctrine/_compiler/compile/final_output.py`, examples `83`, `84`, `85`, `90`, `104`, `105`, `106`, `119` | render review meaning once and payload meaning once | prevents the same review contract from drifting across carrier, payload, and semantics sections | include |
| Workflow-law wording | `doctrine/_compiler/compile/workflows.py`, `doctrine/_compiler/display.py` | use sentence-first wording for fixed mode, current artifact, own-only, preserve, stop, and route text | prevents raw IR wording from surviving in workflow-law-heavy examples | include |
| Single-child shell lowering | `doctrine/_compiler/resolve/outputs.py::_lower_omitted_io_section`, `doctrine/_compiler/compile/outputs.py`, `doctrine/_compiler/compile/records.py` | reuse the shipped one-child lowering rule for compiler-generated shells | prevents wrapper-collapse logic from diverging across two I/O families | include |
| Structure compaction | `doctrine/_compiler/compile/outputs.py::_compile_output_structure_section` | pick compact form only when there is no preamble and no detail block | prevents accidental loss of real structure detail | include |
| Semantic render modes | `doctrine/_renderer/semantic.py`, `doctrine/_renderer/blocks.py`, examples `64` and `67` | keep existing sentence and concise shell modes as the final style layer | avoids inventing a second render-profile surface for this cleanup | include |
| Public docs sync | `examples/README.md`, `docs/EMIT_GUIDE.md` | refresh only if the shipped emitted-markdown story changed | prevents stale live docs without forcing speculative doc churn | include |

## 6.3 Detailed evidence and target render

### Split review and final-output duplication

This is the biggest Doctrine-owned presentation bloat front.

Today, split review examples often render:

- a readable review carrier
- a payload table for the final output
- a semantics table mapping meanings back to fields
- another field-by-field outline

That means the same contract appears in three or four forms.

Source:
`examples/105_review_split_final_output_output_schema_control_ready/ref/acceptance_review_split_control_ready_demo/AGENTS.md`

Today:

```md
### Acceptance Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Verdict

State whether the plan passed review or asked for changes.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.

#### Output Contents That Matter

State what the next owner should read first.
```

Then later in the same file:

```md
#### Review Response Semantics

This final response is separate from the review carrier: AcceptanceReviewComment.

| Meaning | Field |
| --- | --- |
| Verdict | `verdict` |
| Current Artifact | `current_artifact` |
| Next Owner | `next_owner` |
| Blocked Gate | `blocked_gate` |

#### Field Notes

Keep `verdict` aligned with the review verdict.
Use null for `next_owner` and `blocked_gate` when this review does not set them.

#### Verdict

State whether the review accepted the plan or asked for changes.
```

Best case:

```md
### Acceptance Review

- Verdict: say whether the plan passed review or needs changes.
- Reviewed artifact: name the draft plan.
- Analysis: give the short reason for the verdict.
- Read first: say what the next owner should read first.
- Current artifact: include only when one still stands.
- Next owner: include only when one exists.
- Failure detail: include only on reject.

## Final Output

Return one control-ready JSON object with:

- `verdict`
- `current_artifact`
- `next_owner`
- `blocked_gate`

This JSON mirrors the review outcome. Do not restate the review contract here.
```

Owner path:

- `doctrine/_compiler/compile/final_output.py`

### Single-child wrapper headings and binding shells

Doctrine still emits a lot of wrapper structure that does not add meaning.

Source:
`examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md`

Today:

```md
### Current Handoff Binding

#### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

### Approved Plan Binding

#### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
```

A smaller version of the same issue appears in inherited bound roots.

Source:
`examples/51_inherited_bound_io_roots/ref/inherited_bound_current_truth_demo/AGENTS.md`

Today:

```md
## Inputs

### Approved Plan Binding

#### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
```

Best case:

```md
## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required
```

The clean fix is earlier lowering, not punctuation at the end.

Owner paths:

- `doctrine/_compiler/compile/outputs.py`
- `doctrine/_compiler/compile/records.py`
- pattern reference: `doctrine/_compiler/resolve/outputs.py::_lower_omitted_io_section`

### Artifact-structure emission

This is still a formatting and emit-presentation problem, even though the owner
path sits in compile code.

Source:
`examples/56_document_structure_attachments/ref/lesson_plan_structure_demo/AGENTS.md`

Today:

```md
### Next Lesson Plan

| Contract | Value |
| --- | --- |
| Target | File |
| Path | `lesson_root/NEXT_LESSON_PLAN.md` |
| Shape | Markdown Document |
| Requirement | Required |
| Structure | Lesson Plan |

#### Artifact Structure

This artifact must follow the `Lesson Plan` structure below.

| Required Section | Kind | What it must do |
| --- | --- | --- |
| **Overview** | Section | Start with the plan overview. |
| **Sequence** | Section | List the lesson steps in order. |
```

This is not terrible. But it already shows the default pattern:

- contract table
- structure row
- structure heading
- prose lead-in
- second table

That pattern scales poorly once the structure gets larger.

Best case:

```md
### Next Lesson Plan

- Target: file
- Path: `lesson_root/NEXT_LESSON_PLAN.md`
- Shape: Markdown document
- Required structure:
  - Overview
  - Sequence
```

Owner path:

- `doctrine/_compiler/compile/outputs.py::_compile_output_structure_section`

### Raw guard, mode, and route syntax

Some rendered Doctrine examples still read like compiler IR.

Source:
`examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md`

Today:

```md
Active mode: section-summary.

Current artifact: Section Metadata.

Make sure current_handoff.preserve_basis == approved_structure.

Own only {`section_metadata.name`, `section_metadata.description`}.

Preserve exact `section_metadata.*` except `section_metadata.name`, `section_metadata.description`.

If unclear(pass_mode, current_handoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.
```

Source:
`examples/119_route_only_final_output_contract/build_ref/route_only_final_output_contract_demo/AGENTS.md`

Today:

```md
This pass runs only when RouteFacts.live_job is route_only_final.

No artifact is current for this turn.

Use exactly one mode:
- Routing Owner

If the mode is Routing Owner:
- Route to Routing Owner.
```

Best case:

```md
This pass is for `section-summary` mode.

The current artifact is Section Metadata.

Only edit:

- `section_metadata.name`
- `section_metadata.description`

Keep the rest of `section_metadata.*` unchanged.

If the mode or preserve basis is unclear, stop and route the issue back to
RoutingOwner.
```

And for the route-only case:

```md
This is a route-only turn.

No specialist artifact is current.

Route the work to Routing Owner and end the turn.
```

Owner paths:

- `doctrine/_compiler/compile/workflows.py`
- `doctrine/_compiler/display.py`

### Small scalar contracts

Doctrine already has proof that compact output can work.

Source:
`examples/09_outputs/ref/turn_response_output_agent/AGENTS.md`

Today:

```md
# Turn Response Output Agent

Core job: return a short issue summary in the turn response.

## Your Job

- Return the issue summary in the turn response.

## Outputs

### Issue Summary Response

- Target: TurnResponse
- Shape: Issue Summary Text
- Requirement: Required
```

That is close to the right answer.

By contrast, small scalar review contracts still render too heavily.

Source:
`examples/85_review_split_final_output_output_schema/ref/acceptance_review_split_json_demo/AGENTS.md`

Today:

```md
### Acceptance Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |

#### Verdict

State whether the plan passed review.

#### Reviewed Artifact

Name the reviewed artifact.

#### Analysis Performed

Summarize the review analysis.
```

Best case:

```md
### Acceptance Review

- Target: turn response
- Shape: comment
- Verdict: say whether the plan passed review.
- Reviewed artifact: name the reviewed artifact.
- Analysis: summarize the review analysis.
```

This does not mean "no tables." It means tables should be for payload schema,
real comparison, or columns, not every small scalar contract.

### What already looks good

Doctrine already has proof that smaller surfaces are possible.

- `examples/09_outputs/ref/turn_response_output_agent/AGENTS.md:1-24` is short
  and clear.
- `doctrine/_renderer/semantic.py:19-37` already ships sentence and concise
  modes for `ArtifactMarkdown` and `CommentMarkdown`.
- `examples/64_render_profiles_and_properties/prompts/AGENTS.prompt:1-31`
  proves that authored `render_profile` can already lower some surfaces into
  sentences and concise guard shells.
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or `if needed` placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns and gotchas in code comments at the canonical boundary when that prevents future drift.

## Phase 1. Remove split review and final-output restatement

- Goal: make split review outputs explain the review once and the final payload
  once.
- Work: update `final_output.py` so the review carrier stays rich, the final
  output payload stays control-ready, and redundant review-response restatement
  disappears.
- Checklist (must all be done):
  - update `_compile_final_output_section` and
    `_compile_final_output_review_response_semantics` in
    `doctrine/_compiler/compile/final_output.py`
  - remove standalone repeated review-response semantics when the split final
    output already shows the payload contract and support items
  - preserve payload shape, field notes, trust surface, standalone read,
    control-ready text, route sections, and emitted
    `final_output.contract.json` metadata
  - refresh touched `ref/`, `build_ref/`, and emitted contract artifacts for
    examples `83`, `84`, `85`, `90`, `104`, `105`, `106`, and `119`
  - verify that same-output review finals in `83` and `104` do not regress
  - verify that shared or imported split-review surfaces in `90` and `106` do
    not regress
- Verification (required proof):
  - focused review and final-output coverage in:
    - `tests/test_final_output.py:1061-1618`
    - `tests/test_emit_docs.py:194-269`
    - `tests/test_emit_flow.py:206-234`
    - `tests/test_review_imported_outputs.py:138-261`
  - focused manifest verification for:
    - `examples/83_review_final_output_output_schema/cases.toml`
    - `examples/84_review_split_final_output_prose/cases.toml`
    - `examples/85_review_split_final_output_output_schema/cases.toml`
    - `examples/105_review_split_final_output_output_schema_control_ready/cases.toml`
    - `examples/119_route_only_final_output_contract/cases.toml`
- Docs/comments (propagation; only if needed):
  - add one short boundary comment in `final_output.py` only if the dedupe rule
    is hard to infer from the final helper split
- Exit criteria (all required):
  - split review outputs no longer emit a redundant `Review Response Semantics`
    section where the same meaning is already carried elsewhere
  - review meaning, payload meaning, route metadata, and control-ready behavior
    remain unchanged
  - the focused tests and manifests above pass
- Rollback:
  - revert `doctrine/_compiler/compile/final_output.py` together with the
    refreshed example and emitted contract artifacts

## Phase 2. Compact ordinary comment contracts and tiny scalar outputs

- Goal: stop using tables for contracts that do not need columns.
- Work: add bullet-first ordinary-output compaction for small turn-response
  contracts and simple comment carriers while preserving table form for real
  table-shaped contracts.
- Checklist (must all be done):
  - update ordinary-output contract selection in
    `doctrine/_compiler/compile/outputs.py`
  - keep table rendering for:
    - `files:` outputs
    - schema-backed JSON outputs
    - outputs with `structure` or `schema` rows
    - outputs with delivery-skill or target-config rows
    - outputs whose support content still needs tables
  - compact eligible tiny scalar outputs and simple ordinary comment contracts
    into bullet-first markdown without changing their meaning
  - refresh touched example artifacts for examples `09`, `83`, `84`, `85`,
    `104`, and `105`
  - confirm delivery-skill contract rows still render correctly when present
- Verification (required proof):
  - focused table-shape coverage in `tests/test_output_target_delivery_skill.py:75-140`
  - focused manifest verification for:
    - `examples/09_outputs/cases.toml`
    - `examples/83_review_final_output_output_schema/cases.toml`
    - `examples/85_review_split_final_output_output_schema/cases.toml`
- Docs/comments (propagation; only if needed):
  - add one short comment near the ordinary-output shape selector only if the
    table-versus-bullets rule would otherwise be unclear
- Exit criteria (all required):
  - eligible tiny scalar contracts render without `Contract | Value` bloat
  - complex contracts still keep their table form
  - delivery-skill and config-row outputs do not regress
  - the focused tests and manifests above pass
- Rollback:
  - revert the ordinary-output compaction change and the matching artifact
    refresh together

## Phase 3. Flatten compiler-generated binding shells

- Goal: remove heading ladders caused by compiler-generated wrapper shells.
- Work: collapse only the wrappers that are compiler-owned, single-child, and
  semantically empty, while preserving explicit authored long-form wrappers.
- Checklist (must all be done):
  - update the binding-shell lowering path in
    `doctrine/_compiler/compile/outputs.py` and
    `doctrine/_compiler/compile/records.py`
  - reuse the shipped omitted-title rule shape from
    `doctrine/_compiler/resolve/outputs.py::_lower_omitted_io_section`
  - collapse compiler-generated wrappers only when they add no authored prose,
    no extra siblings, and no extra metadata
  - preserve current behavior for explicit wrapper titles and fail-loud
    ambiguity
  - refresh touched example artifacts for examples `38`, `51`, and `117`
- Verification (required proof):
  - focused manifest verification for:
    - `examples/38_metadata_polish_capstone/cases.toml`
    - `examples/51_inherited_bound_io_roots/cases.toml`
    - `examples/117_io_omitted_wrapper_titles/cases.toml`
- Docs/comments (propagation; only if needed):
  - add one short comment at the collapse boundary only if the distinction
    between compiler-generated shells and explicit authored wrappers is subtle
- Exit criteria (all required):
  - compiler-generated `* Binding` ladders collapse where the child title
    already carries the meaning
  - explicit long-form wrappers remain intact
  - the omitted-title fail-loud behavior stays intact
  - the focused manifests above pass
- Rollback:
  - revert the shell-collapse change and the matching artifact refresh together

## Phase 4. Compact simple artifact structure

- Goal: keep simple structure attachments compact while preserving rich
  structure proofs.
- Work: use the existing summary and detail split in `outputs.py` to choose
  compact form only for simple structures and full form for richer structures.
- Checklist (must all be done):
  - update `_compile_output_structure_section`,
    `_compile_output_structure_summary_rows`, and
    `_compile_output_structure_summary_row` in
    `doctrine/_compiler/compile/outputs.py`
  - emit compact structure summaries only when there is no preamble and no
    detail block
  - preserve the full `Artifact Structure` section when a document has a
    preamble, definitions contract, table contract, or any other detail block
  - refresh touched example artifacts for examples `56` and any inherited
    structure examples affected by the selector
- Verification (required proof):
  - focused structure coverage in:
    - `tests/test_output_rendering.py:179-239`
    - `tests/test_output_inheritance.py:211-233`
  - focused manifest verification for:
    - `examples/56_document_structure_attachments/cases.toml`
- Docs/comments (propagation; only if needed):
  - add one short comment at the compact-versus-full selector only if the no
    preamble and no detail-block rule would otherwise be hard to read
- Exit criteria (all required):
  - simple structure attachments no longer default to eager multi-layer dumps
  - rich structure attachments still render the full detail path
  - the focused tests and manifest above pass
- Rollback:
  - revert the structure-selector change and the matching artifact refresh
    together

## Phase 5. Humanize workflow-law wording

- Goal: make route-heavy and mode-heavy workflow-law sections read like plain
  instructions without changing the law.
- Work: move the wording cleanup to the real owner path in
  `compile/workflows.py` and `display.py`, while leaving renderer semantic modes
  as support only.
- Checklist (must all be done):
  - update sentence-level wording for:
    - fixed mode lines
    - current artifact and current-none lines
    - own-only and preserve lines
    - stop lines
    - route-only wording and mode-selection wording
    - route-exists phrasing
  - preserve exact law meaning, route guards, and route-contract metadata
  - leave `doctrine/_renderer/semantic.py` and `doctrine/_renderer/blocks.py`
    unchanged unless a small supporting shell-style tweak is truly required
  - refresh touched example artifacts for examples `38` and `119`
  - confirm supporting semantic-render examples `64` and `67` still read
    truthfully if any renderer touch was required
- Verification (required proof):
  - focused manifest verification for:
    - `examples/38_metadata_polish_capstone/cases.toml`
    - `examples/119_route_only_final_output_contract/cases.toml`
  - use the full corpus pass later as the final no-regression proof for route
    and workflow-law wording
- Docs/comments (propagation; only if needed):
  - add one short comment near the compiler or display helper boundary only if
    the split between wording ownership and renderer style ownership is hard to
    infer
- Exit criteria (all required):
  - workflow-law wording in the touched examples reads closer to plain
    instructions
  - no route or review semantic drift appears in the refreshed examples
  - no renderer-first ownership assumption remains in the code path
  - the focused manifests above pass
- Rollback:
  - revert the compiler and display wording change together with the matching
    artifact refresh

## Phase 6. Corpus sweep, docs alignment, and final proof

- Goal: prove the final render cleanup across the shipped Doctrine corpus and
  leave no stale truth behind.
- Work: run the full proof set, refresh any stale live docs, and confirm the
  key example families all moved in the intended direction.
- Checklist (must all be done):
  - run `make verify-examples`
  - run `make verify-diagnostics` when diagnostics changed
  - inspect `examples/README.md` and update it if its grouped-table story is
    stale after the final diffs
  - inspect `docs/EMIT_GUIDE.md` and update it if the public emitted-markdown
    guidance is stale after the final diffs
  - manually read the refreshed outputs for examples `09`, `38`, `51`, `56`,
    `64`, `67`, `83`, `84`, `85`, `90`, `104`, `105`, `106`, `117`, and `119`
  - confirm no sibling repo cleanup work entered the change set
- Verification (required proof):
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics changed
  - manual read of the representative example families listed above
- Docs/comments (propagation; only if needed):
  - keep touched docs aligned with shipped behavior
- Exit criteria (all required):
  - the full corpus proof passes
  - any required diagnostics proof passes
  - live docs are not stale
  - the representative example families are tighter and clearer without
    semantic drift
- Rollback:
  - revert the render-change set and refreshed artifacts together
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer existing test surfaces if they already cover the touched compiler or
  renderer helpers.
- Add a targeted unit test only if a new deterministic helper carries real risk.
- Do not add tests whose only job is enforcing exact wording, deleted headings,
  or doc inventory shape.

## 8.2 Integration tests (flows)

- Primary proof is the shipped corpus.
- Use targeted manifest-backed example verification during implementation where
  that is cheaper.
- Run `make verify-examples` before calling the change complete.
- Run `make verify-diagnostics` only if diagnostics change.

## 8.3 E2E / device tests (realistic)

- No device testing applies here.
- Final manual proof is a short read of the representative rendered examples in
  this plan.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Single repo cutover.
- No bridge and no staged rollout.
- Land the render changes with the refreshed example artifacts in the same
  change set.

## 9.2 Telemetry changes

- None planned.
- The proof surface is still the example corpus, not runtime telemetry.

## 9.3 Operational runbook

- If an example render gets smaller but meaning drifts, stop and revert that
  path. Semantic drift is not allowed.
- If a render stays too large after the first pass, treat that as a follow-up in
  Doctrine owner paths, not a reason to spill into sibling repos.
- Keep implementation, examples, docs, and instructions aligned in the same
  repo change.

# 10) Decision Log (append-only)

## 2026-04-16 - Reframe the audit as one Doctrine-only formatting plan

### Context

The original doc was a Doctrine-only audit of rendered markdown problems. The
next step needed to turn that audit into one authoritative artifact that can
support a real plan.

### Options

- Keep the audit as a findings-only note.
- Expand the effort into a broader language or functionality change.
- Convert the audit into a canonical architecture plan focused on Doctrine-owned
  formatting and presentation work.

### Decision

Convert the audit into a canonical `miniarch-step` plan artifact and keep the
scope on Doctrine-owned markdown formatting, lowering, and emit presentation.

### Consequences

- The doc now stays in `draft` until the North Star is confirmed.
- The work stays focused on formatting and presentation at the product level.
- Some fixes may still land in compiler code because that is where structure is
  decided.
- Sibling repo cleanup is explicitly excluded.

### Follow-ups

- Run the deep-dive pass to clear Section `3.3`.
- Refine the target architecture and call-site audit with exact owner-path
  assignments.
- Build the implementation against Section `7` only after the draft is
  confirmed.

## 2026-04-16 - Clarify that workflow-law wording is a compile and display concern

### Context

The original audit treated raw guard, mode, and route wording mostly as a
renderer problem. Deep-dive showed that examples `38` and `119` get much of
their wording earlier from `compile/workflows.py` and `display.py`.

### Options

- Keep the cleanup pointed mainly at renderer files.
- Move the primary owner path for workflow-law wording to compiler and display
  files, while keeping renderer files as a final style layer only.

### Decision

Treat workflow-law sentence humanization as a compiler and display change.
Keep renderer semantic modes as supporting style, not the primary owner of this
cleanup.

### Consequences

- The implementation plan must send route and mode cleanup to
  `doctrine/_compiler/compile/workflows.py` and `doctrine/_compiler/display.py`.
- `doctrine/_renderer/semantic.py` and `doctrine/_renderer/blocks.py` stay in
  scope only as supporting style surfaces.
- Section `7` must not assume renderer-first ownership for this part of the
  work.

### Follow-ups

- Use the hook-owned `phase-plan` pass to tighten Section `7` against the new
  owner split.
- Keep `examples/38_metadata_polish_capstone` and
  `examples/119_route_only_final_output_contract` in the proof set for that
  phase.

## 2026-04-16 - Replace the draft execution checklist with implementation-only phases

### Context

The draft Section `7` still carried a planning-only phase and bundled multiple
code concerns into broad mixed phases. After deep-dive, the owner paths and
compaction rules were settled well enough to write an implementation-only plan.

### Options

- Keep the draft five-phase checklist with a planning-only first phase.
- Replace it with smaller implementation-only phases that track the real owner
  paths and proof surfaces.

### Decision

Replace the draft checklist with six implementation-only phases:

- split review and final-output dedupe
- ordinary comment and tiny scalar contract compaction
- compiler-generated binding-shell collapse
- simple artifact-structure compaction
- workflow-law wording cleanup
- final corpus and docs proof

### Consequences

- Section `7` no longer carries planning work that is already complete.
- The execution order now follows the actual owner split from Sections `5` and
  `6`.
- The auto-plan controller can truthfully stop after `phase-plan` and hand off
  to `implement-loop`.

### Follow-ups

- Keep implementation aligned to the ordered phases in Section `7`.
- Use the existing focused tests and manifest-backed examples as the first proof
  line before the full corpus run.

## 2026-04-16 - Preserve public Doctrine language and semantics

### Context

The user wanted this effort to be mostly about markdown formatting, not about
changing Doctrine itself.

### Options

- Use this work to change Doctrine syntax or behavior.
- Keep the public language and behavior stable and focus only on rendering.

### Decision

Keep Doctrine syntax, payload shapes, review semantics, and route semantics
stable. Limit the planned cutover to generated markdown wording and layout in
Doctrine-owned artifacts.

### Consequences

- The plan cannot justify new declarations, new authored semantic features, or
  payload-shape changes.
- Any implementation that needs semantic drift is out of scope and should be
  rejected or moved into a separate plan.

### Follow-ups

- Audit each phase against the invariants in Section `0.5`.
- Update docs only when the public emitted-markdown story truly changes.

# Appendix A) Imported Notes (unplaced; do not delete)

No unplaced notes remain. The prior audit content was mapped into Sections `1`,
`2`, `3`, `6`, and `7`.

# Appendix B) Conversion Notes

- The old `Scope`, `Out Of Scope`, and `Review Bar` sections now live in
  Sections `0` and `1`.
- The old findings now live in Sections `2` and `6`.
- The old "What Already Looks Good" notes now live in Sections `3` and `6`.
- The old "Doctrine-only Next Pass" list now lives in Section `7`.
- No content was intentionally dropped in this reformat.
- I did not run verify commands for this docs-only reformat.
