---
title: "Doctrine - Fail-Loud Gap Audit And Enforcement - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: phased_refactor
related:
  - docs/FAIL_LOUD_GAPS.md
  - docs/COMPILER_ERRORS.md
  - docs/VERSIONING.md
  - CHANGELOG.md
---

# TL;DR

## Outcome

Doctrine gets a grounded plan to turn real silent-accept bugs into clear
compile errors without guessing, over-tightening the language, or breaking
accepted behavior by accident.

## Problem

The new fail-loud gap doc lists many places where the compiler seems to accept
easy author mistakes. Some are likely real bugs. Some may be intentional
language flexibility. Right now we do not have a reviewed plan that separates
those cases.

## Approach

Audit the shipped compiler, parser, resolver, validators, docs, and manifest
corpus first. Classify each candidate gap before planning any enforcement
change. During research and deep-dive, add other proven silent-accept failure
points that should fail loudly.

## Plan

Research the current shipped truth, deep-dive the highest-risk gap families,
lock the owner-layer and compatibility rubric, then execute a phased plan that
starts with a required family-classification phase and implements only the
confirmed errors plus the adjacent docs, diagnostics, tests, and example-proof
updates they require.

## Non-negotiables

- Do not assume every item in `FAIL_LOUD_GAPS.md` is correct.
- Do not add lint-like errors for style, taste, or speculative misuse.
- Preserve shipped accepted behavior unless repo evidence shows it is a true
  semantic bug or the plan explicitly chooses a public behavior change.
- Keep one canonical error story across compiler logic, diagnostics, docs, and
  manifest-backed proof.
- Treat tests, manifest-backed examples, and required doc updates as part of
  the shipped change, not as optional follow-up cleanup.
- No runtime shims, soft fallbacks, or hidden downgrade paths.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-16
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If we audit the shipped compiler against the candidate fail-loud gaps before
planning fixes, then we can separate true silent-accept bugs from acceptable
language behavior, choose the right compatibility posture for each confirmed
bug family, and produce one implementation plan that tightens real errors
without inventing speculative ones while requiring aligned tests, examples,
and docs before any confirmed change counts as done.

## 0.2 In scope

- Audit the candidate gaps in `docs/FAIL_LOUD_GAPS.md` against shipped code,
  tests, manifest-backed examples, and live docs.
- Add newly discovered silent-accept failure points when research proves they
  are real, easy-to-make mistakes that should fail loudly.
- Decide the correct disposition for each audited gap:
  - confirmed compiler error to add
  - accepted behavior to preserve
  - public behavior change that needs versioning treatment
  - deferred only if blocked by a real unresolved decision
- Default compatibility posture: preserve shipped accepted behavior unless the
  audit proves the current behavior is a true bug or the plan explicitly
  approves a public behavior change.
- Plan the compiler, parser, resolver, validation, diagnostics, docs, and
  corpus work needed for confirmed fail-loud changes.
- Require the plan to name the needed unit-test updates, manifest-backed
  example updates, and doc updates for each confirmed fix, so implementation
  cannot stop at compiler code alone.
