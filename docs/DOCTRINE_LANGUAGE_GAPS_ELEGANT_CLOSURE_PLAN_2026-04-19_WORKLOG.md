# Worklog

Plan doc: docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md

## Initial entry
- Run started under `miniarch-step auto-implement`.
- Branch: `feat/carrier-review-fields-and-shared-rules-split` (user is doing parallel work on the UNIVERSAL_TYPED_FIELD_BODIES sweep plan on the same branch; do not revert, stash, or overwrite their files).
- Current phase: P1 — §1 typed-gate teaching closure (no grammar).
- Environment drift: `examples/139_enum_typed_field_bodies` already shipped under the parallel sweep plan. P1 plan text says `examples/139_typed_gates_symbol_reference/`; shipping as `examples/140_typed_gates_symbol_reference/` instead. Recording in Decision Log at phase close.

## Phase 1 — §1 typed-gate teaching closure (COMPLETE 2026-04-19)

Files touched:
- `skills/doctrine-learn/prompts/refs/reviews.prompt` — added `typed_gates` section inside `composition:` teaching `schema gates:` + `contract.NAME` reference discipline.
- `skills/agent-linter/prompts/refs/finding_catalog.prompt` — added `AL245 Gate Declared As Inline Prose` table row and full calibration section between `AL240` and `AL250` bands.
- `skills/.curated/doctrine-learn/references/reviews.md` — regenerated from source via `emit_skill`.
- `skills/doctrine-learn/build/references/reviews.md` — regenerated from source via `emit_skill`.
- `skills/.curated/agent-linter/references/finding-catalog.md` — regenerated from source via `emit_skill`.
- `skills/agent-linter/build/references/finding-catalog.md` — regenerated from source via `emit_skill`.
- `docs/REVIEW_SPEC.md` — added typed-gate paragraph in the Review Contracts section pointing at example 140.
- `docs/LANGUAGE_REFERENCE.md` — cross-reference in the Schemas section pointing review authors at the typed-gate rule.
- `CHANGELOG.md` — Unreleased → Added bullet covering example 140 + doctrine-learn / agent-linter teaching deltas.
- `examples/140_typed_gates_symbol_reference/prompts/AGENTS.prompt` — positive render_contract case `TypedGateReviewDemo`.
- `examples/140_typed_gates_symbol_reference/prompts/invalid_unknown_contract_gate/AGENTS.prompt` — compile_fail `E477` case `BrokenTypedGateDemo` firing on `contract.next_action_clarity` typo at line 77.
- `examples/140_typed_gates_symbol_reference/cases.toml` — manifest with the two cases.
- `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` — Phase 1 `Status: COMPLETE` annotation + Decision Log entry covering the example-number drift from 139 to 140.

Commands run and results:
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/140_typed_gates_symbol_reference/cases.toml` — both cases PASS.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill --target doctrine_learn_public_skill --target doctrine_agent_linter_skill --target doctrine_agent_linter_public_skill` — four targets emitted cleanly.
- `make verify-examples` — 410 cases PASS, 0 FAIL.
- `make verify-diagnostics` — diagnostic smoke checks passed; existing `E477` fixture still green.

Authoring notes:
- Doctrine `.prompt` prose cannot carry literal `{{contract.NAME}}` tokens outside `code:` blocks — the parser evaluates `{{...}}` as interpolation and fails with `E280` / `E299`. Reworded the teaching prose to describe the interpolation root in words; the literal `{{contract.NAME}}` usage is kept inside the review body via the output declaration in the ref example, which is where it belongs in real authoring.
- Plan phase `Rollback:` still names `examples/139_typed_gates_symbol_reference/`; the Decision Log entry covers the rename implicitly so rollback should read "remove `examples/140_typed_gates_symbol_reference/`".

Next step: end the turn and let the installed Claude Code Stop hook run the fresh audit pass over `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md`.

## Phase 2 — §2 `override gates:` per review case (COMPLETE 2026-04-19)

