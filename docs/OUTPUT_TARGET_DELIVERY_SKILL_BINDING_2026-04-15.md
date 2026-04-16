---
title: "Doctrine - Output Target Delivery Skill Binding - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - examples/09_outputs/prompts/AGENTS.prompt
  - examples/12_role_home_composition/prompts/AGENTS.prompt
  - doctrine/grammars/doctrine.lark
  - doctrine/_model/io.py
  - doctrine/_compiler/resolve/outputs.py
  - doctrine/_compiler/compile/outputs.py
  - tests/test_output_rendering.py
  - tests/test_output_inheritance.py
---

# TL;DR

## Outcome

Add an optional `delivery_skill:` attachment on `output target` so authors can keep outputs small and still bind a reusable delivery skill at the target boundary.

## Problem

Today custom delivery mechanics can leak into `output` authoring through target-specific config. That makes the output contract noisy and exposes runtime adapter details in the wrong place.

## Approach

Extend `output target` with a typed `delivery_skill:` attachment. Resolve it through a target-specific contract path that keeps current target config intact. Render the bound skill in output Markdown as a compact `Delivered Via` contract row instead of exposing raw adapter glue.

## Plan

1. Add the typed `delivery_skill: SkillRef` attachment on `output target`.
2. Resolve and validate the bound skill across local and imported targets.
3. Render the bound skill cleanly in output contract tables.
4. Add one dedicated generic imported-target example plus fail-loud tests and docs updates.

## Non-negotiables

- `output` must keep owning the emitted artifact contract.
- `output target` must keep owning destination and delivery binding.
- `skill` must stay a reusable capability, not become a second output system.
- Existing target config must keep working.
- Render human-facing delivery intent, not raw shell or adapter internals.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-15
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None. `uv run --locked python -m unittest tests.test_output_target_delivery_skill tests.test_output_rendering tests.test_output_inheritance tests.test_final_output` and `make verify-examples` passed, including the dedicated `examples/118_output_target_delivery_skill_binding` proof.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
recommended_flow: research -> deep dive -> phase plan -> consistency pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine lets `output target` declare `delivery_skill: SkillRef`, then authors can express skill-backed delivery at the right boundary, outputs can stay clean and typed, existing target config can keep working, and emitted Markdown can show delivery intent cleanly without leaking shell glue.

## 0.2 In scope

- Add optional `delivery_skill:` on `output target`.
- Resolve local and imported skill refs from that field.
- Keep existing `required:` and `optional:` target config behavior intact.
- Render a compact `Delivered Via` row in ordinary output contract tables when the target declares a delivery skill.
- Add one new manifest-backed example that proves the elegant target-level usage and imported-target behavior with generic names.
- Update language docs, authoring guidance, examples index, and test coverage for the new surface.
- Update release-facing docs if the change lands as a public backward-compatible language feature.

## 0.3 Out of scope

- Replacing `target:` with a bare skill ref.
- Making `skill` or `skills` own output contracts.
- Exposing raw shell, CLI, or harness adapter details in emitted Markdown.
- Defining a new skill-package execution protocol in Doctrine.
- Adding per-output delivery-skill override in the first cut.

## 0.4 Definition of done (acceptance evidence)

- The motivating authored example in this plan should read exactly like this:

```prompt
skill RallyIssueNoteAppendSkill: "rally-issue-note-append"
    purpose: "Append a markdown note to the current Rally issue ledger."

    use_when: "Use When"
        "Use this when an output targets the Rally issue ledger append path."


output target RallyIssueNoteAppend: "Rally Issue Note Append"
    delivery_skill: RallyIssueNoteAppendSkill


document LessonsIssueNoteDocument: "Lessons Issue Note"
    section summary: "Summary"
        "Say what changed."

    table lesson_changes: "Lesson Changes"
        columns:
            lesson: "Lesson"
                "Name the lesson."

            change: "Change"
                "Say what changed."


output LessonsIssueNote: "Lessons Issue Note"
    target: RallyIssueNoteAppend
    shape: MarkdownDocument
    structure: LessonsIssueNoteDocument
    requirement: Advisory

    standalone_read: "Standalone Read"
        "This note should stand on its own for the next owner."
```

- The expected output render should read exactly like this:

```md
### Lessons Issue Note

| Contract | Value |
| --- | --- |
| Target | Rally Issue Note Append |
| Delivered Via | `rally-issue-note-append` |
| Shape | Markdown Document |
| Requirement | Advisory |

#### Artifact Structure

Lessons Issue Note includes:
- Summary
- Lesson Changes

#### Standalone Read

This note should stand on its own for the next owner.
```

- The dedicated shipped corpus example for this feature should stay generic even though this plan keeps the motivating Rally example verbatim.
- Ordinary output Markdown renders one clean `Delivered Via` row and does not print raw adapter details.
- Existing outputs and custom targets still compile and render without authored changes.
- New unit tests cover parsing, resolution, rendering, imports, and fail-loud validation.
- One new manifest-backed example proves the feature end to end with generic names and imported target reuse.
- Relevant verification passes run and stay green.

