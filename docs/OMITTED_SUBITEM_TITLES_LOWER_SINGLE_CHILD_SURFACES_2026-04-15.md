---
title: "Doctrine - Omitted Subitem Titles Lower Single-Child Surfaces - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/OMITTED_SUBITEM_TITLES_REUSE_PARENT_TITLES_2026-04-15.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/EMIT_GUIDE.md
  - doctrine/grammars/doctrine.lark
  - doctrine/_parser/io.py
  - doctrine/_compiler/resolve/outputs.py
  - doctrine/_compiler/compile/outputs.py
  - examples/113_titleless_readable_lists
  - examples/117_io_omitted_wrapper_titles
---

# TL;DR

Outcome
: Doctrine should treat omitted titles on natural wrapper or subitem surfaces as "do not add another visible heading here" when one child already owns the readable heading. The current duplicate-heading behavior should be replaced before release, and the final rule should be as broad as it can be without becoming incoherent.

Problem
: The current omitted-title IO wrapper feature removes repeated authored titles but still emits two headings with the same text. That is the wrong user-facing behavior, and it exposes that the rule was framed as title reuse instead of wrapper lowering.

Approach
: Replace "reuse the child title on the wrapper" with a canonical lowering rule for the surfaces where omitted titles naturally mean "no wrapper heading of their own." Audit adjacent section-like surfaces so the final behavior is consistent where it truly fits, while keeping inherited-title override behavior separate unless repo evidence shows a better unification.

Plan
: Phase 1 replaces the internal title-copy data with flattening data. Phase 2 implements IO lowering and rewrites the focused proof. Phase 3 proves adjacent surfaces stayed stable. Phase 4 updates public docs, release notes, and full verification.

Non-negotiables
: No duplicate headings from omitted-title shorthand. No dual semantics on the same surface. Explicit-title syntax stays valid. No runtime shims or fallback heuristics. If the current unreleased behavior is wrong, replace it cleanly instead of preserving both stories.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

When an author omits a title on a natural wrapper or subitem surface, Doctrine should not emit a second visible heading that duplicates a child declaration title. On the surfaces where omitted titles are natural, the wrapper should lower instead. The final shipped rule should be broad where it is elegant and canonical, and narrow only where repo evidence shows that lowering would be wrong.

## 0.2 In scope

- Replace the current base `inputs` / `outputs` omitted-title behavior that reuses a child title and emits duplicate headings.
- Audit section-like and wrapper-like omitted-title surfaces to decide where lowering is the canonical omitted-title meaning.
- Keep the broad consistency goal explicit: do this everywhere it makes sense, not only for `inputs` / `outputs`, unless research shows that a narrower boundary is the cleanest architecture.
- Update grammar, parser, resolve, compile, docs, examples, and manifest-backed proof together where the final rule changes shipped behavior.
- Retire or rewrite the new docs, examples, and proof that currently encode the duplicate-heading story.
- Preserve explicit-title long forms.

## 0.3 Out of scope

- Changing top-level declaration titles such as `input Foo: "Title"` or `workflow Foo: "Title"`.
- Keeping both "reuse child title" and "lower wrapper" semantics on the same authored surface.
- Adding humanized-key, guessed-title, or renderer-only dedupe fallback magic.
- Changing keyed identity, inheritance accounting, or addressable-path semantics.
- Blindly forcing every existing omitted-title surface into lowering when the current behavior is clearly a different semantic contract, such as inherited override titles that intentionally keep parent identity.
- Shipping a compatibility bridge for a feature that is still cleanly fixable before release.

## 0.4 Definition of done (acceptance evidence)

- No approved omitted-title surface emits duplicate wrapper and child headings with the same text.
- The final shipped omitted-title matrix is documented clearly enough that authors can predict whether omission means lower, inherit, or fail loud.
- Explicit-title forms keep current rendered output.
- Updated manifest-backed examples prove the new one-heading behavior on approved surfaces and fail loud where omission is still invalid.
- Existing list-lowering proof and any intentionally unchanged inherited-title proof still pass.
- `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, `examples/README.md`, `docs/VERSIONING.md`, and `CHANGELOG.md` match the final rule.
- Relevant repo verification runs pass cleanly.

## 0.5 Key invariants (fix immediately if violated)

- No duplicate headings from omitted-title shorthand.
- One omitted-title meaning per surface family.
- Explicit titles stay supported.
- Keys stay structural, not fallback display labels.
- No runtime shims, no dual paths, and no silent guessing.
- Prefer clean cutover before public release over preserving an obviously wrong unreleased behavior.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Remove the duplicate-heading behavior and replace it with the intended one-heading result.
2. Choose the broadest elegant and canonical surface rule, not an ad hoc `inputs` / `outputs` patch.
3. Preserve current explicit-title authoring and structural key behavior.
4. Keep emitted Markdown, examples, docs, and diagnostics aligned.

## 1.2 Constraints

- The repo now has three omitted-title stories in play: inherited overrides keep parent titles, titleless lists lower into the parent, and new base IO wrappers reuse a child title.
- Emitted Markdown, checked-in examples, and diagnostics are part of the shipped public surface.
- The current duplicate-heading behavior is already encoded in the dirty worktree docs and example proof, so a clean cutover has to update those surfaces together.

## 1.3 Architectural principles (rules we will enforce)

- Omitted title should mean "do not author another heading here," not "copy an existing heading unless proven otherwise."
- Fix the behavior at the canonical owner path, not with renderer-only dedupe.
- Widen the new lowering rule only where the same readable contract really holds.
- Fail loud where omission still has no coherent lowering story.

## 1.4 Known tradeoffs (explicit)

- A broader consistency sweep is more elegant, but it touches more owner paths and proof.
- A narrow IO-only cutover would ship faster, but it risks leaving the same semantic confusion on nearby surfaces.
- Lowering at the compiler-owner layer is cleaner than post-render dedupe, but it may require deeper refactors to keep bindings and section ownership truthful.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already has two distinct omitted-title meanings that make sense: inherited overrides keep the inherited title, and titleless lists lower into the parent. The new base IO wrapper feature introduced a third story: omit the wrapper title, reuse the one child declaration title, and still render the child declaration as its own titled section.

## 2.2 What’s broken / missing (concrete)

That new IO rule solves authored repetition but not emitted repetition. Real builds now show `### Foo` followed by `#### Foo`. This is exactly the outcome the author did not want, and it shows that the feature encoded the wrong semantic model.