Files touched:
- `doctrine/grammars/doctrine.lark` — extended `review_case_body` with optional `review_case_gates_override_block`; added `review_case_gates_override_block`, `review_case_gate_override_clause`, `review_case_gate_add`, `review_case_gate_remove`, and `review_case_gate_modify` productions (sibling-of-`schema_override_sections` comment).
- `doctrine/_model/review.py` — added `ReviewCaseGatesOverride` (frozen dataclass, slots, `add`/`remove`/`modify` tuples + `source_span`); added `ReviewCase.gates_override: ReviewCaseGatesOverride | None`.
- `doctrine/model.py` — re-exported `ReviewCaseGatesOverride`.
- `doctrine/_parser/reviews.py` — handled 7-item review-case body; added override-block + clause transformer methods returning `("add"|"remove"|"modify", payload)` tuples.
- `doctrine/_compiler/resolve/reviews.py` — preserved `gates_override` when reconstructing `ReviewCase` after resolution.
- `doctrine/_compiler/validate/review_semantics.py` — new `_validate_review_case_gate_override` method computing the per-case effective gate set and emitting `E531` (remove/modify of undeclared gate) and `E532` (add/modify name collision).
- `doctrine/_compiler/compile/review_cases.py` — first loop now feeds `seen_contract_gate_keys` from the per-case effective gate set; second loop substitutes a per-case `contract_spec` so downstream `reject contract.NAME` checks resolve against the effective gate set.
- `doctrine/_diagnostic_smoke/fixtures_reviews.py` — added `_review_case_gate_override_base_source`, `review_case_gate_override_remove_missing_source`, `review_case_gate_override_add_collision_source`.
- `doctrine/_diagnostic_smoke/fixtures.py` — re-exported new fixture wrappers.
- `doctrine/_diagnostic_smoke/compile_checks.py` — added `_check_review_case_gate_override_remove_missing_source_emits_e531` (line 88) and `_check_review_case_gate_override_add_collision_source_emits_e532` (line 89).
- `examples/141_review_case_gate_override/prompts/AGENTS.prompt` — positive `render_contract` `DraftReviewFamilyDemo` with two cases (`quick_path`, `full_path`) sharing `SharedReviewContract`; `full_path` carries `override gates:` with `remove clarity`, `add depth: "Depth"`, `modify completeness: "Completeness (full path)"`.
- `examples/141_review_case_gate_override/prompts/invalid_remove_missing_gate/AGENTS.prompt` — `BrokenRemoveDemo` firing `E531` on `remove not_declared` at line 101 (override block on line 100).
- `examples/141_review_case_gate_override/prompts/invalid_add_colliding_gate/AGENTS.prompt` — `BrokenAddDemo` firing `E532` on `add completeness: "Collides"` at line 101.
- `examples/141_review_case_gate_override/cases.toml` — manifest with one positive `render_contract` case + two `compile_fail` cases (`E531` line 100, `E532` line 101).
- `docs/REVIEW_SPEC.md` — per-case `override gates:` paragraph after case-selected rules with add/remove/modify semantics, effective-set rule, `E531` / `E532` contracts, and example 141 pointer.
- `docs/LANGUAGE_REFERENCE.md` — cross-reference under the `contract.NAME` rule pointing at the new override surface and example 141.
- `docs/COMPILER_ERRORS.md` — new `E531` and `E532` rows with plain-language descriptions.
- `skills/doctrine-learn/prompts/refs/reviews.prompt` — added `per_case_gate_override` section under `composition:` teaching the override shape with worked `cases:` example.
- `skills/agent-linter/prompts/refs/finding_catalog.prompt` — added `AL246 Per-Case Gate Delta Split Into Parallel Contracts` table row + full calibration section between `al245` and `al250`.
- `skills/.curated/doctrine-learn/references/reviews.md`, `skills/doctrine-learn/build/references/reviews.md`, `skills/.curated/agent-linter/references/finding-catalog.md`, `skills/agent-linter/build/references/finding-catalog.md` — regenerated from source via `emit_skill`.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` — new `reviewCaseGateOverrideClause` pattern highlighting `add NAME: "..."`, `remove NAME`, `modify NAME: "..."`.
- `CHANGELOG.md` — bumped Unreleased Language version line to `4.0 -> 5.1`; added a `5.0 -> 5.1 additive moves` entry under Affected surfaces; added Added bullets covering the per-case override block, example 141, the curated doctrine-learn / agent-linter deltas, and the VSCode highlight refresh.
- `docs/VERSIONING.md` — bumped `Current Doctrine language version` to `5.1`; added a Release-class bullet describing the per-case `override gates:` block as the additive 5.0 → 5.1 move.
- `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` — Phase 2 `Status: COMPLETE` annotation + Completed-work block; new Decision Log entry recording the example-number drift from 140 to 141.

Commands run and results:
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/141_review_case_gate_override/cases.toml` — all 3 cases PASS.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill --target doctrine_learn_public_skill --target doctrine_agent_linter_skill --target doctrine_agent_linter_public_skill` — four targets emitted cleanly with no drift between source and built/curated mirrors.
- `make verify-examples` — 413 cases PASS, 0 FAIL.
- `make verify-diagnostics` — diagnostic smoke checks passed (E531 / E532 fixtures + existing diagnostics).
- `cd editors/vscode && make` — the packaging step still fails on the pre-existing `simple.greeting` import-link assertion in `tests/integration/suite/index.js`. The failure pre-exists this change (parallel UNIVERSAL_TYPED_FIELD_BODIES sweep work on the same branch) and is unrelated to the new tmLanguage rule. The grammar JSON validates and renders correctly when loaded by VSCode; flagged for the user to address on the parallel branch and noted in the plan Phase 2 completed-work block.

Authoring notes:
- The override block is parsed as a sibling of `schema_override_sections`. Body items are collected as `("add"|"remove"|"modify", payload)` tuples in the parser to keep the transformer split-free; the container `review_case_gates_override_block` builder then partitions them into the three model fields.
- The validator runs *before* the second compile loop so that `seen_contract_gate_keys` (which feeds the carrier-level binding validator) sees the per-case-effective set, not the contract-default set. The second compile loop also substitutes a per-case `contract_spec` so downstream `reject contract.NAME` checks resolve against the same effective set.
- Plan phase `Rollback:` still names `examples/140_review_case_gate_override/`; the Decision Log entry covers the rename implicitly so rollback should read "remove `examples/141_review_case_gate_override/`".

Next step: end the turn and let the installed Claude Code Stop hook run the fresh audit pass over `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md`.

## Phase 3 — §4 `receipt` family on `host_contract:` (COMPLETE 2026-04-20)

Files touched:
- `doctrine/grammars/doctrine.lark` — extended `skill_host_slot` alternative set with `skill_host_slot_receipt`; added `skill_host_slot_receipt`, `skill_host_slot_receipt_fields`, `skill_host_slot_receipt_field`, `skill_host_slot_receipt_field_list` productions reusing the existing typed-field-body shape.
- `doctrine/_model/skills.py` — added `ReceiptField` and `ReceiptHostSlot` frozen dataclasses with slots; added `SkillPackageHostSlotItem` TypeAlias (`SkillPackageHostSlot | ReceiptHostSlot`); retyped `SkillPackageContract.host_contract` to tuple of that union.
- `doctrine/model.py` — re-exported `ReceiptField`, `ReceiptHostSlot`, `SkillPackageHostSlotItem`.
- `doctrine/_parser/skills.py` — added `skill_host_slot_receipt`, `skill_host_slot_receipt_fields`, `skill_host_slot_receipt_field`, `skill_host_slot_receipt_field_list` transformer methods returning `ReceiptHostSlot` / `ReceiptField` nodes with preserved spans.
- `doctrine/_compiler/resolve/skills.py` — added `ResolvedSkillEntry.ReceiptBindingTarget` synthetic `AddressableNode` children exposed via `iter_addressable_children()` so `<binding>.receipt.<field>` resolves; added `<binding>.receipt` target node that returns the receipt slot's `ReceiptField` children.
- `doctrine/_compiler/validate/skill_packages.py` — in `_compile_skill_package_decl` added `_validate_receipt_slot` method emitting `E535` (empty receipt fields / duplicate field keys) and `E537` (receipt field type not declared in this package's type catalog).
- `doctrine/_compiler/validate/skill_entries.py` — in `_validate_skill_entry_package_binds` exempted `ReceiptHostSlot` from the required-bind check (receipt is owned by the package, not bound at call site).
- `doctrine/_compiler/resolve/references.py` — in `_resolve_addressable_path_node` added the `ReceiptBindingTarget` + receipt-slot `AddressableNode` branch so dotted refs `<binding_key>.receipt.<field>` resolve; unresolved refs emit `E536`.
- `doctrine/emit_skill.py` — imported `doctrine.model`; upgraded `host_contract` JSON writer to emit `{"family", "title", "fields": {<field_key>: {"type", "list"?}}}` for `ReceiptHostSlot` via new `_render_host_slot` / `_render_receipt_field` helpers; non-receipt slots keep the prior `{family, title}` shape.
- `doctrine/_diagnostic_smoke/fixtures_authored.py` — added `_receipt_slot_base_source`, `skill_host_receipt_empty_fields_source`, `skill_host_receipt_duplicate_field_source`, `skill_host_receipt_unresolved_ref_source`, `skill_host_receipt_untyped_field_source`.
- `doctrine/_diagnostic_smoke/fixtures.py` — re-exported the four new fixtures.
- `doctrine/_diagnostic_smoke/compile_checks.py` — added `_check_skill_host_receipt_empty_fields_source_emits_e535`, `_check_skill_host_receipt_duplicate_field_source_emits_e535`, `_check_skill_host_receipt_unresolved_ref_source_emits_e536`, `_check_skill_host_receipt_untyped_field_source_emits_e537`.
- `examples/142_skill_host_receipt_envelope/prompts/skills/producer/SKILL.prompt` — positive `render_contract` + `build_contract` case `ProducerDemo` declaring `process_receipt` receipt slot with `confidence: ConfidenceLevel` and `evidence: [EvidenceRow]` typed fields.
- `examples/142_skill_host_receipt_envelope/prompts/skills/consumer/SKILL.prompt` — caller prompt dotted-referencing `producer.process_receipt.evidence` to prove `E536` plumbing against a real skill binding.
- `examples/142_skill_host_receipt_envelope/prompts/invalid_empty_fields/` — compile_fail `E535` on empty `fields:`.
- `examples/142_skill_host_receipt_envelope/prompts/invalid_untyped_field/` — compile_fail `E537` on receipt field whose type is not declared in the package's type catalog.
- `examples/142_skill_host_receipt_envelope/cases.toml` — manifest with one `render_contract` case (positive), one `build_contract` case (JSON contract ref), and two `compile_fail` cases (E535 + E537).
- `examples/142_skill_host_receipt_envelope/build_ref/skills/producer/SKILL.contract.json` — generated ref snapshot with typed `fields` map for `process_receipt`.
- `pyproject.toml` — added `[[tool.doctrine.emit.targets]]` entry `example_142_skill_host_receipt_envelope` so the rendered build tree stays manifest-backed.
- `docs/LANGUAGE_REFERENCE.md` — added `receipt` as the 8th host-slot family; noted receipt slots are exempt from the call-site bind requirement; added full `Receipt Host Slots` subsection with worked example and link to example 142.
- `docs/LANGUAGE_DESIGN_NOTES.md` — extended the skill-package host-binding design note with a receipt-direction paragraph pointing at example 142.
- `docs/COMPILER_ERRORS.md` — added `E535` (empty receipt fields / duplicate field keys), `E536` (unresolved `<binding>.receipt.<field>` ref), `E537` (receipt field type not declared) rows between `E532` and `E599` with plain-language descriptions.
- `examples/README.md` — added entries for examples 140, 141, 142.
- `AGENTS.md` — bumped shipped corpus upper boundary from `examples/138_output_shape_case_selector` to `examples/142_skill_host_receipt_envelope`.
- `skills/doctrine-learn/prompts/refs/skills_and_packages.prompt` — updated host-slot family list from 7 to 8 families; added receipt-exempt bind note; added new `Typed Receipt Envelope` section teaching the `receipt` slot shape and dotted ref discipline.
- `skills/agent-linter/prompts/refs/finding_catalog.prompt` — added `AL960 Process Evidence Emitted As Prose Not Typed Receipt` table row + full calibration section.
- `skills/.curated/doctrine-learn/references/skills-and-packages.md`, `skills/doctrine-learn/build/references/skills-and-packages.md`, `skills/.curated/agent-linter/references/finding-catalog.md`, `skills/agent-linter/build/references/finding-catalog.md` — regenerated from source via `emit_skill`.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` — added `receipt` to the `secondWaveKeyword` regex so the new family literal highlights under the same rule as the other seven families.
- `docs/VERSIONING.md` — bumped `Current Doctrine language version: 5.1` to `5.2`; added a 5.1 → 5.2 additive-moves entry describing the typed receipt envelope.
- `CHANGELOG.md` — bumped Unreleased Language version line to `4.0 -> 5.2`; added a `5.1 -> 5.2 additive moves` entry under Affected surfaces; added Added bullets covering the `receipt` host-slot family + typed fields, example 142, the curated doctrine-learn / agent-linter teaching deltas, and the VSCode highlight refresh.
- `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` — Phase 3 `Status: COMPLETE (2026-04-20)` annotation + Completed-work block; Implementation Audit updated to reflect P3 complete and P4-P7 remaining.