## 0.5 Key invariants (fix immediately if violated)

- No new parallel ownership path for delivery semantics.
- No output-owned adapter glue when a target-owned delivery skill can express the same intent.
- No behavior drift for existing target config semantics.
- No hidden compatibility shim or fallback path.
- No product-specific names in shipped docs or examples.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Keep output authoring elegant at the use site.
2. Keep current Doctrine owner boundaries clear.
3. Make the feature additive and fail loud.
4. Keep rendered Markdown compact and human-facing.
5. Prove imported-target reuse with generic examples.

## 1.2 Constraints

- `output target` is currently modeled as a config-spec surface plus title.
- Existing `required:` and `optional:` target keys are already shipped and must stay stable.
- `output` contract tables already have a clear grouped render shape.
- Public docs and examples must stay generic and repo-neutral.
- The feature must fit current named-ref, import, and inheritance patterns instead of creating a new binding system.

## 1.3 Architectural principles (rules we will enforce)

- Delivery skill binding lives on `output target`, not on `output`.
- `output` keeps owning artifact shape, structure, schema, trust, and requirement.
- The bound skill is a typed ref, resolved with the same fail-loud import rules as other named refs.
- Output rendering shows only the delivery signal a reader needs.
- Raw adapter internals do not become emitted doctrine.

## 1.4 Known tradeoffs (explicit)

- A target-level binding is the cleanest default, but it means one target chooses one delivery skill in the first cut.
- That is acceptable because the goal is elegance and reusable target ownership, not per-output routing complexity.
- A later per-output override can be considered only if a real repo use case proves the need.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already has:

- typed `output`, `output target`, `output shape`, and `output schema` surfaces
- custom target config through `required:` and `optional:` keys
- reusable `skill` declarations and `skills` relationship blocks
- grouped Markdown output contracts that already show target, shape, requirement, schema, and structure

## 2.2 What’s broken / missing (concrete)

- There is no first-class way for an output target to say "deliver this output with this skill."
- That pushes delivery intent into noisy target config or output-local glue.
- The authored output contract becomes harder to read than it needs to be.
- The emitted Markdown cannot show the reusable delivery path cleanly because the language does not model it.

## 2.3 Constraints implied by the problem

- The fix should add one typed binding, not a second output system.
- The binding must preserve current target config behavior.
- The feature must work across imported shared targets so one repo can publish the target and another can consume it cleanly.
- The rendered output contract should stay readable and small.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- none beyond Doctrine's own shipped patterns — reject importing a second adapter or transport model here — this change is about preserving Doctrine's current ownership split, not borrowing a foreign abstraction

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) — `output target` is a first-class declaration today, so the new syntax belongs on that surface instead of on `output`
  - [doctrine/_parser/io.py](doctrine/_parser/io.py) — `output_target_decl` currently lowers a target to `OutputTargetDecl(name, title, items)` with no typed attachment support yet
  - [doctrine/_model/io.py](doctrine/_model/io.py) — `OutputTargetDecl` is the canonical model owner for target-level metadata
  - [doctrine/_compiler/validate/display.py](doctrine/_compiler/validate/display.py) — `_config_spec_from_decl` currently treats output targets as config-spec declarations built from `required:` and `optional:` sections only
  - [doctrine/_compiler/resolve/outputs.py](doctrine/_compiler/resolve/outputs.py) — `_resolve_output_target_spec` currently resolves targets through the config-spec path only, which is the clean seam to extend
  - [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) — `_compile_ordinary_output_contract_rows` is the current output-contract table path that should render `Delivered Via`
- Canonical path / owner to reuse:
  - `output target` parse -> model -> resolve -> output compile — this path should own target-level delivery skill binding end to end
- Adjacent surfaces tied to the same contract family:
  - [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md) — public syntax and render story for `output` and `output target` must stay aligned
  - [docs/AGENT_IO_DESIGN_NOTES.md](docs/AGENT_IO_DESIGN_NOTES.md) — the I/O contract story must explain the new target-owned delivery row cleanly
  - [examples/09_outputs/prompts/AGENTS.prompt](examples/09_outputs/prompts/AGENTS.prompt) — current generic custom-target example should be updated or complemented so the new pattern is teachable
  - [examples/12_role_home_composition/prompts/AGENTS.prompt](examples/12_role_home_composition/prompts/AGENTS.prompt) — current repo-local custom target example shows the noisy status quo
  - [examples/14_handoff_truth/prompts/contracts/outputs.prompt](examples/14_handoff_truth/prompts/contracts/outputs.prompt) — shared imported target reuse already exists and should keep working
  - [examples/109_imported_review_handoff_output_inheritance/prompts/shared/review.prompt](examples/109_imported_review_handoff_output_inheritance/prompts/shared/review.prompt) — imported target reuse in shared review prompts is an adjacent proof surface
  - [tests/test_output_rendering.py](tests/test_output_rendering.py) — ordinary output contract render assertions will need the new row coverage
  - [tests/test_output_inheritance.py](tests/test_output_inheritance.py) — imported target reuse proof should stay green with the new target metadata
  - [tests/test_final_output.py](tests/test_final_output.py) — custom-target final-output rejection should keep working and should not be changed by target-level delivery skill metadata