## 2.3 Constraints implied by the problem

- The fix must define one-heading behavior, not just hide a duplicate in one renderer.
- The final rule must explain how omitted-title lowering differs from inherited-title reuse.
- The consistency sweep must be honest about where lowering is natural and where it is not.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- none — reject external prior-art hunting for now — this is a local language
  and emit-contract correction grounded in Doctrine's compiler and corpus

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` — base `io_section` now allows
    `string?`, readable `sequence` / `bullets` / `checklist` allow optional
    titles, inherited override forms allow optional titles, and most other
    base section-like forms still require explicit titles.
  - `doctrine/_parser/io.py` — base IO wrappers parse to `IoSection` with
    `title: str | None`, while IO overrides parse to `OverrideIoSection` with
    the same optional-title shape.
  - `doctrine/_compiler/resolve/outputs.py` — current base IO omission calls
    `_resolve_io_section_title(...)` and returns
    `resolved_bucket.sole_direct_title`, which creates the duplicate heading
    when the direct declaration also renders its own title.
  - `doctrine/_compiler/resolve/io_contracts.py` — direct IO bucket refs
    compile to titled child declaration sections and populate
    `direct_artifacts` plus `sole_direct_title`.
  - `doctrine/_compiler/compile/outputs.py` — input and output declarations
    always compile to titled `CompiledSection` objects, so a wrapper that
    copies the same title will nest two equal headings.
  - `doctrine/_compiler/compile/agent.py` — resolved IO bodies render by
    appending each resolved IO item section under the enclosing `Inputs` or
    `Outputs` section.
  - `doctrine/_compiler/compile/readable_blocks.py` and
    `doctrine/_renderer/blocks.py` — titleless readable lists already carry
    `title=None` and render list items directly with no nested heading, which
    is the closest shipped lowering pattern.
- Canonical path / owner to reuse:
  - first-class IO lowering should be owned before rendering, along
    `IoSection` -> `_resolve_contract_bucket_items(...)` ->
    `_resolve_io_section_item(...)` -> `ResolvedIoBody`, not by renderer-only
    dedupe.
  - the list-lowering pattern proves `title=None` is a valid compiled concept
    for list blocks, but `CompiledSection.title` is currently required, so IO
    lowering likely needs a distinct resolved representation or section-body
    splicing instead of simply making all sections title-optional.
- Adjacent surfaces tied to the same contract family:
  - `sequence`, `bullets`, and `checklist` already lower when their title is
    omitted; keep this as the canonical lower-into-parent precedent.
  - inherited overrides across workflow, skills, analysis, IO, review,
    readable blocks, and output schema keep inherited titles when no new title
    is written; this is a separate inherited-identity contract, not the same
    as base wrapper lowering.
  - `output schema field` / `def` titles lower into JSON Schema metadata, so
    base omission there is not a natural readable-heading lowering surface.
  - generic `RecordSection`, output record sections, guarded output sections,
    workflow sections, skills sections, analysis sections, and readable
    `section` still require explicit titles on base declarations; deep dive
    must decide whether any have a true single-child lowering source or should
    remain explicit.
  - `examples/117_io_omitted_wrapper_titles`, `docs/LANGUAGE_REFERENCE.md`,
    `docs/EMIT_GUIDE.md`, `examples/README.md`, `docs/VERSIONING.md`, and
    `CHANGELOG.md` currently encode the wrong child-title-reuse story and must
    be rewritten if the code changes.
- Compatibility posture (separate from `fallback_policy`):
  - clean cutover — the wrong duplicate-heading behavior exists in the dirty
    local worktree after `v1.0.2`, with language version `1.1` still
    unreleased, so preserve explicit-title behavior but replace the new
    omitted-title behavior before public release.
- Existing patterns to reuse:
  - titleless readable lists — omit the title, keep the key for structure,
    and render content directly in the parent.
  - inherited override title reuse — omit the override title only to keep the
    inherited title on the same inherited item identity.
  - fail-loud IO ambiguity — current omitted IO wrappers already reject
    multiple direct refs and keyed child sections; keep that boundary unless
    the deep dive finds a stronger lowering contract.
- Prompt surfaces / agent contract to reuse:
  - not applicable — this is compiler and emitted Markdown behavior, not an
    agent prompt behavior.
- Native model or agent capabilities to lean on:
  - not applicable.
- Existing grounding / tool / file exposure:
  - manifest-backed examples and emitted Markdown refs already prove the
    affected authoring and render surfaces.
- Duplicate or drifting paths relevant to this change:
  - `ResolvedContractBucket.sole_direct_title` exists only to support the
    current child-title-reuse rule and may become dead or change shape if
    lowering replaces title inference.
  - public docs and `examples/117_io_omitted_wrapper_titles` currently prove
    the wrong duplicate-heading output, so they must move with the code.
- Capability-first opportunities before new tooling:
  - not applicable — no new tooling is needed.
- Behavior-preservation signals already available:
  - `examples/117_io_omitted_wrapper_titles/cases.toml` — must be rewritten to
    prove one-heading lowering and retained fail-loud ambiguity.
  - `examples/113_titleless_readable_lists/cases.toml` — protects existing
    list lowering.
  - `examples/23_first_class_io_blocks/cases.toml`,
    `examples/24_io_block_inheritance/cases.toml`, and
    `examples/27_addressable_record_paths/cases.toml` — protect explicit IO,
    inherited IO, and addressable record-path behavior.
  - `make verify-examples` and `make verify-diagnostics` — final repo proof.

## 3.3 Decision gaps that must be resolved before implementation

- none that require user input — repo evidence and the confirmed North Star
  are enough to continue. Deep dive must still produce the exact surface
  matrix and canonical owner path before `phase-plan`.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Base first-class IO wrappers:
  - `doctrine/grammars/doctrine.lark` now parses `io_section` as
    `CNAME ":" string? ...`.
  - `doctrine/_parser/io.py` lowers base IO wrappers to `IoSection` with
    `title: str | None`.
  - `doctrine/_model/io.py` keeps `IoSection` local to first-class `inputs` /
    `outputs`; generic `RecordSection` still requires `title: str`.
- IO resolution:
  - `doctrine/_compiler/resolve/io_contracts.py` compiles direct declaration
    refs into titled `CompiledSection` values and stores
    `direct_artifacts`, `sole_direct_title`, and `has_keyed_children` in
    `ResolvedContractBucket`.
  - `doctrine/_compiler/resolve/outputs.py` turns each base `IoSection` into a
    `ResolvedIoSection` with a required titled `CompiledSection`.
  - `doctrine/_compiler/resolved_types.py` requires `CompiledSection.title` and
    stores IO wrapper output as `ResolvedIoSection(key, section, artifacts,
    bindings)`.
- Existing lowering precedent:
  - `sequence`, `bullets`, and `checklist` already use `title: str | None`.
  - `doctrine/_renderer/blocks.py` renders list blocks with `title=None`
    directly in the parent, with no heading.
- Existing inherited-title reuse:
  - Workflow, skills, analysis, IO, output-schema, review, and readable-block
    override paths accept omitted titles and keep the inherited parent title or
    kind-specific inherited display.
- Surfaces that still require base titles:
  - Generic record sections, output record sections, guarded output sections,
    workflow sections, skills sections, analysis sections, schema items,
    output schema fields/defs, and most readable block kinds still require
    explicit base titles.

## 4.2 Control paths (runtime)

Current duplicate-heading IO path:

1. The author writes a base IO wrapper without a title:
   `issue_ledger:`.
2. The parser emits `IoSection(key="issue_ledger", title=None, items=...)`.
3. `_resolve_contract_bucket_items(...)` walks that wrapper body.
4. Direct declaration refs such as `LessonsIssueLedger` compile into their own
   titled child `CompiledSection(title="Lessons Issue Ledger", ...)`.
5. The bucket stores that child section in `body` and also records
   `sole_direct_title="Lessons Issue Ledger"`.
6. `_resolve_io_section_title(...)` returns the same child title for the outer
   wrapper.
7. `_resolve_io_section_item(...)` emits an outer
   `CompiledSection(title="Lessons Issue Ledger", body=(..., child_section))`.
8. `_compile_resolved_io_body(...)` appends that outer section under `Inputs`
   or `Outputs`.
9. The Markdown renderer emits the outer heading and then the nested child
   heading, producing `### Foo` followed by `#### Foo`.

