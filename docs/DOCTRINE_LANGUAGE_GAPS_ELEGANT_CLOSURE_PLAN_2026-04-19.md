---
title: "Doctrine - Language Gaps Elegant Closure - Architecture Plan"
date: 2026-04-19
status: active
fallback_policy: forbidden
owners: [Amir Elaguizy]
reviewers: []
doc_type: architectural_change
related:
  - docs/LAYERED_AUTHORING_LANGUAGE_GAPS_2026-04-19.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/REVIEW_SPEC.md
  - docs/COMPILER_ERRORS.md
  - skills/.curated/agent-linter/SKILL.md
  - skills/.curated/doctrine-learn/SKILL.md
---

# TL;DR

- **Outcome**: doctrine closes the six real language gaps surfaced by the 2026-04-19 layered-authoring audit (§2, §3, §4, §5, §6, §7) and normalizes the peer patterns they touch so authors see one consistent language across reviews, skills, agents, outputs, and lint. Gap §1 (typed `gate`) is shipped today; the closure work there is teaching, docs, and lint, not grammar.
- **Problem**: doctrine already has most of the primitives needed (typed declarations with symbol references, `override`, `family:` slot enums, `mode` as a case selector, agent inheritance, compiler error codes). But the primitives stop one step short of where authors need them, and the places that do exist aren't uniformly taught or cross-referenced — the psflows audit missed §1 entirely because `gates:` lives in a schema block and never surfaces in doctrine-learn's review chapter.
- **Approach**: each gap is closed by extending an existing primitive rather than inventing a parallel mechanism. `override gates:` inside a review case (§2) reuses agent-slot `override` grammar. `receipt` as a new `family:` value on `host_contract:` (§4) extends the shipped slot-family enum. `mode` on skill binding (§7) reuses the review-case mode selector. Typed handoff-note identity (§3) extends `output_target_decl` with a `typed_as:` binding that downstream agents read as a typed input family. Typed parameters on abstract agents (§6) follow the skill `host_contract` slot pattern, so typed slots bind the same way in both places. Declarative lint rules (§5) ship as a top-level `rule` declaration that follows the same declare-then-reference shape as `gate`/`skill`/`document`/`table`, with `RULE###` diagnostics landing alongside existing `E###` codes in the shared catalog. The shipped §1 gap is closed by teaching: doctrine-learn gets a "typed gates vs inline gate prose" section, agent-linter gets a finding for gates declared as free-form prose when a `gates:` block would own them, and examples surface the pattern at both the contract and the critic edge.
- **Plan**: seven execution phases (the peer-pattern audit originally scoped as P0 is complete in §3.2 and §6.1 and is not a separate execution phase). P1 `gate` teaching/linter/example normalization (no grammar; closes §1's teaching gap). P2 `override gates:` on review cases (§2, block-level override reuse). P3 `receipt` family on `host_contract:` (§4, slot-family enum extension). P4 typed handoff-note identity via `typed_as:` on `output_target_decl` (§3, typed downstream binding). P5 `mode` on skill binding plus output-shape selector drift normalization (§7, shared `mode_stmt` production, soft-deprecates enum-only form with `E543`). P6 typed parameters on abstract agents (§6, narrow typed annotation; explicit non-convergence with skill host_contract slots and output-schema fields). P7 declarative `rule` primitive + `RULE###` diagnostics (§5). The original P3/P4 bundlings (§3+§4 and §6+§7) split into single-gap phases because each pair touches different grammar productions, different validators, and ships independently testable units; biasing toward more phases keeps each one fully understood and safe to build on. Each phase ships grammar (if applicable), model, compiler validation, manifest-backed examples, docs, and doctrine-learn/agent-linter teaching in one move so the language stays coherent as the surface grows.
- **Non-negotiables**: no parallel mechanisms for the same idea (one `mode` shape, one `override` shape, one `family:` shape, one typed-parameter shape). No runtime shims or fallback paths. No prose-only gates, modes, or rules authors are expected to keep consistent by discipline. Every new primitive ships with an `E###` compile-time check, a manifest-backed example, and a doctrine-learn teaching surface in the same phase. Every new grammar move preserves existing examples verbatim. Peer-pattern normalization is scope, not follow-up.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-19
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

After this plan ships, an author reading doctrine's language reference, writing a fresh layered-review pipeline, and running it through the agent-linter can:

1. Declare a `gate` once in a contract and reference it by symbol from any review case; typos fail at compile time with `E477` (shipped) — falsified if an author still has to spell the gate ID twice as prose.
2. Give different review cases different gate bundles within one review family using `override gates:`, without declaring separate contracts per case — falsified if authors still split to N contracts when all they wanted was a per-case gate delta.
3. Declare a skill's emitted receipt envelope inside `host_contract:` as `family: receipt` and bind it by field name on a downstream critic — falsified if a critic still reads receipts by bashing into a CLI and parsing prose.
4. Declare a producer's handoff note output with typed identity so the next agent binds it as a typed input without reconstructing structure from a ledger — falsified if handoffs with typed tables still round-trip through prose.
5. Declare a project-local `rule` that fires across the agent graph ("every composer-style agent must inherit `UpstreamPoisoningInvariant`") and break the build when violated — falsified if that invariant still rests on comment-block discipline.
6. Write one abstract agent with typed policy parameters and N thin concrete descendants that bind those parameters — falsified if the N concretes still restate the shared workflow inline with the variable spliced by hand.
7. Bind the same skill package in producer mode at a producer and audit mode at a critic, with the compiler distinguishing them — falsified if audit still means "call the producer skill again and compare prose."

Across all seven: the syntax and semantics of typed entity declaration, `override`, `family:`, `mode`, typed parameters, and declarative rules behave the same way everywhere they appear. An author's mental model from one context transfers to every other context. Falsified if a user has to learn a new shape to express the same idea in a different corner of the language.

## 0.2 In scope

**Requested behavior scope** (what authors will be able to express):

- §2 `override gates:` inside a `review_case` block.
- §3 typed handoff-note identity on `output_target_decl` that binds as a typed input on downstream agents.
- §4 `family: receipt` on `package_host_contract_block` with typed field references.
- §5 top-level `rule` declaration with declarative scope + assertion DSL, enforced at compile time with new `RULE###` or `E###` diagnostics.
- §6 typed parameters on `abstract agent` declarations with named-value binding on concrete descendants.
- §7 `mode` parameter on skill binding at the point of use.
- §1 teaching-only closure: doctrine-learn, agent-linter, and examples normalize around the already-shipped `gates:` block.

**Allowed architectural convergence scope** (internal refactors):

- Normalize the `mode` grammar so review-case mode selection and skill-binding mode selection share one production.
- Normalize the `override` grammar so agent-slot override, review-case gate override, and any future override site share one production.
- Normalize the typed-parameter grammar so abstract-agent parameters and skill `host_contract` slots share one declaration shape.
- Extend `family:` enum consistently — `receipt` and the handoff-note family plug into the same slot-family machinery as `input`, `output`, `document`, `analysis`, `schema`, `table`, `final_output`.
- Sweep existing grammar productions that express the same idea slightly differently and converge them on one canonical production. Concrete candidates land in `# 3.2` and `# 6`; the phase plan resolves each.
- Update docs (`LANGUAGE_REFERENCE.md`, `REVIEW_SPEC.md`, `COMPILER_ERRORS.md`), doctrine-learn references, and agent-linter finding catalog for every primitive extended. This is not follow-up work.

**Adjacent surfaces** (must move with the same phase that changes their contract):

- `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`.
- `skills/.curated/doctrine-learn/references/*.md` and the built `skills/doctrine-learn/prompts/refs/*.prompt` mirrors.
- `skills/.curated/agent-linter/references/*.md` and the built `skills/agent-linter/prompts/refs/*.prompt` mirrors.
- `examples/` corpus — every new primitive ships with at least one manifest-backed example, every normalization ships a regression example.
- `editors/vscode/` grammar files if the syntax surface changes.

## 0.3 Out of scope

- Runtime orchestration for the new primitives — doctrine stays on the authoring side. Rally is where handoff-note typed identity lands on the runtime side; this plan extends doctrine's declaration surface only, with the rally delivery contract tracked as a separate work item.
- Performance tuning, caching, or compiler speedups unrelated to the new primitives.
- New product features that did not appear in the 2026-04-19 audit (no "templating," "plugins," "config layers," or speculative extension points).
- Retroactive deprecation of existing examples — existing examples keep working verbatim.
- Language version jump beyond what's needed (language version moves only if a breaking change is required; default posture is additive).

## 0.4 Definition of done (acceptance evidence)

- `make verify-examples` passes with at least one new manifest-backed example per closed gap.
- `make verify-diagnostics` passes with new `E###` or `RULE###` codes for each new compile-time check.
- `uv run --locked python -m unittest tests.test_release_flow` passes for any release-adjacent surface touched.
- Every touched `docs/*.md` and every `skills/.curated/*/references/*.md` surface is updated in the same phase that changes the language behavior.
- doctrine-learn ships a teaching section for every new or normalized primitive before the phase closes — no "follow-up teaching" entries.
- agent-linter ships a finding (AL###) for the inline-prose-instead-of-typed-primitive anti-pattern for every new primitive before the phase closes.
- A fresh psflows-style layered-review author (simulated by re-reading the 2026-04-19 audit doc against shipped doctrine) can express every gap with the shipped primitive, without prose workarounds.
- Peer-pattern normalization targets in `# 3.2` and `# 6` each resolve to "shipped" or "explicit deferred with Decision Log entry."

## 0.5 Key invariants (fix immediately if violated)

- **No parallel mechanisms.** One `mode` syntax, one `override` syntax, one `family:` enum, one typed-parameter shape. If two parts of the language express the same idea differently, converge them in the phase that touches either.
- **No fallbacks.** Fail-loud compile errors at the new boundaries. No runtime shims for declarations that didn't exist before.
- **No dual sources of truth.** Every new primitive lives in grammar + model + compiler + example + docs + doctrine-learn + agent-linter. Missing one surface is missing the primitive.
- **No prose-only replacements for typed primitives.** Once the typed primitive ships, authors who keep the old prose form get a compile or lint warning.
- **No silent behavior drift in existing examples.** Every example 01–138 still passes its manifest verbatim after every phase.
- **Peer-pattern normalization is scope.** A phase that touches `mode`/`override`/`family:` in one place and not the other is incomplete.
- **Teaching surfaces ship with grammar surfaces.** A phase that ships a primitive without a doctrine-learn teaching entry and an agent-linter finding is incomplete.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. **Peer-pattern convergence.** Every new primitive must reuse an existing grammar shape or converge a drifted one. Authors must not learn two ways to say the same thing.
2. **Compile-time teeth.** Every closure must ship a new E-code or RULE-code with `make verify-diagnostics` proof. No prose-only enforcement.
3. **Teaching parity.** doctrine-learn and agent-linter move in the same phase as grammar. A shipped primitive without teaching is unshipped.
4. **Example-first proof.** One manifest-backed example per new primitive. The example is the acceptance artifact.
5. **Additive by default.** Existing examples keep working. Breaking changes only when explicitly approved with language-version bump.

## 1.2 Constraints

- Doctrine's shipped truth discipline: `doctrine/grammars/doctrine.lark`, `doctrine/model.py`, `doctrine/_compiler/`, and `examples/` are the source of truth; docs and skills follow shipped code.
- Definition-of-done in `AGENTS.md` requires `make verify-examples`, `make verify-diagnostics` (when diagnostics change), and `make verify-package` (when package metadata changes). These run per phase, not at the end.
- Plain-language hard requirement: docs and teaching surfaces must be 7th-grade-readable. New compiler errors and lint findings must read as plain, direct English.
- `fallback_policy: forbidden` — no runtime shims, no opt-in flags, no silent feature detection.

## 1.3 Architectural principles (rules we will enforce)

- **Declare-then-reference is the universal shape.** Every typed entity (gate, skill, agent, document, table, rule, typed parameter, receipt, handoff note) is declared in one place and referenced by symbol from others. Reference mismatch is a compile error.
- **Slot families are a closed enum, extended consciously.** Adding `receipt` and a handoff-note family is not "anything goes" — the grammar still lists the finite set.
- **`override` is one grammar production.** Agent-slot override, review-case gate override, and any future override site parse and validate through one path.
- **`mode` is one grammar production.** Review-case mode selector and skill-binding mode selector parse through one path and validate against one registry per context.
- **Typed parameters are one shape.** Abstract agent parameters and skill `host_contract` slots share one declaration and binding syntax.
- **Compile-time enforcement over prose discipline.** Invariants that matter end up as E-codes or RULE-codes, not as comment-block warnings on base agents.
- **Teaching follows shipped truth, not intent.** When grammar moves, the doctrine-learn reference and the agent-linter finding catalog move in the same phase.

## 1.4 Known tradeoffs (explicit)

- **Normalization cost vs. grammar stability.** Converging drifted grammar productions touches more of the parser than strictly needed for gap closure. Accepted because letting drift accumulate costs more per new primitive over time.
- **Additive-only vs. retiring legacy shapes.** Keeping old examples working verbatim means some legacy shapes stay in the grammar during transition. Accepted because breaking every existing example for elegance is not elegant.
- **One big plan vs. seven small plans.** Bundling into one doc risks scope creep; splitting risks per-gap fixes that each bend the grammar a different way. Accepted the bundle because peer-pattern normalization is a first-class goal and cannot be delivered one gap at a time.
- **Rule DSL expressiveness vs. compiler simplicity.** A full rule DSL (with boolean logic, pattern matching, cross-graph queries) is out of scope for P5's first cut; the initial `rule` surface covers the enumerable inheritance/binding assertions the audit names and leaves richer rule shapes as a Decision Log follow-up.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Doctrine's grammar at `doctrine/grammars/doctrine.lark` ships typed entities (`gate`, `skill`, `agent`, `document`, `table`), `override` on agent slots, `mode` on review-case selectors, and a `family:` slot enum on `host_contract:` blocks.
- The `examples/` corpus at 01–138 demonstrates every shipped primitive with manifest-backed proofs.
- `docs/LANGUAGE_REFERENCE.md` and `docs/REVIEW_SPEC.md` teach the shipped surface.
- doctrine-learn and agent-linter are judgment-first skills that wrap the shipped surface with reference material and heuristic findings.

## 2.2 What's broken / missing (concrete)

- §2: review cases cannot override gates inline; authors split to N contracts when the cases should share one contract with case-scoped gate overrides.
- §3: `output_target_decl` has no typed identity, so note-appended outputs cannot round-trip as typed inputs downstream.
- §4: `package_host_contract_block`'s `family:` enum does not include `receipt`, so skills cannot declare typed receipt envelopes.
- §5: no project-author-definable lint rule DSL exists. `skills/.curated/agent-linter/SKILL.md:25` explicitly treats the linter as judgment-first, not declarative-rule.
- §6: abstract-agent slots accept only `string | name_ref`, not typed parameters.
- §7: `mode` exists only as a review-case selector; skill binding has no mode parameter.
- §1: shipped today, but doctrine-learn's review references do not teach the `gates:` block strongly enough to prevent a fresh author from writing gate IDs as inline prose. The 2026-04-19 audit missed §1 entirely for this reason.
- Peer-pattern drift risk: whenever a gap is closed without normalizing its sibling productions, authors accumulate inconsistent mental models. `# 3.2` and `# 6` will produce the concrete audit.

## 2.3 Constraints implied by the problem

- Closures must reuse shipped primitives whenever possible; new primitives are last resort.
- Teaching surfaces are a first-class deliverable because §1's teaching gap shows that shipped-but-untaught is effectively unshipped.
- Peer-pattern audit must run before phase planning locks, because the audit result determines which grammar productions phase-plan must touch.

# 3) Research Grounding (external + internal "ground truth")

<!-- arch_skill:block:research_grounding:start -->

## 3.1 External anchors (papers, systems, prior art)

- ESLint custom-rule registry — **reject as model, adopt as cautionary tale.** Custom-rule registries tend toward open JavaScript-predicate authoring, which doctrine's "no scripts in the language" posture forbids. Take only the lesson: declarative rule identities with named codes (e.g., `no-unused-vars`) and scoped selectors.
- Semgrep pattern rules — **adopt the rule-identity + scope-selector + message-template shape.** Semgrep rules declare `id`, `languages`, `patterns`, `message`, `severity` as structured fields. The P5 `rule` primitive follows this pattern closely: name, scope predicate, assertion predicate, failure message. No pattern-matching DSL — enumerated predicates only in the first cut.
- Scala implicit parameters / Rust generic type parameters — **reject as full typing model, adopt narrow idea.** Full generics would force doctrine into variance/bounds territory. The narrow idea we adopt for §6: a typed parameter is a named slot whose declared type is a doctrine typed-entity reference (document, schema, enum, agent), bound on the concrete descendant with a `name_ref`. That is additive to doctrine's existing `name_ref` vocabulary.
- 2026-04-19 psflows audit (`docs/LAYERED_AUTHORING_LANGUAGE_GAPS_2026-04-19.md`) — **adopt the six real gap identifications; reject the §1 framing.** The audit's §1 claim that gates are "prose tokens" is wrong against shipped truth: schemas ship typed `gates:` blocks with symbol references (`contract.NAME`) and E477 enforcement. The audit's §1 framing is itself evidence of the teaching gap P1 closes.

## 3.2 Internal ground truth (code as spec)

### Authoritative behavior anchors (do not reinvent)

- **Typed entity declaration shape** (universal): `doctrine/grammars/doctrine.lark:58-80`. Every exportable top-level declaration follows `KEYWORD CNAME [inheritance?] ":" [string?] _NL _INDENT body _DEDENT`. Applies to `analysis_decl`, `decision_decl`, `schema_decl`, `table_decl`, `document_decl`, `review_decl`, `skill_decl`, `enum_decl`, `output_target_decl`, `output_shape_decl`, `output_schema_decl`. **Canonical. P5's new `rule` declaration and any new typed entities must follow this shape.**
- **Typed `gates:` block** (§1's shipped surface): `doctrine/grammars/doctrine.lark:382-386` (`schema_gates_block`, `schema_gate_item`); model `SchemaGate`, `SchemaGatesBlock` in `doctrine/_model/*`. Example proof: `examples/57_schema_review_contracts/prompts/AGENTS.prompt` (gate declarations); `examples/45_review_contract_gate_export_and_exact_failures` (symbol references via `contract.NAME`).
- **Symbol reference for typed entities**: `contract_gate_ref` at `doctrine.lark:256` (`"contract" "." CNAME`) → `ContractGateRef` in model. Enforcement: `doctrine/_compiler/validate/review_semantics.py:174,186,196,231,265` emits E477 when a `contract.NAME` ref doesn't resolve. **Canonical for `entity.symbol` typed refs; nothing else in the grammar uses this shape under a different name.**
- **`family:` slot enum**: `package_host_contract_block` at `doctrine.lark:888-896` with `package_host_slot_family: input | output | document | analysis | schema | table | final_output`. **Canonical.** No parallel "kind:" or "type:" enum expresses the same idea elsewhere.
- **Agent-slot `override`**: `agent_slot_override` at `doctrine.lark:143` (`"override" CNAME ":" slot_value`) → `AuthoredSlotOverride` in `doctrine/_model/agent.py:33-36`. This is the **parameter-level** override shape.
- **Block-level section override** (distinct from parameter override): `review_override_*` (`doctrine.lark:218-224`), `schema_override_sections` (`doctrine.lark:397-400`), `analysis_override_section` (`:323`), `document_override_block` (`:426`). Shape: `"override" BLOCK_NAME ":" _NL _INDENT ... _DEDENT`. **Canonical for hierarchical section replacement inside a typed container.**
- **`mode` as variant selector** — two drifted sites today:
  - `review_selector_stmt` at `doctrine.lark:206`: `"mode" CNAME "=" expr "as" name_ref`
  - `mode_stmt` in law block at `doctrine.lark:957`: same shape — `"mode" CNAME "=" expr "as" name_ref`
  - `output_shape_selector_stmt` at `doctrine.lark:740`: `"mode" CNAME "as" name_ref` (no `=expr`) — **drifted peer**
  - Models: `ReviewSelectorConfig` (review.py:66-70), `ModeStmt` (law.py:31), `OutputShapeSelectorConfig` (io.py:255-258)
  - **Canonical convergence target: law/review expr-based form.** Output-shape's enum-only form is a legitimate drift to converge on the expr-based form in this plan (§7 and peer-pattern normalization).
- **Abstract agent + slot value**: `doctrine.lark:82-105` (inheritance), `:139-146` (`agent_slot_field: CNAME ":" slot_value`, `?slot_value: string | name_ref`) → `AuthoredSlotField(key, value: WorkflowSlotValue)` in `doctrine/_model/agent.py:14-17`. **Canonical for parameter slots on agents. Value is untyped in grammar; type resolution happens at compile time.**
- **Output target**: `output_target_decl` at `doctrine.lark:74` → `OutputTargetDecl` in `doctrine/_model/io.py:243-248`. Body lines: `output_target_delivery_skill_stmt | record_item`. **No typed-identity field today.** `delivery_skill_ref` is semantic, not a type.
- **`case` dispatch**: `review_case_decl` (`doctrine.lark:208`) is the canonical named-case block. Peer sites express different control structures (`output_record_case_stmt:837`, `output_schema_variant:804`, `match_case:976`). **Distinct semantics — no normalization opportunity for §2.**
- **Diagnostics** — stringly typed, no central enum. Emission: `review_compile_error(code="E477", ...)` at `doctrine/_compiler/validate/review_semantics.py`. Fallback stage labels in `doctrine/_compiler/diagnostics.py:6-27`. Format in `doctrine/diagnostics.py:86`: code-agnostic, renders any prefix. `RULE###` namespace is free and integrates with zero conflict.
- **Validator composition**: `ValidateMixin` in `doctrine/_compiler/validate/__init__.py:33-47` composes per-concern mixins (agents, reviews, readables, routes, outputs, output-structure, route-semantics, contracts, display, schema-helpers, addressable-children, addressable-display, law-paths) via Python MRO. **New validators plug in by adding a mixin class and appending to `ValidateMixin.__bases__`.**
- **Diagnostic test harness**: `make verify-diagnostics` → `doctrine.diagnostic_smoke`. Fixture shape: `_expect_compile_diagnostic(exc, code=..., line=..., related=(...))` in `doctrine/_diagnostic_smoke/compile_checks.py:29-51`. Reference error rendering: `examples/*/ref/*/COMPILER_ERROR.md`.
- **E-code catalog**: `docs/COMPILER_ERRORS.md:40-275`. Bands: E001-E099 (language), E100-E199 (parse), E200-E468 (compile), E469-E500 (review-specific), E501-E699 (emit), E900-E999 (internal). Latest shipped code: E530. Stability rule (`COMPILER_ERRORS.md:34`): existing codes are frozen once shipped.

### Canonical owner paths for each gap

- **§1** (teaching gap): doctrine-learn references at `skills/.curated/doctrine-learn/references/reviews.md` and agent-linter catalog at `skills/.curated/agent-linter/references/finding-catalog.md`. No grammar work needed; `gates:` block at `doctrine.lark:382-386` is shipped.
- **§2** (per-case gate override): grammar change in `review_case_body` (`doctrine.lark:207-215`); model extension in review.py; validator in `doctrine/_compiler/validate/review_semantics.py`. **Canonical owner path: follow the block-level section-override pattern (e.g., `schema_override_sections`), not the agent-slot parameter override. `override gates:` inside a case is a hierarchical section replacement, not a parameter tweak.**
- **§3** (typed handoff-note identity): extend `output_target_body` at `doctrine.lark:74` with a nested `type:` line referencing a typed entity (document / schema / table). Mirrors `output_schema_field`'s `type_ref: FieldTypeRef` pattern. Downstream binding reuses existing `name_ref` resolution.
- **§4** (`receipt` family): one-line grammar addition to `package_host_slot_family` enum at `doctrine.lark:890-896`. Model: new `ReceiptHostSlot` variant. Validator: typed receipt-field references in critic prose must resolve.
- **§5** (rule DSL): new top-level `rule_decl` following canonical typed-entity shape from `doctrine.lark:58-80`. Minimal body: `scope:` (agent-tag / flow / role-class predicate), one or more assertions (`requires inherit X`, `forbids bind Y`, `requires declare Z`), `message:` template. Validator: new `ValidateRulesMixin` in `doctrine/_compiler/validate/rules.py`. Diagnostics: `RULE001+` in a new band documented in `COMPILER_ERRORS.md`.
- **§6** (typed abstract-agent parameters): narrow extension of `agent_slot_field` / abstract slot declaration at `doctrine.lark:139-146`. Grammar adds an optional `: <typed_entity_ref>` annotation to abstract slot declarations. Concrete descendants bind via existing `inherit`/`override` syntax. **Do NOT unify with skill `host_contract` slots** — research shows three distinct shapes with legitimate semantic differences; forced convergence is high-risk for no language-user-visible win.
- **§7** (skill-binding mode): extend `skill_entry` at `doctrine.lark:664-673` with the expr-based mode pattern already in law/review (`"mode" CNAME "=" expr "as" name_ref`). One shared production, not a parallel shape.

### Adjacent surfaces tied to the same contract family

- `docs/LANGUAGE_REFERENCE.md` — authoritative language surface; updated in every phase that adds/changes grammar.
- `docs/REVIEW_SPEC.md` — touched in P1 (§1 teaching of `gates:`) and P2 (§2 per-case gate override).
- `docs/COMPILER_ERRORS.md` — touched in P2 (new review E-code), P3 (new receipt/handoff E-codes), P4 (new mode/param E-codes), P5 (new `RULE001+` band).
- `docs/EMIT_GUIDE.md` — touched only if P3/§3 changes emit shape for handoff-note typed identity.
- `skills/.curated/doctrine-learn/references/*.md` — `reviews.md` (P1, P2), `skills-and-packages.md` (P3, P4), `agents-and-workflows.md` (P6), `outputs-and-schemas.md` (P3), `principles.md` (touches cross-cutting). Built `.prompt` mirrors under `skills/doctrine-learn/prompts/refs/` are regenerated via `emit_skill.py`, not hand-edited.
- `skills/.curated/agent-linter/references/finding-catalog.md` — new AL-findings per phase: `AL###` for inline-prose gates (P1), per-case gate-drift (P2), missing-receipt envelope (P3), handoff-note-as-prose (P3), skill-mode drift (P4), typed-parameter anti-pattern (P6), inheritance-invariant-missing (P5 after rules ship).
- `editors/vscode/syntaxes/doctrine.tmLanguage.json:1214,1375` — already reserves `rule`, `gate`, `mode` as keywords. Additive: new enum values for `family:` and new reserved words land here in the same phase.
- `examples/` — new manifest-backed examples from `139_*` onward (latest shipped is `138_output_shape_case_selector` per AGENTS.md). At least one new example per gap, plus regression examples for any peer-pattern normalization.

### Compatibility posture (separate from `fallback_policy`)

- **Preserve existing contracts for every shipped surface.** All 138 examples pass their manifests verbatim after every phase. No example is rewritten to accommodate normalization.
- **Clean additive cutover for new syntax.** New grammar productions are additive; old forms stay parseable. The one exception is the `output_shape_selector_stmt` drift (§3.2) — we normalize it to the expr-based `mode` form and emit a soft `E###` diagnostic for the enum-only form, timeboxed for removal at the next language-version bump. Logged as a Decision Log entry in P4.
- **No runtime shims.** Failures are compile-time. `fallback_policy: forbidden` holds.

### Existing patterns to reuse

- Typed-entity declaration skeleton (`doctrine.lark:58-80`) — reuse for `rule`.
- Block-level section override (`schema_override_sections`, `analysis_override_section`) — reuse for §2 `override gates:`.
- `family:` enum additive extension — reuse for `receipt`.
- `mode CNAME = expr as name_ref` (law/review) — reuse for skill-binding mode.
- `name_ref` typed-entity reference — reuse for typed parameter binding on concrete agents.
- Nested `type:` inside typed container (`output_schema_field` → `FieldTypeRef`) — reuse for typed handoff-note identity inside `output_target_body`.
- Mixin-composed validator pattern (`ValidateMixin`) — reuse for every new validator.
- Diagnostic fixture shape (`_expect_compile_diagnostic`) — reuse for every new E-code or RULE-code test.

### Duplicate or drifting paths relevant to this change

- **`mode` drift**: `output_shape_selector_stmt` (enum-only) vs. `review_selector_stmt` / `mode_stmt` (expr-based). Plan converges output-shape on the expr-based form in P4 as part of §7's `mode` normalization.
- **Gate-teaching drift**: `skills/.curated/doctrine-learn/references/reviews.md` teaches gates as workflow-prose-embedded, not as a typed `gates:` block. P1 rewrites the gate section and adds the symbol-reference teaching.
- **No agent-linter finding for inline-prose gates** — closest existing are `AL270` (parallel workflows as contracts), `AL450` (coarse check against multi-gate contract), `AL730` (gates mixed with craft), `AL830` (cross-workflow gate-ID drift), `AL930` (skill needs host contract). P1 adds a new `AL###` finding for "gate declared as inline prose when typed `gates:` block would own it."

### Behavior-preservation signals already available

- `make verify-examples` — runs 138 manifest-backed examples. Primary preservation signal for every phase.
- `make verify-diagnostics` — runs `doctrine.diagnostic_smoke`. Extends per phase with new fixtures.
- `make verify-package` — runs on package metadata / publish surface changes. Touched only if P5's `rule` declaration crosses the package boundary.

## 3.3 Decision gaps that must be resolved before implementation

Each gap below is a design choice that `deep-dive` will resolve against repo truth plus the North Star. None require user input — but if the user wants to steer, now is the time.

1. **§2 `override gates:` grammar shape** — repo evidence checked: `schema_override_sections`, `analysis_override_section`, `document_override_block` (block-level section override family). Default recommendation: treat `override gates:` inside a `review_case_body` as a block-level section-override that takes optional per-gate additions/deletions/message-overrides. Answer needed from `deep-dive`: exact item grammar inside the override block (add/remove/modify individual gates; or whole-list replacement).
2. **§3 typed handoff-note identity field placement** — repo evidence checked: `output_target_decl`, `output_schema_field`, `FieldTypeRef`. Default recommendation: nested `type:` line inside `output_target_body`, referencing a document / schema / table typed entity. Answer needed from `deep-dive`: whether `type:` is a new grammar production or reuses an existing nested-type shape verbatim; whether the downstream input-binding side auto-resolves by name or requires explicit `from_output:` binding.
3. **§4 receipt field reference syntax** — repo evidence checked: `contract.NAME` shape for gate refs. Default recommendation: receipt fields referenced as `<skill_binding_name>.receipt.<field>` in critic prose, validated like `contract.NAME`. Answer needed from `deep-dive`: the exact dotted path (three-part vs. two-part) and new E-code range.
4. **§5 `rule` DSL minimal predicate set for P5** — repo evidence checked: psflows audit §5 names three concrete assertion shapes (`inherit X`, `bind Y` forbidden, `declare Z`). Default recommendation: ship exactly those three predicates in P5's first cut, plus a typed `scope:` block that takes agent-tag, flow-name, or role-class selectors. Answer needed from `deep-dive`: whether `scope:` reuses an existing selector grammar or adds a new one; new `RULE001-RULE010` initial allocation.
5. **§6 typed abstract-agent parameters — convergence scope** — repo evidence checked: agent-slot shape vs. skill `host_contract` slot shape vs. output-schema field shape are three distinct productions with legitimate semantic differences. Default recommendation: extend abstract-agent slots narrowly with an optional type annotation (`abstract key: TypedEntity`), do NOT unify with skill `host_contract`. Answer needed from `deep-dive`: exact annotation grammar; concrete-agent binding shape (implicit by-name vs. explicit declaration).
6. **§7 skill-binding mode syntax** — repo evidence checked: `mode CNAME = expr as name_ref` in law/review. Default recommendation: reuse the expr-based form inside `skill_entry_body`, allowing selection like `mode m = CurrentHandoff.active_mode as SkillMode`. Answer needed from `deep-dive`: whether mode binding is per-skill-entry or per-agent; how audit-mode skill bindings differ in validator enforcement (audit skills reject emission side-effects).
7. **§1 teaching-side grammar tightening** — repo evidence checked: doctrine-learn treats gates as workflow-prose; agent-linter has no inline-prose finding. Default recommendation: teaching and lint only; no grammar tightening. Answer needed from `deep-dive`: whether a new soft-deprecation E-code fires when authors declare what look like gate IDs in a workflow `bullets` block without a typed `gates:` block — **or** whether that stays an AL-finding (heuristic) only. The former is more elegant; the latter is less risky.
8. **Output-shape `mode` drift** — repo evidence checked: `output_shape_selector_stmt:740` uses enum-only `mode CNAME as name_ref` while law/review use expr-based form. Default recommendation: normalize to expr-based in P4, keep enum-only form parseable with a soft diagnostic for one language-version cycle, Decision Log the deprecation. Answer needed from `deep-dive`: exact timebox (one minor vs. until next major).

<!-- arch_skill:block:research_grounding:end -->

## 3.4 Consistency follow-ups (from research)

- TL;DR and Section 0 hold. Research sharpens the specific owner paths (§2 block-override, §6 narrow extension without full convergence) without changing scope.
- Section 1 priority 1 (peer-pattern convergence) is strengthened: research found one concrete drift (`mode` enum-only in output-shape) that the plan now explicitly folds into P4.
- Section 10 Decision Log entry to append in P4: "normalize `output_shape_selector_stmt` to expr-based `mode` form; soft-deprecate enum-only form with timebox."

# 4) Current Architecture (as-is)

<!-- arch_skill:block:current_architecture:start -->

## 4.1 On-disk structure

- **Grammar**: `doctrine/grammars/doctrine.lark` — single authoritative Lark grammar; ~1000 lines; all typed-entity productions, slot families, mode/override/case shapes, and dotted refs defined here.
- **Model**: `doctrine/model.py` re-exports from `doctrine/_model/` submodules (`agent.py`, `review.py`, `io.py`, `law.py`, `schema.py`, etc.). Each submodule holds dataclasses mirroring grammar productions.
- **Parser**: `doctrine/_parser/` — thin lark wrapper; produces model instances.
- **Compiler**: `doctrine/_compiler/` — `session.py` orchestrates; `context.py:61` composes `CompilationContext` from mixins (`FlowMixin, ValidateMixin, CompileMixin, DisplayMixin, ResolveMixin`).
- **Validators**: `doctrine/_compiler/validate/` — `__init__.py:33-47` composes `ValidateMixin` from 13 concern-specific mixins (agents, reviews, readables, routes, outputs, output-structure, route-semantics, contracts, display, schema-helpers, addressable-children, addressable-display, law-paths). Each mixin owns its own file; methods called on-demand during compilation via Python MRO.
- **Diagnostics**: `doctrine/diagnostics.py` (public surface, code-agnostic formatter at `:86`); `doctrine/_compiler/diagnostics.py:6-27` defines stage labels and fallback codes. Codes are stringly typed (`"E###"`); no central enum.
- **Diagnostic harness**: `doctrine/_diagnostic_smoke/` — `compile_checks.py:29-51` defines `_expect_compile_diagnostic(exc, code=..., line=..., related=(...))`; run by `make verify-diagnostics`.
- **Examples**: `examples/01_*` through `examples/138_output_shape_case_selector`. Each has `prompts/AGENTS.prompt`, `cases.toml`, and `ref/` expected artifacts. `make verify-examples` runs the manifest-backed corpus.
- **Skills (curated source)**: `skills/.curated/doctrine-learn/` and `skills/.curated/agent-linter/`. Reference files under `references/*.md`.
- **Skills (built mirrors)**: `skills/doctrine-learn/prompts/refs/*.prompt`, `skills/agent-linter/prompts/refs/*.prompt`. Generated from curated source via `emit_skill.py` (not hand-edited).
- **Editor syntax**: `editors/vscode/syntaxes/doctrine.tmLanguage.json` — keyword lists at `:1214` (`lawKeyword` incl. `mode`) and `:1375` (`readableBlockHeader` incl. `rule`, `gate`).
- **Docs**: `docs/LANGUAGE_REFERENCE.md`, `docs/REVIEW_SPEC.md`, `docs/COMPILER_ERRORS.md`, `docs/EMIT_GUIDE.md`, `docs/VERSIONING.md`.

## 4.2 Control paths (runtime)

1. Author writes `.prompt` files → 2. `doctrine/_parser/` parses with Lark → 3. model dataclasses built → 4. `CompilationSession.compile_*()` runs → 5. resolve phase (name refs bound) → 6. validate phase (all `ValidateMixin` concerns run) → 7. emit phase (markdown, SVG, manifest artifacts) → 8. `make verify-examples` diffs against `ref/`.

Diagnostics can fire at any of steps 2–7. Stage labels in `diagnostics.py` tag errors so users see "parse error", "compile error", "emit error". On error, compilation fails loud — **no fallback, no partial emit**.

## 4.3 Object model + key abstractions

**Shared canonical shapes (shipped, do not reinvent):**

- **Typed entity declaration**: one universal shape at `doctrine.lark:58-80`. `KEYWORD CNAME [inheritance?] ":" [string?] _NL _INDENT body _DEDENT`. Applies to `analysis_decl`, `decision_decl`, `schema_decl`, `table_decl`, `document_decl`, `review_decl`, `skill_decl`, `enum_decl`, `output_target_decl`, `output_shape_decl`, `output_schema_decl`.
- **Symbol reference (typed entity prefix)**: `contract_gate_ref` at `doctrine.lark:256` (`"contract" "." CNAME`) → `ContractGateRef` in model. E477 enforces resolution at `doctrine/_compiler/validate/review_semantics.py:174,186,196,231,265`. **Only site using typed-entity dotted-symbol refs today.**
- **Slot family enum**: `package_host_slot_family` at `doctrine.lark:890-896` — seven values: `input | output | document | analysis | schema | table | final_output`.
- **Block-level override**: `schema_override_sections`, `analysis_override_section`, `document_override_block`, `review_override_*` family. Shape: `"override" BLOCK_NAME ":" _NL _INDENT items _DEDENT`. Hierarchical replacement inside a typed container.
- **Parameter-level override**: `agent_slot_override` at `doctrine.lark:143`: `"override" CNAME ":" slot_value`. Scalar-value substitution.
- **Expr-based mode selector** (canonical): `"mode" CNAME "=" expr "as" name_ref`. Two sites today: `review_selector_stmt:206` and `mode_stmt:957`.
- **Enum-only mode selector** (drifted peer): `output_shape_selector_stmt:740`: `"mode" CNAME "as" name_ref`. One site.
- **Abstract agent slots**: `agent_slot_abstract`, `agent_slot_field`, `agent_slot_inherit`, `agent_slot_override` at `doctrine.lark:139-146`. Slot value: `?slot_value: string | name_ref` — untyped in grammar, resolved at compile.
- **Skill `host_contract:` slots**: `package_host_contract_block` at `doctrine.lark:888-896`. Each slot `<family> <CNAME>: <string>`. Distinct from agent slots (family-typed vs. untyped).
- **Output target**: `output_target_decl:74` → `OutputTargetDecl` in `doctrine/_model/io.py:243-248`. Body: `output_target_delivery_skill_stmt | record_item`. No typed-identity field.
- **Review case body**: `review_case_body:207-215` requires `when`, `subject`, `contract`, `checks`, `on_accept`, `on_reject`. No per-case gate override surface.
- **Skill entry binding**: `skill_entry:664-673` — `skill CNAME: name_ref` + optional body of `bind` items. No mode parameter.

## 4.4 Observability + failure behavior today

- **Fail-loud compile errors** with stable E-codes (bands: E001-099 language, E100-199 parse, E200-468 compile, E469-500 review, E501-699 emit, E900-999 internal). Latest shipped: E530. Stability rule: once shipped, meanings are frozen (`COMPILER_ERRORS.md:34`).
- **No runtime fallback.** `fallback_policy: forbidden` in every ordinary doctrine doc.
- **Diagnostic fixtures** in `doctrine/_diagnostic_smoke/` verify each E-code emits on the right input with the right line number and related sites.
- **Manifest verification** via `ref/` diff — any silent behavior change breaks the example's manifest.
- **No telemetry, no runtime probes** — doctrine is authoring-side; runtime state is harness territory.

## 4.5 UI surfaces (ASCII mockups, if UI work)

N/A — doctrine is a DSL with no UI. Editor syntax highlighting in `editors/vscode/` is the only UI-adjacent surface and is additive.

<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)

<!-- arch_skill:block:target_architecture:start -->

## 5.1 On-disk structure (future)

Same layout as §4.1. Every new primitive lands in the existing directory structure — no new top-level directories or parallel implementation paths.

Additions per gap:

- **§2**: grammar change in `doctrine/grammars/doctrine.lark` (extend `review_case_body`); model field on `ReviewCase`; new validator method on `ValidateReviewsMixin`; new E-code in the review band (E531+); new example at `examples/139_review_case_gate_override/`; doctrine-learn update in `reviews.md`; agent-linter update in `finding-catalog.md`.
- **§3**: grammar change (extend `output_target_body` with `typed_as:` line); model field on `OutputTargetDecl`; validator in `ValidateOutputsMixin`; new E-code; new example at `examples/140_typed_handoff_note_identity/`; doctrine-learn update in `emit-targets.md` and `outputs-and-schemas.md`; agent-linter update.
- **§4**: grammar change (add `receipt` to `package_host_slot_family`); model: new `ReceiptHostSlot` variant; validator for receipt-field reference resolution; new E-code; new example at `examples/141_skill_host_receipt_envelope/`; doctrine-learn update in `skills-and-packages.md`; agent-linter update.
- **§5**: new `rule_decl` grammar production following canonical typed-entity shape; new model classes in `doctrine/_model/rule.py`; new `doctrine/_compiler/validate/rules.py` with `ValidateRulesMixin`; new `RULE001+` diagnostic namespace documented in `docs/COMPILER_ERRORS.md`; new example at `examples/142_declarative_project_lint_rule/`; new doctrine-learn reference `rules.md`; agent-linter update.
- **§6**: grammar change (add optional `: <TypedEntityRef>` type annotation to `agent_slot_abstract`); model: typed `WorkflowSlotValue` variant; validator for typed-binding resolution on concrete descendants; new E-code; new example at `examples/143_abstract_agent_typed_parameters/`; doctrine-learn update in `agents-and-workflows.md`; agent-linter update.
- **§7**: grammar change (extend `skill_entry_body` with expr-based `mode` statement); model: mode field on `SkillEntry`; validator for audit-mode skill emission restrictions; new E-code; new example at `examples/144_skill_binding_producer_audit_mode/`; doctrine-learn update in `skills-and-packages.md`; agent-linter update.
- **§1 + `output_shape_selector_stmt` normalization (P1 + P4)**: no new grammar primitives; P1 ships doctrine-learn + agent-linter teaching deltas and a new AL-finding for inline-prose gates. P4 ships grammar alternation allowing both enum-only and expr-based `mode` in `output_shape_selector_stmt`, with soft diagnostic for enum-only form, deprecation timeboxed to one minor-version cycle. Decision Log entry in P4.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json:1214,1375` — additive keyword entries per phase (already reserves `rule`, `gate`, `mode`).

## 5.2 Control paths (future)

Identical to §4.2. No new pipeline phases. Every gap's new check plugs into the existing `ValidateMixin` composition at `doctrine/_compiler/validate/__init__.py:33-47`. New diagnostics use the existing code-agnostic formatter (`diagnostics.py:86`). The `RULE###` namespace for §5 reuses the same formatter and fixture harness as E-codes.

## 5.3 Object model + abstractions (future)

**Locked design decisions (resolved from repo truth + North Star):**

### §2 Per-case gate override (review_family)

- **Grammar shape**: extend `review_case_body:207-215` with an optional `review_case_gates_override_block` following the **block-level override** pattern (mirrors `schema_override_sections`).
  ```
  override gates:
      add <CNAME>: <string>
      remove <CNAME>
      modify <CNAME>: <string>
  ```
- **Semantics**: inherits contract's declared gates; the override block adds, removes, or modifies message text per-case. `failing_gates[]` enum at runtime is the per-case union.
- **Model**: `ReviewCase.gates_override: ReviewCaseGatesOverride | None` with `add: list[SchemaGate]`, `remove: list[str]`, `modify: list[SchemaGate]`.
- **Validator**: new method in `ValidateReviewsMixin` — every `remove` must reference a declared contract gate; every `add`/`modify` name must be unique within the case's effective gate set.
- **Diagnostics**: `E531` (remove of undeclared gate), `E532` (add/modify name collision).
- **Peer-pattern**: uses block-level override, same shape as `schema_override_sections`, `analysis_override_section`, `document_override_block`. Agent-slot parameter override (`agent_slot_override`) is deliberately not reused — different semantics.

### §3 Typed handoff-note identity (output_target)

- **Grammar shape**: extend `output_target_body_line:74` with new `typed_as_stmt: "typed_as" ":" name_ref _NL`. The name_ref points to a `document`, `schema`, or `table` entity.
- **Semantics**: when an agent binds this output target's key as an input in its `inputs` block, the resolved type is the typed-as entity. Downstream agents get field-level resolution instead of prose reconstruction.
- **Model**: `OutputTargetDecl.typed_as: NameRef | None` in `doctrine/_model/io.py:243-248`.
- **Validator**: new method in `ValidateOutputsMixin` — `typed_as` target must be a declared `document`/`schema`/`table`; any downstream agent binding this output must match on family.
- **Diagnostics**: `E533` (typed_as target not a document/schema/table), `E534` (downstream input-family mismatch).
- **Peer-pattern**: reuses `name_ref` resolution. Lexical position inside `output_target_body` mirrors where `delivery_skill:` lives, keeping the body shape flat.

### §4 Typed receipt envelope (host_contract)

- **Grammar shape**: add `receipt` to `package_host_slot_family:890-896`. Receipt slot declared as `receipt <CNAME>: "<title>"` with an optional indented body listing typed fields.
  ```
  host_contract:
      document section_map: "Section Map"
      final_output final_response: "Final Response"
      receipt process_receipt: "Process Receipt"
          queries: list[QueryRecord]
          citations: list[CitationRecord]
          omissions: list[OmissionRecord]
  ```
- **Semantics**: every invocation of the skill emits the receipt envelope alongside the substantive output. Downstream critics bind the receipt by symbol.
- **Model**: new `ReceiptHostSlot(key, title, fields)` variant in `SkillPackageHostSlot` union in `doctrine/_model/io.py:463-468`.
- **Reference syntax**: `<skill_binding_key>.receipt.<field>` — three-part dotted path. Validator resolves against the bound skill's declared receipt slot.
- **Validator**: new method in `ValidateContractsMixin` — each receipt field reference must resolve; each declared receipt field must have a typed field expression.
- **Diagnostics**: `E535` (receipt slot declared without fields), `E536` (unresolved receipt field reference), `E537` (receipt field type not a declared entity).
- **Peer-pattern**: extends the shipped `family:` enum; receipt-field dotted-path reuses the `contract.NAME` shape semantics (one-hop-to-declared-entity).

### §5 Declarative rule DSL

- **Grammar shape**: new top-level `rule_decl` following canonical typed-entity shape from `doctrine.lark:58-80`.
  ```
  rule UpstreamPoisoningInvariantRequired: "Every composer-style agent inherits UpstreamPoisoningInvariant"
      scope:
          agent_tag: composer_style
      assertions:
          requires inherit UpstreamPoisoningInvariant
      message: "Composer-style agents must inherit UpstreamPoisoningInvariant to prevent identifier leakage."
  ```
- **Scope predicates (P5 first cut — enumerated, closed set)**: `agent_tag: <TAG>`, `flow: <FLOW_NAME>`, `role_class: <CLASS>`, `file_tree: <GLOB>`. Scope predicates combine with AND within one `scope:` block.
- **Assertion predicates (P5 first cut — enumerated, closed set)**:
  - `requires inherit <ENTITY_REF>` — agent must transitively inherit from the named module/agent
  - `forbids bind <SKILL_REF>` — agent must not bind the named skill (or any of a listed set)
  - `requires declare <SLOT_NAME>` — agent must declare the named abstract slot
- **Model**: new `doctrine/_model/rule.py` with `RuleDecl`, `RuleScope`, `RuleAssertion` classes.
- **Validator**: new `doctrine/_compiler/validate/rules.py` with `ValidateRulesMixin` — at end of compile, every rule evaluates its scope predicate across the declared agent graph; every scoped agent is checked against the assertions; failures emit `RULE###`.
- **Diagnostics (new namespace)**: `RULE001` (rule declaration references unknown scope predicate), `RULE002` (assertion target unresolved), `RULE003` (scoped agent fails `requires inherit`), `RULE004` (scoped agent fails `forbids bind`), `RULE005` (scoped agent fails `requires declare`).
- **Peer-pattern**: `rule` is a typed entity declaration following the universal shape. Predicates are a closed set in P5 — no open expression language yet. Future expansion (`RULE100+` band reserved) can add pattern-matching, cross-agent graph queries.

### §6 Typed abstract-agent parameters (narrow extension)

- **Grammar shape**: extend `agent_slot_abstract` at `doctrine.lark:139-146` with optional typed annotation.
  ```
  abstract CNAME [: <TypedEntityRef>]
  ```
  Concrete descendant binding reuses existing `inherit`/`override` syntax; the bound `name_ref` must resolve to an entity of the declared type.
- **Semantics**: compile-time typed binding check — no runtime effect. Enables N concrete agents to share one abstract with typed policy slots bound differently.
- **Model**: extend `AuthoredSlotField` in `doctrine/_model/agent.py:14-17` with optional `declared_type: NameRef | None`.
- **Validator**: new method in `ValidateAgentsMixin` — every bound concrete slot whose abstract parent declared a type must resolve to a `name_ref` of that type family.
- **Diagnostics**: `E538` (typed abstract slot bound to wrong-family entity), `E539` (typed annotation references unknown entity).
- **Peer-pattern — explicit non-convergence**: do NOT unify with skill `host_contract` slots or output-schema fields. Research showed three semantically distinct shapes (agent slot = untyped name_ref, skill host slot = family-keyed, output-schema field = nested type_ref). Forced convergence risks breaking all three for no language-user-visible elegance win. Decision logged in §10.

### §7 Skill-binding mode

- **Grammar shape**: extend `skill_entry_body:664-673` with the expr-based mode statement already shipped in law/review.
  ```
  skill my_audit_skill: MyAuditSkill
      mode invocation_mode = CriticContext.current_mode as SkillInvocationMode
      bind:
          target_receipt: ProducerBinding.process_receipt
  ```
- **Semantics**: per-skill-entry mode binding. A skill package can declare its contract differentiated per mode (producer mode emits results + receipt; audit mode takes a receipt and emits a reproducibility verdict). The mode value is resolved from the agent's runtime input, and the compiler enforces that producer-mode-only side effects (emit to output target) aren't invoked from audit-mode bindings.
- **Model**: extend `SkillEntry` with `mode: ModeStmt | None`.
- **Validator**: new method in `ValidateAgentsMixin` — mode ref must resolve to a declared enum; skill package must declare contract variants per mode; audit-mode bindings emit no output-target side effects.
- **Diagnostics**: `E540` (mode ref unresolved), `E541` (audit-mode skill binding with output-target emission), `E542` (skill package has no contract for the declared mode).
- **Peer-pattern — one `mode` production**: reuse `mode_stmt` from `doctrine.lark:957` verbatim. No parallel shape.

### §1 Teaching-only closure

- No grammar, model, or compiler work. Shipped `gates:` block is canonical; the closure is teaching and lint.
- `skills/.curated/doctrine-learn/references/reviews.md` gains a canonical section on typed `gates:` block declaration and `contract.NAME` symbol references, promoted to early teaching (before the first review workflow example).
- `skills/.curated/agent-linter/references/finding-catalog.md` gains a new `AL245` (between `AL270` and `AL450` bands): "Gate Declared As Inline Prose" — fires when a review contract's prose gate-like IDs (regex: `<snake_case_id>.<dotted_path>`) appear inside a `bullets:` or `sequence:` block without a companion `gates:` block.
- Built `.prompt` mirrors regenerated via `emit_skill.py` in the same phase.

### Output-shape `mode` drift normalization (P4)

- `output_shape_selector_stmt:740` accepts both enum-only (`mode CNAME as name_ref`) and expr-based (`mode CNAME = expr as name_ref`) forms. Enum-only form emits soft diagnostic `E543` (deprecated `mode` form).
- `docs/COMPILER_ERRORS.md` entry notes timebox: "deprecated at language version X.Y.Z; removed at next minor bump."
- Decision Log entry in §10 when P4 ships.

## 5.4 Invariants and boundaries

- **Single source of truth per concept**: one `mode` production (expr-based), one block-level `override` shape, one `family:` enum (extended additively), one typed-entity declaration shape, one symbol-reference shape for typed entity prefixes, one slot-binding shape per context (agent vs. skill vs. output-schema — intentionally distinct).
- **Fail-loud boundaries**: every new primitive has at least one new E-code or RULE-code with a diagnostic fixture.
- **No parallel mechanisms**: if a phase introduces a new syntax for an idea the language already expresses, the phase is incomplete and does not pass audit.
- **Teaching parity**: every grammar/model change ships with a doctrine-learn reference update and at least one agent-linter finding in the same phase. Both built `.prompt` mirrors are regenerated.
- **Compatibility posture (locked)**: additive-only for six gaps. The one soft-deprecation is `output_shape_selector_stmt` enum-only form, timeboxed to one minor-version cycle. Version classification per `docs/VERSIONING.md`: minor bump per phase that adds a new first-class primitive; patch bump for teaching-only phases.
- **No runtime shims**: `fallback_policy: forbidden` holds across the plan.

## 5.5 UI surfaces (ASCII mockups, if UI work)

N/A.

<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)

<!-- arch_skill:block:call_site_audit:start -->

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar §2 | `doctrine/grammars/doctrine.lark` | `review_case_body:207-215` | Fixed body (when, subject, contract, checks, on_accept, on_reject) | Add optional `review_case_gates_override_block` | Per-case gate override | New production `review_case_gates_override_block` | Diagnostic fixture for E531/E532 |
| Model §2 | `doctrine/_model/review.py` | `ReviewCase` | No gates_override field | Add `gates_override: ReviewCaseGatesOverride \| None` | Model the new block | New dataclass `ReviewCaseGatesOverride(add, remove, modify)` | Model round-trip tests |
| Validator §2 | `doctrine/_compiler/validate/review_semantics.py` | New method in `ValidateReviewsMixin` | N/A | Add `_validate_review_case_gate_override` | Enforce override target existence and name uniqueness | E531/E532 | Diagnostic fixtures in `_diagnostic_smoke/compile_checks.py` |
| Example §2 | `examples/139_review_case_gate_override/` | new | N/A | Add manifest-backed example | Prove the feature | New prompts + cases.toml + ref/ | `make verify-examples` |
| Docs §2 | `docs/REVIEW_SPEC.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md` | gate / review_family / E531-532 sections | Current sections document shared gate lists | Add per-case override surface + E531/E532 | Language user needs one place to learn it | N/A | Docs render |
| Teaching §2 | `skills/.curated/doctrine-learn/references/reviews.md` | gates + cases section | Teaches family-wide gate lists | Add per-case override section | doctrine-learn stays in sync | Rebuild `skills/doctrine-learn/prompts/refs/reviews.prompt` | Skill build |
| Linter §2 | `skills/.curated/agent-linter/references/finding-catalog.md` | New AL finding | N/A | Add AL-finding for cases that would benefit from override instead of separate contract | Prevent drift back to per-contract duplication | New AL code | Linter regression |
| Grammar §3 | `doctrine/grammars/doctrine.lark` | `output_target_body:74` | Body = delivery_skill or record_item | Add `typed_as_stmt` | Typed handoff identity | New production `typed_as_stmt` | Parser round-trip |
| Model §3 | `doctrine/_model/io.py:243-248` | `OutputTargetDecl` | No typed_as field | Add `typed_as: NameRef \| None` | Model new statement | N/A | Model tests |
| Validator §3 | `doctrine/_compiler/validate/outputs.py` | `ValidateOutputsMixin` | No typed-identity checks | Add `_validate_output_target_typed_as` + downstream-family-match check | Enforce family matching | E533/E534 | Diagnostic fixtures |
| Example §3 | `examples/140_typed_handoff_note_identity/` | new | N/A | Add manifest-backed example | Prove feature | New prompts + cases.toml + ref/ | `make verify-examples` |
| Docs §3 | `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md` | output target + E533/E534 sections | Emit guide documents delivery_skill | Add typed_as section | Doc parity | N/A | Docs render |
| Teaching §3 | `skills/.curated/doctrine-learn/references/emit-targets.md`, `outputs-and-schemas.md` | output_target section | Teaches delivery_skill | Add typed_as teaching | Skill sync | Rebuild built mirrors | Skill build |
| Linter §3 | `skills/.curated/agent-linter/references/finding-catalog.md` | New AL finding | N/A | Add AL-finding for "handoff carries typed structure but is bound as prose downstream" | Nudge typed bindings | New AL code | Linter regression |
| Grammar §4 | `doctrine/grammars/doctrine.lark:890-896` | `package_host_slot_family` enum | 7 values | Add `receipt` (8th value) | Receipt family | Enum extension + new slot-body production for fields | Parser round-trip |
| Model §4 | `doctrine/_model/io.py:463-468` | `SkillPackageHostSlot` union | 7 variants | Add `ReceiptHostSlot(key, title, fields)` | Model new family | New dataclass | Model tests |
| Validator §4 | `doctrine/_compiler/validate/contracts.py` | `ValidateContractsMixin` | No receipt-field checks | Add `_validate_receipt_field_references` | Enforce `.receipt.<field>` resolution | E535/E536/E537 | Diagnostic fixtures |
| Example §4 | `examples/141_skill_host_receipt_envelope/` | new | N/A | Add manifest-backed example | Prove feature | New prompts + cases.toml + ref/ | `make verify-examples` |
| Docs §4 | `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md` | host_contract section + E535-537 | Current doc omits receipt | Add receipt family + new codes | Doc parity | N/A | Docs render |
| Teaching §4 | `skills/.curated/doctrine-learn/references/skills-and-packages.md` | host_contract teaching | 7 families taught | Add receipt family | Skill sync | Rebuild built mirror | Skill build |
| Linter §4 | `skills/.curated/agent-linter/references/finding-catalog.md` | New AL finding | N/A | Add AL-finding for "skill emits process evidence as prose instead of typed receipt" | Nudge typed receipts | New AL code | Linter regression |
| Grammar §5 | `doctrine/grammars/doctrine.lark:58-80` | Top-level entity list | 11 exportable entity types | Add `rule_decl` | New rule primitive | Canonical entity shape + new body | Parser round-trip |
| Model §5 | `doctrine/_model/rule.py` | new file | N/A | Add `RuleDecl`, `RuleScope`, `RuleAssertion` | Model rule | New dataclasses + union members | Model tests |
| Validator §5 | `doctrine/_compiler/validate/rules.py` | new file | N/A | Add `ValidateRulesMixin` + composition into `ValidateMixin` | Evaluate rules across agent graph | RULE001-RULE005 | Diagnostic fixtures |
| Diagnostics §5 | `doctrine/diagnostics.py`, `_diagnostic_smoke/compile_checks.py` | E-code formatter | Handles `E###` | Extend tests for `RULE###` | New namespace | Formatter is code-agnostic; harness needs RULE fixtures | Diagnostic tests |
| Example §5 | `examples/142_declarative_project_lint_rule/` | new | N/A | Add manifest-backed example | Prove feature | New prompts + cases.toml + ref/ | `make verify-examples` |
| Docs §5 | `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md` | N/A (no rule section today) | N/A | Add `rule` entity section + RULE### band | Doc parity | New RULE001-099 band, RULE100+ reserved | Docs render |
| Teaching §5 | `skills/.curated/doctrine-learn/references/rules.md` (new) + `SKILL.md` index | No rules reference | N/A | Add new reference file + curated-skill index entry | Teach the primitive | New .md + rebuild built mirror | Skill build |
| Linter §5 | `skills/.curated/agent-linter/references/finding-catalog.md` | N/A | N/A | AL-finding for "project lacks an enforcement rule for this inheritance invariant" | Nudge rules over commentary | New AL code | Linter regression |
| Grammar §6 | `doctrine/grammars/doctrine.lark:139-146` | `agent_slot_abstract` + `slot_value` | `?slot_value: string \| name_ref` | Add optional `: <TypedEntityRef>` annotation to `agent_slot_abstract` | Typed parameters | Optional type annotation | Parser round-trip |
| Model §6 | `doctrine/_model/agent.py:14-17` | `AuthoredSlotField` | No declared_type | Add `declared_type: NameRef \| None` | Model new annotation | N/A | Model tests |
| Validator §6 | `doctrine/_compiler/validate/agents.py` | `ValidateAgentsMixin` | No typed-binding checks | Add `_validate_typed_abstract_slot_binding` | Enforce family match | E538/E539 | Diagnostic fixtures |
| Example §6 | `examples/143_abstract_agent_typed_parameters/` | new | N/A | Add manifest-backed example | Prove feature | New prompts + cases.toml + ref/ | `make verify-examples` |
| Docs §6 | `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md` | abstract agent section | Current doc does not mention typed slots | Add typed-slot section + E538/E539 | Doc parity | N/A | Docs render |
| Teaching §6 | `skills/.curated/doctrine-learn/references/agents-and-workflows.md` | inheritance section | Teaches untyped slots | Add typed-slot teaching | Skill sync | Rebuild built mirror | Skill build |
| Linter §6 | `skills/.curated/agent-linter/references/finding-catalog.md` | New AL finding | N/A | AL-finding for "N near-duplicate concrete agents that could share an abstract with typed parameters" | Nudge parameterization | New AL code | Linter regression |
| Grammar §7 | `doctrine/grammars/doctrine.lark:664-673` | `skill_entry_body` | No mode line | Add expr-based mode stmt (reuse `mode_stmt:957` production directly) | Skill mode binding | Production reuse, no new syntax | Parser round-trip |
| Model §7 | `doctrine/_model/io.py` | `SkillEntry` | No mode field | Add `mode: ModeStmt \| None` | Model new statement | N/A | Model tests |
| Validator §7 | `doctrine/_compiler/validate/agents.py` | `ValidateAgentsMixin` | No skill-mode checks | Add `_validate_skill_entry_mode` | Mode resolution + audit-mode side-effect restriction | E540/E541/E542 | Diagnostic fixtures |
| Example §7 | `examples/144_skill_binding_producer_audit_mode/` | new | N/A | Add manifest-backed example | Prove feature | New prompts + cases.toml + ref/ | `make verify-examples` |
| Docs §7 | `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md` | skill binding section | No mode surface | Add mode + E540/E541/E542 | Doc parity | N/A | Docs render |
| Teaching §7 | `skills/.curated/doctrine-learn/references/skills-and-packages.md` | skill binding | Teaches unmoded bindings | Add mode binding + producer/audit idiom | Skill sync | Rebuild built mirror | Skill build |
| Linter §7 | `skills/.curated/agent-linter/references/finding-catalog.md` | New AL finding | N/A | AL-finding for "critic re-invokes producer skill instead of binding audit mode" | Nudge mode-specific bindings | New AL code | Linter regression |
| Normalization P4 | `doctrine/grammars/doctrine.lark:740` | `output_shape_selector_stmt` | Enum-only form | Accept both forms; emit soft E543 on enum-only form | Converge on expr-based `mode` | Grammar alternation | Parser round-trip + diagnostic fixture |
| Decision Log | `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md:§10` | Append entry at P4 | N/A | Add entry documenting enum-only deprecation + timebox | Visible drift record | N/A | N/A |
| §1 Teaching | `skills/.curated/doctrine-learn/references/reviews.md` | gates section | Gates taught as workflow-prose | Add typed `gates:` block teaching + `contract.NAME` symbol-reference example | Close teaching gap | Rebuild built mirror | Skill build |
| §1 Linter | `skills/.curated/agent-linter/references/finding-catalog.md` | New AL245 | N/A | Add "Gate Declared As Inline Prose" finding | Close the teaching-gap gap | New AL code | Linter regression |
| Editor syntax | `editors/vscode/syntaxes/doctrine.tmLanguage.json:1214,1375` | keyword lists | `mode`, `rule`, `gate` already reserved | Add new enum values for `family:` as keywords; verify VSCode build | Editor parity | Additive | `cd editors/vscode && make` |

## 6.2 Migration notes

- **Canonical owner path / shared code path**:
  - Grammar: `doctrine/grammars/doctrine.lark` — single file.
  - Model: `doctrine/_model/*.py` with `doctrine/model.py` re-export.
  - Validators: `doctrine/_compiler/validate/*.py` composed via `ValidateMixin`.
  - Diagnostics: `doctrine/diagnostics.py` (public) + `doctrine/_compiler/diagnostics.py` (internal).
  - Curated skills: `skills/.curated/*/references/*.md`; built mirrors regenerated via `emit_skill.py`.
- **Deprecated APIs**: `output_shape_selector_stmt` enum-only form — soft deprecated in P4 with `E543`; timebox: one minor-version cycle.
- **Delete list**: no code paths deleted. All changes are additive except the `output_shape_selector_stmt` enum-only form, which is deprecated-but-parseable until the next minor version.
- **Adjacent surfaces tied to the same contract family**: documented per-row in the change map. Live docs/comments/instructions update in the same phase that changes grammar — never deferred.
- **Compatibility posture / cutover plan**: additive cutover per phase. Version classification per `docs/VERSIONING.md` — patch for P1 (teaching-only); minor for P2-P5 (new primitives); no major bump planned.
- **Capability-replacing harnesses to delete or justify**: none. This plan adds compile-time checks, not runtime harnesses. The §5 `rule` primitive replaces comment-block convention discipline with compile-time teeth — not a new harness.
- **Live docs/comments/instructions to update or delete**: every row in the change map names its docs/teaching surface. No docs outlive their grammar changes.
- **Behavior-preservation signals for refactors**: `make verify-examples` (138 existing examples must pass verbatim); `make verify-diagnostics` (all existing E-codes still fire on their fixtures); `make verify-package` (only when P5's `rule` declaration crosses package metadata boundary).

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope |
| --- | --- | --- | --- | --- |
| Mode selectors | `doctrine.lark:740` `output_shape_selector_stmt` | Expr-based `mode CNAME = expr as name_ref` | One `mode` production; no drift between shape selectors and law/review/skill | **Include** in P4 alongside §7; soft-deprecate enum-only form with E543 |
| Symbol references | `doctrine.lark:256` `contract_gate_ref` | Typed-entity dotted prefix (`entity.symbol`) | New §4 receipt refs and potential future typed refs reuse one shape | **Include** in P3 (§4 receipt refs follow this shape) |
| Block-level override | `doctrine.lark:218-224` review override family, `:397-400` schema overrides | Block-level `override BLOCK_NAME:` shape | New §2 `override gates:` reuses this family, not the agent-slot parameter override | **Include** in P2 |
| Typed entity declaration | `doctrine.lark:58-80` universal entity shape | Canonical `KEYWORD CNAME [inheritance?] ":" [string?]` | New §5 `rule_decl` reuses this shape, not an ad-hoc declaration | **Include** in P5 |
| Slot family enum | `doctrine.lark:890-896` `package_host_slot_family` | Additive extension; not forked | `receipt` plugs into the shipped enum; no parallel "kind:" enum | **Include** in P3 |
| Nested type annotation | `output_schema_field` → `FieldTypeRef` | Nested `type:` inside typed container body | New §3 `typed_as:` on `output_target_body` mirrors this shape | **Include** in P3 |
| Expr-based mode production | `doctrine.lark:957` `mode_stmt` | Verbatim reuse (one production for two use sites) | §7 skill-binding mode reuses, no fork | **Include** in P4 |
| Agent abstract-slot parameters | `doctrine.lark:139-146` agent slots | Narrow typed annotation; no skill-host-slot convergence | Three-shape divergence is semantically legitimate; forced convergence is high-risk | **Defer indefinitely** — Decision Log entry in P4 naming why convergence is rejected |
| Case dispatch | `doctrine.lark:208` `review_case_decl` vs. `:837` output-record-case vs. `:976` law match-case vs. `:804` output-schema-variant | No convergence | Four genuinely distinct control structures | **Exclude** — document rationale in Decision Log to prevent future well-meaning convergence |
| Agent-linter finding codes | `skills/.curated/agent-linter/references/finding-catalog.md` | `AL###` namespace | Every new AL-finding lands here; every finding catalog entry maps to a doctrine-learn lesson | **Include** in every phase |
| doctrine-learn reference mirror pipeline | `skills/.curated/*/references/*.md` → built `.prompt` | Edit curated, rebuild built mirror | No hand-edits to built mirrors | **Include** in every phase that touches teaching surfaces |

<!-- arch_skill:block:call_site_audit:end -->

## 6.3 Consistency follow-ups (from deep-dive)

- §6 decision "narrow abstract-agent extension; do NOT converge with skill host_contract" is a plan-shaping choice against the literal reading of "best case for elegance." Research showed three distinct shapes with legitimate semantic differences; forced convergence is high-risk for no user-visible win. Recording this in §10 when phase-plan ships the change. If the user wants full convergence, that's a North Star reshape, not a deep-dive reopening.
- TL;DR's phase shape remains accurate. No Section 0 invariant was contradicted.
- Section 0.4 acceptance evidence updated implicitly: new E-codes land in E531-E543 range; new RULE-codes allocate RULE001-RULE099 initial band with RULE100+ reserved.

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

Phase order (foundational-first, 7 phases):

- P1 — §1 typed-gate teaching closure (no grammar)
- P2 — §2 `override gates:` per review case (block-level override reuse)
- P3 — §4 `receipt` family on `host_contract:` (slot-family enum extension)
- P4 — §3 typed handoff-note identity via `typed_as:` on output targets (typed downstream binding)
- P5 — §7 skill-binding `mode` + output-shape selector drift normalization (shared `mode_stmt` production)
- P6 — §6 typed abstract-agent parameters (narrow typed annotation)
- P7 — §5 declarative `rule` primitive + `RULE###` diagnostics

Every phase ships grammar (if applicable) + model + validator + E-code/RULE-code + manifest-backed example + docs (`LANGUAGE_REFERENCE.md`, `COMPILER_ERRORS.md`, any touched topic doc) + curated doctrine-learn reference + curated agent-linter finding + rebuilt `.prompt` mirrors via `emit_skill.py`, plus `CHANGELOG.md` and `docs/VERSIONING.md` entries per `AGENTS.md` Definition-of-Done. Release classification: patch bump for P1; minor bump for P2-P7 (each adds a first-class primitive or a new diagnostic band). No major bump planned.

## Phase 1 — §1 typed-gate teaching closure (no grammar)

* Goal: close the §1 teaching gap so a fresh author reading doctrine-learn writes typed `gates:` blocks with `contract.NAME` refs instead of inline prose, and the agent-linter catches relapses.
* Work: update curated doctrine-learn `reviews.md` to teach the shipped `gates:` block and `contract.NAME` symbol reference as the first-class review contract surface. Add `AL245 "Gate Declared As Inline Prose"` to the curated agent-linter `finding-catalog.md`. Rebuild both curated→built `.prompt` mirrors via `emit_skill.py`. Ship one manifest-backed example that demonstrates typed gates + `contract.NAME` refs and the E477 failure path as a reference. No grammar, model, or validator changes in this phase.
* Checklist (must all be done):
  - Edit `skills/.curated/doctrine-learn/references/reviews.md`: add a canonical "Typed gates, declared once, referenced by symbol" section positioned before the first review workflow example. The section must show a full `schema_gates_block`, a `contract.NAME` reference inside a review case, and the E477 compile failure when the reference is wrong.
  - Edit `skills/.curated/agent-linter/references/finding-catalog.md`: add `AL245 Gate Declared As Inline Prose` between `AL240` and `AL270` bands. Include trigger, canonical fix, and a pointer to the typed `gates:` block teaching in `reviews.md`.
  - Regenerate built mirrors: `skills/doctrine-learn/prompts/refs/reviews.prompt` and `skills/agent-linter/prompts/refs/finding_catalog.prompt` via `emit_skill.py`; do not hand-edit the `.prompt` files.
  - Verify the curated-mirror pipeline is the only writer: no delta between what `emit_skill.py` emits and what is committed.
  - Add `examples/139_typed_gates_symbol_reference/` with `prompts/AGENTS.prompt`, `cases.toml`, and `ref/` that shows a typed `gates:` block plus a `contract.NAME` reference. Include a negative case that fires E477 on a typo (reuses the shipped E477 code — no new diagnostic in this phase).
  - Update `docs/LANGUAGE_REFERENCE.md` cross-reference to point review authors at the new teaching section; no spec change.
  - Run `make verify-examples` and confirm the full 01-138 corpus plus the new 139 example passes.
  - Add a `CHANGELOG.md` entry under the next patch release noting the teaching-only surface move and new example.
  - Update `docs/VERSIONING.md` entry only if the release-classification rationale changes; otherwise leave unchanged and state that in the phase console summary.
* Verification (required proof):
  - `make verify-examples` green with the new 139 example.
  - `make verify-diagnostics` green (no new codes; existing E477 fixture still green).
  - `diff` against built `.prompt` mirrors is zero after running `emit_skill.py` again on a clean tree.
* Docs/comments (propagation; only if needed):
  - `skills/.curated/doctrine-learn/references/reviews.md` is the primary teaching surface; update in this phase.
  - `skills/.curated/agent-linter/references/finding-catalog.md` gains `AL245`.
  - `docs/LANGUAGE_REFERENCE.md` gets a small cross-reference pointer only.
  - No comments at `doctrine.lark:382-386` required; the shipped `schema_gates_block` already has adequate surrounding context.
* Exit criteria (all required):
  - Curated `reviews.md` teaches typed `gates:` + `contract.NAME` before any review workflow example.
  - `AL245` exists in curated finding-catalog with trigger, fix, and cross-reference.
  - Built `.prompt` mirrors match curated source exactly (no drift).
  - `examples/139_typed_gates_symbol_reference/` exists, passes manifest, and includes both the shipped happy path and the E477 negative case.
  - `make verify-examples` and `make verify-diagnostics` both green on the latest main.
  - `CHANGELOG.md` patch entry written.
  - A simulated layered-review author re-reading the 2026-04-19 audit against the updated doctrine-learn reaches the typed `gates:` block on first encounter instead of writing inline prose.
* Rollback: revert the curated edits and the generated built mirrors; remove `examples/139_typed_gates_symbol_reference/`; revert `CHANGELOG.md` entry. No grammar or model touched, so rollback is a pure docs/skills revert.

## Phase 2 — §2 `override gates:` per review case (block-level override reuse)

* Goal: let one review family cover N cases that share a contract while expressing per-case gate deltas, using the shipped block-level override pattern (not the agent-slot parameter override).
* Work: extend `review_case_body` with an optional `review_case_gates_override_block` that follows the block-level override pattern used by `schema_override_sections`, `analysis_override_section`, and `document_override_block`. Body items are `add CNAME: "<message>"`, `remove CNAME`, and `modify CNAME: "<message>"`. The effective case gate set is the contract's declared gates plus adds, minus removes, with modified messages replacing the contract's text for the named gate. Add `ReviewCase.gates_override: ReviewCaseGatesOverride | None` to the model. Add a new validator method on `ValidateReviewsMixin` in `doctrine/_compiler/validate/review_semantics.py`. Emit `E531` when `remove` references an undeclared contract gate and `E532` when an `add`/`modify` name collides with an existing gate. Ship a manifest-backed example showing one review family with two cases sharing a contract but diverging on gates. Update docs, teaching, and linter in the same phase.
* Checklist (must all be done):
  - Extend `doctrine/grammars/doctrine.lark` `review_case_body:207-215` with optional `review_case_gates_override_block` following the canonical block-level override shape (mirror `schema_override_sections:397-400`).
  - Add `ReviewCaseGatesOverride(add: list[SchemaGate], remove: list[str], modify: list[SchemaGate])` and `ReviewCase.gates_override: ReviewCaseGatesOverride | None` in `doctrine/_model/review.py`.
  - Parser wiring in `doctrine/_parser/io.py` (or the correct submodule) emits the new model from the new grammar production.
  - Add `_validate_review_case_gate_override` to `ValidateReviewsMixin` in `doctrine/_compiler/validate/review_semantics.py`: resolve `remove` names against contract gates, detect `add`/`modify` collisions, compute the effective per-case gate set.
  - Register E-codes in `docs/COMPILER_ERRORS.md`: `E531 Gate removed from review case is not declared in the contract`, `E532 Gate added/modified in review case collides with an existing name`.
  - Add diagnostic fixtures in `doctrine/_diagnostic_smoke/compile_checks.py` for E531 and E532 using `_expect_compile_diagnostic(..., code="E531"/"E532", line=..., related=...)`.
  - Add `examples/140_review_case_gate_override/` with `prompts/AGENTS.prompt`, `cases.toml`, and `ref/` showing one review family with two cases sharing a contract but differing gate sets; include an invalid-example that fires E531 and another that fires E532.
  - Update `docs/REVIEW_SPEC.md` and `docs/LANGUAGE_REFERENCE.md` with the new per-case override surface and the new E-codes.
  - Update curated `skills/.curated/doctrine-learn/references/reviews.md` with a section teaching per-case gate override and when to use it vs. splitting contracts. Regenerate `skills/doctrine-learn/prompts/refs/reviews.prompt`.
  - Add an agent-linter finding to curated `finding-catalog.md` for "per-contract duplication where per-case gate override would suffice" (next AL-band allocation after P1's `AL245`). Regenerate the built mirror.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` if the `override` keyword context changes; run `cd editors/vscode && make` and commit updated artifacts.
  - `make verify-examples` green (all existing examples still pass; new 140 passes).
  - `make verify-diagnostics` green with new E531/E532 fixtures.
  - `CHANGELOG.md` + `docs/VERSIONING.md` entries: minor bump (first-class grammar addition).
* Verification (required proof):
  - `make verify-examples` green against full corpus 01-140.
  - `make verify-diagnostics` green including new E531/E532 fixtures.
  - Behavior preservation: every pre-existing review example (01-138) passes its manifest byte-for-byte (no ref/ diff).
  - `diff` against built `.prompt` mirrors is zero after `emit_skill.py`.
  - `cd editors/vscode && make` produces a clean build if the syntax file changed.
* Docs/comments (propagation; only if needed):
  - `docs/REVIEW_SPEC.md` and `docs/LANGUAGE_REFERENCE.md` document the new surface.
  - `docs/COMPILER_ERRORS.md` adds E531/E532 with plain-language descriptions (7th-grade requirement).
  - `skills/.curated/doctrine-learn/references/reviews.md` gains a per-case override section.
  - `skills/.curated/agent-linter/references/finding-catalog.md` gains the new AL-finding.
  - One-line grammar comment at the new `review_case_gates_override_block` production naming it as a sibling of `schema_override_sections` (pattern propagation; one line, high leverage).
* Exit criteria (all required):
  - Grammar accepts the new block; parser builds `ReviewCaseGatesOverride` model instances.
  - Validator rejects E531 and E532 cases with stable codes, correct line numbers, and related sites.
  - `examples/140_review_case_gate_override/` ships with valid + invalid cases covering E531 and E532.
  - `docs/REVIEW_SPEC.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md` all describe the new surface and codes.
  - Curated and built doctrine-learn + agent-linter surfaces reflect the new primitive with no hand-edit drift in built mirrors.
  - `make verify-examples` and `make verify-diagnostics` both green; manifest of every pre-existing example unchanged (behavior preservation).
  - `CHANGELOG.md` + `docs/VERSIONING.md` updated for the minor bump.
* Rollback: revert grammar production, model dataclass, validator method, and E-code registrations; delete `examples/140_*`; revert doctrine-learn, agent-linter, and docs edits; revert built `.prompt` mirrors and VSCode syntax artifacts. `make verify-examples` on the reverted tree returns to the 01-139 baseline.

## Phase 3 — §4 `receipt` family on `host_contract:` (slot-family enum extension)

* Goal: let a skill declare a typed receipt envelope so downstream critics bind the envelope by symbol instead of parsing prose, reusing the shipped `family:` enum pattern.
* Work: extend `package_host_slot_family` at `doctrine.lark:890-896` with an eighth value, `receipt`. Add a receipt slot body production that lists typed fields (`<field_name>: <type_expr>`), with types referencing declared entities (`list[QueryRecord]`, `document`, `schema`, `table`). Add `ReceiptHostSlot(key, title, fields)` to the `SkillPackageHostSlot` union in `doctrine/_model/io.py`. Add the three-part dotted reference `<skill_binding_name>.receipt.<field>` and wire resolution through a new validator method on `ValidateContractsMixin`. Emit `E535` when a receipt slot has no fields, `E536` when a receipt field reference fails to resolve, and `E537` when a field type is not a declared entity. Ship a manifest-backed example showing a skill that emits a typed receipt and a critic that binds the receipt by symbol.
* Checklist (must all be done):
  - Add `receipt` to `package_host_slot_family` in `doctrine/grammars/doctrine.lark:890-896`.
  - Add `receipt_slot_body` production listing typed fields, and wire it into `package_host_contract_block`.
  - Add `ReceiptHostSlot(key: str, title: str, fields: list[ReceiptField])` variant to `SkillPackageHostSlot` union in `doctrine/_model/io.py:463-468`.
  - Parser wiring in `doctrine/_parser/io.py` emits the receipt-slot model from the new grammar production.
  - Extend dotted-reference resolution (the shape used by `contract.NAME` in `review_semantics.py`) to also handle `<skill_binding_name>.receipt.<field>`. New resolver function lives in `doctrine/_compiler/validate/contracts.py` or its helper module.
  - Add `_validate_receipt_field_references` and `_validate_receipt_slot_fields` to `ValidateContractsMixin` in `doctrine/_compiler/validate/contracts.py`.
  - Register E-codes in `docs/COMPILER_ERRORS.md`: `E535 Receipt slot declared without fields`, `E536 Receipt field reference does not resolve`, `E537 Receipt field type is not a declared entity`.
  - Add diagnostic fixtures for E535/E536/E537 in `_diagnostic_smoke/compile_checks.py`.
  - Add `examples/141_skill_host_receipt_envelope/` with producer-skill declaring a receipt, critic binding the receipt, `prompts/AGENTS.prompt`, `cases.toml`, and `ref/` artifacts. Include invalid cases firing E535, E536, and E537.
  - Update `docs/LANGUAGE_REFERENCE.md`: add `receipt` as an eighth `family:` value; document receipt slot body + dotted-reference syntax.
  - Update `docs/COMPILER_ERRORS.md` with E535-E537.
  - Update curated `skills/.curated/doctrine-learn/references/skills-and-packages.md` with a typed-receipt-envelope teaching section and a worked example. Regenerate the built mirror.
  - Add an agent-linter finding to curated `finding-catalog.md` for "skill emits process evidence as prose instead of typed receipt." Regenerate the built mirror.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` with `receipt` as a new enum-value keyword; run `cd editors/vscode && make` and commit artifacts.
  - `make verify-examples` green (full corpus 01-141).
  - `make verify-diagnostics` green with new E535/E536/E537 fixtures.
  - `make verify-package` green (enum extension on host_contract touches the package-contract surface).
  - `CHANGELOG.md` + `docs/VERSIONING.md` entries for the minor bump.
* Verification (required proof):
  - `make verify-examples` green on 01-141.
  - `make verify-diagnostics` green including new codes.
  - `make verify-package` green to prove the package-contract surface still round-trips under the enum extension.
  - Behavior preservation: every pre-existing `host_contract:` example (all examples that use `package_host_slot_family`) passes its manifest byte-for-byte.
  - Built `.prompt` mirrors match curated source exactly.
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md` documents the eighth family.
  - `docs/COMPILER_ERRORS.md` adds E535-E537.
  - `skills/.curated/doctrine-learn/references/skills-and-packages.md` teaches typed receipts.
  - `skills/.curated/agent-linter/references/finding-catalog.md` gains the new AL-finding.
  - One-line comment at `package_host_slot_family:890-896` noting the closed-enum convention (pattern propagation; prevents future open-enum drift).
* Exit criteria (all required):
  - Grammar accepts `receipt <CNAME>: "<title>"` with a body of typed fields; parser builds `ReceiptHostSlot` model instances.
  - Validator rejects E535/E536/E537 cases with stable codes, correct line numbers, and related sites.
  - Dotted reference `<skill_binding_name>.receipt.<field>` resolves against declared receipt fields and emits E536 when unresolved.
  - `examples/141_skill_host_receipt_envelope/` ships with valid + invalid cases covering E535, E536, E537.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`, `skills/.curated/doctrine-learn/references/skills-and-packages.md`, `skills/.curated/agent-linter/references/finding-catalog.md` all reflect the new primitive.
  - `make verify-examples`, `make verify-diagnostics`, `make verify-package` all green.
  - `CHANGELOG.md` + `docs/VERSIONING.md` minor-bump entries written.
* Rollback: revert grammar enum extension + receipt body production; remove `ReceiptHostSlot`; revert validator methods and resolver additions; revert E-code entries; delete `examples/141_*`; revert doctrine-learn, agent-linter, and docs edits; revert built `.prompt` mirrors and VSCode artifacts.

## Phase 4 — §3 typed handoff-note identity via `typed_as:` on output targets (typed downstream binding)

* Goal: let an output target declare a typed identity so a downstream agent binds it as a typed input by family without reconstructing structure from prose.
* Work: extend `output_target_body:74` with a new optional `typed_as_stmt: "typed_as" ":" name_ref _NL` line. The `name_ref` points to a declared `document`, `schema`, or `table`. Add `OutputTargetDecl.typed_as: NameRef | None` to the model in `doctrine/_model/io.py:243-248`. Extend `ValidateOutputsMixin` with two methods: `_validate_output_target_typed_as` (ensures the target resolves to `document`/`schema`/`table`) and a downstream input-family-match check that validates bindings on agents that receive this output. Emit `E533` (target not document/schema/table) and `E534` (downstream family mismatch). Ship a manifest-backed example where a producer agent emits a typed output and a downstream agent binds the typed value by name.
* Checklist (must all be done):
  - Extend `doctrine/grammars/doctrine.lark` `output_target_body:74` with optional `typed_as_stmt` line.
  - Add `OutputTargetDecl.typed_as: NameRef | None` field in `doctrine/_model/io.py:243-248`.
  - Parser wiring emits the `typed_as` model field from the new grammar production.
  - Add `_validate_output_target_typed_as` and `_validate_output_target_downstream_family_match` methods to `ValidateOutputsMixin` in `doctrine/_compiler/validate/outputs.py`.
  - Wire downstream input-binding resolution to consult `OutputTargetDecl.typed_as` when an agent's input resolves to a typed output target, and match on `document`/`schema`/`table` family.
  - Register E-codes in `docs/COMPILER_ERRORS.md`: `E533 Typed output target references a non-document/schema/table entity`, `E534 Downstream input family does not match typed output target family`.
  - Add diagnostic fixtures for E533/E534 in `_diagnostic_smoke/compile_checks.py`.
  - Add `examples/142_typed_handoff_note_identity/` with producer + downstream consumer agent, `prompts/AGENTS.prompt`, `cases.toml`, and `ref/` artifacts. Include invalid cases firing E533 and E534.
  - Update `docs/LANGUAGE_REFERENCE.md`: document `typed_as:` on output targets; cross-link to the family-match rule.
  - Update `docs/EMIT_GUIDE.md` if the emit shape changes for typed-identity output targets; otherwise note no change.
  - Update `docs/COMPILER_ERRORS.md` with E533/E534.
  - Update curated `skills/.curated/doctrine-learn/references/emit-targets.md` and `skills/.curated/doctrine-learn/references/outputs-and-schemas.md` with typed-handoff-note teaching. Regenerate the built mirrors.
  - Add an agent-linter finding to curated `finding-catalog.md` for "handoff carries typed structure but is bound as prose downstream." Regenerate the built mirror.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` to highlight `typed_as` as a keyword; run `cd editors/vscode && make` and commit artifacts.
  - `make verify-examples` green on 01-142.
  - `make verify-diagnostics` green with new E533/E534 fixtures.
  - `CHANGELOG.md` + `docs/VERSIONING.md` entries for the minor bump.
* Verification (required proof):
  - `make verify-examples` green on 01-142.
  - `make verify-diagnostics` green including new codes.
  - Behavior preservation: every pre-existing example using `output_target_decl` (examples 79, 85, 90, 121 per the staged `git status`) passes its manifest byte-for-byte.
  - Built `.prompt` mirrors match curated source.
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md` documents `typed_as:`.
  - `docs/EMIT_GUIDE.md` updates only if emit shape changes.
  - `docs/COMPILER_ERRORS.md` adds E533/E534.
  - `skills/.curated/doctrine-learn/references/emit-targets.md` and `outputs-and-schemas.md` teach the typed-identity idiom.
  - `skills/.curated/agent-linter/references/finding-catalog.md` gains the new AL-finding.
  - One-line grammar comment at the new `typed_as_stmt` production naming it as a sibling of `FieldTypeRef`'s nested-type shape (pattern propagation).
* Exit criteria (all required):
  - Grammar accepts `typed_as: <name_ref>` inside output_target_body; parser populates `OutputTargetDecl.typed_as`.
  - Validator rejects E533/E534 cases with stable codes, correct line numbers, and related sites.
  - Downstream agents binding the typed output receive a typed input resolved to the declared family; bindings on non-matching families emit E534.
  - `examples/142_typed_handoff_note_identity/` ships with valid + invalid cases covering E533 and E534.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`, `skills/.curated/doctrine-learn/references/emit-targets.md`, `outputs-and-schemas.md`, `skills/.curated/agent-linter/references/finding-catalog.md` all reflect the new primitive.
  - `make verify-examples` and `make verify-diagnostics` green; manifest of every pre-existing example unchanged.
  - `CHANGELOG.md` + `docs/VERSIONING.md` minor-bump entries written.
* Rollback: revert grammar production, model field, validator methods, resolver wiring, and E-code registrations; delete `examples/142_*`; revert doctrine-learn, agent-linter, and docs edits; revert built `.prompt` mirrors and VSCode artifacts.

## Phase 5 — §7 skill-binding `mode` + output-shape selector drift normalization

* Goal: one `mode` production across review cases, law matchers, skill bindings, and output-shape selectors; add mode binding on skill entries so producer vs. audit bindings are compile-time distinguishable; soft-deprecate the enum-only output-shape `mode` form with `E543`.
* Work: extend `skill_entry_body:664-673` with the shipped expr-based `mode_stmt` production from `doctrine.lark:957` (no new grammar; reuse the existing production verbatim). Add `SkillEntry.mode: ModeStmt | None` to the model. Add `_validate_skill_entry_mode` to `ValidateAgentsMixin` in `doctrine/_compiler/validate/agents.py`: resolve the mode `as` target to a declared enum; enforce that audit-mode skill bindings reject output-target emission side effects; verify the skill package declares a contract variant per mode. Emit `E540` (mode ref unresolved), `E541` (audit-mode binding with output-target emission), `E542` (skill package has no contract for the declared mode). Concurrently, normalize `output_shape_selector_stmt:740`: accept both the enum-only form (`mode CNAME as name_ref`) and the expr-based form (`mode CNAME = expr as name_ref`); emit soft-deprecation `E543` when the enum-only form is used. Append a Decision Log entry for the soft-deprecation with timebox. Ship a manifest-backed example showing a skill bound in producer mode on one agent and audit mode on another.
* Checklist (must all be done):
  - Extend `doctrine/grammars/doctrine.lark` `skill_entry_body:664-673` to allow the existing `mode_stmt` production verbatim (one-line alternation; no new production).
  - Extend `output_shape_selector_stmt:740` grammar to accept both enum-only and expr-based forms (alternation).
  - Add `SkillEntry.mode: ModeStmt | None` field in `doctrine/_model/io.py` (or the correct submodule).
  - Extend `OutputShapeSelectorConfig` in `doctrine/_model/io.py:255-258` to carry the optional expr field.
  - Parser wiring emits the new fields.
  - Add `_validate_skill_entry_mode` to `ValidateAgentsMixin` in `doctrine/_compiler/validate/agents.py`: mode target resolves to a declared enum; audit-mode bindings reject output-target side effects; skill package's declared mode contract matches the bound mode.
  - Add `_validate_output_shape_selector_mode_form` to the appropriate validator mixin to emit `E543` (soft-deprecation) when the enum-only form is used.
  - Register E-codes in `docs/COMPILER_ERRORS.md`: `E540 Skill-binding mode reference does not resolve`, `E541 Audit-mode skill binding emits to an output target`, `E542 Skill package has no contract for the declared mode`, `E543 Deprecated enum-only output-shape mode form (use expr-based mode instead)`.
  - Add diagnostic fixtures for E540/E541/E542/E543 in `_diagnostic_smoke/compile_checks.py`.
  - Add `examples/143_skill_binding_producer_audit_mode/` with one producer agent (producer mode) and one critic agent (audit mode) sharing a skill, `prompts/AGENTS.prompt`, `cases.toml`, and `ref/` artifacts. Include invalid cases firing E540, E541, and E542.
  - Migrate `examples/138_output_shape_case_selector` (and any other examples using the enum-only output-shape mode) to show the expr-based form where it is natural. Preserve at least one regression fixture that still uses the enum-only form and produces `E543` to keep the soft-deprecation signal honest until the timebox expires.
  - Update `docs/LANGUAGE_REFERENCE.md`: document `mode` on skill bindings and the expr-based output-shape selector form; note the enum-only form's soft-deprecation and timebox.
  - Update `docs/COMPILER_ERRORS.md` with E540-E543 entries including timebox language for E543 (plain-language 7th grade; "Use the expr-based `mode CNAME = expr as name_ref` form; the enum-only form will be removed at the next minor bump.").
  - Update curated `skills/.curated/doctrine-learn/references/skills-and-packages.md` with skill-binding mode teaching (producer vs. audit idiom) and a cross-reference to the unified `mode` production. Regenerate the built mirror.
  - Update curated `skills/.curated/doctrine-learn/references/outputs-and-schemas.md` to reflect the unified `mode` production on output-shape selectors. Regenerate the built mirror.
  - Add an agent-linter finding to curated `finding-catalog.md` for "critic re-invokes producer skill instead of binding audit mode." Add a second finding for "output-shape selector uses enum-only `mode` form when expr-based is available." Regenerate the built mirror.
  - Append a Decision Log entry in Section 10 with heading `## 2026-04-19 - Normalize `output_shape_selector_stmt` to expr-based `mode` form (soft-deprecation with timebox)` — context, options, decision, consequences, follow-ups, timebox = one minor-version cycle.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` if any new token surfaces; run `cd editors/vscode && make`.
  - `make verify-examples` green on 01-143.
  - `make verify-diagnostics` green with new E540-E543 fixtures.
  - `CHANGELOG.md` + `docs/VERSIONING.md` entries for the minor bump; `docs/VERSIONING.md` records the `E543` timebox.
* Verification (required proof):
  - `make verify-examples` green on 01-143.
  - `make verify-diagnostics` green including new codes.
  - Behavior preservation: every pre-existing example using `skill_entry` or `output_shape_selector_stmt` passes its manifest byte-for-byte; only the `E543` soft-diagnostic changes the diagnostic output of migrated examples (diagnostic is non-fatal; compilation continues).
  - Built `.prompt` mirrors match curated source.
  - `cd editors/vscode && make` is clean if syntax file changed.
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md` documents the unified `mode` production on skill bindings and output-shape selectors, with the soft-deprecation timebox.
  - `docs/COMPILER_ERRORS.md` adds E540-E543 with plain-language descriptions.
  - `docs/VERSIONING.md` records the soft-deprecation timebox.
  - `skills/.curated/doctrine-learn/references/skills-and-packages.md` and `outputs-and-schemas.md` teach the unified `mode`.
  - `skills/.curated/agent-linter/references/finding-catalog.md` adds two AL-findings.
  - One-line grammar comment at `skill_entry_body:664-673` naming `mode_stmt` as the canonical mode production shared with review cases and law matchers (pattern propagation).
* Exit criteria (all required):
  - Grammar accepts `mode_stmt` inside `skill_entry_body` and accepts both enum-only and expr-based forms inside `output_shape_selector_stmt`; parser populates the new model fields.
  - Validator resolves skill-binding mode references, rejects audit-mode bindings that emit to output targets, rejects skill packages missing contract variants for the bound mode, and emits the soft-deprecation E543 on the enum-only output-shape form.
  - `examples/143_skill_binding_producer_audit_mode/` ships with valid + invalid cases covering E540, E541, E542.
  - At least one example fires E543 (the soft-deprecation regression fixture).
  - `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, `skills/.curated/doctrine-learn/references/skills-and-packages.md`, `outputs-and-schemas.md`, `skills/.curated/agent-linter/references/finding-catalog.md` all reflect the new surface.
  - Decision Log entry for the soft-deprecation timebox is appended to Section 10.
  - `make verify-examples` and `make verify-diagnostics` green; manifest of every pre-existing example unchanged except for diagnostic additions on the migrated examples.
  - `CHANGELOG.md` + `docs/VERSIONING.md` minor-bump entries written.
* Rollback: revert grammar alternations on `skill_entry_body` and `output_shape_selector_stmt`; revert model field additions; revert validator methods and E-code registrations; revert the Decision Log entry; delete `examples/143_*` and re-migrate the existing output-shape example; revert doctrine-learn, agent-linter, and docs edits; revert built `.prompt` mirrors and VSCode artifacts.

## Phase 6 — §6 typed abstract-agent parameters (narrow typed annotation)

* Goal: let one abstract agent declare typed policy slots and N concrete descendants bind them by typed name reference, with compile-time type checking — without forcing convergence with skill `host_contract` slots or output-schema fields (explicit non-convergence, per the locked §6 decision in §5.3).
* Work: extend `agent_slot_abstract` at `doctrine.lark:139-146` with an optional `: <TypedEntityRef>` annotation on the abstract-slot declaration. Concrete-agent binding continues to use the shipped `inherit`/`override` syntax; the bound `name_ref` must resolve to an entity of the declared family. Extend `AuthoredSlotField` in `doctrine/_model/agent.py:14-17` with `declared_type: NameRef | None`. Add `_validate_typed_abstract_slot_binding` to `ValidateAgentsMixin` in `doctrine/_compiler/validate/agents.py`: the bound value on every concrete descendant whose abstract parent declared a type must resolve to a `name_ref` of the declared family. Emit `E538` (bound entity family mismatch) and `E539` (type annotation references unknown entity). Ship a manifest-backed example with one abstract agent carrying typed policy slots and at least two concrete descendants that bind the slots to different typed entities. Append a Decision Log entry explicitly recording the non-convergence with skill `host_contract` slots and output-schema fields.
* Checklist (must all be done):
  - Extend `doctrine/grammars/doctrine.lark` `agent_slot_abstract` at `:139-146` with optional type annotation: `abstract CNAME [: name_ref]`.
  - Extend `AuthoredSlotField` in `doctrine/_model/agent.py:14-17` with `declared_type: NameRef | None`.
  - Parser wiring populates `declared_type` from the new grammar production.
  - Add `_validate_typed_abstract_slot_binding` to `ValidateAgentsMixin` in `doctrine/_compiler/validate/agents.py`: look up declared type on every abstract slot; verify the bound value on every concrete descendant resolves to a `name_ref` of the declared family; reject mismatches.
  - Register E-codes in `docs/COMPILER_ERRORS.md`: `E538 Concrete agent binds typed abstract slot to a wrong-family entity`, `E539 Typed abstract slot annotation references an unknown entity`.
  - Add diagnostic fixtures for E538/E539 in `_diagnostic_smoke/compile_checks.py`.
  - Add `examples/144_abstract_agent_typed_parameters/` with one abstract agent declaring typed policy slots and at least two concrete descendants binding the slots to different entity instances. Include invalid cases firing E538 and E539.
  - Update `docs/LANGUAGE_REFERENCE.md`: document typed abstract-slot annotation + concrete-binding family-match rule.
  - Update `docs/COMPILER_ERRORS.md` with E538/E539.
  - Update curated `skills/.curated/doctrine-learn/references/agents-and-workflows.md` with typed-parameter teaching; cross-reference the inheritance teaching. Regenerate the built mirror.
  - Add an agent-linter finding to curated `finding-catalog.md` for "N near-duplicate concrete agents that could share an abstract with typed parameters." Regenerate the built mirror.
  - Append a Decision Log entry in Section 10 with heading `## 2026-04-19 - Typed abstract-agent parameters stay narrow; no convergence with skill host_contract slots or output-schema fields` — context, options, decision, consequences (three-shape semantic distinction preserved), follow-ups.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` to highlight the optional `:` type annotation on abstract slots; run `cd editors/vscode && make`.
  - `make verify-examples` green on 01-144.
  - `make verify-diagnostics` green with new E538/E539 fixtures.
  - `CHANGELOG.md` + `docs/VERSIONING.md` entries for the minor bump.
* Verification (required proof):
  - `make verify-examples` green on 01-144.
  - `make verify-diagnostics` green including new codes.
  - Behavior preservation: every pre-existing example using abstract agents (extensive across the corpus) passes its manifest byte-for-byte.
  - Built `.prompt` mirrors match curated source.
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md` documents typed abstract-slot annotation.
  - `docs/COMPILER_ERRORS.md` adds E538/E539.
  - `skills/.curated/doctrine-learn/references/agents-and-workflows.md` teaches typed parameters.
  - `skills/.curated/agent-linter/references/finding-catalog.md` gains the new AL-finding.
  - One-line grammar comment at `agent_slot_abstract` noting that the annotation is deliberately narrower than skill `host_contract` family typing (pattern propagation; records the non-convergence inline to prevent future mistaken unification).
* Exit criteria (all required):
  - Grammar accepts the optional type annotation; parser populates `declared_type`.
  - Validator rejects E538/E539 cases with stable codes, correct line numbers, and related sites.
  - `examples/144_abstract_agent_typed_parameters/` ships with valid + invalid cases covering E538 and E539.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`, `skills/.curated/doctrine-learn/references/agents-and-workflows.md`, `skills/.curated/agent-linter/references/finding-catalog.md` all reflect the new surface.
  - Decision Log entry for the non-convergence choice is appended to Section 10.
  - `make verify-examples` and `make verify-diagnostics` green; manifest of every pre-existing example unchanged.
  - `CHANGELOG.md` + `docs/VERSIONING.md` minor-bump entries written.
* Rollback: revert grammar annotation; revert model field; revert validator method and E-code registrations; revert Decision Log entry; delete `examples/144_*`; revert doctrine-learn, agent-linter, and docs edits; revert built `.prompt` mirrors and VSCode artifacts.

## Phase 7 — §5 declarative `rule` primitive + `RULE###` diagnostics

* Goal: ship a top-level `rule` declaration that lets projects encode inheritance/binding invariants as compile-time checks, with a new `RULE###` diagnostic namespace that renders through the existing code-agnostic formatter and fixture harness.
* Work: add `rule_decl` to `doctrine/grammars/doctrine.lark:58-80` following the canonical typed-entity shape. Body contains `scope:` (closed predicate set in P7: `agent_tag: <TAG>`, `flow: <FLOW_NAME>`, `role_class: <CLASS>`, `file_tree: <GLOB>`, combined with AND); `assertions:` (closed predicate set: `requires inherit <ENTITY_REF>`, `forbids bind <SKILL_REF>`, `requires declare <SLOT_NAME>`); `message:` template. Add `doctrine/_model/rule.py` with `RuleDecl`, `RuleScope`, `RuleAssertion` dataclasses. Add `doctrine/_compiler/validate/rules.py` with `ValidateRulesMixin`; compose it into `ValidateMixin.__bases__` at `doctrine/_compiler/validate/__init__.py:33-47`. Rules evaluate at the end of compile: every rule's scope predicate runs across the declared agent graph; every scoped agent is checked against the assertions; failures emit `RULE001-RULE005`. Add the `RULE###` band to `docs/COMPILER_ERRORS.md`. Ship a manifest-backed example with a project-local rule enforcing an inheritance invariant across a set of agents. Update teaching and linter in the same phase.
* Checklist (must all be done):
  - Add `rule_decl` to `doctrine/grammars/doctrine.lark:58-80` following the canonical typed-entity declaration shape.
  - Add grammar productions for `rule_scope_block`, `rule_assertions_block`, and the closed predicate set (`agent_tag_predicate`, `flow_predicate`, `role_class_predicate`, `file_tree_predicate`; `requires_inherit`, `forbids_bind`, `requires_declare`).
  - Add `doctrine/_model/rule.py` with `RuleDecl(name, title, scope, assertions, message)`, `RuleScope(predicates)`, `RuleAssertion(kind, target)` dataclasses; export from `doctrine/model.py`.
  - Parser wiring emits `RuleDecl` from the new grammar production.
  - Add `doctrine/_compiler/validate/rules.py` with `ValidateRulesMixin` exposing `_validate_all_rules`. Compose it into `ValidateMixin.__bases__` at `doctrine/_compiler/validate/__init__.py:33-47`.
  - Implement scope-predicate evaluation over the declared agent graph; implement assertion evaluation (`requires inherit`, `forbids bind`, `requires declare`).
  - Extend `doctrine/_compiler/diagnostics.py` fallback stage labels to include a `rule-check` stage; the public formatter at `doctrine/diagnostics.py:86` is already code-agnostic and needs no change.
  - Extend `doctrine/_diagnostic_smoke/compile_checks.py` `_expect_compile_diagnostic` harness (if needed) to accept `code="RULE###"` the same way it accepts `E###`. If the harness is already code-agnostic, confirm the existing pattern works with the new codes by adding RULE fixtures.
  - Register diagnostic codes in `docs/COMPILER_ERRORS.md` under a new `RULE###` band: `RULE001 Rule declaration references an unknown scope predicate`, `RULE002 Rule assertion target does not resolve`, `RULE003 Scoped agent fails `requires inherit` assertion`, `RULE004 Scoped agent violates `forbids bind` assertion`, `RULE005 Scoped agent fails `requires declare` assertion`. Reserve `RULE006-RULE099` for future P7 extensions and `RULE100+` for future open-expression-language evolution.
  - Add diagnostic fixtures for RULE001-RULE005 in `_diagnostic_smoke/compile_checks.py`.
  - Add `examples/145_declarative_project_lint_rule/` with one `rule` declaration enforcing an inheritance invariant, at least two in-scope agents, and both a passing case and an invalid case firing RULE003.
  - Update `docs/LANGUAGE_REFERENCE.md` with the `rule` entity section (declaration, scope predicate set, assertion predicate set, message template, evaluation semantics).
  - Update `docs/COMPILER_ERRORS.md` with the new `RULE###` band and the first five codes; note the closed-predicate scope for P7 and the `RULE100+` reservation for future open expressions.
  - Add new curated reference `skills/.curated/doctrine-learn/references/rules.md` with a teaching section; register it in `skills/.curated/doctrine-learn/SKILL.md` and in any curated index. Regenerate the built mirror `skills/doctrine-learn/prompts/refs/rules.prompt`.
  - Add an agent-linter finding to curated `finding-catalog.md` for "project lacks an enforcement rule for this inheritance invariant (comment-block discipline is not enough)." Regenerate the built mirror.
  - Update `editors/vscode/syntaxes/doctrine.tmLanguage.json` to reserve `scope`, `assertions`, `requires`, `forbids` as rule-body keywords (the `rule` keyword is already reserved per `:1375`); run `cd editors/vscode && make` and commit artifacts.
  - `make verify-examples` green on 01-145.
  - `make verify-diagnostics` green with new RULE001-RULE005 fixtures.
  - `make verify-package` green (new entity type crosses the public package surface).
  - `uv run --locked python -m unittest tests.test_release_flow` green (release flow recognizes the new primitive and new diagnostic band).
  - `CHANGELOG.md` + `docs/VERSIONING.md` entries for the minor bump; `docs/VERSIONING.md` names the new `RULE###` band classification and its stability rule (codes are frozen once shipped, same as E-codes).
* Verification (required proof):
  - `make verify-examples` green on 01-145.
  - `make verify-diagnostics` green including all RULE001-RULE005 fixtures; diagnostic output renders through the existing formatter without a code-specific branch.
  - `make verify-package` green to prove the new entity does not break public package metadata.
  - `uv run --locked python -m unittest tests.test_release_flow` green.
  - Behavior preservation: every pre-existing example (01-144) passes its manifest byte-for-byte (rules default to empty; existing agents are never in any rule's scope).
  - Built `.prompt` mirrors match curated source exactly; the new `rules.prompt` mirror is registered in the skill index.
  - `cd editors/vscode && make` is clean.
* Docs/comments (propagation; only if needed):
  - `docs/LANGUAGE_REFERENCE.md` documents the `rule` entity.
  - `docs/COMPILER_ERRORS.md` adds the `RULE###` band and the first five codes.
  - `docs/VERSIONING.md` names the RULE-code stability rule.
  - `skills/.curated/doctrine-learn/references/rules.md` is the new teaching reference; `SKILL.md` index updated.
  - `skills/.curated/agent-linter/references/finding-catalog.md` gains the new AL-finding.
  - Three-line comment header at `doctrine/_compiler/validate/rules.py` describing the closed-predicate scope for P7 and the reserved `RULE100+` band for future evolution (pattern propagation; prevents future contributors from inventing an open-expression DSL without explicit planning).
* Exit criteria (all required):
  - Grammar accepts `rule <CNAME>: "<title>"` with scope/assertions/message body; parser populates `RuleDecl`.
  - `ValidateRulesMixin` is composed into `ValidateMixin`; all rules evaluate at the end of compile against the agent graph.
  - Validator rejects RULE001-RULE005 cases with stable codes, correct line numbers, and related sites.
  - `examples/145_declarative_project_lint_rule/` ships with one passing rule and an invalid case firing RULE003.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, `skills/.curated/doctrine-learn/references/rules.md`, `skills/.curated/doctrine-learn/SKILL.md`, `skills/.curated/agent-linter/references/finding-catalog.md` all reflect the new primitive.
  - `make verify-examples`, `make verify-diagnostics`, `make verify-package`, and `tests.test_release_flow` all green.
  - `CHANGELOG.md` + `docs/VERSIONING.md` minor-bump entries written; `RULE###` band documented as the second stable diagnostic namespace.
  - A simulated layered-review author re-expresses the psflows audit's §5 "every composer-style agent inherits UpstreamPoisoningInvariant" invariant using `rule` + `RULE003` and breaks the build on the violation.
* Rollback: revert grammar production, model module, validator mixin + composition, diagnostic-stage label, fixture extensions, and E-code registrations; delete `examples/145_*`; revert doctrine-learn and agent-linter curated edits and built mirrors; revert docs edits and VSCode artifacts. After rollback, `make verify-examples` and `make verify-diagnostics` return to the 01-144 baseline (P6 end state).
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

_Per-phase: new E-code or RULE-code fixtures under `tests/` or `examples/` manifest, covering the positive path and at least one negative path per new primitive._

## 8.2 Integration tests (flows)

_Per-phase: at least one manifest-backed example that exercises the primitive end-to-end from grammar through emit. `make verify-examples` is the primary signal._

## 8.3 E2E / device tests (realistic)

_Simulated psflows-style layered-review author re-expresses each audit gap using the shipped primitive. This is a manual walk-through per phase, not a harness — simulated authorship is the E2E signal._

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

_Additive, per-phase, behind no flags. Each phase is a normal doctrine release following `AGENTS.md` rules. Version bump classification per `docs/VERSIONING.md`: prefer patch for additive grammar; minor only when a new first-class primitive lands (e.g., `rule`); major only if an existing example breaks — not expected._

## 9.2 Telemetry changes

_None required. Doctrine is authoring-side; runtime telemetry is harness territory._

## 9.3 Operational runbook

_None required. Standard `make verify-examples` / `make verify-diagnostics` per phase._

# 10) Decision Log (append-only)

## 2026-04-19 - Plan bootstrap: bundle all seven gaps into one elegant-convergence plan

- Context: psflows 2026-04-19 audit surfaced seven claimed gaps; doctrine audit confirmed six real, one shipped-but-untaught. User asked for best case for elegance plus peer-pattern normalization.
- Options: (a) seven small plans, one per gap; (b) one bundled plan with peer-pattern normalization as a first-class goal.
- Decision: (b). Rationale: peer-pattern convergence cannot be delivered one gap at a time without accumulating drift. Each gap closure shares grammar with at least one other gap's closure (`mode` across §7 and review cases, `override` across §2 and agent slots, `family:` across §3 and §4, typed parameters across §6 and skill host_contract). Bundling lets each phase ship grammar, model, compiler, example, docs, and teaching surfaces in lockstep.
- Consequences: larger single plan; tighter cross-phase consistency; slower time-to-first-ship-of-any-gap, but faster time-to-coherent-language-surface.
- Follow-ups: research stage must produce the peer-pattern audit in `# 3.2` before phase-plan locks the phase split.

## 2026-04-19 - Phase-plan: split §3+§4 and §6+§7 bundles into single-gap execution phases

- Context: the bootstrap TL;DR grouped §3+§4 into P3 (shared "typed envelope" shape) and §6+§7 into P4 (shared "parameterized binding" shape). Deep-dive confirmed these pairs share motivation but touch different grammar productions, different validator mixins, and different downstream resolution paths.
- Options: (a) keep the bundles; (b) split each bundle into single-gap phases, biasing toward more phases than fewer per `section-quality.md` guidance.
- Decision: (b). Rationale: §3's `typed_as:` extends `output_target_body` and adds downstream input-binding checks in `ValidateOutputsMixin`; §4's `receipt` family extends `package_host_slot_family` and adds dotted-reference resolution in `ValidateContractsMixin`. They can be verified independently. Same split for §6 (narrow typed annotation on `agent_slot_abstract` in `ValidateAgentsMixin`) and §7 (`mode_stmt` reuse on `skill_entry_body` plus output-shape normalization, also in `ValidateAgentsMixin` but a distinct coherent unit). The section-quality rule "if two decompositions are both valid, bias toward more phases than fewer" applies.
- Consequences: execution phases grow from 5 (P1-P5, dropping the already-complete P0) to 7 (P1-P7). Each phase is smaller, more self-contained, and more credibly testable. Cross-phase dependencies remain lightweight; no phase depends on work from a later phase.
- Follow-ups: audit-implementation must validate each phase's checklist and exit criteria independently; the `implement-loop` frontier runs in P1→P7 order.

## 2026-04-19 - Phase-plan: authoritative Section 7 written; no planning blockers remain

- Context: `phase-plan` stage of the `auto-plan` controller converted the locked architecture + call-site audit into the authoritative execution checklist for all seven gap closures plus the output-shape `mode` drift normalization.
- Options: N/A — this is a sequencing record, not an architectural choice.
- Decision: Section 7 now owns the one execution checklist. Every obligation from Section 5 (locked design decisions), Section 6.1 (change map), Section 6.2 (migration notes), and Section 6.1 Pattern Consolidation Sweep is represented in one phase's `Checklist (must all be done)` or `Exit criteria (all required)`. No required work lives only in prose, migration notes, or verification narration.
- Consequences: the plan is decision-complete. Doc is ready for `implement-loop` handoff. E-code allocations in `E531-E543` and initial RULE band `RULE001-RULE005` (with `RULE006-RULE099` reserved for P7 extensions and `RULE100+` reserved for future open-expression evolution) are locked.
- Follow-ups: `implement-loop` runs P1→P7 against this doc. Each phase's Exit criteria is the audit surface that gates phase completion. Soft-deprecation of the output-shape enum-only `mode` form (via `E543`) is timeboxed to one minor-version cycle; the P5 Decision Log entry records the exact removal trigger.