- Compatibility posture (separate from `fallback_policy`):
  - preserve existing contract — this should be a fully additive language change, with no authored migration required for existing `output target` declarations
- Existing patterns to reuse:
  - [examples/14_handoff_truth/prompts/contracts/outputs.prompt](examples/14_handoff_truth/prompts/contracts/outputs.prompt) — shared target declarations imported across prompt boundaries
  - [examples/109_imported_review_handoff_output_inheritance/prompts/shared/review.prompt](examples/109_imported_review_handoff_output_inheritance/prompts/shared/review.prompt) — imported target reuse in a different agent family
  - [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md) and [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) — grouped contract-table rendering should stay the same shape with one new row
- Prompt surfaces / agent contract to reuse:
  - [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md) — owns the public authored syntax
  - [docs/AUTHORING_PATTERNS.md](docs/AUTHORING_PATTERNS.md) — should teach when to keep delivery semantics on `output target`
  - [examples/README.md](examples/README.md) — should point readers at the new dedicated proof example
- Native model or agent capabilities to lean on:
  - none — this is a compiler and authoring-surface feature, not a model-capability gap
- Existing grounding / tool / file exposure:
  - existing grammar, parser, model, resolver, compile, docs, and example surfaces are sufficient; no new harness or tool exposure is needed
- Duplicate or drifting paths relevant to this change:
  - current custom-target examples show target config only and can encourage output-local delivery glue because the language does not model delivery intent yet
  - the config-spec-only target resolve path is the current limitation and should be extended directly instead of adding a second metadata side channel
- Capability-first opportunities before new tooling:
  - a target-level `delivery_skill:` binding solves the authoring problem without adding a new adapter runtime, wrapper, or fallback surface
  - rendering one compact `Delivered Via` row solves the readability problem without surfacing raw CLI details
- Behavior-preservation signals already available:
  - [tests/test_output_rendering.py](tests/test_output_rendering.py) — protects the grouped output contract render shape
  - [tests/test_output_inheritance.py](tests/test_output_inheritance.py) — protects imported target reuse and output inheritance behavior
  - [tests/test_final_output.py](tests/test_final_output.py) — protects target-kind semantics around final output
  - `make verify-examples` — protects the shipped corpus and example docs alignment

## 3.3 Decision gaps that must be resolved before implementation

- none — repo evidence checked: grammar, parser, target model, target resolve path, output compile path, current custom-target examples, imported-target examples, and existing render tests — default recommendation: add `delivery_skill:` on `output target`, keep it target-owned in the first cut, and render one compact `Delivered Via` row — answer needed: none; the user confirmed this direction
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) declares `output target` as a full declaration, but today its body is still generic record content.
- [doctrine/_parser/io.py](doctrine/_parser/io.py) lowers `output_target_decl` straight to `OutputTargetDecl(name, title, items)` with no typed attachment handling.
- [doctrine/_parser/parts.py](doctrine/_parser/parts.py) has no target-specific body parts today. That is different from `output`, which already has typed attachment parts such as `schema`, `structure`, and `render_profile`.
- [doctrine/_model/io.py](doctrine/_model/io.py) models `OutputTargetDecl` as `name`, `title`, and `items` only.
- [doctrine/_compiler/constants.py](doctrine/_compiler/constants.py) stores built-in output targets as `ConfigSpec` values in `_BUILTIN_OUTPUT_TARGETS`.
- [doctrine/_compiler/validate/display.py](doctrine/_compiler/validate/display.py) extracts custom target config from `required:` and `optional:` sections only.
- [doctrine/_compiler/resolve/outputs.py](doctrine/_compiler/resolve/outputs.py) resolves output targets through `_resolve_output_target_spec`, which returns config-only data.
- [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) compiles ordinary output contract tables from that resolved target spec.
- [doctrine/_compiler/flow.py](doctrine/_compiler/flow.py) and [doctrine/_compiler/validate/addressable_display.py](doctrine/_compiler/validate/addressable_display.py) also read the resolved target spec for target title and config labels.
- Public truth and proof live in [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md), [docs/AGENT_IO_DESIGN_NOTES.md](docs/AGENT_IO_DESIGN_NOTES.md), [docs/EMIT_GUIDE.md](docs/EMIT_GUIDE.md), [examples/09_outputs](examples/09_outputs), [examples/12_role_home_composition](examples/12_role_home_composition), [examples/14_handoff_truth](examples/14_handoff_truth), [examples/109_imported_review_handoff_output_inheritance](examples/109_imported_review_handoff_output_inheritance), and the output test modules.

## 4.2 Control paths (runtime)

Today a custom target follows one narrow path:

1. Parse `output target` through the generic record-body path.
2. Store the declaration as `OutputTargetDecl(..., items=...)`.
3. Extract `required:` and `optional:` sections into a `ConfigSpec`.
4. Resolve `output ... target: TargetRef` through that config-only spec.
5. Compile target config rows into the grouped `Contract | Value` table.
6. Reuse the same target title in flow output and addressable display.