Current explicit-title IO path:

1. The author writes `issue_ledger: "Issue Ledger Packet"`.
2. The resolver keeps the authored wrapper title.
3. The direct child declaration still renders as its own nested titled section.
4. This is intentional because the author explicitly asked for a wrapper
   heading.

Current inherited override path:

1. The author writes `override issue_ledger:`.
2. The resolver keeps the inherited wrapper title.
3. This is an inherited identity rule, not a base wrapper lowering rule.

## 4.3 Object model + key abstractions

- `IoSection.title: str | None` represents the new base IO omitted-title
  syntax.
- `ResolvedContractBucket.body` is the emitted body for an IO wrapper; today it
  already includes the direct child `CompiledSection`.
- `ResolvedContractBucket.sole_direct_title` exists only to copy a child title
  onto a wrapper. It is the drift-prone abstraction behind the duplicate
  heading.
- `ResolvedIoSection.key` is still needed for bindings and inherited
  accounting.
- `ContractBinding(binding_path=(key,), artifact=...)` is the mechanism that
  binds a wrapper local key to a single direct `input` or `output`
  declaration.
- `ContractSectionSummary.title` is used by validation and inherited-summary
  logic. It can still use the direct declaration title for omitted IO wrappers
  without requiring emitted duplicate headings.

