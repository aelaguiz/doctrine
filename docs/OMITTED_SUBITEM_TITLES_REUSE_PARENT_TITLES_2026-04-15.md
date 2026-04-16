---
title: "Doctrine - Omitted Subitem Titles Reuse Parent Titles - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/LANGUAGE_REFERENCE.md
  - docs/EMIT_GUIDE.md
  - doctrine/grammars/doctrine.lark
  - doctrine/_parser/io.py
  - doctrine/_compiler/compile/records.py
  - examples/23_first_class_io_blocks
  - examples/24_io_block_inheritance
---

# TL;DR

Outcome
: Doctrine supports omitted quoted titles on first-class `inputs` / `outputs` wrapper sections when one clear human-facing declaration title already exists. Inherited override sections keep the parent title, and first-class IO wrapper sections around one direct titled declaration may reuse that declaration title.

Problem
: Today authors often have to repeat the same title in nested blocks. That adds noise and lets authored labels drift from the titled contract they wrap.

Approach
: Add the new omitted-title rule on first-class IO wrapper sections, reuse existing human-facing titles where they are unambiguous, and fail loud when they are not. Keep current list lowering behavior separate.

Plan
: Move first-class IO wrapper sections onto one owner path, add the omitted-title rule and fail-loud proof there, then align public docs and release-surface notes.

Non-negotiables
: No silent fallback maze. No second title system per surface. Existing explicit-title syntax stays valid. `sequence`, `bullets`, and `checklist` keep their current lower-into-parent behavior unless we approve a separate change.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
recommended_flow: research -> deep dive -> phase plan -> consistency pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-16
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.

## Evidence checked
- Phase 1 owner path is present: `IoSection` exists with `title: str | None`, `IoItem` uses it, `io_section` parses to it, and first-class IO resolve reads it through the dedicated path (`doctrine/_model/io.py:34`, `doctrine/_model/io.py:114`, `doctrine/_parser/io.py:739`, `doctrine/_compiler/resolve/outputs.py:1506`).
- Phase 2 omitted-title behavior is present: grammar allows optional base IO titles, resolver carries the sole direct title source, omitted titles fail loud on ambiguous buckets, and validation summaries infer the same title source (`doctrine/grammars/doctrine.lark:615`, `doctrine/_compiler/resolve/io_contracts.py:111`, `doctrine/_compiler/resolve/io_contracts.py:177`, `doctrine/_compiler/resolve/outputs.py:1552`, `doctrine/_compiler/validate/contracts.py:470`).
- Phase 2 preserved boundaries are intact: generic record/output wrappers, arbitrary-body sections, output schema titles, inherited overrides, and titleless list rules were not widened by this feature (`doctrine/grammars/doctrine.lark:671`, `doctrine/grammars/doctrine.lark:672`, `doctrine/_compiler/resolve/outputs.py:1476`, `doctrine/_compiler/compile/records.py:132`).
- Phase 3 proof and public truth are present: the focused example covers omitted-title success, explicit-title parity, and fail-loud cases, while docs, versioning, changelog, and the examples index describe the shipped rule and limits (`examples/117_io_omitted_wrapper_titles/cases.toml:5`, `examples/117_io_omitted_wrapper_titles/cases.toml:40`, `examples/117_io_omitted_wrapper_titles/cases.toml:76`, `docs/LANGUAGE_REFERENCE.md:609`, `docs/EMIT_GUIDE.md:421`, `docs/VERSIONING.md:87`, `CHANGELOG.md:40`, `examples/README.md:96`).
- No implementation-side narrowing was found. The audit checked all approved Section 7 phases in order, not just the final docs and proof work.
- Commands run during audit: `uv sync`, `npm ci`, `make verify-examples`, and `make verify-diagnostics`; all passed.
<!-- arch_skill:block:implementation_audit:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine should let authors omit the quoted title on approved first-class IO wrapper sections when one unambiguous human-facing title already exists nearby. In those cases, compile and render output should match the explicit-title form. If no single title source exists, Doctrine should fail loud instead of guessing.

## 0.2 In scope

- Add omitted-title support for first-class `inputs` / `outputs` wrapper sections when the section resolves one direct titled declaration.
- Make the rule consistent with the override surfaces that already treat omitted titles as "keep the parent title."
- Reuse referenced child titles on wrapper-section surfaces only when that source is unambiguous.
- Update parser, model, resolve, compile, docs, examples, and manifest-backed proof together.
- Preserve existing explicit-title syntax as the still-valid long form.
- Keep adjacent proof and docs surfaces in sync, including examples that show first-class `inputs` / `outputs` blocks and inherited patching.

## 0.3 Out of scope