- Plan adjacent-surface updates for any confirmed public compatibility change,
  including `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, and
  `CHANGELOG.md` when required.
- Allow architectural convergence across the canonical compiler and diagnostics
  paths when needed to avoid parallel validation rules or duplicate truth.

## 0.3 Out of scope

- Blindly implementing every item already listed in `FAIL_LOUD_GAPS.md`.
- Adding style warnings, best-practice lint, or opinionated authoring rules
  that do not protect real shipped semantics.
- Rewriting the language around a new validation model before the audit proves
  that it is needed.
- Runtime workarounds, downgrade behavior, or compatibility shims.
- Unrelated compiler cleanup that does not serve the confirmed fail-loud
  boundary work.

## 0.4 Definition of done (acceptance evidence)

- Every audited candidate gap has a recorded disposition grounded in shipped
  code and proof surfaces.
- The plan names which gap families are true errors, which are accepted
  behavior, and which require explicit public-compatibility handling.
- The plan identifies the canonical owner paths for the confirmed fixes across
  parser, resolve, validate, compile, diagnostics, docs, and examples.
- The plan names the required unit tests, manifest-backed example updates, and
  doc updates needed to keep the public language story aligned.
- The plan makes it explicit which doc surfaces must stay in sync, including
  `docs/FAIL_LOUD_GAPS.md`, `docs/COMPILER_ERRORS.md`,
  `docs/VERSIONING.md`, and `CHANGELOG.md` when required by the confirmed
  behavior change.
- The plan is decision-complete enough that implementation does not need to
  guess which documented gaps to enforce.

## 0.5 Key invariants (fix immediately if violated)

- No assumption that a listed gap is wrong just because it feels confusing.
- No new compiler errors for cases that the audit decides are intentional or
  public accepted behavior.
- No parallel error stories between compiler logic, diagnostics docs, and proof
  corpus.
- No confirmed fail-loud change counts as complete until its required tests,
  examples, and docs land together.
- No silent behavior drift in public language surfaces.
- No fallbacks or runtime shims.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Separate true bugs from accepted behavior.
2. Tighten fail-loud boundaries only where the language truly needs them.
3. Keep the public error and compatibility story honest.
4. Route fixes through canonical compiler and diagnostics paths.
5. Add new gap families only when research proves them.

## 1.2 Constraints

- Doctrine treats `doctrine/` plus the manifest-backed corpus as shipped truth.
- Existing error-code meaning is stable once shipped.
- Public compatibility changes may require `docs/VERSIONING.md` and
  `CHANGELOG.md` updates.
- The current gap list mixes proven bugs, probable bugs, and likely boundary
  questions, so classification work comes before implementation planning.

## 1.3 Architectural principles (rules we will enforce)

- Fail loud for real semantic mistakes, not for style.
- Reuse canonical validation or resolution paths instead of adding shadow
  checks.
- Keep compiler logic, diagnostic wording, docs, and proof aligned.
- Treat tests, examples, and public docs as first-class outputs of any
  confirmed fail-loud change.
- Prefer explicit disposition over hidden compatibility assumptions.

## 1.4 Known tradeoffs (explicit)

- Tightening compiler behavior may improve DX but still count as a public
  behavior change.
- Some silent-accept cases may be better fixed by docs or rendering changes
  instead of new compile errors.
- A broad fail-loud sweep can overreach if we do not keep the audit grounded in
  shipped truth.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine now has a curated doc of likely fail-loud gaps in
`docs/FAIL_LOUD_GAPS.md`. The compiler already enforces many sharp language
rules, but several surfaces still appear to accept easy author mistakes and
then render plausible output.

## 2.2 What’s broken / missing (concrete)

We do not yet have a reviewed architecture plan that says which listed gaps are
real errors, which are accepted behavior, which adjacent surfaces must move
with each confirmed fix, and which compatibility posture applies when shipped
behavior changes.

## 2.3 Constraints implied by the problem

- The audit must inspect live code, docs, and proof together.
- The plan must allow new proven fail-loud gaps to enter scope during research
  and deep-dive.
- The final implementation plan must not treat the current gap doc as a source
  of unquestioned truth.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- No external anchor is adopted for the initial controller pass. Reject generic
  parser or compiler prior art as the primary spec for now because Doctrine
  already ships a grammar, stable error bands, and manifest-backed proof.
- Revisit external material only if deep-dive hits a design choice that repo
  truth cannot settle on its own.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors:
  - `docs/FAIL_LOUD_GAPS.md` - candidate gap ledger only. It is a starting set,
    not shipped language truth.
  - `doctrine/grammars/doctrine.lark` - shipped grammar boundary. It keeps
    agent fields open through `agent_slot_field: CNAME ...`, which is the root
    reason near-miss reserved field typos can currently fall through as normal
    authored slots.
  - `doctrine/parser.py` - parse boundary from Lark trees into typed AST nodes.
  - `doctrine/_compiler/indexing.py` - first compile-time registry boundary. It
    already owns duplicate declaration checks and other early fail-loud shape
    checks, so it is the reference pattern for duplicate-name and structural
    enforcement.
  - `doctrine/_compiler/session.py` and `doctrine/_compiler/context.py` -
    stable compile entry and orchestration. `CompilationContext` composes
    resolve, validate, compile, display, and flow mixins, so new enforcement
    should land in the real owner phase instead of a post-render patch.
  - `doctrine/_compiler/validate/__init__.py` - semantic validation boundary.
    Route, review, output, readable, contract, schema-helper, and law-path
    checks all funnel through this surface today.
  - `doctrine/_compiler/resolve/outputs.py`,
    `doctrine/_compiler/compile/final_output.py`, and
    `doctrine/_compiler/output_schema_validation.py` - canonical owner path for
    `final_output`, output-shape/schema lowering, and structured-output
    validation. Existing `E211` through `E218` are the shipped fail-loud
    pattern here.
  - `doctrine/_compiler/validate/routes.py`,
    `doctrine/_compiler/validate/route_semantics_context.py`,
    `doctrine/_compiler/validate/route_semantics_reads.py`, and
    `doctrine/_compiler/resolve/law_paths.py` - canonical owner path for
    workflow-law totality, mode bindings, `match`, `route_from`,
    route/currentness carriers, and route-semantics liveness.
  - `doctrine/_compiler/resolve/reviews.py`,
    `doctrine/_compiler/validate/review_preflight.py`,
    `doctrine/_compiler/validate/review_agreement.py`,
    `doctrine/_compiler/validate/review_gate_observation.py`, and
    `doctrine/_compiler/validate/review_branches.py` - canonical owner path for
    review declaration shape, gate refs, semantic bindings, carried fields, and
    currentness alignment.
  - `doctrine/_compiler/validate/outputs.py` and
    `doctrine/_compiler/validate/readables.py` - canonical owner path for
    output and readable guard validation. Current code walks refs and nested
    expressions, but it does not close helper names, helper arity, or literal
    guard heads.
  - `doctrine/_compiler/diagnostics.py` and `docs/COMPILER_ERRORS.md` - stable
    diagnostic formatting plus the public error-code catalog. New fail-loud
    rules must land with aligned codes and docs, not raw string-only
    exceptions.
  - `doctrine/verify_corpus.py` - manifest-backed proof runner for shipped
    examples and invalid surfaces.
- Canonical path / owner to reuse:
  - Parse- or index-time structural duplicates and reserved-surface collisions
    should fail in grammar, parser, indexing, or the matching resolve layer,
    not in rendering.
  - Workflow-law truth, review meaning, guards, route/currentness, and carrier
    alignment should fail in `doctrine/_compiler/validate/**`.
  - `final_output` and output-schema contradictions should fail in the
    existing `resolve/outputs -> compile/final_output ->
    output_schema_validation` pipeline.
  - New user-facing errors should use `doctrine/_compiler/diagnostics.py` and
    be documented in `docs/COMPILER_ERRORS.md`.
- Adjacent surfaces tied to the same contract family:
  - `docs/FAIL_LOUD_GAPS.md` - must track the audited truth after
    classification.
  - `docs/COMPILER_ERRORS.md` - canonical public error story for any newly
    confirmed parse or compile errors.
  - `docs/VERSIONING.md` and `CHANGELOG.md` - required if a confirmed fail-loud
    fix changes a public accepted authoring surface.
  - `tests/test_parse_diagnostics.py` - existing pattern for parse-stage line
    and column accuracy, including later-conflict pointing.
  - `tests/test_final_output.py` and `tests/test_output_schema_validation.py`
    - preservation signals for `final_output`, output-shape, and schema paths.
  - `tests/test_route_output_semantics.py` - preservation signals for
    workflow-law totality, route guards, and route/currentness semantics.
  - `tests/test_review_imported_outputs.py` and
    `tests/test_diagnostics_formatting.py` - preservation signals for review
    output alignment and public diagnostic shape.
  - `examples/45_review_contract_gate_export_and_exact_failures/cases.toml`,
    `examples/55_owner_aware_schema_attachments/cases.toml`,
    `examples/57_schema_review_contracts/cases.toml`,
    `examples/64_render_profiles_and_properties/cases.toml`,
    `examples/67_semantic_profile_lowering/cases.toml`,
    `examples/91_handoff_routing_route_output_binding/cases.toml`,
    `examples/93_handoff_routing_route_from_final_output/cases.toml`,
    `examples/110_final_output_inherited_output/cases.toml`,
    `examples/111_inherited_output_route_semantics/cases.toml`, and
    `examples/114_workflow_root_readable_blocks/cases.toml` - existing
    manifest-backed proof surfaces closest to the audited gap families.
- Compatibility posture (separate from `fallback_policy`):
  - Preserve existing contract by default, but treat each newly rejected
    previously accepted authoring pattern as a possible public language change
    that must be classified in deep-dive.
  - No runtime bridge or soft downgrade is allowed.
  - If a gap proves to be a docs mismatch or a render-text bug instead of a
    language bug, preserve authoring compatibility and fix the docs or emitted
    explanation instead of inventing a new compiler error.
- Existing patterns to reuse:
  - `doctrine/_compiler/indexing.py::_register_decl` plus shipped duplicate-key
    surfaces such as `E261` and `E491` already show the expected duplicate
    diagnostic shape, including related-source pointers.
  - `tests/test_parse_diagnostics.py` shows the repo standard for
    line-accurate later-conflict parse errors.
  - `docs/COMPILER_ERRORS.md` already defines stable code bands and existing
    routed, review, and `final_output` error families we should extend instead
    of creating a shadow error surface.
- Prompt surfaces / agent contract to reuse:
  - Not primary. This is compiler-owned work, not prompt or runtime-behavior
    work.
- Native model or agent capabilities to lean on:
  - Not primary. Research does not justify any new agent-side tooling.
- Existing grounding / tool / file exposure:
  - unit tests under `tests/`
  - manifest-backed examples under `examples/**/cases.toml`
  - repo verification through `doctrine/verify_corpus.py`
  - public error and compatibility docs under `docs/`
- Duplicate or drifting paths relevant to this change:
  - `docs/FAIL_LOUD_GAPS.md` can drift from `docs/COMPILER_ERRORS.md` and
    shipped code if the audit does not classify each item cleanly.
  - Similar fail-loud rules are already split across parse, indexing, resolve,
    validate, and compile layers. Deep-dive must choose one owner path per gap
    family so we do not create duplicate or contradictory enforcement.
- Capability-first opportunities before new tooling:
  - Use the existing compiler stages, diagnostics helpers, unit tests, and
    manifest verification. No new linter, repo-policing script, or sidecar
    harness is justified by the current research.
- Behavior-preservation signals already available:
  - `tests/test_parse_diagnostics.py` - parse-stage surface and location
    behavior.
  - `tests/test_final_output.py` - prose vs structured final output, inherited
    outputs, split review final output, and routed final-output rendering.
  - `tests/test_output_schema_validation.py` - lowered-schema validation and
    example-instance validation.
  - `tests/test_route_output_semantics.py` - route/currentness liveness and
    `route.exists` guard enforcement.
  - `tests/test_review_imported_outputs.py` - review comment output, imported
    outputs, and split-final trust-surface alignment.
  - `tests/test_verify_corpus.py` plus targeted manifests - emitted proof and
    manifest-backed regression coverage.

## 3.3 Decision gaps that must be resolved before implementation

No unresolved plan-shaping decisions remain at the planning level.

The remaining family-by-family classification output is Phase 1 execution work,
not a missing architecture decision. Phase 1 must record, for every audited
family:

- which currently accepted cases are intentional open-language behavior that
  must stay legal
- which confirmed fail-loud rules need new stable error codes versus a
  tightening of an existing shipped code
- which gap families are public compatibility changes versus bug fixes inside
  the current compatibility promise
- which unit tests and manifest-backed examples prove both the new rejection
  path and the nearby legal authoring that must stay legal
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

The shipped compiler already has clear phase boundaries, but fail-loud
ownership is spread across them.

- `doctrine/grammars/doctrine.lark` keeps many typed fields explicit, but agent
  slots stay open through `agent_slot_field: CNAME ...`.
- `doctrine/parser.py` turns parsed trees into typed AST nodes. It does not try
  to decide semantic intent.
- `doctrine/_compiler/indexing.py` owns duplicate declaration-name checks and a
  few early structural rules before normal compile work starts.
- `doctrine/_compiler/context.py` and `session.py` are the real compile entry.
  They fan work into resolve, validate, compile, display, and flow mixins.
- `doctrine/_compiler/resolve/**` merges inheritance, declaration refs, and
  declaration-level config such as reviews and outputs.
- `doctrine/_compiler/validate/**` owns most typed semantic checks for
  workflows, route/currentness, guards, reviews, and carriers.
- `doctrine/_compiler/compile/**` shapes rendered sections and final-output
  contracts after resolution and validation.
- `doctrine/_compiler/diagnostics.py`, `docs/COMPILER_ERRORS.md`,
  `tests/**`, and `examples/**/cases.toml` are the public error and proof
  surface that must stay aligned with code.

## 4.2 Control paths (runtime)

The current compile flow is:

1. Parse authored prompt text into AST nodes.
2. Index declarations, imports, and duplicate declaration names.
3. Build one `CompilationContext` for the requested agent or declaration.
4. Resolve inherited and imported declarations into concrete bodies.
5. Validate typed semantics such as route/currentness, review meaning, output
   guards, and schema helper rules.
6. Compile final sections, `final_output` metadata, and emitted contract data.
7. Format diagnostics and verify shipped proof through unit tests and the
   manifest-backed corpus.

The silent-accept gaps enter at different stages today. That is why a single
late validator or docs-only fix would be the wrong design.

## 4.3 Object model + key abstractions

The key abstractions already point to the likely owner layer for each gap
family.

- Agents split fields into reserved typed fields plus authored slots. Duplicate
  `role` and typed fields already fail loud in
  `doctrine/_compiler/compile/agent.py`, but open authored slots mean
  near-miss reserved keys still slip through.
- Reviews are resolved by `_resolve_review_body()` in
  `doctrine/_compiler/resolve/reviews.py`. Section keys get duplicate checks,
  but singleton config items like `subject` and `comment_output` are just
  reassigned as the body is walked.
- Workflow law validation uses `_validate_law_stmt_tree()`,
  `_validate_handoff_routing_law_stmt_tree()`, `_validate_match_stmt()`,
  `_validate_route_from_stmt()`, and `_collect_law_leaf_branches()` in
  `doctrine/_compiler/validate/routes.py`.
- Review semantics use `_validate_review_field_bindings()`,
  `_validate_review_gate_label()`, `_collect_review_gate_observation_from_expr`
  logic, and review-agreement checks across
  `validate/review_preflight.py`, `validate/review_gate_observation.py`, and
  `validate/review_agreement.py`.
- Output and readable guards use `_validate_output_guard_expr()` and
  `_validate_readable_guard_expr()`. These walkers recurse through refs,
  binary expressions, calls, and sets.
- Config declaration sections such as `required` and `optional` are split by
  `_config_keys_from_decl()` in `doctrine/_compiler/validate/display.py`, then
  consumed later by `_compile_output_config_rows()` and related compile paths.
- Special output support sections such as `must_include`, `current_truth`,
  `support_files`, `notes`, `standalone_read`, and file sets are shaped in
  `doctrine/_compiler/compile/outputs.py` with partial validation spread across
  output validation and output compilation.
- Structured `final_output` stays on one existing owner path:
  `resolve/outputs.py -> compile/final_output.py ->
  output_schema_validation.py`.

## 4.4 Observability + failure behavior today

Doctrine already has a strong fail-loud spine, but the coverage is uneven.

- Strong today:
  - duplicate agent `role` and typed fields already fail loud with stable codes
    `E203` and `E204`
  - `final_output` has stable error families `E211` through `E218`
  - route/currentness and review semantics already have stable code families in
    the `E331` through `E384` and `E469` through `E500` ranges
  - parse diagnostics already prove line-accurate later-conflict behavior in
    `tests/test_parse_diagnostics.py`
- Weak today:
  - open agent slots plus `_RESERVED_AGENT_FIELD_KEYS` with no close-miss check
    mean reserved-key typos can compile as ordinary authored slots
  - `_resolve_review_body()` silently last-writes singleton config items such
    as `subject`, `contract`, `comment_output`, `selector`, and `cases`
  - `_validate_law_stmt_tree()` and the handoff-routing variant overwrite
    `local_mode_bindings[item.name]` with no duplicate-mode rejection
  - `_collect_law_leaf_branches()` expands `when` bodies only, so the implicit
    false fallthrough path is not modeled
  - `_select_match_cases()` and `_select_route_from_cases()` narrow branches
    before the full author intent is proven, which lets some bad explicit arms
    hide behind `else` or fixed choices
  - `_validate_output_guard_expr()` and `_validate_readable_guard_expr()` walk
    call arguments but do not close helper names, helper arity, or literal-only
    conditions
  - `_config_keys_from_decl()` ignores extra config sections, and compile-time
    config merging can still let one key appear with conflicting required and
    optional meaning
  - `_validate_standalone_read_guard_contract()` is a special-case guarded
    detail check, but the same guard-parity rule is not enforced across all
    support surfaces such as `trust_surface`
  - `doctrine/_compiler/compile/outputs.py` still has output-support surfaces
    where wrong shapes, duplicate trusted paths, duplicate file paths, or
    duplicate table-style keys can fall through to plausible rendered output
  - workflow law inheritance already protects parent accounting with `E382`
    through `E384`, but new child-only law subsection keys do not yet have one
    explicit uniqueness rule

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

Keep the current compiler package layout. Do not add a sidecar linter, repo
policing script, or post-render validator.

Confirmed fail-loud rules should extend the existing owner seams:

- agent field scanning stays on the agent compile boundary
- review singleton config stays on the review resolve boundary
- workflow-law and route semantics stay in route validation and branch
  collection
- review helper and carrier meaning stays in review validation
- guard closure and support-surface guard parity stay in output and readable
  validation
- structured `final_output` and output-schema contradictions stay on the
  existing output-shape and schema pipeline
- diagnostics, tests, examples, and public docs stay part of the same shipped
  change

## 5.2 Control paths (future)

Use one owner-layer rule per gap family.

1. Grammar remains open where Doctrine intentionally allows custom authored
   slots.
2. Parser and indexing own pure syntax errors, declaration-name duplicates, and
   other structure that can be rejected without resolved bodies.
3. Resolve owns singleton declaration-shape conflicts that only make sense once
   inherited and authored review or output bodies are merged.
4. Validate owns typed semantic closure:
   - branch totality
   - enum selector typing
   - helper name and arity
   - review gate and field refs
   - carrier meaning
   - guard parity across support surfaces
5. Compile and output-schema lowering own `final_output` and lowered-schema
   contradictions that depend on the final resolved output shape.
6. Diagnostics remain one public surface through stable codes plus
   `docs/COMPILER_ERRORS.md`.

Each confirmed fail-loud rule should be a clean compile-time cutover with no
runtime bridge. Nearby legal authoring must stay legal and be proven by tests
and manifest-backed examples.

## 5.3 Object model + abstractions (future)

The future architecture should sharpen existing abstractions instead of adding
new ones.

- Keep authored slots as a real feature. Add a narrow reserved-key typo guard
  on the existing agent field scan rather than closing the grammar.
- Treat review singleton config items as compiler-owned singleton keys with the
  same duplicate-accounting discipline the compiler already uses for duplicate
  sections and duplicate typed fields.
- Treat workflow-law branch collection as total-state modeling. The compiler
  must preserve reachable fallthrough paths before it claims route or
  currentness totality.
- Treat mode bindings as closed typed enum sources. A mode binding should be
  rejected unless the compiler can prove it resolves to the declared enum
  source shape.
- Treat `match` and `route_from` as closed typed selector surfaces. Validation
  should prove selector kind and arm meaning before branch narrowing hides bad
  authored arms.
- Treat review helpers and output/readable guard helpers as a closed helper
  vocabulary with checked arity and checked argument meaning.
- Treat compiler-owned carriers such as `current artifact`, `invalidate`, and
  review semantic bindings as needing structural meaning, not just path
  existence and trust-surface presence.
- Treat `standalone_read`, `trust_surface`, and similar support prose as one
  guard-consistency family rather than one-off special cases.
- Treat config declarations and config instances as one closed contract family:
  only shipped sections, no cross-section duplicate keys, and type-appropriate
  config values on output targets.
- Treat compiler-owned output support sections as closed shapes. If a special
  section is present, it should either match the expected structure or fail
  loud instead of falling back to generic prose.
- Keep structured JSON `final_output` owned by resolved output shape and schema
  typing. Do not let prose-only or contradictory shape surfaces coexist once
  the compiler classifies the output as structured JSON.

## 5.4 Invariants and boundaries

- One truthful owner layer per fail-loud rule.
- Grammar stays open for valid custom authored slots.
- No compiler-owned singleton config may silently last-write-win.
- No config declaration or compiler-owned support section may silently ignore
  unknown structure.
- No branch collector may drop a reachable path and still claim totality.
- No helper call may compile unless the compiler knows the helper name, arity,
  and argument meaning.
- No carrier may count as compiler truth unless the bound field can actually
  carry that truth.
- No new linter, shim, or runtime workaround.
- No confirmed fail-loud rule counts as shipped until tests, examples, and
  docs land together.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI surface is in scope.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Reserved agent fields | `doctrine/grammars/doctrine.lark`, `doctrine/_compiler/constants.py`, `doctrine/_compiler/compile/agent.py` | `agent_slot_field`, `_RESERVED_AGENT_FIELD_KEYS`, `_compile_agent_decl()` | Unknown slot keys compile as authored slots even when they are close typos of reserved fields | Add near-miss reserved-field rejection on the existing agent field scan while keeping valid custom slots legal | Grammar is intentionally open; the fail-loud fix belongs on the existing agent field boundary, not in rendering | Close-miss reserved keys become compile errors; legitimate custom slot keys stay valid | New unit coverage near agent compile boundary; likely new invalid manifest-backed example |
| Review singleton config | `doctrine/_compiler/resolve/reviews.py` | `_resolve_review_body()` | `subject`, `subject_map`, `contract`, `comment_output`, `fields`, `selector`, and `cases` silently overwrite earlier values | Track singleton config keys explicitly and reject duplicates in the resolve layer | These conflicts depend on merged review bodies and inheritance, so resolve is the real owner path | Review singleton config is keyed and fail-loud like other compiler-owned review entries | `tests/test_review_imported_outputs.py`; targeted review manifests such as `examples/45_*` and `examples/57_*` |
| Duplicate law mode bindings | `doctrine/_compiler/validate/routes.py` | `_validate_law_stmt_tree()`, `_validate_handoff_routing_law_stmt_tree()` | `local_mode_bindings[item.name] = item` overwrites earlier mode meaning | Reject duplicate mode names in one active law scope | `match`, `when`, and `route_from` depend on one stable mode meaning | One mode name per scope; duplicate mode binding is a compile error | `tests/test_route_output_semantics.py`; route and workflow manifests such as `examples/91_*`, `examples/93_*`, and `examples/111_*` |
| Mode binding type closure | `doctrine/_compiler/validate/routes.py`, `doctrine/_compiler/resolve/law_paths.py` | `_validate_mode_stmt()`, enum and law-path resolution helpers | Some non-constant mode bindings still compile without proving enum-typed meaning | Tighten mode binding validation on the existing law validation path | Route and match logic should not rely on mode sources the compiler has not proved typed | Mode bindings must resolve to the declared enum member or an enum-typed scalar source | `tests/test_route_output_semantics.py`; targeted workflow and routing manifests |
| Law branch totality | `doctrine/_compiler/validate/routes.py`, `doctrine/_compiler/validate/route_semantics_context.py` | `_collect_law_leaf_branches()`, route semantics context builders | `when` bodies expand, but the implicit false fallthrough path is dropped | Preserve false-branch fallthrough when collecting reachable law states | Totality, route liveness, and currentness claims are wrong if reachable false branches vanish | Route/currentness totality is computed from all reachable branches, not only true branches | `tests/test_route_output_semantics.py`; manifests close to routed outputs and route-only flows |
| Closed selector validation | `doctrine/_compiler/validate/routes.py`, `doctrine/_compiler/resolve/law_paths.py` | `_validate_match_stmt()`, `_validate_route_from_stmt()`, selector resolution helpers | Full arm validation is uneven when selectors are fixed, non-mode refs, or `else` is present | Validate selector kind and explicit arm legality before branch narrowing | Authors think they wrote typed branching; compiler must prove that claim before continuing | `match` and `route_from` become closed typed selector surfaces | `tests/test_route_output_semantics.py`; `examples/91_*`, `examples/93_*`, `examples/111_*` |
| Review helper refs and field meaning | `doctrine/_compiler/resolve/reviews.py`, `doctrine/_compiler/validate/review_preflight.py`, `doctrine/_compiler/validate/review_gate_observation.py`, `doctrine/_compiler/validate/review_agreement.py` | review helper resolution, gate observation, semantic-agreement checks | Gate names, field names, and some semantic bindings are checked unevenly; some wrong refs or wrong meanings still compile | Close helper refs and semantic binding meaning on existing review validation paths | Review semantics are compiler-owned truth, so name and meaning must both be proven | Review helper refs, semantic bindings, and carried field names must resolve and structurally match their declared meaning | `tests/test_review_imported_outputs.py`; targeted review manifests such as `examples/45_*`, `examples/53_*`, and `examples/57_*` |
| Currentness and invalidation carriers | `doctrine/_compiler/validate/routes.py`, `doctrine/_compiler/resolve/reviews.py`, `doctrine/_compiler/validate/review_agreement.py` | current-artifact and invalidation carrier checks | Existing checks focus on root, emission, and trust-surface presence more than payload meaning | Extend carrier validation to prove the bound field structurally carries the compiler-owned value | Existence-only carrier checks let the wrong field become trusted semantic truth | Carriers must prove meaning, not just path existence | `tests/test_route_output_semantics.py`, `tests/test_review_imported_outputs.py`; routed review and output manifests |
| Guard helper closure | `doctrine/_compiler/validate/outputs.py`, `doctrine/_compiler/validate/readables.py`, `doctrine/_compiler/validate/review_gate_observation.py` | `_validate_output_guard_expr()`, `_validate_readable_guard_expr()`, review helper expression walkers | Literal guards, unknown helper names, and wrong helper arity can still compile | Add closed helper whitelist, arity checks, and literal rejection on existing guard validation surfaces | Guard text is rendered as if it has compiler meaning; the compiler must reject cases it cannot interpret | Guards become a closed boolean expression surface | New output/readable/review guard unit tests; targeted manifests such as `examples/64_*` and `examples/114_*` |
| Config declaration closure | `doctrine/_compiler/validate/display.py`, `doctrine/_compiler/compile/outputs.py` | `_config_keys_from_decl()`, `_compile_output_config_rows()` | Unknown config sections are ignored, and one key can still get conflicting required and optional meaning | Close config declaration shape and duplicate cross-section keys on the existing config validation path | Misspelled compiler-owned config sections and split key meaning currently disappear into plausible output | Config declarations accept only shipped sections and one meaning per key | Unit tests around config declarations and output target rendering; likely targeted manifest addition |
| Typed config value closure | `doctrine/_compiler/compile/outputs.py`, `doctrine/_compiler/validate/display.py` | config value rendering and display helpers | Some single-artifact output target values are humanized for display instead of type-checked as authored literals | Add type-appropriate config value checks on the existing target config path | A missing quote or wrong ref can silently change a file path or similar config surface | Output target config values must satisfy the declared config contract, not just render cleanly | Targeted output-target unit tests and manifest-backed examples |
| Special output section closure | `doctrine/_compiler/compile/outputs.py`, `doctrine/_compiler/validate/outputs.py` | special output section compilers for `must_include`, `current_truth`, `support_files`, `notes`, `standalone_read`, and file sets | Wrong section shapes can fall back to generic prose or duplicate rendered rows | Add closed-shape and uniqueness checks on compiler-owned output support sections | Compiler-owned contract sections should not silently lose meaning when misshaped | Special output sections are either well-shaped compiler surfaces or compile errors | `tests/test_output_rendering.py`, `tests/test_output_inheritance.py`, `tests/test_output_target_delivery_skill.py`; targeted manifest additions |
| Guarded support-surface parity | `doctrine/_compiler/validate/outputs.py`, `doctrine/_compiler/compile/outputs.py` | `_validate_standalone_read_guard_contract()`, trust-surface rendering | Only `standalone_read` gets the guarded-detail parity check; related support surfaces can still leak guarded detail | Extend the same parity rule across `trust_surface` and other compiler-owned support surfaces | Guard leaks confuse downstream readers even when the main output surface is guarded correctly | Support surfaces follow one guard-consistency contract | `tests/test_output_rendering.py`, `tests/test_output_inheritance.py`, `tests/test_final_output.py` |
| Structured `final_output` contract | `doctrine/_compiler/resolve/outputs.py`, `doctrine/_compiler/compile/final_output.py`, `doctrine/_compiler/output_schema_validation.py` | `_resolve_final_output_decl()`, `_resolve_final_output_json_shape_summary()`, final-output compilation and lowered-schema validation | Existing `E211` through `E218` cover many contradictions, but remaining JsonObject inference and mixed prose/schema cases still need closure | Tighten structured final-output classification only on the existing output-shape and schema pipeline | This surface already has the right owner path and stable error family; do not split it | Structured `final_output` is either one valid prose contract or one valid JSON contract, never both | `tests/test_final_output.py`, `tests/test_output_schema_validation.py`; manifests such as `examples/55_*`, `examples/67_*`, and `examples/110_*` |
| Output-schema typing closure | `doctrine/_compiler/resolve/output_schemas.py`, `doctrine/_compiler/output_schema_validation.py` | output-schema lowering and validation helpers | Type-incompatible keywords and literal shapes can still lower into misleading or impossible schemas | Add closed type/keyword compatibility checks on the existing output-schema lowering and validation path | Schema-owned final output should not claim enforcement the lowered schema does not actually provide | Output schemas reject incompatible keyword, enum, and const combinations before lowering completes | `tests/test_output_schema_validation.py`, `tests/test_final_output.py`; manifests tied to schema-backed final output |
| Duplicate compiler-owned output support entries | `doctrine/_compiler/validate/outputs.py`, `doctrine/_compiler/compile/outputs.py` | `trust_surface` items, output support sections, file-target path surfaces | Repeated trusted paths or repeated compiler-owned support entries can still render plausible repeated truth | Add duplicate-entry checks on compiler-owned output support surfaces | Repeated trusted or delivered facts look intentional to users and downstream tooling | Compiler-owned support surfaces should be unique unless the language explicitly models repetition | `tests/test_output_rendering.py`, `tests/test_output_target_delivery_skill.py`; targeted manifest additions if public behavior changes |
| Law subsection identity | `doctrine/_compiler/resolve/workflows.py` | `_resolve_law_body()` and inherited law section accounting | Parent-accounting duplicates already fail, but duplicate new child-only law subsection keys do not yet have one explicit uniqueness rule | Add one explicit child-law subsection uniqueness rule on the workflow law resolve path | Law subsection keys are stable patch identities and should not have two bodies with one key | New law subsection keys stay unique even outside inherited parent accounting | Workflow-law unit tests plus targeted manifest additions |
| Public docs and proof sync | `docs/FAIL_LOUD_GAPS.md`, `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `tests/**`, `examples/**/cases.toml` | public docs, unit tests, manifest-backed corpus | Docs and proof can drift from the compiler if they are treated as follow-up cleanup | Update docs and proof in the same change family as the confirmed compiler rule | The user explicitly wants tests, docs, and examples treated as required shipped work | Each confirmed fail-loud family ships with aligned docs, tests, and examples | `make verify-examples`, `make verify-diagnostics`, targeted unit tests, and targeted manifest verification |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - Agent reserved-key typo checks stay on the agent field scan.
  - Review singleton config stays in review resolution.
  - Law totality and selector closure stay in route validation and branch
    collection.
  - Review helper meaning stays in review validation.
  - Guard closure and support-surface parity stay in output and readable
    validation.
  - Structured `final_output` stays on the output-shape and schema pipeline.