## 4.4 Observability + failure behavior today

- `examples/117_io_omitted_wrapper_titles` currently proves the wrong
  duplicate-heading output.
- Real downstream emitted Markdown shows the same pattern:
  `### Rally Workspace Dir` followed by `#### Rally Workspace Dir`.
- Omitted IO wrappers already fail loud when there are multiple direct refs or
  keyed child sections.
- Existing titleless list examples prove that lowering with no heading is
  already valid in the renderer.
- No runtime telemetry applies; this is compile/render behavior.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep base first-class `inputs` / `outputs` title omission on `io_section`.
- Replace the `sole_direct_title` title-copy rule with a single-child lowering
  rule in the IO resolver path.
- Keep the existing titleless readable list lowering rule unchanged.
- Keep inherited override omitted-title behavior unchanged.
- Do not add optional base titles to generic record sections, workflow
  sections, skills sections, analysis sections, output schema fields/defs, or
  other readable block kinds in this change.
- Rewrite docs and examples that currently describe or prove child-title reuse.

## 5.2 Control paths (future)

Future omitted-title IO wrapper path:

1. Parse omitted base IO wrappers into `IoSection(title=None)` as today.
2. Resolve the wrapper body through `_resolve_contract_bucket_items(...)`.
3. Allow lowering only when the wrapper has exactly one direct declaration ref
   and no keyed child sections.
4. Preserve the existing fail-loud behavior for multiple direct refs, no direct
   refs, scalar keyed items, or keyed child sections.
5. Build one visible section using the direct child declaration title.
6. Replace the direct child `CompiledSection` in the wrapper body with that
   child section's body, preserving authored order around it.
7. Keep wrapper-authored prose before or after the ref in the same relative
   order, now under the one child-owned heading.
8. Preserve the wrapper local key and binding path.

Example target render:

```md
## Your Inputs

### Lessons Issue Ledger

Use this ledger to track repeated section issues.

- Source: File
- Path: `catalog/lessons_issue_ledger.json`
- Shape: JSON Document
- Requirement: Required
```

Future explicit-title IO wrapper path:

1. If the wrapper has an explicit title, keep current wrapper rendering.
2. Direct child declarations remain nested under that explicit wrapper.
3. If an author explicitly repeats the child title, the duplication is
   authored, not caused by omitted-title shorthand.

Future inherited override path:

1. Omitted override titles continue to keep the inherited title.
2. This stays separate because the inherited keyed item already owns a visible
   identity.

## 5.3 Object model + abstractions (future)

- `ResolvedContractBucket` should expose enough information to flatten one
  direct child section without guessing:
  - direct artifacts
  - whether keyed children exist
  - the direct child `CompiledSection`
  - the body index or equivalent marker for that direct child section
- `ResolvedContractBucket.sole_direct_title` should be removed or replaced,
  because the owner path needs the child section and its body, not just its
  title.
- `ResolvedIoSection` can remain the emitted wrapper item as long as its
  `section` is the flattened one-heading section and its `key`, `artifacts`,
  and `bindings` still represent the wrapper local key.
- `CompiledSection.title` should stay required. Do not make all sections
  nullable to solve this one IO lowering problem.
- Validation summaries should mirror the same eligibility rule and keep using
  the direct declaration title for summary identity when an omitted IO wrapper
  is valid.

## 5.4 Invariants and boundaries

- No renderer-only duplicate suppression.
- No title copy without body flattening.
- No new optional base titles outside surfaces with a coherent lowering owner.
- No behavior change for explicit titles.
- No behavior change for titleless lists except docs may cite them as the
  existing lowering precedent.