- Changing top-level declaration titles such as `input Foo: "Title"` or `workflow Foo: "Title"`.
- Making arbitrary-body workflow, skills, analysis, or general readable `section` families title-optional when they do not have one clear title source.
- Changing the current titleless list rule for `sequence`, `bullets`, or `checklist`.
- Extending the first cut to `output schema field` or `output schema def`, whose `title` lowers into structured schema JSON rather than ordinary wrapper headings.
- Adding humanized-key fallback magic to stand in for a missing real title source on new section-like shorthand.
- Changing patch keys, addressable paths, or output routing semantics.
- Adding runtime shims, compatibility bridges, or dual syntax modes.

## 0.4 Definition of done (acceptance evidence)

- New manifest-backed examples show omitted-title and explicit-title forms rendering the same on approved surfaces.
- New compile-fail cases prove Doctrine rejects omitted-title forms when no unambiguous visible title source exists.
- Existing explicit-title examples still pass unchanged.
- Existing titleless list examples still pass unchanged.
- `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, and `examples/README.md` explain the new rule and its limits in plain language.
- `docs/VERSIONING.md` and `CHANGELOG.md` reflect the additive public language change.
- Relevant repo verification runs for the touched surfaces and completes cleanly.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks or runtime shims.
- Explicit titles stay supported and keep current behavior.
- Keys stay structural. Titles stay human-facing.
- Omitted-title shorthand works only when there is one clear title source.
- List lowering stays its own rule and does not get mixed into this feature.
- One shared rule should explain the feature. Surface-specific one-off behavior should be avoided.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make omitted-title behavior predictable across first-class IO wrapper sections and consistent with existing inherited overrides.
2. Preserve current behavior for all existing explicit-title authoring.
3. Fail loud on ambiguity instead of guessing.
4. Keep docs, examples, and diagnostics aligned with shipped truth.

## 1.2 Constraints

- The shipped truth lives in `doctrine/`, not in design notes alone.
- Grammar, parser, resolve, and compile behavior all have to agree.
- The corpus already proves titleless list lowering and inherited-title override behavior. This change must not blur those two stories.
- The repo expects manifest-backed examples, not docs-only claims.

## 1.3 Architectural principles (rules we will enforce)

- Prefer one shared title-resolution rule over per-surface special cases.
- Reuse the strongest existing titled surface instead of duplicating the same human label in authored syntax.
- Keep fail-loud boundaries when a title source is missing or ambiguous.
- Preserve the canonical owner path for title resolution instead of re-implementing it in each emitter.

## 1.4 Known tradeoffs (explicit)

- A broader surface sweep gives a cleaner language rule, but it touches more grammar and proof.
- A narrow first cut would ship faster, but it would leave more odd exceptions and more docs burden.
- Reusing referenced child titles is more natural for authors than humanizing keys, but only when the source is truly unambiguous.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Most section-like subitems still require an explicit quoted title. Some override surfaces already let authors omit a title and keep the inherited parent title. `sequence`, `bullets`, and `checklist` already have a different special rule where omitting the title lowers the list into the parent section.

## 2.2 What’s broken / missing (concrete)

Authors have to repeat titles that already exist on the wrapped contract or inherited parent. That adds noise and creates drift risk. It also makes the language feel inconsistent because a few surfaces already allow title omission, but many natural sibling surfaces do not.

## 2.3 Constraints implied by the problem

- The new rule has to be simple enough to explain in docs.
- It has to avoid guessing when multiple candidate titles exist.
- It has to preserve current emitted output for the long form.
- It has to name which surfaces are intentionally included now and which are not.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- none — reject external prior-art hunting for now — this is a local language consistency change grounded in shipped Doctrine behavior

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` — `io_section` and `output schema field/def` still require explicit `string`, while override sections across workflow, skills, analysis, IO, readable blocks, and output schema already allow `string?`
  - `doctrine/_parser/io.py` — `io_section` always builds `RecordSection` with an explicit title, `io_override_section` already stores `title: None`, and output/record keyed items with non-string heads still lower through `RecordScalar`
  - `doctrine/_compiler/resolve/outputs.py` — IO override sections already reuse `parent_item.section.title`, and `_resolve_io_section_item` is the compiled wrapper-section owner for first-class `inputs` / `outputs`
  - `doctrine/_compiler/resolve/io_contracts.py` — `_resolve_contract_bucket_ref_entry` already resolves direct declaration refs to titled compiled sections and artifacts, and `ResolvedContractBucket.direct_artifacts` plus `has_keyed_children` gives the natural signal for "one direct titled declaration"
  - `doctrine/_compiler/compile/records.py` — direct `RecordRef` entries already render with `_display_ref(...)`, while ref-backed keyed scalars with bodies still fall through `_compile_fallback_scalar` and humanize the key
  - `doctrine/_compiler/resolve/refs.py` — `_display_ref` is the shared human-facing declaration title display path