- Deprecated APIs (if any):
  - None approved yet. Deep-dive pass 1 does not approve any new public
    deprecation surface.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - Do not add a linter, sidecar validator, or runtime shim for fail-loud
    gaps.
  - If implementation adds a duplicate rule in the wrong layer, remove it and
    keep one owner path only.
  - Remove or rewrite any fail-loud doc entry the audit proves is accepted
    behavior instead of leaving stale guidance in `docs/FAIL_LOUD_GAPS.md`.
- Adjacent surfaces tied to the same contract family:
  - `docs/FAIL_LOUD_GAPS.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/VERSIONING.md` and `CHANGELOG.md` when compatibility changes
  - targeted unit tests under `tests/**`
  - targeted manifest-backed examples under `examples/**/cases.toml`
- Compatibility posture / cutover plan:
  - Default posture stays preserve-first, but phase planning must classify each
    family into one of three buckets before implementation starts:
    - confirmed bug fix inside current public compatibility
    - intentional accepted behavior to preserve and remove from fail-loud scope
    - public compatibility change that newly rejects shipped accepted authoring
  - Each confirmed invalid pattern gets a clean compile-time cutover with no
    runtime bridge.
  - No family may move into implementation with an unresolved compatibility
    bucket.
- Capability-replacing harnesses to delete or justify:
  - None. This is compiler-owned work. No agent-side harness is justified.