- No behavior change for inherited override title reuse.
- Addressable keys and contract bindings must remain structural and stable.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | `io_section` | Base IO titles are already optional | Keep optional base IO title syntax; do not widen other base section grammars in this change | The syntax is correct; the emitted semantics are wrong | Same authored syntax, changed emitted lowering for omitted title | `examples/117_*`, full corpus |
| Parser / model | `doctrine/_parser/io.py`, `doctrine/_model/io.py` | `IoSection(title: str | None)` | Carries omitted base IO title into resolver | Keep this carrier; use `title=None` as the lowering signal | It already isolates the feature to first-class IO | No public API; internal meaning of `None` changes from title-copy to lowering | `examples/23_*`, `examples/117_*` |
| Contract bucket | `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/resolved_types.py` | `_resolve_contract_bucket_items`, `ResolvedContractBucket` | Stores direct child title but not enough body-position data to flatten safely | Replace or extend `sole_direct_title` with direct child section plus position metadata | Lowering needs to splice the child body, not copy its title | Internal resolved bucket carries a direct section/position signal | `examples/117_*`, `examples/27_*` |
| IO resolve | `doctrine/_compiler/resolve/outputs.py` | `_resolve_io_section_item`, `_resolve_io_section_title` | Builds a wrapper `CompiledSection` titled with the child title and leaves the child section inside its body | Replace title inference with omitted-title lowering helper; flatten one direct child section into the wrapper position | Produces one visible heading while preserving wrapper key and binding | Omitted base IO wrapper lowers only when one direct declaration ref exists and no keyed child sections exist | `examples/117_*`, `examples/24_*` |
| Validation summary | `doctrine/_compiler/validate/contracts.py` | `_summarize_contract_section` | Mirrors child-title inference for omitted IO wrapper summaries | Mirror the same eligibility rule; keep summary title as the direct declaration title for valid omitted wrappers | Validation and resolve must agree on fail-loud boundaries and inherited summaries | Same user-facing failure boundary; wording may update from "title source" to "single direct declaration" | `make verify-diagnostics`, `examples/117_*` |
| Agent compile | `doctrine/_compiler/compile/agent.py` | `_compile_resolved_io_body` | Appends each resolved IO item section under `Inputs` / `Outputs` | No direct change expected; it should receive one flattened section for omitted wrappers | Confirms the fix is resolver-owned, not renderer-owned | No API change | `make verify-examples` |
| Output declaration compile | `doctrine/_compiler/compile/outputs.py` | `_compile_input_decl`, `_compile_output_decl` | Direct declarations compile as titled child sections | No direct behavior change; resolver flattens the child section only when used through omitted wrapper shorthand | Direct refs and explicit wrappers must still render titled declarations | No API change | `examples/23_*`, `examples/117_*` |
| Renderer | `doctrine/_renderer/blocks.py` | `_render_titled_block`, `_render_body_lines` | Renders whatever titled section tree the compiler gives it | No renderer-only dedupe; leave renderer honest | Prevents hidden behavior and preserves non-IO section rendering | No API change | full corpus |
| Existing list lowering | `doctrine/_compiler/compile/readable_blocks.py`, `doctrine/_renderer/blocks.py` | titleless `sequence` / `bullets` / `checklist` | Already lowers into parent when title is omitted | Preserve unchanged; use as docs precedent | It is already the canonical lower-into-parent story | No API change | `examples/113_titleless_readable_lists` |
| Inherited overrides | workflow, skills, analysis, IO, review, output schema, readable-block resolve paths | omitted override titles | Keep inherited parent titles | Preserve unchanged | These are inherited identity updates, not base wrapper lowering | No API change | existing inheritance examples, `examples/24_*` |
| Other base section families | grammar / parser / compile paths for workflow, skills, analysis, schema, output schema, record, guarded output, readable sections | Most require explicit base titles; reviews have special untitled fallback headings | Keep current behavior unless a later plan targets them | They lack one direct child declaration heading and would broaden product behavior | No new syntax | full corpus |
| Focused proof | `examples/117_io_omitted_wrapper_titles` | render and compile-fail cases | Proves duplicate-heading child-title reuse | Rewrite to prove one-heading lowering, explicit-title preservation, wrapper-prose order, and fail-loud ambiguity | The current example encodes the wrong behavior | New expected emitted shape | focused manifest and full corpus |
| Public docs | `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, `examples/README.md` | omitted title docs | Describe child-title reuse and point to the old proof | Rewrite to describe lower / inherit / fail-loud matrix | Docs must match shipped truth | Public language docs changed | docs reviewed by corpus alignment |
| Release-facing docs | `docs/VERSIONING.md`, `CHANGELOG.md` | unreleased additive feature notes | Describe omitted IO wrapper titles as title reuse | Rewrite to describe omitted IO wrapper lowering; keep additive classification | This is still unreleased local work after `v1.0.2` | Clean pre-release cutover | release-flow only if release policy changes |

## 6.2 Migration notes

* Canonical owner path / shared code path:
  * `IoSection(title=None)` -> `_resolve_contract_bucket_items(...)` ->
    `_resolve_io_section_item(...)` -> flattened `ResolvedIoSection` ->
    `_compile_resolved_io_body(...)`.
* Deprecated APIs (if any):
  * None public.
  * Internal `ResolvedContractBucket.sole_direct_title` should be removed or
    replaced if the final implementation no longer needs it.
* Delete list:
  * Remove docs and expected-output wording that says omitted IO wrapper titles
    "reuse direct declaration titles."
  * Remove the current `examples/117_*` duplicate-heading expected lines.
* Adjacent surfaces tied to the same contract family:
  * Include: base first-class IO omitted-title wrappers and the focused proof.
  * Preserve: titleless readable list lowering.
  * Preserve: inherited override omitted-title reuse.
  * Exclude: base generic section families with no single direct declaration
    child heading.
  * Exclude: output schema field/def title omission.
* Compatibility posture / cutover plan:
  * Clean cutover before public release. Explicit-title authoring stays
    backward compatible; the wrong unreleased omitted-title render changes.
* Capability-replacing harnesses to delete or justify:
  * None.
* Live docs/comments/instructions to update or delete:
  * `docs/LANGUAGE_REFERENCE.md`
  * `docs/EMIT_GUIDE.md`
  * `examples/README.md`
  * `docs/VERSIONING.md`
  * `CHANGELOG.md`
  * Any code comments introduced for `sole_direct_title` if the field is
    removed or replaced.
* Behavior-preservation signals for refactors:
  * Focused manifest: `examples/117_io_omitted_wrapper_titles/cases.toml`.
  * Guards: `examples/23_first_class_io_blocks/cases.toml`,
    `examples/24_io_block_inheritance/cases.toml`,
    `examples/27_addressable_record_paths/cases.toml`,
    `examples/113_titleless_readable_lists/cases.toml`.
  * Full proof: `make verify-examples` and `make verify-diagnostics`.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Base first-class IO wrappers | `io_section`, `IoSection`, `_resolve_io_section_item` | Omitted title lowers one direct child declaration section into the wrapper position | Fixes the duplicate-heading bug at the canonical owner path | include |
| Titleless readable lists | `sequence`, `bullets`, `checklist` | Existing titleless lower-into-parent behavior | Keeps the established lowering precedent stable | include as preservation |
| Inherited overrides | workflow, skills, analysis, IO, review, readable blocks, output schema | Omitted override title keeps inherited title | Prevents false uniformity across inherited identity patches | include as preservation |
| Base generic sections | `RecordSection`, workflow sections, skills sections, analysis sections, readable `section` | Keep explicit title requirement | These do not have a single direct child declaration heading to lower into | exclude |
| Output schema titles | `output_schema_field`, `output_schema_def` | Keep explicit JSON Schema metadata titles | Their titles are structured schema metadata, not wrapper headings | exclude |
| Review untitled sections | review section and outcome fallback paths | Keep existing key/default fallback heading behavior | This is case/control rendering, not single-child wrapper lowering | exclude |
| Renderer dedupe | `_renderer/blocks.py` | No renderer-only duplicate suppression | Avoids hiding bad compiler tree shape and breaking legitimate repeated headings | exclude |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->
> Rule: Build the canonical owner path first, then prove behavior, then update public truth. `Work` explains the unit. `Checklist (must all be done)` is the required work. `Exit criteria (all required)` is the concrete done state the audit must validate. No fallback paths, renderer dedupe, or compatibility bridge are allowed.

## Phase 1 - Replace title-copy bucket data with flattening data

Status: COMPLETE

Completed work:

- Replaced `ResolvedContractBucket.sole_direct_title` with direct child section
  and body-position data.
- Updated IO bucket resolution to record direct child sections without changing
  wrapper keys, direct artifacts, keyed-child tracking, or bindings.

Tests run:

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/23_first_class_io_blocks/cases.toml` - PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/27_addressable_record_paths/cases.toml` - PASS.

* Goal:
  Prepare the resolver to lower a single direct child section without guessing or copying only a title.

* Work:
  This phase changes the internal resolved bucket shape. It should keep existing behavior until Phase 2 uses the new data.

* Checklist (must all be done):
  - Update `doctrine/_compiler/resolved_types.py` so `ResolvedContractBucket` can identify the one direct child `CompiledSection` and its position in `body`.
  - Update `doctrine/_compiler/resolve/io_contracts.py` so direct declaration refs record enough data for safe body splicing.
  - Replace `sole_direct_title` title-copy use with direct child section data.
  - Remove `sole_direct_title` and use direct child section data for resolver and validator summary needs.
  - Keep `direct_artifacts`, `has_keyed_children`, wrapper keys, and `ContractBinding(binding_path=(key,), ...)` behavior intact.

* Verification (required proof):
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/23_first_class_io_blocks/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/27_addressable_record_paths/cases.toml`.
  - Use `rg -n "sole_direct_title"` during implementation only to find remaining internal call sites, not as final proof.