- Canonical path / owner to reuse:
  - `doctrine/_parser/io.py` + `doctrine/_compiler/resolve/io_contracts.py` + `doctrine/_compiler/resolve/outputs.py` + `doctrine/_compiler/compile/records.py` — these own wrapper-section parsing, artifact binding, and visible title rendering for the user’s `inputs` / `outputs` example class
- Adjacent surfaces tied to the same contract family:
  - `doctrine/_parser/workflows.py`, `doctrine/_parser/skills.py`, `doctrine/_parser/analysis_decisions.py`, and matching resolve modules — existing omitted-title override behavior that should be documented as the same convention, not as unrelated one-off behavior
  - `doctrine/_compiler/resolve/output_schemas.py` — also reuses parent titles on override, but this `title` lowers into JSON Schema `title`, so it should stay out of this first cut
  - `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, and `examples/README.md` — public explanation surfaces that currently describe titleless lists clearly but do not explain the broader omitted-title convention
  - `examples/23_first_class_io_blocks`, `examples/24_io_block_inheritance`, `examples/27_addressable_record_paths`, and `examples/113_titleless_readable_lists` — immediate proof surfaces for wrapper sections, inherited titles, keyed record paths, and unchanged list lowering
- Compatibility posture (separate from `fallback_policy`):
  - preserve existing contract with additive syntax — explicit titles remain valid, and the first cut adds shorthand only where one visible title source already exists
- Existing patterns to reuse:
  - `doctrine/_compiler/resolve/workflows.py`, `doctrine/_compiler/resolve/addressable_skills.py`, `doctrine/_compiler/resolve/analysis.py`, `doctrine/_compiler/resolve/outputs.py`, and `doctrine/_compiler/resolve/output_schemas.py` — omitted override titles already mean "keep the inherited title"
  - `doctrine/_compiler/resolve/refs.py` — `_display_ref` already gives the right human-facing title for direct declaration refs
  - `doctrine/_compiler/resolve/io_contracts.py` — `direct_artifacts` and `has_keyed_children` already express when a wrapper section resolves to one direct declaration instead of a more complex bucket
- Prompt surfaces / agent contract to reuse:
  - not applicable — this feature is compiler and language only
- Native model or agent capabilities to lean on:
  - not applicable — this feature is compiler and language only
- Existing grounding / tool / file exposure:
  - the shipped corpus, grammar, parser, and docs already expose the affected syntax families directly
- Duplicate or drifting paths relevant to this change:
  - inherited omitted-title behavior is already duplicated across workflow, skills, analysis, IO, readable-block, and output-schema resolve paths, while wrapper sections still require repeated explicit titles
  - `_compile_fallback_scalar` currently humanizes keyed wrapper titles instead of reusing the referenced declaration title, which is the main drift point behind the user example
- Capability-first opportunities before new tooling:
  - not applicable — no new tooling is needed; this is a direct compiler-path change
- Behavior-preservation signals already available:
  - `examples/23_first_class_io_blocks/cases.toml` — current first-class `inputs` / `outputs` wrapper rendering
  - `examples/24_io_block_inheritance/cases.toml` — inherited IO title preservation
  - `examples/27_addressable_record_paths/cases.toml` — keyed record paths stay stable
  - `examples/113_titleless_readable_lists/cases.toml` — list lowering stays unchanged
  - `make verify-examples` and `make verify-diagnostics` when diagnostics move

## 3.3 Decision gaps that must be resolved before implementation

- none — repo evidence checked: grammar, parser, resolve, compile, docs, and adjacent examples — the approved first cut keeps inherited omitted-title override sections as the existing base convention, adds new omitted-title shorthand only on first-class IO wrapper sections that can prove one direct titled declaration source, and keeps arbitrary-body section families plus `output schema field/def` out of scope
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Grammar surfaces split into three relevant families:
  - first-class IO wrapper sections:
    - `doctrine/grammars/doctrine.lark` `io_section` still requires `CNAME ":" string`
    - `io_override_section` already allows `string?`
  - arbitrary-body section families:
    - workflow local sections, skills sections, analysis sections, readable `section` blocks, review sections, and output guarded sections still rely on authored titles for their visible heading
  - structured-schema titles:
    - `output schema field` and `output schema def` carry titles that lower into JSON Schema metadata, not ordinary wrapper headings
- Parser ownership is split the same way:
  - `doctrine/_parser/io.py` lowers explicit IO sections to `RecordSection` and IO overrides to `OverrideIoSection`
  - generic record keyed items in `doctrine/_parser/io.py` and `doctrine/_parser/skills.py` only become `RecordSection` when there is an explicit string head; non-string keyed items remain `RecordScalar`
- Resolve and summary ownership for first-class IO lives in:
  - `doctrine/_compiler/validate/contracts.py`
  - `doctrine/_compiler/resolve/io_contracts.py`
  - `doctrine/_compiler/resolve/outputs.py`
- Public truth surfaces live in:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/EMIT_GUIDE.md`
  - `examples/README.md`
  - manifest-backed examples under `examples/`