- Live docs/comments/instructions to update or delete:
  - `docs/FAIL_LOUD_GAPS.md`
  - `docs/COMPILER_ERRORS.md`
  - `docs/VERSIONING.md` and `CHANGELOG.md` when a family is classified as a
    public compatibility change
  - touched manifest examples and any nearby example README guidance when proof
    surfaces change
- Behavior-preservation signals for refactors:
  - `tests/test_parse_diagnostics.py`
  - `tests/test_final_output.py`
  - `tests/test_output_schema_validation.py`
  - `tests/test_route_output_semantics.py`
  - `tests/test_review_imported_outputs.py`
  - `tests/test_verify_corpus.py`
  - targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  - `make verify-diagnostics` when diagnostics move
  - `make verify-examples` for the full shipped corpus when implementation
    lands

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Duplicate compiler-owned singleton surfaces | `resolve/reviews.py`, `validate/routes.py`, `validate/outputs.py` | One duplicate-accounting rule for singleton compiler-owned entries | Prevent last-write-wins in one subsystem and fail-loud in another | include |
| Closed helper vocabulary | `validate/outputs.py`, `validate/readables.py`, `validate/review_gate_observation.py` | Helper-name, arity, and argument-meaning closure | Prevent guard and review-condition drift from typos and unsupported helpers | include |
| Closed mode sources | `validate/routes.py`, `resolve/law_paths.py` | Duplicate-mode and enum-typed mode-source enforcement | Prevent branch logic from hanging on unproved mode meaning | include |
| Closed config surfaces | `validate/display.py`, `compile/outputs.py` | Unknown-section rejection, cross-section duplicate-key rejection, and typed config values | Prevent compiler-owned config shape from silently degrading into display-only prose | include |
| Branch-totality modeling | `validate/routes.py`, `validate/route_semantics_context.py` | Preserve all reachable branches before proving route/currentness totality | Prevent false certainty when `when`, `match`, or `route_from` narrows too early | include |
| Closed compiler-owned output section shapes | `compile/outputs.py`, `validate/outputs.py` | Shape and uniqueness checks for special output support sections | Prevent compiler-owned contract sections from degrading into generic rendered prose | include |
| Structured-output consistency | `resolve/outputs.py`, `compile/final_output.py`, `output_schema_validation.py`, `resolve/output_schemas.py` | One structured-output classification and schema-typing path | Prevent mixed prose and JSON contracts and prevent lowered schemas from claiming impossible or ignored constraints | include |
| Law subsection identity | `resolve/workflows.py` | One uniqueness rule for new child-only law subsection keys | Prevent stable patch identities from splitting into duplicate section bodies | include |
| Public error and proof sync | `docs/COMPILER_ERRORS.md`, `tests/**`, `examples/**`, `docs/VERSIONING.md`, `CHANGELOG.md` | Ship code, docs, tests, and examples together | Prevent compiler truth from drifting away from public docs and corpus proof | include |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best
> sequence of coherent self-contained units, optimizing for phases that are
> fully understood, credibly testable, compliance-complete, and safe to build
> on later. If two decompositions are both valid, bias toward more phases than
> fewer. `Work` explains the unit and is explanatory only for modern docs.
> `Checklist (must all be done)` is the authoritative must-do list inside the
> phase. `Exit criteria (all required)` names the exhaustive concrete done
> conditions the audit must validate. Resolve adjacent-surface dispositions and
> compatibility posture before writing the checklist. Before a phase is valid,
> run an obligation sweep and move every required promise from architecture,
> call-site audit, migration notes, delete lists, verification commitments,
> docs/comments propagation, approved bridges, and required helper follow-through
> into `Checklist` or `Exit criteria`. The authoritative checklist must name
> the actual chosen work, not unresolved branches or "if needed" placeholders.
> Refactors, consolidations, and shared-path extractions must preserve existing
> behavior with credible evidence proportional to the risk. For agent-backed
> systems, prefer prompt, grounding, and native-capability changes before new
> harnesses or scripts. No fallbacks/runtime shims - the system must work
> correctly or fail loudly (delete superseded paths). If a bridge is explicitly
> approved, timebox it and include removal work; otherwise plan either clean
> cutover or preservation work directly. Prefer programmatic checks per phase;
> defer manual/UI verification to finalization. Avoid negative-value tests and
> heuristic gates (deletion checks, visual constants, doc-driven gates, keyword
> or absence gates, repo-shape policing). Also: document new patterns/gotchas in
> code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Family Classification Lock