* Docs/comments (propagation; only if needed):
  - No public docs change in this phase.
  - Remove stale internal comments that describe title reuse.

* Exit criteria (all required):
  - The bucket exposes direct child section data and body position data needed for lowering.
  - No live internal field or comment says the omitted wrapper should copy a child title.
  - Existing binding and artifact data still flow through the bucket.

* Rollback:
  Revert the bucket-shape change and restore the prior resolver fields before Phase 2 depends on them.

## Phase 2 - Implement IO lowering and focused proof

Status: COMPLETE

Completed work:

- Implemented resolver-owned flattening for omitted base IO wrapper titles.
- Updated validation to use the same lowerable-direct-declaration rule.
- Rewrote `examples/117_io_omitted_wrapper_titles` to prove one-heading
  omitted lowering, explicit long-form nesting, and fail-loud ambiguity.

Tests run:

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/117_io_omitted_wrapper_titles/cases.toml` - PASS.
- `make verify-diagnostics` - PASS.

* Goal:
  Replace duplicate-heading IO output with one visible child-owned heading and prove it in the focused example.

* Work:
  This phase changes behavior at `_resolve_io_section_item(...)`, mirrors the rule in validation, and rewrites `examples/117_io_omitted_wrapper_titles` to prove the new contract.

* Checklist (must all be done):
  - Update `doctrine/_compiler/resolve/outputs.py` so `IoSection(title=None)` lowers exactly one direct child declaration section into the wrapper position.
  - Preserve authored prose before and after the direct ref in the same order under the one visible heading.
  - Preserve explicit-title IO wrappers as nested wrapper plus child declaration output.
  - Preserve omitted override title behavior as inherited-title reuse.
  - Preserve fail-loud behavior for omitted base IO wrappers with zero direct refs, multiple direct refs, keyed children, or scalar keyed items.
  - Update error wording from "title source" to one lowerable direct declaration.
  - Update `doctrine/_compiler/validate/contracts.py` so validation summaries mirror the same eligibility rule and summary title.
  - Leave `doctrine/_renderer/blocks.py` honest; do not add renderer-only duplicate suppression.
  - Leave `CompiledSection.title` required; do not make all sections nullable for this feature.
  - Rewrite `examples/117_io_omitted_wrapper_titles/cases.toml` so the main omitted-title render case expects one heading, not duplicate headings.
  - Rename or reword the focused case names so they say "lower" or "one heading", not "reuse direct declaration titles".
  - Update `examples/117_io_omitted_wrapper_titles/prompts/AGENTS.prompt` role text to describe lowering.
  - Update `examples/117_io_omitted_wrapper_titles/prompts/EXPLICIT.prompt` so explicit-title output is documented as the long form, not as the same render as omitted-title output.
  - Keep compile-fail cases for multiple direct refs and keyed children.
  - Update compile-fail expected messages to match the new "one lowerable direct declaration" wording.
  - Add wrapper-authored prose after the direct ref in the focused omitted-title prompt and expected output so order is proven on both sides of the ref.

* Verification (required proof):
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/117_io_omitted_wrapper_titles/cases.toml`.
  - Run `make verify-diagnostics`.