## 4.2 Control paths (runtime)

Current explicit IO wrapper path:

1. `inputs` / `outputs` bodies parse `section_key: "Visible Title"` through `io_section`.
2. The parser lowers that to `RecordSection(key, title, items)`.
3. IO summarization and resolution treat the section as a contract bucket:
   - prose is compiled into body lines
   - direct declaration refs compile to titled child sections
   - nested keyed sections become keyed children
4. `_resolve_io_section_item` emits one `ResolvedIoSection` with the authored wrapper title plus the compiled child content.

Current inherited override path:

1. `override key:` in workflow, skills, analysis, IO, readable blocks, and output schema already parses with `title: None` when the author omits the title.
2. The matching resolve path reuses the inherited visible title instead of guessing.

Current non-IO fallback path:

1. Generic keyed record items without an explicit string head parse as `RecordScalar`.
2. `_compile_fallback_scalar` humanizes the key for the section label.
3. That path is not the same thing as a true wrapper section that reuses a child contract title.

## 4.3 Object model + key abstractions

- `RecordSection` currently assumes an explicit visible title.
- `OverrideIoSection` already models the existing “keep parent title” convention for inherited IO sections.
- `ResolvedContractBucket` already exposes the signals the first cut needs:
  - `body`
  - `direct_artifacts`
  - `has_keyed_children`
- `ResolvedIoSection.section.title` is the point where IO wrapper titles become concrete compiled headings.
- `_display_ref` in `doctrine/_compiler/resolve/refs.py` is the existing human-facing declaration-title display path.

## 4.4 Observability + failure behavior today

- Missing base-section titles fail at parse time on `io_section`.
- Scalar keyed items inside first-class IO buckets fail at compile time because IO buckets do not allow scalar keyed entries.
- Existing omitted-title behavior is real but fragmented:
  - inherited overrides keep parent titles
  - titleless lists lower into the parent
  - generic keyed record items humanize keys
- Public docs explain the list rule clearly but do not explain the broader override convention or the boundary between real wrapper sections and scalar fallback.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep the first cut local to first-class `inputs` / `outputs` wrapper sections.
- Add new base-syntax omission only to `io_section`.
- Keep generic `RecordSection`, generic keyed record items, workflow sections, skills sections, analysis sections, readable `section` blocks, review sections, and `output schema field/def` unchanged in this plan.
- Update public docs and proof to present one honest convention:
  - inherited overrides already reuse parent titles
  - first-class IO wrapper sections may now omit the title when one direct titled declaration supplies it
  - titleless lists still mean “lower into parent”

## 5.2 Control paths (future)

Future explicit IO wrapper path:

1. If the author writes an explicit title, keep current behavior unchanged.

Future omitted-title IO wrapper path:

1. `io_section` accepts the title as optional.
2. The parser stores an untitled IO wrapper instead of forcing the generic `RecordSection` path.
3. IO summary and resolve run the same contract-bucket logic as today.
4. The resolve layer infers the visible wrapper title only when:
   - the wrapper resolves exactly one direct declaration artifact
   - there are no keyed child sections competing for section ownership
5. The inferred visible title comes from the same declaration-title display path used for direct refs.
6. The compiled heading shape matches the explicit-title form.

Future fail-loud path:

1. If an omitted IO wrapper title does not have exactly one direct titled declaration source, compile fails loudly.
2. The fix is explicit authoring, not key humanization or silent fallback.

## 5.3 Object model + abstractions (future)

- Introduce a dedicated IO-section carrier with `title: str | None` so this feature stays local to first-class IO instead of weakening generic `RecordSection`.
- Route both explicit and omitted IO wrapper sections through one shared resolver helper.
- Extend the resolved contract-bucket output to carry the one direct rendered declaration title needed for wrapper-title inference.
- Keep generic record compile behavior unchanged for this first cut.

## 5.4 Invariants and boundaries