There is no first-class target-owned metadata path beyond config keys and title.

## 4.3 Object model + key abstractions

- `OutputTargetDecl` is a thin readable declaration, not a typed attachment owner yet.
- `ConfigSpec` is shared by input sources and output targets today, so output targets do not have their own richer resolved contract type.
- `OutputDecl` owns artifact shape, schema, structure, trust, and render details.
- `skill` declarations are separate capability objects resolved through the normal skill-ref registry path.
- Imported target reuse already works because `output target` refs are ordinary named refs.

## 4.4 Observability + failure behavior today

- Unknown target config keys fail loud in output compile.
- Missing required target config keys fail loud.
- Imported target reuse is already covered by output-inheritance tests and shipped examples.
- Final-output validation already rejects custom non-`TurnResponse` targets and should stay unchanged.
- A would-be `delivery_skill:` line on `output target` has no shipped typed meaning today. Under the current generic target-body model, that kind of line would not become live target behavior.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Extend [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) so `output target` uses a dedicated target-body rule that supports ordinary target record items plus one typed `delivery_skill:` statement.
- Add target-specific parser parts in [doctrine/_parser/parts.py](doctrine/_parser/parts.py) so the attachment is explicit and fail-loud, not a generic ignored extra.
- Extend [doctrine/_parser/io.py](doctrine/_parser/io.py) and [doctrine/_model/io.py](doctrine/_model/io.py) so `OutputTargetDecl` owns an optional `delivery_skill_ref`.
- Introduce a target-specific resolved contract in [doctrine/_compiler/resolved_types.py](doctrine/_compiler/resolved_types.py) and stop treating output targets as plain `ConfigSpec`.
- Switch built-in output targets in [doctrine/_compiler/constants.py](doctrine/_compiler/constants.py) to the new resolved target type with no delivery skill.
- Extend [doctrine/_compiler/resolve/outputs.py](doctrine/_compiler/resolve/outputs.py) so output target resolution returns both config keys and optional bound skill identity.
- Extend [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) so ordinary output contract tables render `Delivered Via` from target-owned metadata.

## 5.2 Control paths (future)

1. Parse `delivery_skill: SkillRef` only on `output target`.
2. Store the ref on `OutputTargetDecl` as target-owned metadata.
3. Resolve the ref through the existing skill registry path.
4. Build one `ResolvedOutputTargetSpec` that contains:
   - target title
   - required config keys
   - optional config keys
   - optional delivery-skill display data
5. Keep target config validation unchanged for `output ... target:`.
6. In ordinary output contract rendering, emit rows in this order:
   - `Target`
   - `Delivered Via` when present
   - target config rows
   - `Shape`
   - `Requirement`
   - `Schema` / `Structure` when present
7. Keep flow output and addressable display compatible with the new resolved target type, but do not add new visible delivery rows there in the first cut.

## 5.3 Object model + abstractions (future)

- `OutputTargetDecl` becomes a target contract plus optional delivery-skill attachment.
- `delivery_skill:` is a typed target attachment, not a generic record scalar and not a config key.
- `ConfigSpec` stays the input-source contract type. Output targets move to a dedicated resolved type instead of overloading input-source config semantics.
- The new resolved target type should expose the same title and key maps current consumers expect so flow and addressable surfaces stay narrow.
- The bound skill display for output rendering should use the skill title, wrapped in backticks, matching the motivating render contract in Section 0.

## 5.4 Invariants and boundaries