* Goal:
  - Turn the candidate fail-loud list into one audited implementation ledger so
    later code phases only touch confirmed compiler work.
* Work:
  - This phase is the audit lock. It does not ship new compiler behavior yet.
    The planning-level architecture, owner seams, and compatibility rubric are
    already locked. This phase records the family-by-family classification
    output under that fixed contract: exact compatibility bucket, owner layer,
    proof surfaces, and docs duties that later phases must follow.
* Checklist (must all be done):
  - Audit every family currently named in `docs/FAIL_LOUD_GAPS.md` and every
    newly proven family surfaced during local deep-dive probes.
  - Record one disposition per family:
    - confirmed bug fix inside current public compatibility
    - intentional accepted behavior to preserve
    - public compatibility change that newly rejects shipped accepted authoring
  - Record one owner layer per confirmed family: grammar, parser, indexing,
    resolve, validate, or compile.
  - Record the required unit tests, manifest-backed example changes, error-doc
    updates, and release-surface updates for each confirmed family.
  - Remove accepted-behavior families from the implementation backlog and
    rewrite their entry in `docs/FAIL_LOUD_GAPS.md` so the doc stops claiming
    they should become errors.
  - Identify which confirmed families need new stable error codes versus reuse
    or tightening of existing shipped codes.
  - Update this plan doc and the call-site audit if classification proves any
    listed family was missing, merged with another family, or placed on the
    wrong owner layer.