- No title inference outside first-class IO wrapper sections in this plan.
- No humanized-key fallback when an omitted IO wrapper title lacks a single clear source.
- Existing explicit-title syntax stays the long form everywhere.
- Inherited overrides continue to mean “keep the parent title.”
- Titleless lists continue to mean “lower into the parent.”
- `output schema field/def` stays out of scope because its title lowers into schema JSON metadata, not wrapper headings.
- No parallel title-inference systems by surface.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | `io_section` | Requires explicit `string` title | Allow omitted title only on base IO wrapper sections | Add the new shorthand at the canonical wrapper-section syntax point | Additive `inputs` / `outputs` authored syntax | New compile/render corpus cases |
| Model | `doctrine/_model/io.py` | IO section item type and `IoItem` union | Base IO sections rely on `RecordSection(title: str)` | Add a dedicated IO-section carrier with optional title | Keep the feature local to first-class IO and avoid weakening generic record sections | Internal model-only change | Compile and validation paths that read `IoItem` |
| Parser | `doctrine/_parser/io.py` | `io_section` | Always lowers to titled `RecordSection` | Parse explicit and omitted IO titles into the new IO-section carrier | Preserve one parser path for base IO wrappers | Internal parse/model change | New parser-backed corpus proof |
| Validation summary | `doctrine/_compiler/validate/contracts.py` | contract-body summarization for IO items | Expects `RecordSection` or `OverrideIoSection`; fallback labels may use keys | Accept the new IO-section carrier and use resolved or inferred wrapper titles in diagnostics | Keep compile-time summaries aligned with the new authoring form | Internal compile contract only | Existing IO inheritance failures plus new omitted-title failures |
| Resolve bucket | `doctrine/_compiler/resolve/io_contracts.py` | `_resolve_contract_bucket_items` and `_resolve_contract_bucket_ref_entry` | Knows direct artifacts and keyed children, but does not expose a direct wrapper-title signal | Carry the sole direct rendered declaration title needed for inference | Let omitted-title IO wrappers reuse the same human-facing declaration title as direct refs | Internal resolved-bucket shape | New omitted-title render and compile-fail cases |
| Resolve IO section | `doctrine/_compiler/resolve/outputs.py` | `_resolve_io_section_item` | Emits wrapper headings from explicit authored title only | Infer wrapper title from the sole direct declaration title or fail loud | Make emitted wrapper headings deterministic and equivalent to the shorthand contract | Additive emitted-heading behavior | IO render-contract cases |
| Docs | `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, `examples/README.md`, `docs/VERSIONING.md`, `CHANGELOG.md` | public title rules, corpus map, and release-surface notes | Explain titleless lists, but not the broader omitted-title convention, and do not yet account for this additive language feature in release-facing notes | Document the first-cut matrix, the boundary between inherited-title reuse, IO wrapper inference, and list lowering, and the additive release classification for this public syntax change | Keep public docs and release-facing notes aligned with shipped truth | Public docs update | Checked indirectly via corpus alignment |
| Examples | `examples/23_first_class_io_blocks`, `examples/24_io_block_inheritance`, `examples/117_io_omitted_wrapper_titles` | IO wrapper proof | Current examples prove explicit titles and inherited overrides only | Add one focused example for omitted IO wrapper titles and fail-loud boundaries, and keep the older explicit-title examples readable | Preserve “one new idea per example” while showing the feature where it matters | New manifest-backed example set plus unchanged guards | `make verify-examples` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `io_section` parser path -> IO contract bucket resolution -> `_resolve_io_section_item` -> compiled IO wrapper heading
- Deprecated APIs (if any):
  - none
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - no code-path delete is planned
  - remove stale doc wording that implies title optionality only exists for titleless lists
- Adjacent surfaces tied to the same contract family:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/EMIT_GUIDE.md`
  - `examples/README.md`
  - `examples/23_first_class_io_blocks`
  - `examples/24_io_block_inheritance`
  - `examples/117_io_omitted_wrapper_titles`
  - `examples/113_titleless_readable_lists`
- Compatibility posture / cutover plan:
  - additive syntax; explicit titles remain valid; omitted-title IO wrappers are a new shorthand only
- Capability-replacing harnesses to delete or justify:
  - none
- Live docs/comments/instructions to update or delete:
  - public language docs that currently explain titleless lists without explaining inherited-title reuse
  - example index text that should mention the new omitted-title IO wrapper proof
  - `docs/VERSIONING.md` and `CHANGELOG.md` because this is an additive public language change