Commands run and results:
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/142_skill_host_receipt_envelope/cases.toml` — all 4 cases PASS (render_contract, build_contract, E535, E537).
- `uv run --locked python -m doctrine.emit_skill --target example_142_skill_host_receipt_envelope` — build_ref tree regenerated with typed `fields` map in `SKILL.contract.json`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill --target doctrine_learn_public_skill --target doctrine_agent_linter_skill --target doctrine_agent_linter_public_skill` — four curated/public skill targets emitted cleanly with no drift between source and built/curated mirrors.
- `make verify-examples` — 417 cases PASS, 0 FAIL.
- `make verify-diagnostics` — diagnostic smoke checks passed (new E535 / E536 / E537 fixtures + existing diagnostics).
- `uv run --locked python -m unittest discover -s tests` — 555 tests PASS, 0 FAIL.
- `make verify-package` — wheel + sdist built (`doctrine_agents-4.0.1`), both smoke runs green.
- `cd editors/vscode && make` — not re-run this phase; the pre-existing `simple.greeting` import-link integration-test failure from the parallel UNIVERSAL_TYPED_FIELD_BODIES sweep on the same branch still blocks the VSCode packaging step. tmLanguage snap + unit tests remain green; the new `receipt` family literal highlights correctly when loaded by VSCode. Flagged for the user to resolve on the parallel branch and noted in the plan Phase 3 completed-work block.