* Verification (required proof):
  - Reproduce or anchor every family against shipped code, existing tests, or
    targeted read-only compile probes.
  - Confirm that every confirmed family maps to at least one concrete owner
    file and at least one concrete proof surface.
* Docs/comments (propagation; only if needed):
  - Update `docs/FAIL_LOUD_GAPS.md` so it reflects the classification ledger
    instead of an undifferentiated list.
  - Update this plan doc if any family grouping or owner layer changes during
    the audit lock.
* Exit criteria (all required):
  - Every in-scope family is classified into exactly one compatibility bucket.
  - No confirmed implementation family is still missing an owner layer, proof
    surface, or docs/update duty.
  - No accepted-behavior family remains mislabeled as a future compiler error.
* Rollback:
  - Revert only the classification-doc edits for this phase and reopen the
    affected families in the plan if the audit evidence turns out inconsistent.

## Phase 2 — Structural And Config Surface Closure

* Goal:
  - Add the confirmed fail-loud checks that belong in early structure or shape
    boundaries before deeper semantic phases build on them.
* Work:
  - This phase owns structure-first compiler surfaces: reserved agent field
    typo checks, review singleton config closure, config declaration closure,
    typed config values, special output section shape, duplicate compiler-owned
    output support entries, and child-only law subsection identity.