- Behavior-preservation signals for refactors:
  - existing explicit-title IO render cases in `examples/23_*` and `examples/24_*`
  - existing addressable record-path proof in `examples/27_*`
  - focused omitted-title success and fail-loud proof in `examples/117_io_omitted_wrapper_titles`
  - existing list-lowering proof in `examples/113_*`
  - `make verify-examples`
  - `make verify-diagnostics` if the new fail-loud path adds or changes diagnostics

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Existing convention docs | `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md` | Explain inherited omitted-title overrides as the base convention | Prevents docs drift between override behavior and new IO shorthand | include |
| First-class IO proof | `examples/23_first_class_io_blocks`, `examples/24_io_block_inheritance`, `examples/117_io_omitted_wrapper_titles` | Show explicit-title, inherited-title, and omitted-title IO wrapper behavior together | Keeps the contract family honest across examples | include |
| Generic record wrappers | `record_keyed_item`, `output_record_keyed_item`, `record_section_block`, `output_section_block` | Omitted-title wrapper inference outside first-class IO | These surfaces lack the same dedicated owner path and would widen scope materially | exclude |
| Arbitrary-body section families | workflow local sections, skills sections, analysis sections, readable `section` blocks, review sections | Optional base-section titles | These sections do not have one built-in direct declaration title source | exclude |
| Structured output schema | `output schema field`, `output schema def` | Optional base title with inherited or inferred schema title | Their `title` lowers into JSON Schema metadata, not wrapper headings | exclude |
| Existing inherited overrides | workflow, skills, analysis, IO, readable blocks, output schema override paths | Keep omitted override titles as “reuse parent title” | This is already shipped behavior and should stay the shared convention baseline | include |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Move first-class IO wrapper sections onto one owner path

Status: COMPLETE

* Goal: Put base `inputs` / `outputs` wrapper sections on one dedicated model and resolver path before the new shorthand widens syntax.
* Work: Replace the current dependence on generic `RecordSection` with a first-class IO-section carrier that already owns explicit-title behavior end to end. This phase is about ownership and preservation, not about shipping new syntax yet.
* Checklist (must all be done):
  - Add a dedicated IO-section carrier with `title: str | None` in the IO model surface and thread it through the `IoItem` union.
  - Update `doctrine/_parser/io.py` so explicit base IO wrapper sections lower to the new carrier instead of generic `RecordSection`.
  - Update `doctrine/_compiler/validate/contracts.py`, `doctrine/_compiler/resolve/io_contracts.py`, and `doctrine/_compiler/resolve/outputs.py` so explicit-title IO wrapper sections still compile through the new owner path with unchanged visible output.
  - Keep inherited override omission behavior unchanged.
  - Keep generic record/output wrapper paths, arbitrary-body section families, and list lowering unchanged.
* Verification (required proof):
  - Run focused manifest proof for the current explicit-title IO surfaces in `examples/23_first_class_io_blocks/cases.toml`, `examples/24_io_block_inheritance/cases.toml`, and `examples/27_addressable_record_paths/cases.toml`.
* Docs/comments (propagation; only if needed):
  - Add one short code comment at the canonical IO-section owner boundary only if the new carrier makes the title-preservation path hard to read.
* Exit criteria (all required):
  - Explicit-title first-class IO wrapper sections now run through one dedicated IO-section path.
  - Existing explicit-title IO wrapper output and addressable record-path proof stay unchanged.
  - No non-IO surface behavior changes in this phase.
* Rollback:
  - Revert the new IO-section carrier path and restore the current explicit-title `RecordSection` flow.

## Phase 2 — Add omitted-title IO wrapper inference and fail-loud boundaries

Status: COMPLETE

* Goal: Ship the new omitted-title shorthand for first-class IO wrapper sections only, with one clear title source rule and no fallback magic.
* Work: Widen `io_section` authoring so the title may be omitted, then infer the visible wrapper title only from one direct titled declaration on the same contract-bucket path. Unsupported shapes must fail loudly instead of humanizing keys or guessing.
* Checklist (must all be done):
  - Update `doctrine/grammars/doctrine.lark` so base `io_section` titles become optional.
  - Parse omitted-title base IO wrapper sections into the dedicated IO-section carrier.
  - Extend the resolved contract-bucket output so it carries the sole direct rendered declaration title needed for wrapper-title inference.
  - Update the IO resolve path so omitted-title wrapper sections reuse that one direct declaration title only when there are no competing keyed child sections.
  - Update the validation-summary path so diagnostics for omitted-title IO wrapper sections use the same resolved visible wrapper title as the render path.
  - Add a clear compile-fail path for omitted-title IO wrapper sections that do not resolve exactly one usable declaration title source.
  - Keep `_compile_fallback_scalar`, generic record/output wrapper behavior, arbitrary-body section families, inherited override semantics, `output schema field/def`, and titleless list lowering unchanged.
  - Add the focused manifest-backed proof in `examples/117_io_omitted_wrapper_titles` for explicit-title parity, omitted-title success, and omitted-title fail-loud cases.