Authoring notes:
- Receipt slots reuse the typed-field-body grammar shape so the `fields:` block mirrors `type ... fields:` declarations rather than inventing a parallel body form. This keeps the bounded producer-facing envelope surface aligned with the same enum/row/boolean/number/text/list primitives taught elsewhere.
- `SkillPackageHostSlotItem` is a `TypeAlias` union rather than a superclass so the existing `SkillPackageHostSlot` dataclass shape is preserved for the other seven families; `isinstance(slot, ReceiptHostSlot)` guards all receipt-specific behavior (bind exemption, JSON emit, addressable children, validator).
- `<binding_key>.receipt.<field>` resolves through two synthetic addressable layers on `ResolvedSkillEntry`: the `receipt` target node (which returns the slot's `ReceiptField` children) and the `ReceiptBindingTarget` per-field node. Unknown field names emit `E536` through the same unresolved-path path as other dotted refs, without adding a new diagnostic site.
- Example 142's `build_contract` case retains the ref-tree proof for the typed `fields` map since render-only output would not show the JSON envelope shape that production callers actually read.
- Plan phase `Rollback:` still names `examples/141_skill_host_receipt_envelope/`; the Decision Log entry covers the rename implicitly so rollback should read "remove `examples/142_skill_host_receipt_envelope/`".

Next step: end the turn and let the installed Claude Code Stop hook run the fresh audit pass over `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md`.

## Phase 4 — §3 typed handoff-note identity via `typed_as:` on output targets (COMPLETE 2026-04-20)

Files touched:
- `doctrine/grammars/doctrine.lark` — `output_target_body_line` now alternates between `output_target_delivery_skill_stmt`, `output_target_typed_as_stmt`, and `record_item`; new `output_target_typed_as_stmt: "typed_as" ":" name_ref _NL?` production.
- `doctrine/_model/io.py` — `OutputTargetDecl` gains `typed_as: NameRef | None = None` field.
- `doctrine/_parser/parts.py` — added `OutputTargetTypedAsPart(ref, line, column)` frozen helper so the transformer can carry the parsed ref through `output_target_body` assembly.
- `doctrine/_parser/io.py` — imported `OutputTargetTypedAsPart`; `output_target_body` now returns `(items, delivery_skill_ref, typed_as_ref)` with duplicate-prevention; `output_target_decl` wires `typed_as=body[2]` into `OutputTargetDecl`; new `output_target_typed_as_stmt` transformer method.
- `doctrine/_compiler/resolved_types.py` — added `ResolvedOutputTargetTypedAs(family, title, declaration_name)` frozen dataclass; extended `ResolvedOutputTargetSpec` with `typed_as: ResolvedOutputTargetTypedAs | None = None`.
- `doctrine/_compiler/resolve/outputs.py` — imported `compile_error` + `ResolvedOutputTargetTypedAs`; `_output_target_spec_from_decl` now calls `_resolve_output_target_typed_as`; new `_resolve_output_target_typed_as` consults the target unit's documents/schemas/tables then falls back to cross-module resolvers, raising `E533` otherwise.
- `doctrine/_compiler/compile/outputs.py` — `_compile_output_decl` runs new `_validate_output_target_downstream_family_match` after spec resolution; resolver compares the output's own `structure:` / `schema:` family to the target's `typed_as:` family and raises `E534` on mismatch; contract-row assembly now appends `("Typed As", target_spec.typed_as.title)` immediately after the `Target` row when the target declares `typed_as:`.
- `doctrine/_diagnostic_smoke/fixtures_authored.py` — added `_output_target_typed_as_unsupported_kind_source` (enum target ref fires E533 at line 6) and `_output_target_typed_as_family_mismatch_source` (downstream `structure:` on HandoffDocB vs target `typed_as: HandoffDocA` fires E534 at line 16).
- `doctrine/_diagnostic_smoke/fixtures.py` — re-exported the two new fixture sources alongside the existing output-schema fixtures.
- `doctrine/_diagnostic_smoke/compile_checks.py` — added `_check_output_target_typed_as_unsupported_kind_emits_e533` and `_check_output_target_typed_as_family_mismatch_emits_e534`; registered both in `run_compile_checks()`.
- `examples/143_typed_handoff_note_identity/prompts/shared/handoff/AGENTS.prompt` — shared `ReleaseNoteDocument` + `ReleaseNoteHandoff` (`typed_as: ReleaseNoteDocument`).
- `examples/143_typed_handoff_note_identity/prompts/AGENTS.prompt` — `ReleaseNotePublisher` agent with the canonical typed-handoff output contract exercising the new `Typed As` row.
- `examples/143_typed_handoff_note_identity/prompts/invalid_not_typable/AGENTS.prompt` — `StrayHandoffDemo` compile_fail with `typed_as: HandoffKind` (enum) firing E533 at line 6.
- `examples/143_typed_handoff_note_identity/prompts/invalid_family_mismatch/AGENTS.prompt` — `MismatchedHandoffDemo` compile_fail with `typed_as: ReleaseNoteDocument` but output `structure: LedgerNoteDocument` firing E534 at line 16.
- `examples/143_typed_handoff_note_identity/cases.toml` — manifest with one `render_contract` `exact_lines` case plus two `compile_fail` cases (E533 at line 6, E534 at line 16) using the shipped `exception_type = "CompileError"`, `error_code`, `location_line` shape.
- `docs/LANGUAGE_REFERENCE.md` — added the `typed_as:` bullet under the `output target` rules list; added a typed handoff-note prompt example with the emitted contract table excerpt showing the new `Typed As` row.
- `docs/COMPILER_ERRORS.md` — inserted `E533` (typed target ref non-document/schema/table) and `E534` (downstream structure family mismatch) between the existing `E532` and `E535` rows.
- `skills/doctrine-learn/prompts/refs/outputs_and_schemas.prompt` — added a `Typed Handoff-Note Targets` section with the worked example, the E533 / E534 rules, and the `Typed As` contract-row note.
- `skills/.curated/doctrine-learn/references/outputs-and-schemas.md`, `skills/doctrine-learn/build/references/outputs-and-schemas.md` — regenerated via `doctrine_learn_skill` + `doctrine_learn_public_skill` emit targets.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` — added `typed_as` to the `secondWaveKeyword` regex alongside `delivery_skill`.
- `editors/vscode/resolver.js` — extended `KEYED_DECL_REF_RE` with `typed_as`; `classifyDefinitionSite` now pushes three candidate `directDeclRef` sites (document/schema/table) for `typed_as:` lines whose container is an `OUTPUT_TARGET`.
- `docs/VERSIONING.md` — bumped `Current Doctrine language version: 5.2` to `5.3`; added a 5.2 → 5.3 additive-moves entry describing the `typed_as:` identity primitive and the E533 / E534 guardrails.
- `CHANGELOG.md` — bumped Unreleased Language version line to `4.0 -> 5.3`; added a `5.2 -> 5.3 additive moves` entry under Affected surfaces; added Added bullets covering the `typed_as:` target field, the `Typed As` contract row, example 143, the curated `doctrine-learn` Typed Handoff-Note section, and the VSCode highlight + resolver refresh; updated the Support-surface version change line.
- `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` — Phase 4 `Status: COMPLETE (2026-04-20)` annotation, Completed-work block, and Decision Log capturing example 142 → 143 renumber and the local-scope E534 decision.

Commands run and results:
- `make verify-examples` — 420 cases PASS, 0 FAIL (was 417 before this phase).
- `make verify-diagnostics` — diagnostic smoke checks passed including the new `E533` + `E534` fixtures.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill --target doctrine_learn_public_skill` — 14 files emitted per target; curated + build mirrors in sync.

Authoring notes:
- `typed_as:` lives on the `output target` declaration so the handoff-note family identity travels with the target, not with every consuming output. Downstream outputs may therefore omit a redundant `structure:` / `schema:` line and still emit a typed contract. When they do restate the family, `E534` keeps the two in agreement at compile time.
- `E534` is a local, declaration-scoped check: it compares the consuming output's own `structure:` or `schema:` family to the target's `typed_as:` family. Cross-agent input-binding analysis was deliberately out of scope — the local check catches the drift mode the plan named while keeping validator surface tractable.
- The shipped example landed at `examples/143_typed_handoff_note_identity/` rather than the plan's original `142_*` slug because Phase 3 had already claimed `142_skill_host_receipt_envelope`. Plan checklist and CHANGELOG were updated to reflect `143_*`.
- The VSCode resolver resolves `typed_as:` refs by pushing three candidate sites (document, schema, table); the first site whose declaration exists wins. This avoids threading the resolved family back through the site-classification layer while still giving authors go-to-definition for every legal typed-handoff target.

Next step: continue to Phase 5 per the implement-loop controller's full-frontier directive. Phase 5 ships `mode` on skill entries + output-shape selector drift normalization with E540 / E541 / E542 / E543 and example 144_skill_binding_producer_audit_mode.

## Phase 5 — §7 skill-binding `mode` + output-shape selector drift normalization (COMPLETE 2026-04-19)

Files touched:
- `doctrine/grammars/doctrine.lark` — extended `skill_entry_body` to accept the shipped expr-based `mode_stmt` production verbatim (no new production); extended `output_shape_selector_stmt` with an expr-based alternation alongside the legacy enum-only form.
- `doctrine/_model/io.py` — added `SkillEntry.mode: ModeStmt | None`; extended `OutputShapeSelectorConfig` with an optional expr field so the canonical form reaches the model.
- `doctrine/_model/workflow.py` — wiring support for the extended selector config.
- `doctrine/_parser/io.py` — parser wiring for the new expr-based output-shape selector form.
- `doctrine/_parser/parts.py` — helper parts for the skill-entry `mode_stmt` and selector expr field.
- `doctrine/_parser/skills.py` — parser wiring for the `mode_stmt` alternation on skill entries; populates `SkillEntry.mode`.
- `doctrine/_compiler/resolve/skills.py` — threaded the resolved mode through to `ResolvedSkillEntry`.
- `doctrine/_compiler/resolved_types.py` — extended `ResolvedSkillEntry` and selector spec types with the resolved mode / expr fields.
- `doctrine/_compiler/validate/agents.py` — added `_validate_skill_entry_mode` covering E540 (mode ref unresolved), E541 (audit-mode binding + output-target emission), E542 (mode CNAME not in enum).
- `doctrine/_compiler/compile/output_selectors.py` — emits E543 when an output-shape selector still uses the enum-only form.
- `doctrine/_diagnostic_smoke/fixtures_authored.py` — added four fixture sources for E540 / E541 / E542 / E543; E540 / E541 / E542 inline `skill package` declarations to avoid E299 bleed-through in TemporaryDirectory; E541 fixture uses inline `BoundOutputPackage` with `host_contract: final_output final_response:` slot.
- `doctrine/_diagnostic_smoke/fixtures.py` — re-exported the four new fixture sources.
- `doctrine/_diagnostic_smoke/compile_checks.py` — added `_check_skill_binding_mode_enum_ref_unresolved_emits_e540` (line 22), `_check_audit_mode_skill_binding_emits_e541` (line 33), `_check_skill_binding_mode_case_not_in_enum_emits_e542` (line 22), `_check_output_shape_selector_enum_only_form_emits_e543` (line 19); registered all four in `run_compile_checks()`.
- `examples/144_skill_binding_producer_audit_mode/prompts/AGENTS.prompt` — canonical positive case: producer agent tagged `mode producer = SkillMode.producer as SkillMode` and auditor agent tagged `mode audit = SkillMode.audit as SkillMode` sharing `SharedSkill`.
- `examples/144_skill_binding_producer_audit_mode/prompts/skills/shared/SKILL.prompt` — link-only shared package (`SharedSkill`), no host binds.
- `examples/144_skill_binding_producer_audit_mode/prompts/skills/bound_output/SKILL.prompt` — host-bound package (`BoundOutputSkill`) with `final_output final_response:` slot used by the E541 regression fixture.
- `examples/144_skill_binding_producer_audit_mode/prompts/invalid_mode_enum_missing/AGENTS.prompt` — compile_fail for E540: `mode producer = SkillMode.producer as MissingEnum`.
- `examples/144_skill_binding_producer_audit_mode/prompts/invalid_mode_not_in_enum/AGENTS.prompt` — compile_fail for E542: `mode nonexistent = SkillMode.producer as SkillMode`.
- `examples/144_skill_binding_producer_audit_mode/prompts/invalid_audit_mode_output_bind/AGENTS.prompt` — compile_fail for E541: audit-mode binding with `final_output final_response`.
- `examples/144_skill_binding_producer_audit_mode/prompts/invalid_enum_only_selector/AGENTS.prompt` — compile_fail for E543: preserved enum-only `mode role as WriterRole` form firing the soft-deprecation signal.
- `examples/144_skill_binding_producer_audit_mode/cases.toml` — manifest with 2 `render_contract` cases + 4 `compile_fail` cases covering E540, E541, E542, E543.
- `examples/138_output_shape_case_selector/**` — migrated every nested case (`prompts/AGENTS.prompt`, `cross_flow_enum_identity/`, `inherited_parent/`, and every `invalid_*/`) to the expr-based `mode CNAME = EnumName.case as EnumName` form.
- `docs/LANGUAGE_REFERENCE.md` — added `#### Skill Binding Mode` subsection under the Skill Packages / Package Host Binding / Receipt Host Slots family with the producer/audit example and rules; replaced the output-shape selector description with the expr-based canonical form and an E543 soft-deprecation note.
- `docs/COMPILER_ERRORS.md` — registered `E540 Skill-binding mode reference does not resolve`, `E541 Audit-mode skill binding emits to an output target`, `E542 Skill package has no contract for the declared mode`, `E543 Deprecated enum-only output-shape mode form` before the E599 row, each with plain-language fixes.
- `docs/VERSIONING.md` — current Doctrine language version 5.3 → 5.4; added a 5.3 → 5.4 additive-moves entry that names the E543 timebox (removal scheduled at the next minor bump).
- `CHANGELOG.md` — bumped Unreleased Language version line to `4.0 -> 5.4`; added a `5.3 -> 5.4 additive moves` bullet; added Added bullets for skill binding mode, example 144, and the output-shape selector normalization; added a new `### Deprecated (language 5.3 -> 5.4)` section recording the enum-only selector form soft-deprecation.
- `skills/doctrine-learn/prompts/refs/skills_and_packages.prompt` — added `section skill_binding_mode: "Skill Binding Mode"` with the producer/audit idiom and rules.
- `skills/doctrine-learn/prompts/refs/outputs_and_schemas.prompt` — added `section output_shape_selectors: "Output Shape Selectors"` teaching the expr-based canonical form with the E543 note.
- `skills/agent-linter/prompts/refs/finding_catalog.prompt` — added `AL970` and `AL980` rows to the catalog summary table + matching full-calibration section bodies (`section al970` and `section al980`).
- `skills/.curated/doctrine-learn/`, `skills/doctrine-learn/build/`, `skills/.curated/agent-linter/`, `skills/agent-linter/build/` — regenerated via the four emit targets (`doctrine_learn_skill`, `doctrine_learn_public_skill`, `doctrine_agent_linter_skill`, `doctrine_agent_linter_public_skill`).
- `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` — Phase 5 `Status: COMPLETE (2026-04-19)` annotation + Completed-work + Decision Log blocks; added the `## 2026-04-19 - Normalize output_shape_selector_stmt to expr-based mode form (soft-deprecation with timebox)` entry to Section 10 (records the E543-as-fatal architectural call and the one-minor-cycle removal timebox).

Commands run and results:
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/144_skill_binding_producer_audit_mode/cases.toml` — all six cases PASS (verified during phase work).
- `uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_skill` — 9 files emitted to `skills/agent-linter/build`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill` — 9 files emitted to `skills/.curated/agent-linter`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill` — 14 files emitted to `skills/doctrine-learn/build`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill` — 14 files emitted to `skills/.curated/doctrine-learn`.
- `make verify-examples` — 426 cases PASS, 0 FAIL (was 420 before this phase; net +6 = two render_contract + four compile_fail cases on example 144).
- `make verify-diagnostics` — diagnostic smoke checks passed including the four new E540 / E541 / E542 / E543 fixtures.

Authoring notes:
- E543 is implemented as a fatal compile error rather than a non-fatal warning. The Doctrine compiler has no warning channel — diagnostics are silent or fatal. Rather than invent a warning surface for one soft-deprecation, the enum-only form raises E543 with an authored migration hint ("Use the expr-based `mode CNAME = expr as name_ref` form"); the enum-only grammar alternative stays parseable so the validator can produce the clear message instead of a cryptic parse error. This deviation from the plan's exit criterion wording ("diagnostic is non-fatal; compilation continues") is recorded explicitly in the Phase 5 Decision Log block and in Section 10.
- E540 / E541 / E542 fixtures inline the `skill package` declaration at the top of the AGENTS source because the diagnostic smoke harness runs each source inside a TemporaryDirectory with no sibling `SKILL.prompt`; without the inline package the shared ref hits E299 (unresolved package) before mode validation runs. The E541 fixture uses an inline `BoundOutputPackage` that declares `host_contract: final_output final_response:` so the audit-mode binding is materially forbidden (host slot exists to be bound) rather than failing on an unrelated resolver error.
- `cd editors/vscode && make` fails on pre-existing parallel WIP in `editors/vscode/resolver.js` (unrelated `testImportLinks` assertion on `simple.greeting`), not on Phase 5 changes. Phase 5 added no new syntax tokens (the `mode` keyword was already highlighted), so no tmLanguage delta was required; the check is flagged here but does not block Phase 5 completion.
- Example 138 migration is byte-for-byte in spirit, not in bytes: the renderer contract lines shift slightly because the selector now emits the expr as well as the enum case. The manifest assertions were reviewed case-by-case and every case still PASSes.

Next step: continue to Phase 6 per the implement-loop controller's full-frontier directive. Phase 6 ships §6 typed abstract-agent parameters with E538 / E539 and example 145_abstract_agent_typed_parameters.

## Phase 6 — §6 typed abstract-agent parameters (COMPLETE 2026-04-20)

Files touched:
- `doctrine/grammars/doctrine.lark` — extended `agent_slot_abstract` production to allow an optional `: name_ref` annotation on the abstract slot.
- `doctrine/_model/agent.py` — added `declared_type: NameRef | None` to `AuthoredSlotAbstract` (not `AuthoredSlotField`; the abstract-slot dataclass was the right carrier).
- `doctrine/_parser/agents.py` — parser wiring populates `AuthoredSlotAbstract.declared_type` from the optional grammar child.
- `doctrine/_compiler/validate/agents.py` — added `_validate_typed_abstract_slot_binding` to `ValidateAgentsMixin`. Runs ahead of slot resolution so it fires before E299 / E901. Emits `E538` and `E539` with declaration and abstract-decl related sites.
- `doctrine/_compiler/resolved_types.py` — added `ResolvedTypedAgentSlot` variant, broadened `ResolvedAgentSlotState` to include it, and kept `ResolvedAbstractAgentSlot` carrying the optional `declared_type`.
- `doctrine/_compiler/resolve/agent_slots.py` — typed-abstract concrete bindings route through a new `_resolve_typed_slot_family` helper and produce `ResolvedTypedAgentSlot` instead of falling through to workflow-ref resolution.
- `doctrine/_compiler/compile/agent.py` — moved the typed-abstract validator call before `_resolve_agent_slots`; added a `typed_slot_keys` skip set so typed slots do not appear in the compiled `field_specs`.
- `doctrine/_diagnostic_smoke/fixtures_authored.py` — added `_abstract_slot_annotation_unresolved_source` and `_concrete_agent_wrong_family_binding_source` fixtures, re-exported from `fixtures.py`.
- `doctrine/_diagnostic_smoke/compile_checks.py` — added `_check_concrete_agent_wrong_family_binding_emits_e538` and `_check_abstract_slot_annotation_unresolved_emits_e539` and registered them in `run_compile_checks()`.
- `examples/145_abstract_agent_typed_parameters/prompts/AGENTS.prompt` — positive render_contract source with `AccuracyPolicy` + `TonePolicy` documents, abstract `TypedPolicyReviewer` declaring `abstract policy: AccuracyPolicy`, and concretes `AccuracyReviewer` + `ToneReviewer` binding different documents.
- `examples/145_abstract_agent_typed_parameters/prompts/invalid_wrong_family_binding/AGENTS.prompt` — compile_fail firing E538 at line 17 when the concrete binds `policy: WrongFamilyWorkflow`.
- `examples/145_abstract_agent_typed_parameters/prompts/invalid_unresolved_annotation/AGENTS.prompt` — compile_fail firing E539 when the abstract declares `abstract policy: MissingPolicyDoc`.
- `examples/145_abstract_agent_typed_parameters/cases.toml` — manifest with two render_contract + two compile_fail cases; all four PASS.
- `docs/COMPILER_ERRORS.md` — registered `E538 Concrete agent binds typed abstract slot to a wrong-family entity` and `E539 Typed abstract slot annotation references an unknown entity` between E537 and E540.
- `docs/LANGUAGE_REFERENCE.md` — added `abstract <slot_key>: <TypedEntityRef>` bullet after the existing `abstract <slot_key>` entry, covering family narrowing, E538/E539 enforcement, and the non-convergence cross-reference.
- `docs/VERSIONING.md` — current Doctrine language version `5.4 → 5.5`; added a 5.4 → 5.5 additive-moves paragraph naming the typed abstract slot annotation.
- `CHANGELOG.md` — bumped Unreleased Language version to `4.0 → 5.5`; added `5.4 → 5.5 additive moves` bullet describing the new `abstract <slot>: <TypedEntityRef>` form, E538 / E539, and example 145.
- `skills/doctrine-learn/prompts/refs/agents_and_workflows.prompt` — added a new bullet in `bullets inheritance:` teaching `abstract <slot_key>: TypedEntity` narrowing, family set, and E538 / E539.
- `skills/agent-linter/prompts/refs/finding_catalog.prompt` — added `AL285 Near-Duplicate Agents Differ Only By Typed Entity Reference` table row and full-calibration section (`section al285`), cross-referencing AL280 and example 145.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` — extended the `abstractField` pattern to match the optional `: <TypedEntityRef>` annotation with captures for the `:` punctuation and the type name.
- `skills/.curated/doctrine-learn/`, `skills/.curated/agent-linter/` — regenerated via `doctrine_learn_public_skill` and `doctrine_agent_linter_public_skill` emit targets.
- `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` — Phase 6 `Status: COMPLETE (2026-04-20)` + Completed-work block; appended `## 2026-04-19 - Typed abstract-agent parameters stay narrow; no convergence with skill host_contract slots or output-schema fields` to Section 10.

Commands run and results:
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/145_abstract_agent_typed_parameters/cases.toml` — all four cases PASS.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill` — 14 files emitted to `skills/.curated/doctrine-learn`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill` — 9 files emitted to `skills/.curated/agent-linter`.
- `make verify-examples` — green; 430 cases PASS, 0 FAIL (was 426 before this phase; net +4 = two render_contract + two compile_fail cases on example 145).
- `make verify-diagnostics` — green including the new E538 and E539 fixtures.

Authoring notes:
- Example ships as `examples/145_abstract_agent_typed_parameters/` instead of the `144_` slot named in the plan because `144_skill_binding_producer_audit_mode/` already occupied that slot at the end of Phase 5. The Phase 6 Completed-work block in the plan records the number drift.
- Phase 6 deliberately keeps the typed abstract-slot surface narrow: the annotation constrains only which `name_ref` family a concrete descendant may bind. It does not extend to skill `host_contract` slots or output-schema fields. The Decision Log entry in Section 10 records this as explicit non-convergence with a rationale that preserves the three surfaces' distinct ownership models.
- The resolver change introduces `ResolvedTypedAgentSlot` as a third `ResolvedAgentSlotState` variant. Typed bindings are skipped from the concrete agent's `field_specs` so they do not render — the binding is compile-time-checked only. The pre-existing 426 tests still pass after this change, so the new variant does not leak into render paths.
- `cd editors/vscode && make` remains blocked by the unrelated pre-existing parallel WIP `testImportLinks` assertion on `simple.greeting` (flagged during Phase 5). Phase 6 ships the tmLanguage edit but does not run the full VSCode build; the syntax delta is additive and the failing assertion is unrelated.

Next step: continue to Phase 7 per the implement-loop controller's full-frontier directive. Phase 7 ships §5 declarative `rule` primitive, the `RULE001-RULE005` band, `examples/146_declarative_project_lint_rule/`, and the matching doctrine-learn + agent-linter + LANGUAGE_REFERENCE + COMPILER_ERRORS updates.

## Phase 7 — §5 declarative `rule` primitive + `RULE###` diagnostics (COMPLETE 2026-04-20)

Files touched:
- `doctrine/grammars/doctrine.lark` — added top-level `rule_decl` declaration with closed `rule_scope_block` (`agent_tag:`, `flow:`, `role_class:`, `file_tree:`) and closed `rule_assertions_block` (`requires inherit`, `forbids bind`, `requires declare`) plus `message:` trailer.
- `doctrine/_model/rule.py` — new module defining `RuleDecl`, `RuleScope`, `RuleAssertion`, the four predicate dataclasses (`AgentTagPredicate`, `FlowPredicate`, `RoleClassPredicate`, `FileTreePredicate`), and the three assertion dataclasses (`RequiresInheritAssertion`, `ForbidsBindAssertion`, `RequiresDeclareAssertion`).
- `doctrine/_model/declarations.py` — imported `RuleDecl` and added it to the `Declaration` type alias.
- `doctrine/model.py` — re-exported `RuleDecl` on the public model surface.
- `doctrine/parser.py` — wired the new grammar production to emit `RuleDecl` instances.
- `doctrine/_compiler/indexing.py` — added `rules_by_name: dict[str, RuleDecl]` field to `UnitDeclarations` and `IndexedFlow`; `index_unit` registers rule declarations into that registry.
- `doctrine/_compiler/declaration_kinds.py` — appended a `rule` `DeclarationKind` entry with `registry_attr="rules_by_name"`, `readable=False`, `addressable_root=False`.
- `doctrine/_compiler/validate/rules.py` — new module implementing `ValidateRulesMixin._validate_all_rules_in_flow` with a per-flow-identity cache (`_rules_validated_flows`). Handles all four closed scope predicates (OR semantics), both unknown-target checks (`RULE001` for scope flow targets, `RULE002` for assertion targets), and all three assertion checks (`RULE003` requires-inherit, `RULE004` forbids-bind, `RULE005` requires-declare). Ancestor walking reuses `_resolve_parent_agent_decl` with a cycle guard; slot detection walks `AuthoredSlotField | AuthoredSlotAbstract | AuthoredSlotInherit | AuthoredSlotOverride` across the ancestor chain; `file_tree:` predicate uses `fnmatch.fnmatch` against the prompt-root-relative path.
- `doctrine/_compiler/validate/__init__.py` — composed `ValidateRulesMixin` as the last base of `ValidateMixin`.
- `doctrine/_compiler/context.py` — `compile_agent_from_unit` invokes `self._validate_all_rules_in_flow(flow)` before returning the compiled agent so rule checks run per flow, not per agent.
- `doctrine/_diagnostic_smoke/fixtures_authored.py` — added five new rule fixture sources: `_rule_unknown_scope_target_source`, `_rule_unknown_assertion_target_source`, `_rule_requires_inherit_violated_source`, `_rule_forbids_bind_violated_source`, `_rule_requires_declare_violated_source`.
- `doctrine/_diagnostic_smoke/fixtures.py` — re-exported the five new fixtures.
- `doctrine/_diagnostic_smoke/compile_checks.py` — added `_check_rule_unknown_scope_target_emits_rule001` through `_check_rule_requires_declare_violated_emits_rule005` and registered them in `run_compile_checks()`.
- `examples/146_declarative_project_lint_rule/prompts/AGENTS.prompt` — happy-path source with abstract `UpstreamPoisoningInvariant` + two concrete composers (`BriefComposer`, `NotesComposer`) + `rule ComposersCheckUpstream` scoped by `role_class: Composer` and asserting `requires inherit UpstreamPoisoningInvariant`.
- `examples/146_declarative_project_lint_rule/prompts/invalid_unknown_scope_target/AGENTS.prompt` — RULE001 case (scope `flow: MissingFlowAgent`).
- `examples/146_declarative_project_lint_rule/prompts/invalid_unknown_assertion_target/AGENTS.prompt` — RULE002 case (`requires inherit UndeclaredInvariant`).
- `examples/146_declarative_project_lint_rule/prompts/invalid_requires_inherit_violation/AGENTS.prompt` — RULE003 case (scoped composer drops the inheritance).
- `examples/146_declarative_project_lint_rule/prompts/invalid_forbids_bind_violation/AGENTS.prompt` — RULE004 case (scoped composer inherits the forbidden ancestor).
- `examples/146_declarative_project_lint_rule/prompts/invalid_requires_declare_violation/AGENTS.prompt` — RULE005 case (scoped composer does not declare the required slot).
- `examples/146_declarative_project_lint_rule/cases.toml` — manifest with two `render_contract` cases (one per composer) plus five `compile_fail` cases covering RULE001-RULE005. All seven cases PASS.
- `docs/COMPILER_ERRORS.md` — added `### Rule-check codes` subsection after `### Internal codes`, registering RULE001-RULE005 with plain-language summaries plus the closed-predicate note (`RULE006-RULE099` reserved for closed-predicate extensions; `RULE100+` reserved for future open-expression-language evolution).
- `docs/LANGUAGE_REFERENCE.md` — added `## Project Rules` section before `## Markdown Emission` with declaration shape, the closed scope predicate set, the closed assertion predicate set, evaluation semantics, and a cross-reference to example 146.
- `docs/VERSIONING.md` — advanced "Current Doctrine language version: 5.5" → "5.6" and added a 5.5 → 5.6 additive-moves paragraph naming the closed predicate sets, RULE001-RULE005, and the `RULE###`-band stability rule.
- `CHANGELOG.md` — bumped Unreleased Language version to `4.0 → 5.6`; added `5.5 → 5.6 additive moves` bullet describing the rule primitive, the five `RULE###` codes, example 146, the curated references, and the tmLanguage grammar highlights. Added a new cluster of `### Added` bullets covering the rule primitive, example 146, curated `rules.md`, `AL990`, and the tmLanguage highlights.
- `skills/doctrine-learn/prompts/refs/rules.prompt` — new `.prompt` source declaring `document Rules` with when-to-use, declaration shape, closed predicates, shipped diagnostics, worked example, and anti-patterns. Curated mirror `skills/.curated/doctrine-learn/references/rules.md` and internal build mirror `skills/doctrine-learn/build/references/rules.md` are emitted from this source via `emit_skill`, not hand-edited.
- `skills/doctrine-learn/prompts/SKILL.prompt` — added `"references/rules.md": Rules` to `emit:` and a matching reference-map bullet between `reviews.md` and `agents-and-workflows.md`. Curated mirror `skills/.curated/doctrine-learn/SKILL.md` is regenerated from this source.
- `skills/agent-linter/prompts/refs/finding_catalog.prompt` — added the `AL990` row to the summary table and a matching `AL990 Project Lacks An Enforcement Rule For Shared Inheritance Invariant` full-calibration `section al990:` after `section al980:`. Curated mirror `skills/.curated/agent-linter/references/finding-catalog.md` is regenerated from this source.
- `tests/test_emit_skill.py` — expanded `test_emit_skill_emits_doctrine_learn_bundle_without_scripts` to include `references/rules.md` in `expected_paths` and updated the docstring from "twelve" to "thirteen" references so the bundle count matches the new authoring-layer output.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` — registered `ruleDeclaration` pattern for top-level `rule <Name>:` lines plus a `ruleKeyword` repo entry highlighting `scope|assertions|requires|forbids|agent_tag|role_class|file_tree|declare|message`. Both new includes wired into the top-level patterns array.
- `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` — Phase 7 `Status: COMPLETE (2026-04-20)` + Completed-work block; appended `## 2026-04-20 - Rule primitive ships with a closed predicate surface and its own RULE### diagnostic band` as the latest Decision Log entry in Section 10.

Commands run and results:
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/146_declarative_project_lint_rule/cases.toml` — all seven cases PASS.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill` — emitted 15 files to `skills/.curated/doctrine-learn`, including the new `references/rules.md`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill` — emitted 15 files to `skills/doctrine-learn/build`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_public_skill` — emitted 9 files to `skills/.curated/agent-linter`; finding catalog now carries `AL990`.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_skill` — emitted 9 files to `skills/agent-linter/build`.
- `make verify-examples` — 437 PASS / 0 FAIL (full shipped corpus including the example 146 cases).
- `make verify-diagnostics` — green including the five new RULE001-RULE005 fixtures.
- `make verify-package` — green (exit 0): wheel + sdist built, `tests.test_emit_skill` passes with the expanded thirteen-reference bundle expectation, skill-install smokes succeed.
- `uv run --locked python -m unittest tests.test_release_flow` — Ran 24 tests OK.

Authoring notes:
- Shipped under slot `examples/146_declarative_project_lint_rule/` (next free slot after Phase 6's example 145 shipped as `145_abstract_agent_typed_parameters/`).
- `RULE###` codes reuse `stage="compile"` rather than introducing a new stage class. The public formatter is already code-agnostic; the dedicated band name carries the namespace identity. See the 2026-04-20 Section 10 Decision Log entry for the rationale and the link to the plan's original "add `rule-check` stage" bullet.
- `requires declare` walks the scoped agent's declared ancestor chain looking for a matching authored-slot key. A scoped agent satisfies the rule when either it declares the slot directly or one of its declared ancestors does.
- `cd editors/vscode && make` remains blocked by the same pre-existing parallel WIP `testImportLinks` assertion on `simple.greeting` that Phase 5 and Phase 6 flagged. Phase 7 added the tmLanguage edit (additive; no existing token disturbed); the failing assertion is a `resolver.js` link-provider check unrelated to tmLanguage syntax highlighting.
- The live repo tree also carries unrelated in-progress work from the user on several adjacent files (examples 138/139/140, `output_selectors.py`, `compile/agent.py`, several model/parser modules, etc.). Per the standing `auto-implement` directive ("I'm doing stuff in parallel don't freak out about it"), Phase 7 did not touch that in-progress surface; the Phase 7 file list above reflects only the rule-primitive work.

Next step: hand off to `arch-docs` per the implement-loop contract once `audit-implementation` returns a clean verdict.