* Docs/comments (propagation; only if needed):
  - Resolver comments, when present, must describe lowering rather than title copying.
  - Example prose and role text must match the new lowering rule.

* Exit criteria (all required):
  - A valid omitted base IO wrapper emits one visible heading, using the direct child declaration title.
  - The direct child declaration body is flattened into that heading instead of rendering as a nested duplicate heading.
  - Explicit wrapper titles still render the wrapper heading and nested child heading.
  - Inherited omitted-title overrides still keep inherited titles.
  - Invalid omitted base IO wrapper shapes still fail loud.
  - The renderer has no special duplicate-heading dedupe logic.
  - `examples/117_io_omitted_wrapper_titles` proves one-heading omitted IO lowering.
  - `examples/117_io_omitted_wrapper_titles` proves explicit titles still keep a wrapper heading.
  - Invalid omitted base IO wrapper shapes still have manifest-backed compile-fail proof.

* Rollback:
  Revert resolver, validation, and focused example changes together so compile behavior and proof do not disagree.

## Phase 3 - Prove adjacent surfaces stayed stable

Status: COMPLETE

Completed work:

- Preserved explicit IO, inherited IO, addressable record paths, and titleless
  readable list behavior.
- Left guard prompts unchanged outside the focused `117` proof.

Tests run:

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/23_first_class_io_blocks/cases.toml` - PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/24_io_block_inheritance/cases.toml` - PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/27_addressable_record_paths/cases.toml` - PASS.
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/113_titleless_readable_lists/cases.toml` - PASS.

* Goal:
  Prove the lowering change did not drift explicit IO, inherited IO, addressable paths, or existing titleless list behavior.

* Work:
  This phase is a preservation sweep over adjacent surfaces named in the call-site audit. It should not add new language syntax or change prompts outside the intended focused proof.

* Checklist (must all be done):
  - Keep `examples/113_titleless_readable_lists` prompts unchanged and use its manifest only as a preservation guard.
  - Keep `examples/23_first_class_io_blocks` prompts unchanged and use its manifest as explicit IO preservation proof.
  - Keep `examples/24_io_block_inheritance` prompts unchanged and use its manifest as inherited IO preservation proof.
  - Keep `examples/27_addressable_record_paths` prompts unchanged and use its manifest as binding and path preservation proof.
  - Update expected refs in guard examples only for intentional render changes caused by the canonical lowering behavior.

* Verification (required proof):
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/23_first_class_io_blocks/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/24_io_block_inheritance/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/27_addressable_record_paths/cases.toml`.
  - Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/113_titleless_readable_lists/cases.toml`.

* Docs/comments (propagation; only if needed):
  - No public docs change in this phase.

* Exit criteria (all required):
  - Focused adjacent-surface manifests still pass or their expected refs are updated for intentional output changes only.
  - Guard prompts remain unchanged outside intentional expected-output updates.
  - Explicit IO, inherited IO, addressable bindings, and titleless list lowering remain on their documented behavior.

* Rollback:
  Revert guard expected-output changes with the behavior change. Do not change guard prompts to make regressions pass.

## Phase 4 - Update public docs, release notes, and full verification

Status: COMPLETE

Completed work:

- Updated language, emit, examples, versioning, and changelog docs to describe
  lower / inherit / fail-loud semantics.
- Removed scoped public wording that described omitted IO wrapper titles as
  child-title reuse.

Tests run:

- `uv sync` - PASS.
- `npm ci` - PASS.
- `make verify-examples` - PASS.
- `make verify-diagnostics` - PASS.

* Goal:
  Make shipped prose and release-facing truth match the final omitted-title matrix.

* Work:
  This phase updates docs after code and proof settle the exact rule.