* Verification (required proof):
  - Run the focused manifest-backed proof in `examples/117_io_omitted_wrapper_titles/cases.toml`, plus the adjacent unchanged guards for `examples/23_first_class_io_blocks/cases.toml`, `examples/24_io_block_inheritance/cases.toml`, `examples/27_addressable_record_paths/cases.toml`, and `examples/113_titleless_readable_lists/cases.toml`.
  - Run `make verify-diagnostics` so the new fail-loud path stays aligned with shipped diagnostics.
* Docs/comments (propagation; only if needed):
  - Keep public docs unchanged in this phase unless diagnostic wording or internal boundary comments must move with the new fail-loud rule.
* Exit criteria (all required):
  - Omitted-title first-class IO wrapper sections compile only when one direct visible declaration title exists.
  - Explicit-title and omitted-title approved forms render the same visible wrapper heading.
  - Validation summaries and fail-loud diagnostics use the same resolved visible wrapper title as the render path.
  - Unsupported omitted-title forms fail loudly.
  - Generic record/output wrappers, arbitrary-body sections, inherited overrides, `output schema field/def`, and titleless lists keep current behavior.
* Rollback:
  - Remove base IO title omission from the grammar and resolver while leaving the Phase 1 owner-path cleanup intact.

## Phase 3 — Align examples, docs, release notes, and full proof

Status: COMPLETE

* Goal: Make the shipped teaching surface, release-facing notes, and verifier-owned corpus all tell the same story about the new shorthand and its limits.
* Work: Finish the outward-facing alignment after the compiler behavior is stable. This phase is where the repo’s public truth catches up to the new shipped syntax and where final proof runs across the touched surfaces.
* Checklist (must all be done):
  - Update `docs/LANGUAGE_REFERENCE.md` to explain the first-cut omitted-title matrix in plain language.
  - Update `docs/EMIT_GUIDE.md` to explain how omitted-title IO wrapper sections render and how that differs from titleless list lowering.
  - Update `examples/README.md` so the corpus map points readers at the omitted-title IO proof without blurring the one-new-idea-per-example rule.
  - Update `docs/VERSIONING.md` for the additive public language change and keep its language-version and release-class guidance aligned with the new syntax.
  - Update `CHANGELOG.md` so unreleased or next-release notes describe the new shorthand, who it affects, and the relevant proof path.
  - Run `uv sync`.
  - Run `npm ci`.
  - Run `make verify-examples`.
  - Run `make verify-diagnostics` again after all final wording and proof files settle.
* Verification (required proof):
  - The full shipped corpus passes under `make verify-examples`.
  - Diagnostics verification passes after the final docs, examples, and error text settle.
* Docs/comments (propagation; only if needed):
  - All touched live docs and release-facing notes must match shipped behavior before this phase can close.
* Exit criteria (all required):
  - Public language docs, example index text, versioning guidance, and changelog notes all match the shipped feature and its limits.
  - The full example corpus passes.
  - Diagnostics proof passes.
  - The repo has one clear public story for inherited-title reuse, first-class IO omitted-title inference, and titleless list lowering.
* Rollback:
  - Revert the outward-facing docs, release notes, and proof additions together if the compiler behavior from earlier phases is not ready to ship.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer manifest-backed compile-fail and render-contract cases over new bespoke test harnesses.
- Add cases that prove omitted-title shorthand and explicit-title long form render the same.
- Add cases that prove ambiguous or unsupported omitted-title forms fail loud.

## 8.2 Integration tests (flows)

- Run `uv sync`.
- Run `npm ci`.
- Run `make verify-examples`.
- Run `make verify-diagnostics`.
- `make verify-package` is out of scope unless the implementation grows into package metadata, publish-flow, or public install changes.

## 8.3 E2E / device tests (realistic)

No UI or device layer applies here. Final trust should come from corpus-backed compile/render proof plus the relevant repo verification commands.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Ship as an additive language feature with code, examples, public docs, `docs/VERSIONING.md`, `CHANGELOG.md`, and verifier-owned proof aligned in the same change.

## 9.2 Telemetry changes

No runtime telemetry is expected.

## 9.3 Operational runbook

If omitted-title authoring proves ambiguous on a surface, tighten the fail-loud rule and docs instead of adding silent fallback behavior.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, `# TL;DR`, `# 0)` through `# 10)`, `planning_passes`, and helper-block drift
  - owner path, adjacent surfaces, compatibility posture, phase obligations, verification burden, rollout burden, and release-surface follow-through