* Checklist (must all be done):
  - Implement near-miss reserved-field rejection on the existing agent field
    scan without closing valid custom authored slot keys.
  - Implement duplicate singleton-config rejection in
    `doctrine/_compiler/resolve/reviews.py`.
  - Implement config declaration closure in
    `doctrine/_compiler/validate/display.py`, including unknown-section
    rejection and cross-section duplicate-key rejection.
  - Implement typed config value checks on the existing output-target config
    path in `doctrine/_compiler/compile/outputs.py`.
  - Implement closed-shape checks for compiler-owned output support sections in
    `doctrine/_compiler/compile/outputs.py` and
    `doctrine/_compiler/validate/outputs.py`.
  - Implement duplicate trusted-path, duplicate file-path, and duplicate
    compiler-owned output-support entry rejection on the existing output
    support surfaces.
  - Implement one explicit uniqueness rule for new child-only law subsection
    keys in `doctrine/_compiler/resolve/workflows.py`.
  - Add targeted unit tests for every implemented family in this phase.
  - Add or update manifest-backed invalid examples for every newly rejected
    authoring shape in this phase, and keep nearby legal examples passing.
  - Update `docs/COMPILER_ERRORS.md` for every new or tightened shipped error
    in this phase.
  - Update `docs/FAIL_LOUD_GAPS.md` to remove or rewrite the families resolved
    by this phase.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for any family in this phase
    that Phase 1 classified as a public compatibility change.
* Verification (required proof):
  - Run the targeted unit tests that cover agent fields, review shape, config
    declarations, output support sections, and workflow law section identity.
  - Run `make verify-diagnostics` if any user-facing diagnostics or error-code
    formatting changes in this phase.
  - Run targeted manifest verification for the changed example manifests tied
    to these surfaces.
* Docs/comments (propagation; only if needed):
  - Add short code comments only where a new canonical boundary would otherwise
    be hard to infer from the code.
  - Keep public docs aligned with the shipped structural rules from this phase.
* Exit criteria (all required):
  - Every Phase 2 family now fails loud or is explicitly preserved according to
    the Phase 1 classification ledger.
  - The compiler no longer silently drops unknown config sections or duplicate
    compiler-owned support entries on the touched surfaces.
  - Tests, manifests, and public docs for these families are updated together.
* Rollback:
  - Revert the structural checks and their proof/doc updates together if they
    break clearly legal authored shapes or land on the wrong owner layer.

## Phase 3 — Route And Law Semantic Closure

* Goal:
  - Tighten the workflow-law and routing semantics that currently let branch or
    mode mistakes compile into misleading control logic.
* Work:
  - This phase owns mode-source closure, duplicate mode binding rejection,
    branch-totality modeling, and typed selector closure for `match` and
    `route_from`.
* Checklist (must all be done):
  - Implement duplicate mode binding rejection on the existing law validation
    paths.
  - Tighten mode binding validation so the compiler rejects mode sources it
    cannot prove enum-typed.
  - Update `_collect_law_leaf_branches()` and any dependent route-semantics
    context builders so reachable false-branch fallthrough is preserved.
  - Tighten `match` selector validation so arm legality is proven before fixed
    branch narrowing can hide authored mistakes.
  - Tighten `route_from` selector validation so selector typing and explicit
    arm legality are proven before branch narrowing.
  - Keep routed-owner and currentness behavior stable for nearby legal
    workflows while the fail-loud surface tightens.
  - Add targeted route and workflow unit tests for every implemented family in
    this phase.
  - Add or update manifest-backed invalid examples for every newly rejected law
    or routing shape in this phase, and keep nearby legal examples passing.
  - Update `docs/COMPILER_ERRORS.md` and `docs/FAIL_LOUD_GAPS.md` for the
    shipped changes in this phase.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for any Phase 3 family that
    Phase 1 classified as a public compatibility change.
* Verification (required proof):
  - Run the targeted route and workflow unit tests, especially
    `tests/test_route_output_semantics.py`.
  - Run `make verify-diagnostics` if any routing or workflow diagnostics change
    in this phase.
  - Run targeted manifest verification for the workflow and routing examples
    touched in this phase.
* Docs/comments (propagation; only if needed):
  - Add a short code comment at the canonical branch collector only if the new
    fallthrough modeling would otherwise be easy to undo by accident.
* Exit criteria (all required):
  - The compiler models reachable law branches honestly enough that totality,
    route liveness, and currentness claims are based on all reachable paths.
  - Mode bindings, `match`, and `route_from` now reject unproved or contradictory
    typed branch logic on the touched surfaces.
  - Tests, manifests, and public docs for these routing families are updated
    together.
* Rollback:
  - Revert the route and law semantic changes together if preserved legal route
    behavior regresses or if the branch collector proves to be the wrong owner
    layer.

## Phase 4 — Review And Guard Semantic Closure

* Goal:
  - Tighten the review and guard semantics that currently render plausible
    conditions and carriers without the compiler proving their meaning.
* Work:
  - This phase owns review helper refs, semantic binding meaning, carrier
    meaning, guard helper closure, literal-guard rejection, and support-surface
    guard parity.
* Checklist (must all be done):
  - Implement review helper-name and field-name closure on the existing review
    validation paths.
  - Tighten review semantic binding checks so compiler-owned review fields must
    structurally match the semantic value they claim to carry.
  - Tighten currentness and invalidation carrier checks so existence, emission,
    and trust-surface presence are not enough without payload meaning.
  - Implement closed helper-name and arity checks for output, readable, and
    review-condition helpers on the existing guard validation paths.
  - Reject literal-only guard conditions on output and readable guard surfaces.
  - Extend guarded-detail parity from `standalone_read` to the other
    compiler-owned support surfaces that can currently leak guarded detail.
  - Add targeted review, guard, and carrier unit tests for every implemented
    family in this phase.
  - Add or update manifest-backed invalid examples for every newly rejected
    review or guard shape in this phase, and keep nearby legal examples
    passing.
  - Update `docs/COMPILER_ERRORS.md` and `docs/FAIL_LOUD_GAPS.md` for the
    shipped changes in this phase.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for any Phase 4 family that
    Phase 1 classified as a public compatibility change.
* Verification (required proof):
  - Run the targeted review and guard unit tests, especially
    `tests/test_review_imported_outputs.py` and the touched guard-focused tests.
  - Run `make verify-diagnostics` if any review or guard diagnostics change in
    this phase.
  - Run targeted manifest verification for the review and guard examples
    touched in this phase.
* Docs/comments (propagation; only if needed):
  - Add short comments only at the canonical helper-closure or carrier-meaning
    boundary if the rule would otherwise be easy to weaken accidentally.
* Exit criteria (all required):
  - No touched review or guard surface still accepts helper names, helper
    shapes, or carrier bindings the compiler cannot interpret semantically.
  - Guarded output detail can no longer leak through the compiler-owned support
    surfaces touched in this phase.
  - Tests, manifests, and public docs for these families are updated together.
* Rollback:
  - Revert the review and guard semantic changes together if they reject legal
    review flows or expose the wrong owner layer.

## Phase 5 — Structured Output And Schema Closure

* Goal:
  - Finish the structured-output surface so `final_output` and output-schema
    typing only compile when the compiler can prove one coherent structured
    contract.
* Work:
  - This phase owns the remaining structured `final_output` contradictions and
    output-schema type/keyword compatibility gaps on the existing output-shape
    and schema pipeline.
* Checklist (must all be done):
  - Tighten structured `final_output` classification on the existing
    `resolve/outputs -> compile/final_output ->
    output_schema_validation` path.
  - Reject remaining contradictory prose-plus-JSON shapes on structured
    `final_output` surfaces.
  - Add closed type/keyword compatibility checks for output-schema lowering so
    incompatible keyword, enum, and const combinations fail before the lowered
    schema is accepted.
  - Preserve existing legal structured-output behavior and stable `E211`
    through `E218` meaning where those codes already own the surface.
  - Add targeted unit tests for every implemented structured-output and
    schema-typing family in this phase.
  - Add or update manifest-backed examples for every newly rejected structured
    shape in this phase, and keep nearby legal examples passing.
  - Update `docs/COMPILER_ERRORS.md` and `docs/FAIL_LOUD_GAPS.md` for the
    shipped changes in this phase.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for any Phase 5 family that
    Phase 1 classified as a public compatibility change.