* Checklist (must all be done):
  - Update `docs/LANGUAGE_REFERENCE.md` so omitted base IO wrapper titles are documented as lowering one direct declaration, not reusing a title.
  - Update `docs/LANGUAGE_REFERENCE.md` with the final matrix: base IO lowers, titleless lists lower, inherited overrides inherit, other base section families stay explicit or keep their existing special rule.
  - Update `docs/EMIT_GUIDE.md` to remove the "not list lowering" title-reuse story and replace it with the one-heading IO lowering story.
  - Update `examples/README.md` so example `117` describes lowering and fail-loud ambiguity.
  - Update `docs/VERSIONING.md` so the versioned surface says omitted first-class IO wrapper titles lower one direct declaration.
  - Update `CHANGELOG.md` so the unreleased entry says omitted IO wrapper titles lower one direct declaration and points to the focused proof.
  - Do not delete docs in this phase; no doc deletion is required for this cutover.
  - Keep release classification as additive because this plan treats the wrong duplicate-heading behavior as unreleased local work.

* Verification (required proof):
  - Run `uv sync`.
  - Run `npm ci`.
  - Run `make verify-examples`.
  - Run `make verify-diagnostics`.
  - Do not change package metadata or release helper output in this plan.

* Docs/comments (propagation; only if needed):
  - Public docs, examples index, versioning notes, and changelog must all use the same lower / inherit / fail-loud wording.
  - Remove live wording that says omitted IO wrapper titles reuse a direct declaration title.

* Exit criteria (all required):
  - Public docs and release notes no longer describe child-title reuse for omitted IO wrappers.
  - The docs clearly separate lowering, inherited title reuse, and fail-loud omission.
  - Full example verification passes.
  - Diagnostics verification passes or any inability to run it is recorded plainly.
  - No compatibility bridge or fallback path exists.

* Rollback:
  Revert docs and release-note updates with the behavior change. Do not keep public docs ahead of code.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- `examples/117_io_omitted_wrapper_titles/cases.toml` is the focused proof
  for one-heading omitted IO lowering and fail-loud ambiguity.
- `examples/23_first_class_io_blocks/cases.toml` protects explicit first-class
  IO behavior.
- `examples/24_io_block_inheritance/cases.toml` protects inherited IO title
  behavior.
- `examples/27_addressable_record_paths/cases.toml` protects addressable
  record paths and bindings.
- `examples/113_titleless_readable_lists/cases.toml` protects existing list
  lowering.

## 8.2 Integration tests (flows)

- `uv sync`
- `npm ci`
- `make verify-examples`
- `make verify-diagnostics`
- `make verify-package` is out of scope unless package metadata or release
  helper output changes outside the plan.

## 8.3 E2E / device tests (realistic)

Not applicable.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Prefer a clean pre-release cutover. If repo evidence later shows this behavior has already shipped publicly, the plan must say so explicitly and update the compatibility posture before implementation.

## 9.2 Telemetry changes

No runtime telemetry expected.

## 9.3 Operational runbook

If a surface cannot lower cleanly without breaking a stronger existing contract, fail loud or keep its current distinct meaning. Do not blur the rule for convenience.

# 10) Decision Log (append-only)

## 2026-04-15 - Start a replacement plan for omitted-title semantics

Context

The first omitted-title plan chose "reuse the child title on the wrapper" for base IO wrappers. Real emitted output now shows duplicate headings, which conflicts with the intended user-facing behavior.

Options

- Patch only the current IO renderer to hide matching duplicates.
- Replace the new omitted-title semantic model with lowering and audit where that broader rule should apply.
- Keep the current behavior and document the duplicate headings as intended.

Decision

Default to the replacement plan. The current duplicate-heading behavior is the wrong semantic model, and the clean answer is to redefine omitted-title behavior around lowering where that story is canonical.

Consequences

- The earlier omitted-title plan is now prior context, not the current North Star.
- Research must audit the full omitted-title matrix instead of assuming `inputs` / `outputs` are the only relevant surface.

Follow-ups

- Confirm this North Star before deeper planning.

## 2026-04-15 - Lock phase plan around resolver-owned IO lowering

Context

Research and deep dive found that only base first-class IO wrappers have the
single direct child declaration heading needed for this lowering rule. Existing
titleless lists already lower, and inherited overrides already reuse inherited
titles for a different reason.

Options

- Patch the renderer to hide duplicate headings.
- Make all sections title-optional.
- Lower only base first-class IO wrappers and preserve the other existing
  omitted-title stories.

Decision

Use resolver-owned lowering for omitted base first-class IO wrappers. Preserve
titleless list lowering. Preserve inherited override title reuse. Keep other
base section families explicit or on their current special rules.

Consequences

- Implementation must replace `sole_direct_title` title copying with direct
  child section flattening data.
- Public docs must explain the three outcomes: lower, inherit, or fail loud.
- No renderer-only dedupe or compatibility bridge is allowed.

## 2026-04-15 - Implement resolver-owned omitted IO lowering

Context

The focused `117` example proved the previous behavior emitted duplicate
headings when wrapper titles were omitted.

Decision

Replace title-copy data with direct child section position data and lower the
direct child body into the omitted wrapper's visible heading.

Consequences

- Omitted base IO wrappers now render one heading when they contain exactly one
  direct declaration and no keyed children.
- Explicit wrapper titles still render the long nested form.
- Public docs and release notes now describe lower, inherit, and fail-loud
  outcomes.