- Findings summary:
  - the phase plan left the proof owner path partly unresolved
  - some diagnostics and preservation duties were still outside authoritative checklist and exit criteria
  - the artifact was missing the required consistency-pass gate block
- Integrated repairs:
  - locked the focused proof path to `examples/117_io_omitted_wrapper_titles`
  - added the missing preservation guards for `examples/23_*` and `examples/27_*`
  - pulled diagnostics-title alignment and the `output schema field/def` unchanged guard into Phase 2 checklist and exit criteria
  - strengthened rollout language so release-facing notes ship with the same change
  - appended a decision-close entry to the log and recorded this helper block
- Remaining inconsistencies:
  - none
- Unresolved decisions:
  - none
- Unauthorized scope cuts:
  - none
- Decision-complete:
  - yes
- Decision: proceed to implement? yes
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

Read entries in order. Later entries may close earlier draft follow-ups without rewriting the earlier record.

## 2026-04-15 - Seed omitted-title feature as an additive consistency change

Context

The ask is to make omitted titles work across most natural subitem surfaces, update proof, and keep the language easy to author.

Options

- Add one narrow new shortcut only for `inputs` / `outputs`.
- Add a broader consistency rule across natural keyed subitem surfaces.
- Leave current mixed behavior and add more examples only.

Decision

Default recommendation is the broader consistency rule, but keep it fail loud and separate from existing list lowering. This draft plan assumes additive syntax, no bridges, and one shared title source rule.

Consequences

- The implementation will likely touch grammar, parser, resolution, compile, docs, and example proof together.
- Surface scope and title source order still need confirmation before implementation planning.

Follow-ups

- Complete deep-dive and convert the resolved first-cut scope into an implementation plan.

## 2026-04-15 - Deep-dive narrows the first cut to first-class IO wrapper sections

Context

Research showed that inherited override sections already reuse parent titles across several surfaces, but new base omission is only strongly grounded in first-class `inputs` / `outputs` wrapper sections. Those sections already have one dedicated contract-bucket owner path and a real direct-declaration title source.

Options

- Broaden the first cut to arbitrary-body section families.
- Broaden the first cut to generic record and output wrapper sections.
- Keep the new base omission local to first-class IO wrapper sections and document inherited overrides as the existing baseline convention.

Decision

Keep the first cut local to first-class IO wrapper sections. Treat inherited override omission as already-shipped convention, and keep arbitrary-body sections, generic record/output wrappers, and `output schema field/def` out of scope.

Consequences

- The implementation stays on one canonical owner path instead of widening title inference across unrelated surfaces.
- The plan still needs docs and example updates so the broader convention is explained honestly.
- Generic record/output wrapper omission can be revisited later as separate work if it still matters after this cut ships.

Follow-ups

- Convert this architecture into a phased implementation plan.

## 2026-04-15 - Consistency pass closes planning and locks the proof path

Context

The cold-read consistency pass found a few real readiness gaps: the focused proof path was still open, some diagnostics and preservation duties were stranded outside the authoritative phase gates, and the artifact did not yet record the implementation-readiness gate.

Options

- Proceed to implementation without tightening the plan.
- Tighten the main artifact so the proof path, diagnostics duties, preserved unchanged surfaces, and rollout burden are all explicit before implementation starts.

Decision

Tighten the main artifact before implementation. The focused proof path is now `examples/117_io_omitted_wrapper_titles`, the missing diagnostics and unchanged-surface duties are part of Phase 2, and the consistency gate now records that planning is decision-complete.

Consequences

- The implementation can now start from Phase 1 without guessing about proof ownership or preserved adjacent surfaces.
- The older planning entries remain historical context, but they no longer represent open decisions.

Follow-ups

- Start implementation at Phase 1 on the canonical IO owner path.

## 2026-04-15 - Implementation pass completes the approved feature and proof

Context

The implementation pass ran across the full approved frontier: dedicated
first-class IO wrapper ownership, omitted-title inference, public docs, release
notes, and final repo proof.

Options

- Stop after the code change and leave docs or release notes behind.
- Finish code, proof, public docs, release-facing notes, and required repo
  verification in one pass.

Decision

Finish the full approved implementation frontier in one pass. Keep the
implement-loop state armed for a fresh audit instead of self-certifying the
change.

Consequences

- The code, docs, examples, versioning notes, and changelog now match the
  approved first-class IO omitted-title feature and its fail-loud limits.
- `uv sync`, `npm ci`, `make verify-examples`, and `make verify-diagnostics`
  all passed on 2026-04-15.
- The next required controller step is fresh `audit-implementation`.

Follow-ups

- Run the audit pass before closing the implement-loop controller.