- The canonical owner path for delivery semantics is `output target`.
- `output` must not gain a second delivery-binding surface in the first cut.
- `skill` must not gain output-schema, target-config, or delivery-target ownership in the first cut.
- Existing target config remains the single source of truth for target-local authored keys.
- Imported target reuse keeps working through ordinary named refs; `output target` itself still does not need inheritance.
- Rendered Markdown shows only the delivery skill label. It does not expose adapter commands, shell glue, or hidden harness internals.
- Flow graphs and addressable target display keep their current scope unless a later need proves they should show delivery metadata too.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | `output_target_decl` body rule | `output target` uses generic `record_body` only | Add dedicated target body with typed `delivery_skill:` support | Make the binding first-class and fail loud | `delivery_skill: SkillRef` on `output target` | parse and compile tests |
| Parser body parts | `doctrine/_parser/parts.py` | target body parts | No target-specific typed parts | Add target-body parts for optional `delivery_skill_ref` | Keep parser structure explicit and parallel to other typed attachments | target body with typed attachment | parser tests |
| Parser transform | `doctrine/_parser/io.py` | `output_target_decl` lowering | Lowers to `OutputTargetDecl(name, title, items)` | Lower target body into items plus optional `delivery_skill_ref` | Preserve record items while making delivery binding typed | `OutputTargetDecl(..., delivery_skill_ref=...)` | parse tests |
| Target model | `doctrine/_model/io.py` | `OutputTargetDecl` | Title plus items only | Add optional `delivery_skill_ref` | Keep target-owned metadata explicit | target-level skill ref | parse and resolve tests |
| Resolved contract type | `doctrine/_compiler/resolved_types.py` | target config types | Output targets reuse `ConfigSpec` | Add `ResolvedOutputTargetSpec` and keep `ConfigSpec` for input sources | Avoid overloading input-source config semantics | resolved target title + config + delivery skill | resolve, compile, flow compatibility tests |
| Built-ins | `doctrine/_compiler/constants.py` | `_BUILTIN_OUTPUT_TARGETS` | Built-ins stored as `ConfigSpec` | Switch built-in targets to the new resolved target type with no delivery skill | Keep one target resolution type | built-in target contract object | existing output tests |
| Display/config extraction | `doctrine/_compiler/validate/display.py` | `_config_spec_from_decl` | Extracts config keys from target sections only | Keep config extraction narrow and add target-specific helper if needed | Preserve current config semantics cleanly | config extraction stays unchanged; delivery handled separately | validation and compile tests |
| Target resolution | `doctrine/_compiler/resolve/outputs.py` | `_resolve_output_target_spec` | Returns config-only target data | Resolve config keys plus bound skill through one target contract object | Give output compile a typed delivery signal | `ResolvedOutputTargetSpec` | resolution tests |
| Skill ref reuse | `doctrine/_compiler/resolve/refs.py` | `_resolve_skill_decl` | Existing skill ref resolution already works | Reuse this path from target resolution | Avoid inventing a second skill-binding resolver | existing skill named-ref semantics reused | resolution tests |
| Output compile | `doctrine/_compiler/compile/outputs.py` | `_compile_ordinary_output_contract_rows` | Contract table shows target, config, shape, requirement, schema, structure | Add `Delivered Via` row from target-owned delivery skill metadata | Keep render elegant and human-facing | `Delivered Via` contract row | `tests/test_output_rendering.py` |
| Flow compatibility | `doctrine/_compiler/flow.py` | `_flow_output_detail_lines` target path | Reads target title and config from resolved target spec | Keep working with the new resolved target type, with no new visible behavior in first cut | Avoid accidental flow regressions | flow keeps title/config semantics | existing flow tests if touched |
| Addressable display compatibility | `doctrine/_compiler/validate/addressable_display.py` | output target title display | Reads target title from resolved target spec | Keep working with the new resolved target type, with no new visible delivery display in first cut | Avoid accidental display regressions | target title display preserved | existing display tests if touched |
| Output render docs | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md` | output and target docs | No target-level delivery-skill story or `Delivered Via` row | Document syntax and rendered contract row | Keep public truth aligned with shipped output shape | documented `delivery_skill:` and `Delivered Via` | docs-linked example coverage |
| Authoring guidance | `docs/AUTHORING_PATTERNS.md`, `docs/README.md`, `examples/README.md` | authoring guidance and example map | No guidance for target-owned delivery binding | Point users to the elegant target-level pattern and the new example | Keep discovery clean | new guidance and example index entry | docs verification via corpus |
| Example proof | new dedicated `examples/<new_example>/` | generic delivery-skill target example | Feature has no corpus proof | Add one generic example that proves shared target + bound skill + rendered `Delivered Via` row | One new idea per example; keep examples generic | imported/shared target with delivery skill | `make verify-examples` |
| Existing example surfaces | `examples/09_outputs/**`, `examples/12_role_home_composition/**`, `examples/14_handoff_truth/**`, `examples/109_imported_review_handoff_output_inheritance/**` | adjacent target examples | Current examples prove config-only targets and imported target reuse | Keep or lightly tune comments only; do not overload them with a second new idea unless needed for consistency | Preserve the corpus teaching ladder | no required syntax migration in first cut | verify corpus as regression signal |
| Release docs | `docs/VERSIONING.md`, `CHANGELOG.md` | public language feature surfaces | No entry for this target attachment | Record the additive feature if implementation ships publicly | Keep release truth aligned | backward-compatible language addition | package/release checks if touched |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `output target` typed attachment -> resolved target contract -> ordinary output contract row
- Deprecated APIs (if any):
  - none in the first cut
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - no code-path delete is required
  - docs and examples should stop recommending output-local delivery glue once the new feature ships
- Adjacent surfaces tied to the same contract family:
  - public language docs
  - emit/render docs
  - authoring guidance and example index
  - one new dedicated generic example
  - existing target examples as regression surfaces
- Compatibility posture / cutover plan:
  - additive; existing `output target` declarations without `delivery_skill:` keep working unchanged
- Capability-replacing harnesses to delete or justify:
  - none; this feature should reduce pressure to smuggle delivery semantics into config or prose without adding any new runtime harness
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/README.md`
  - `examples/README.md`
  - `CHANGELOG.md` and `docs/VERSIONING.md` if implementation ships publicly
- Behavior-preservation signals for refactors:
  - `tests/test_output_rendering.py`
  - `tests/test_output_inheritance.py`
  - `tests/test_final_output.py`
  - existing flow/display tests if touched
  - `make verify-examples`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Output docs | `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md` | target-owned `delivery_skill:` plus `Delivered Via` row | prevents public doc drift around the output contract shape | include |
| Authoring docs | `docs/AUTHORING_PATTERNS.md`, `docs/README.md`, `examples/README.md` | point readers at target-owned delivery binding | prevents docs from teaching noisy output-local glue as the best pattern | include |
| New corpus proof | new dedicated generic example directory | shared target with bound delivery skill | proves the feature cleanly without overloading older examples | include |
| Current custom-target showcase | `examples/09_outputs` | keep config-only target example focused | prevents one example from trying to teach two ideas at once | exclude |
| Role-home composition example | `examples/12_role_home_composition` | possible future cleanup to use target-owned delivery skill | useful later, but not required for first-cut proof | defer |
| Imported shared-target examples | `examples/14_handoff_truth`, `examples/109_imported_review_handoff_output_inheritance` | imported target delivery binding | imported target reuse matters, but a dedicated new example can prove it more cleanly | exclude unless the new example misses an import edge |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

<!-- arch_skill:block:phase_plan:start -->
## Phase 1 - Target Syntax And Model Foundation

Status: COMPLETE

### Goal

Make `delivery_skill:` a first-class `output target` field in the grammar, parser, model, and resolved target contract so later compile work can read one clean target-owned shape.

### Work

This phase lays the typed foundation. It should end with one resolved target contract type that both built-in and authored output targets use, while keeping current target config behavior intact.

### Checklist (must all be done)

- Extend [doctrine/grammars/doctrine.lark](doctrine/grammars/doctrine.lark) so `output target` uses a dedicated body rule that accepts ordinary target record items plus one typed `delivery_skill: SkillRef` statement.
- Add target-specific parser parts in [doctrine/_parser/parts.py](doctrine/_parser/parts.py) for the optional `delivery_skill` attachment.
- Extend [doctrine/_parser/io.py](doctrine/_parser/io.py) so `output_target_decl` lowers into ordinary target items plus an optional typed `delivery_skill_ref`.
- Extend [doctrine/_model/io.py](doctrine/_model/io.py) so `OutputTargetDecl` owns an optional `delivery_skill_ref`.
- Introduce `ResolvedOutputTargetSpec` in [doctrine/_compiler/resolved_types.py](doctrine/_compiler/resolved_types.py) and keep `ConfigSpec` scoped to input sources.
- Switch built-in output targets in [doctrine/_compiler/constants.py](doctrine/_compiler/constants.py) to the new resolved target type with no delivery skill.
- Add one high-leverage boundary comment at the resolved target contract boundary that explains why output targets no longer reuse `ConfigSpec`.
- Add or start [tests/test_output_target_delivery_skill.py](tests/test_output_target_delivery_skill.py) with parse and model coverage for valid `delivery_skill:` authoring and fail-loud coverage for invalid target-body use.

### Verification

- `uv run --locked python -m unittest tests.test_output_target_delivery_skill`

### Docs / comments

- Keep the new boundary comment local to the resolved target contract or target resolver. Do not spread comment noise across ordinary output compile code.

### Exit criteria (all required)

- `delivery_skill:` parses only on `output target`.
- `OutputTargetDecl` carries the typed ref without turning it into a generic config key.
- Built-in and authored output targets share the same resolved target contract type.
- Existing config-only target declarations still parse and lower unchanged.

### Rollback

- Revert the target-specific parse and model changes before any compile-side dependency lands.

## Phase 2 - Target Resolution And Output Contract Integration

Status: COMPLETE

### Goal

Resolve the bound skill through the existing skill registry path and expose it in ordinary output contract rendering without changing target config semantics or widening flow/addressable display.

### Work

This phase connects the new target field to real output behavior. It should keep current output target config validation intact, add one `Delivered Via` row for ordinary output contracts, and preserve all existing output surfaces that are not part of the new feature.

### Checklist (must all be done)

- Extend [doctrine/_compiler/resolve/outputs.py](doctrine/_compiler/resolve/outputs.py) so output target resolution returns `ResolvedOutputTargetSpec` with title, required keys, optional keys, and optional bound delivery-skill display data.
- Reuse the existing skill resolution path in [doctrine/_compiler/resolve/refs.py](doctrine/_compiler/resolve/refs.py) instead of inventing a second target-skill resolver.
- Keep `required:` and `optional:` target config extraction and validation behavior unchanged. `delivery_skill:` must not become a config key.
- Extend [doctrine/_compiler/compile/outputs.py](doctrine/_compiler/compile/outputs.py) so ordinary output contract rows render in this order:
  - `Target`
  - `Delivered Via` when present
  - target config rows
  - `Shape`
  - `Requirement`
  - `Schema` and `Structure` when present
- Render the delivery skill with the skill title wrapped in backticks, matching the plan acceptance render.
- Keep [doctrine/_compiler/flow.py](doctrine/_compiler/flow.py) compatible with the new resolved target type, with no new visible delivery row in the first cut.
- Keep [doctrine/_compiler/validate/addressable_display.py](doctrine/_compiler/validate/addressable_display.py) compatible with the new resolved target type, with no new visible delivery row in the first cut.
- Extend [tests/test_output_target_delivery_skill.py](tests/test_output_target_delivery_skill.py) to cover target resolution, imported target reuse, and fail-loud unknown-skill behavior.
- Update existing regression coverage in [tests/test_output_rendering.py](tests/test_output_rendering.py), [tests/test_output_inheritance.py](tests/test_output_inheritance.py), and [tests/test_final_output.py](tests/test_final_output.py) only where the new resolved target type touches their current assumptions.

### Verification

- `uv run --locked python -m unittest tests.test_output_target_delivery_skill tests.test_output_rendering tests.test_output_inheritance tests.test_final_output`

### Docs / comments

- Add code comments only where the new row order or resolved target contract would otherwise be non-obvious to a reader.

### Exit criteria (all required)

- Ordinary output contracts render exactly one `Delivered Via` row when the target binds a delivery skill.
- Ordinary output contracts render no `Delivered Via` row when the target has no bound delivery skill.
- Target config rows, shape rows, requirement rows, and schema or structure rows keep their current semantics.
- Flow and addressable display stay behaviorally unchanged apart from consuming the richer resolved target type internally.

### Rollback

- Revert the compile and resolve wiring as one unit if the new resolved target type causes output-surface regressions that cannot be fixed cleanly in phase.

## Phase 3 - Proof Surface And Corpus Example

Status: COMPLETE

### Goal

Prove the feature end to end with one focused test module and one dedicated generic shared-target corpus example, without overloading older examples that already teach other ideas.

### Work

This phase turns the new syntax into shipped proof. It should keep the example ladder clean by adding one new example for this one idea, using that example to prove imported shared-target reuse, and using older output examples only as regression coverage.

### Checklist (must all be done)

- Finish [tests/test_output_target_delivery_skill.py](tests/test_output_target_delivery_skill.py) so it covers:
  - parse
  - resolution
  - ordinary output rendering
  - imported target reuse
  - fail-loud missing or unknown skill refs
- Add [examples/118_output_target_delivery_skill_binding](examples/118_output_target_delivery_skill_binding:1) as the dedicated generic manifest-backed proof for this feature.
- Author the new example so it proves:
  - a reusable delivery skill
  - a shared `output target` with `delivery_skill:`
  - a local output that imports or reuses that shared target
  - the clean `Delivered Via` render row
- Keep older examples such as [examples/09_outputs](examples/09_outputs:1) and [examples/109_imported_review_handoff_output_inheritance](examples/109_imported_review_handoff_output_inheritance:1) focused on their current teaching job unless a tiny consistency touch is required.

### Verification

- `uv run --locked python -m unittest tests.test_output_target_delivery_skill`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/118_output_target_delivery_skill_binding/cases.toml`
- `make verify-examples`

### Docs / comments

- Keep the shipped example generic even though this plan keeps the motivating Rally syntax verbatim in Section 0.

### Exit criteria (all required)

- The new test module exists and covers the feature-specific contracts.
- The new example exists, verifies, proves imported shared-target reuse, and renders `Delivered Via` exactly once.
- The full shipped corpus stays green with the new example included.

### Rollback

- Drop the new example and targeted test module together if the implementation surface changes before merge and the proof no longer matches the shipped contract.

## Phase 4 - Public Docs And Release Alignment

Status: COMPLETE

### Goal

Align the public docs, authoring guidance, example index, and release notes with the shipped target-owned delivery binding so users learn the elegant pattern first.

### Work

This phase updates the human-facing truth after the implementation and proof surfaces are stable. It should make the new ownership model easy to find and remove any touched guidance that still presents output-local delivery glue as the preferred pattern.

### Checklist (must all be done)

- Update [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md) with the new `output target ... delivery_skill:` syntax and the ordinary output `Delivered Via` render row.
- Update [docs/AGENT_IO_DESIGN_NOTES.md](docs/AGENT_IO_DESIGN_NOTES.md) so output contracts stay output-owned while delivery binding stays target-owned.
- Update [docs/EMIT_GUIDE.md](docs/EMIT_GUIDE.md) with the new rendered output contract shape.
- Update [docs/AUTHORING_PATTERNS.md](docs/AUTHORING_PATTERNS.md) so the elegant pattern is target-owned delivery binding instead of output-local adapter glue.
- Update [docs/README.md](docs/README.md) and [examples/README.md](examples/README.md) so readers can find the feature docs and the new canonical example quickly.
- Update [CHANGELOG.md](CHANGELOG.md) and [docs/VERSIONING.md](docs/VERSIONING.md) if the change ships as a public backward-compatible language addition.
- Rewrite or remove any touched live doc sentence that still teaches output-local delivery glue as the best pattern.

### Verification

- `make verify-examples`

### Docs / comments

- Keep public docs and examples generic. Do not move the motivating Rally names from this plan into shipped docs or examples.

### Exit criteria (all required)

- Public docs all tell the same ownership story: `output` owns the artifact contract, `output target` owns destination and delivery binding, and `skill` stays reusable capability.
- At least one public doc shows the clean `Delivered Via` row.
- The release docs are updated when the change counts as a public language addition.
- No touched live doc still presents output-local delivery glue as the preferred new pattern.

### Rollback

- Revert only the doc and release-note edits if implementation slips and the public feature does not ship in the current change set.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Add [tests/test_output_target_delivery_skill.py](tests/test_output_target_delivery_skill.py) as the focused contract suite for:
  - `delivery_skill:` parsing on `output target`
  - target resolution through the existing skill registry path
  - ordinary output rendering of `Delivered Via`
  - imported target reuse
  - fail-loud unknown or invalid skill refs
- Keep [tests/test_output_rendering.py](tests/test_output_rendering.py) as the regression suite for contract-row order and ordinary output Markdown behavior.
- Keep [tests/test_output_inheritance.py](tests/test_output_inheritance.py) as the regression suite for shared-output and shared-target behavior.
- Keep [tests/test_final_output.py](tests/test_final_output.py) green so the richer resolved target type does not leak regressions into final-output behavior.

## 8.2 Integration tests (flows)

- Add [examples/118_output_target_delivery_skill_binding](examples/118_output_target_delivery_skill_binding:1) as the dedicated manifest-backed proof for the new syntax, imported shared-target reuse, and render contract.
- Run `uv run --locked python -m doctrine.verify_corpus --manifest examples/118_output_target_delivery_skill_binding/cases.toml`.
- Run `make verify-examples`.

## 8.3 E2E / device tests (realistic)

No device or UI E2E is needed. The realistic proof is compile plus render plus manifest-backed example coverage.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship as an additive language feature.
- Keep old target config authoring legal.
- Update docs and example guidance to point new users at target-level delivery skill binding as the elegant pattern.

## 9.2 Telemetry changes

No telemetry changes are expected.

## 9.3 Operational runbook

No runtime runbook changes are expected inside Doctrine itself. The feature should stay on the authoring side of the line.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: self-integrator; explorer split simulated locally due to runtime delegation policy
- Scope checked:
  - frontmatter, `planning_passes`, `# TL;DR`, and `# 0)` through `# 10)`
  - cross-section agreement on owner path, compatibility posture, proof surfaces, and phase obligations
- Findings summary:
  - Section 0 promised the new example would prove imported target reuse, but Phase 3 and Section 8 described the example too loosely
  - `examples/README.md` was owned by both the proof phase and the docs phase
- Integrated repairs:
  - tightened the canonical example story so the new example proves a shared imported target with `delivery_skill:`
  - kept `examples/README.md` ownership in the docs phase only
  - rechecked that the verification ladder matches the phased proof story
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

## 2026-04-15 - Put delivery skill binding on output target

### Context

The requested feature is a cleaner way to express skill-backed output delivery without repeating adapter glue in each output declaration.

### Options

- Put the binding on `output`.
- Put the binding on `output target`.
- Replace `target:` with a skill-owned delivery system.

### Decision

Draft the first cut around `output target ... delivery_skill: SkillRef`.

### Consequences

- Authoring stays small at the output use site.
- Current Doctrine owner boundaries stay clean.
- The first cut does not support per-output override.
- Render can stay compact with one `Delivered Via` row.

### Follow-ups

- Carry the confirmed target-level syntax through `phase-plan`.
- Execute with [examples/118_output_target_delivery_skill_binding](examples/118_output_target_delivery_skill_binding:1) as the canonical proof example because example numbers `116` and `117` are already occupied in this worktree.
- Execute with [tests/test_output_target_delivery_skill.py](tests/test_output_target_delivery_skill.py) as the focused feature test module.

## 2026-04-15 - Make delivery_skill a typed output-target attachment

### Context

The current `output target` path is config-spec only. A generic extra field would be too implicit, and overloading `ConfigSpec` would blur the line between input-source config and output-target delivery metadata.

### Options

- Treat `delivery_skill` as an ordinary target record scalar and special-case it later.
- Add a typed `delivery_skill:` attachment on `output target` and resolve it through a target-specific contract type.
- Put the binding on `output`.

### Decision

Use a typed `delivery_skill:` attachment on `output target`, and introduce a target-specific resolved contract type instead of extending input-source `ConfigSpec`.

### Consequences

- Parser and model changes are slightly wider, but the feature is cleaner and fail loud.
- Output target config stays separate from delivery metadata.
- Flow and addressable display can stay narrow by reading the same title/key shape from the new resolved target type.

### Follow-ups

- Encode the exact new target-body parse shape during implementation.
- Keep output contract row order stable with `Delivered Via` directly under `Target`.

## 2026-04-15 - Use example 118 for delivery-skill proof

### Context

The plan originally named `examples/116_output_target_delivery_skill_binding`, but example numbers `116` and `117` are already occupied in this worktree.

### Decision

Use `examples/118_output_target_delivery_skill_binding` for the delivery-skill proof example.

### Consequences

- The implementation preserves the existing untracked example work.
- The proof ladder still uses one dedicated generic imported-target example.
- Docs and verification commands now point at example `118`.