* Verification (required proof):
  - Run the targeted structured-output unit tests, especially
    `tests/test_final_output.py` and `tests/test_output_schema_validation.py`.
  - Run `make verify-diagnostics` if any structured-output diagnostics change
    in this phase.
  - Run targeted manifest verification for the schema-backed and final-output
    examples touched in this phase.
* Docs/comments (propagation; only if needed):
  - Add a short code comment only where the final-output or schema-typing
    boundary would otherwise be easy to misread.
* Exit criteria (all required):
  - Structured `final_output` compiles only as one coherent prose contract or
    one coherent JSON contract on the touched surfaces.
  - Output-schema lowering rejects incompatible typed constraints on the
    touched surfaces before they become misleading emitted schemas.
  - Tests, manifests, and public docs for these families are updated together.
* Rollback:
  - Revert the structured-output and schema-typing changes together if they
    break preserved legal structured-output behavior or land on the wrong
    owner layer.

## Phase 6 — Full Proof, Public Surface Sync, And Implementation Audit

* Goal:
  - Prove the whole fail-loud change set, sync every surviving public surface,
    and leave no stale guidance behind.
* Work:
  - This phase is the integration and audit pass across all earlier confirmed
    families. It makes the repo truth, public docs, examples, and release
    surfaces agree before handoff.
* Checklist (must all be done):
  - Remove every resolved family from `docs/FAIL_LOUD_GAPS.md` or rewrite its
    entry to reflect its final accepted-behavior or shipped-error status.
  - Ensure `docs/COMPILER_ERRORS.md` matches the final shipped diagnostics and
    stable code usage.
  - Ensure `docs/VERSIONING.md` and `CHANGELOG.md` match every family that
    Phase 1 classified as a public compatibility change.
  - Ensure touched manifest-backed examples and nearby example guidance match
    the final shipped behavior.
  - Run the full targeted unit-test set for all touched families.
  - Run `make verify-diagnostics` because the error surface is part of the
    shipped public truth for this work.
  - Run `make verify-examples` because the change set touches shipped language
    behavior across multiple manifest-backed example families.
  - Re-read the changed code and docs for duplicate enforcement, stale
    comments, or stale live instructions, and delete or rewrite those surfaces
    in the same run.
* Verification (required proof):
  - The targeted unit tests for every touched family pass.
  - `make verify-diagnostics` passes.
  - `make verify-examples` passes.
* Docs/comments (propagation; only if needed):
  - This phase owns final public-doc and live-comment cleanup. No touched live
    doc, comment, or instruction should remain stale after it finishes.
* Exit criteria (all required):
  - Compiler behavior, diagnostics docs, fail-loud docs, tests, and
    manifest-backed examples all tell the same final story.
  - Every confirmed public compatibility change is reflected in
    `docs/VERSIONING.md` and `CHANGELOG.md`.
  - No touched live doc, comment, or instruction remains stale or contradictory.
* Rollback:
  - Revert only the final sync-layer changes if proof or docs drift shows the
    shipped story is still inconsistent; reopen the affected earlier phase
    instead of masking the drift.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Use the existing proof surfaces first, and treat them as required completion
work for each confirmed change:

- targeted unit tests for affected validation and compile paths
- focused manifest-backed example verification for changed language behavior
- `make verify-diagnostics` when diagnostics move
- broader repo verification only when the confirmed change surface requires it
- required doc updates for every changed public language or diagnostics story

Verification should prove both sides:

- new fail-loud behavior for confirmed errors
- preserved behavior for nearby accepted surfaces that should stay legal

Docs sync should prove both sides too:

- the gap catalog still matches the audited truth
- compiler error docs match shipped diagnostics behavior
- versioning and changelog surfaces are updated when the audit confirms a
  public compatibility change

# 9) Rollout / Ops / Telemetry

Likely a small rollout surface. If confirmed fixes change public language
behavior, the plan must say so plainly and route that change through versioning
docs and release notes. No special runtime telemetry is assumed today.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter and helper-block drift
  - `# TL;DR`, `# 0)` through `# 10)`
  - cross-section agreement on scope, compatibility, owner layers, proof, and
    rollout duties
- Findings summary:
  - Explorers found no concrete disagreement across the scope, architecture,
    phase-order, verification, rollout, or cleanup sections.
  - Parent integration found one real contradiction: `# 3.3` still framed
    family classification as a pre-implementation decision gap even though
    `# 7` already treats that work as Phase 1 execution under a fixed rubric.
- Integrated repairs:
  - Rewrote `# TL;DR` plan language so the artifact says the first execution
    phase is the family-classification lock.
  - Rewrote `# 3.3` so it no longer blocks implementation readiness with
    already-settled architecture questions.
  - Tightened Phase 1 work text so it clearly records execution-time
    classification output under the locked architecture and compatibility
    contract.
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

- 2026-04-16: Started the full-arch plan from `docs/FAIL_LOUD_GAPS.md` but
  explicitly rejected the assumption that every listed item is a real compiler
  error.
- 2026-04-16: Defaulted the typoed user path `dcs/FAIL_LOUD_GAPS.md` to the
  grounded repo path `docs/FAIL_LOUD_GAPS.md`.
- 2026-04-16: Chose `fallback_policy: forbidden`. Any confirmed fail-loud
  change should use explicit compiler behavior, not soft downgrade logic.
- 2026-04-16: North Star confirmed by the user. Plan status moved from
  `draft` to `active` with no scope change.
- 2026-04-16: Tightened the North Star so tests, manifest-backed examples, and
  required doc updates are explicit completion requirements for any confirmed
  fail-loud change.
- 2026-04-16: `auto-plan` preflight passed against the installed `Stop` hook,
  the active plan doc, and `codex_hooks`. The initial controller pass updated
  research grounding only and left later planning stages to the hook-owned
  continuation flow.
- 2026-04-16: Deep-dive pass 1 chose an owner-layer matrix instead of a new
  validator surface: parse and indexing for pure structure, resolve for merged
  singleton config shape, validate for semantic closure, and the existing
  final-output/schema pipeline for structured-output contradictions.
- 2026-04-16: Deep-dive pass 1 explicitly kept the grammar open for valid
  authored slots. Reserved-field typo detection should extend the existing
  agent field scan rather than closing custom slot authoring at the grammar
  boundary.
- 2026-04-16: Deep-dive pass 2 extended the same owner-layer matrix to the
  medium-risk families: config declaration closure stays on display/config
  validation, compiler-owned output support-section shape stays on
  output compile/validate paths, and child-only law subsection identity stays
  on workflow law resolution.
- 2026-04-16: Deep-dive pass 2 tightened compatibility planning from a vague
  preserve-first stance into a required three-bucket classification for each
  family before implementation: confirmed bug fix, accepted behavior to
  preserve, or public compatibility change.
- 2026-04-16: Phase-plan made the classification lock an explicit first phase
  because the user required audit-first enforcement instead of assuming every
  listed fail-loud gap is a real error. The later phases now split by owner
  layer and keep tests, manifest-backed examples, diagnostics docs, and release
  surfaces inside the authoritative checklist.
- 2026-04-16: Consistency pass resolved one artifact-level contradiction:
  family-by-family classification remains Phase 1 execution work, but the
  planning-level architecture, owner-layer matrix, proof duties, and
  compatibility rubric are already locked, so `# 3.3` no longer stays open as
  an implementation blocker.
