# Changelog

All notable Doctrine release changes live here.
This file is the portable release history. `docs/VERSIONING.md` is the
evergreen policy guide.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

Release kind: Breaking
Release channel: stable
Language version: 4.0 -> 5.6
Affected surfaces:
- 4.0 -> 4.1 additive moves: review-driven agent carrier mode (`E500` now permits `final_output.review_fields:` on the single carrier output when the author opts in), the authored stdlib role-home pattern (splitting `shared_rules:` from `how_to_take_a_turn:` is now a shipped example), `via review.on_*.route` binding inside `next_owner:` output bodies (new compile code `E317`), `selector:` on `output shape` with `case EnumType.member:` dispatch plus agent-side `selectors:` binding (new compile codes `E318` and `E319`), and the numbered example corpus additions (`135_review_carrier_structured`, `136_review_shared_route_binding`, `137_role_home_shared_rules_split`, `138_output_shape_case_selector`).
- 4.1 -> 5.0 breaking cut: the `output schema` field `type:` slot (the inline `type: enum` plus `values:` form and the legacy `type: string` plus `enum:` form are deleted), readable `row_schema` and `item_schema` entry bodies, readable table column bodies, and record-scalar bodies (all four surfaces now accept `type: <EnumName>` to name a declared `enum`), a new compile code `E320` for `type:` names that are neither a builtin primitive nor a resolvable `enum`, the renderer (now emits one `Valid values: ...` line per typed field under a unified helper), the JSON-schema lowering path (now appends `One of ...` after a field description when both a description and a closed vocabulary are present), six shipped examples that migrated from the deleted forms (`79/AGENTS.prompt`, `79/optional_no_example/AGENTS.prompt`, `79/invalid_invalid_example/AGENTS.prompt`, `85/AGENTS.prompt`, `90/AGENTS.prompt`, `121/AGENTS.prompt`), the new example `139_enum_typed_field_bodies`, and docs (`LANGUAGE_REFERENCE.md`, `LANGUAGE_DESIGN_NOTES.md`, `AGENT_IO_DESIGN_NOTES.md`, `VERSIONING.md`, `COMPILER_ERRORS.md`, `examples/README.md`).
- 5.0 -> 5.1 additive moves: per-case `override gates:` block inside a `review_family` case body (one shared `contract:` may now back several cases with `add NAME: "Title"`, `remove NAME`, and `modify NAME: "Title"` clauses; case `checks:` references resolve against the per-case effective gate set), two new compile codes `E531` (remove or modify of a gate the contract never declared) and `E532` (add or modify name collision), the new example `141_review_case_gate_override` with one positive `render_contract` case plus two `compile_fail` cases, the curated `doctrine-learn` reviews reference (new `Per-Case Gate Override` section), the curated `agent-linter` finding catalog (new `AL246 Per-Case Gate Delta Split Into Parallel Contracts` finding), the VSCode tmLanguage grammar (highlights `add` / `remove` / `modify` clauses), and docs (`LANGUAGE_REFERENCE.md`, `REVIEW_SPEC.md`, `COMPILER_ERRORS.md`, `VERSIONING.md`).
- 5.1 -> 5.2 additive moves: a typed `receipt` host-slot family on `skill package` `host_contract:` (author may declare `receipt <slot_key>: "Title"` with typed `<field_key>: <DeclaredType>` or `<field_key>: list[<DeclaredType>]` entries so the package owns the typed envelope it emits on every run), three new compile codes `E535` (empty receipt body or duplicate field key), `E536` (unresolved receipt field reference through a skill binding), and `E537` (receipt field type is not a declared `enum`/`table`/`schema`/`document`), receipt slots are exempt from the exact-once call-site bind requirement (the package owns them), `SKILL.contract.json` now carries each receipt slot with its typed `fields` map, the new example `142_skill_host_receipt_envelope` with a positive `render_contract` case, a `build_contract` case, and two `compile_fail` cases for `E535` and `E537`, the curated `doctrine-learn` skills reference (new `Typed Receipt Envelope` section), the curated `agent-linter` finding catalog (new `AL960 Process Evidence Emitted As Prose Not Typed Receipt` finding), the VSCode tmLanguage grammar (highlights the `receipt` host-slot keyword), and docs (`LANGUAGE_REFERENCE.md`, `LANGUAGE_DESIGN_NOTES.md`, `COMPILER_ERRORS.md`, `VERSIONING.md`, `AGENTS.md`, `examples/README.md`).
- 5.2 -> 5.3 additive moves: a `typed_as:` line inside `output target` bodies pointing at a declared `document`, `schema`, or `table` (the target now carries the handoff-note family identity so downstream outputs can bind the same family without restating the structure), two new compile codes `E533` (typed output target ref that does not resolve to a `document`/`schema`/`table`) and `E534` (downstream structure family mismatch when a consuming output's `structure:` or `schema:` disagrees with the target's `typed_as:` family), the emitted output contract gains a `Typed As` row immediately after `Target`, the new example `143_typed_handoff_note_identity` with one positive `render_contract` case plus two `compile_fail` cases for `E533` and `E534`, the curated `doctrine-learn` outputs reference (new `Typed Handoff-Note Targets` section), the VSCode tmLanguage grammar and go-to-definition resolver (highlights and navigates the `typed_as:` keyword), and docs (`LANGUAGE_REFERENCE.md`, `COMPILER_ERRORS.md`, `VERSIONING.md`).
- 5.3 -> 5.4 additive moves: a canonical `mode CNAME = expr as <Enum>` statement on skill entries so producer vs. audit uses of the same skill stay compile-time distinguishable (three new compile codes `E540` for an unresolved mode enum ref, `E541` for an audit-mode binding that emits to an `output` or `final_output` host slot, and `E542` for a mode whose `CNAME` is not a member of the declared enum), `output shape` `selector:` now accepts the same canonical expr-based production (`mode CNAME = expr as <Enum>`) so shape selectors, review cases, law matchers, and skill-binding modes all share one `mode_stmt` grammar production, a new compile code `E543` soft-deprecates the enum-only shorthand (`mode CNAME as <Enum>`) with a one-minor-bump timebox (the enum-only form will be removed at the next minor bump), example `138_output_shape_case_selector` migrated to the expr-based form on every case, the new example `144_skill_binding_producer_audit_mode` with a producer agent + auditor agent sharing one skill plus four `compile_fail` cases for `E540`/`E541`/`E542`/`E543`, and docs (`LANGUAGE_REFERENCE.md`, `COMPILER_ERRORS.md`, `VERSIONING.md`).
- 5.4 -> 5.5 additive moves: an optional `: <TypedEntityRef>` annotation on `abstract` authored-agent slots so an abstract agent may narrow a policy slot to a specific declared family (`document`, `schema`, `table`, `enum`, `agent`, or `workflow`). Concrete descendants bind the slot to a `name_ref` of the declared family. Two new compile codes: `E538` (concrete agent binds typed abstract slot to a wrong-family entity or with an inline workflow block) and `E539` (typed abstract slot annotation references an unknown entity). The annotation is deliberately narrower than skill `host_contract` family typing and output-schema field typing; the three shapes stay distinct. The new example `145_abstract_agent_typed_parameters` ships one abstract reviewer with a typed `policy:` slot plus two concrete descendants binding it to different documents, along with two `compile_fail` cases for `E538` and `E539`. Docs touched: `LANGUAGE_REFERENCE.md`, `COMPILER_ERRORS.md`, `VERSIONING.md`, and `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` Section 10 Decision Log.
- 5.5 -> 5.6 additive moves: a declarative top-level `rule` primitive so a project may lint its own agent graph at compile time. A `rule` declares a closed `scope:` predicate set (`agent_tag: <CNAME>`, `flow: <NameRef>`, `role_class: <CNAME>`, `file_tree: <STRING>`) and a closed `assertions:` predicate set (`requires inherit <NameRef>`, `forbids bind <NameRef>`, `requires declare <CNAME>`) plus a plain-English `message:` shown when the rule fires. Five new `RULE###`-band diagnostics: `RULE001` (rule scope predicate target does not resolve), `RULE002` (rule assertion target does not resolve), `RULE003` (scoped agent fails `requires inherit`), `RULE004` (scoped agent violates `forbids bind`), `RULE005` (scoped agent fails `requires declare`). Codes `RULE006` through `RULE099` are reserved for future closed-predicate extensions; codes `RULE100` and above are reserved for any future open-expression-language evolution. The new example `146_declarative_project_lint_rule` ships one happy-path rule plus one `compile_fail` case per shipped `RULE###` code. Curated `doctrine-learn` gains `references/rules.md`; curated `agent-linter` gains `AL990 Project Lacks An Enforcement Rule For Shared Inheritance Invariant`. VSCode tmLanguage grammar highlights the `rule` declaration plus the `scope`, `assertions`, `requires`, `forbids`, `agent_tag`, `role_class`, `file_tree`, `declare`, and `message` keywords. Docs touched: `LANGUAGE_REFERENCE.md` (new `Project Rules` section), `COMPILER_ERRORS.md` (new `Rule-check codes` subsection with RULE-band reservation note), `VERSIONING.md`, and `docs/DOCTRINE_LANGUAGE_GAPS_ELEGANT_CLOSURE_PLAN_2026-04-19.md` Section 10 Decision Log.
Who must act: authors whose `.prompt` files use the inline `type: enum` plus `values:` form or the legacy `type: string` plus `enum:` form on any `output schema` field, and downstream tooling that parsed those syntactic forms.
Who does not need to act: authors who already typed `output schema` fields with a declared `enum`, authors who only use builtin primitive `type:` values, authors using split-mode review carriers or existing role homes, and runtime consumers of emitted Markdown or emitted JSON schemas (the wire shape is preserved; only the rendered `Valid values:` line is new).
Upgrade steps: (1) install the matching release from your package index; (2) for every `output schema` field that used `type: enum` plus `values:`, lift the member list into a new top-level `enum X: "..."` decl and rewrite the field body as `type: X`; (3) for every legacy `type: string` plus `enum:` field, do the same; (4) on any readable `row_schema` / `item_schema` entry, table column, or record scalar that previously listed a vocabulary as prose, declare the `enum` once and rewrite the body as `type: X`; (5) re-run `make verify-examples` and `make verify-diagnostics` and confirm `E320` fires only on truly unknown names.
Verification: `uv sync && npm ci && make verify-examples && make verify-diagnostics && make verify-package`
Support-surface version changes: Doctrine language 4.0 -> 5.3; package metadata unchanged until the next public release cuts; distribution name `doctrine-agents` unchanged.

### Added
- Declarative top-level `rule` primitive so a project may lint its own agent
  graph at compile time. A rule declares a closed `scope:` predicate set
  (`agent_tag: <CNAME>`, `flow: <NameRef>`, `role_class: <CNAME>`,
  `file_tree: <STRING>`) and a closed `assertions:` predicate set
  (`requires inherit <NameRef>`, `forbids bind <NameRef>`,
  `requires declare <CNAME>`) plus a plain-English `message:` shown when
  the rule fires. Scope predicates combine with OR semantics. Five new
  `RULE###`-band diagnostics fail loud when a rule is malformed or when
  a scoped concrete agent violates an assertion: `RULE001` (scope predicate
  target does not resolve), `RULE002` (assertion target does not resolve),
  `RULE003` (scoped agent fails `requires inherit`), `RULE004` (scoped
  agent violates `forbids bind`), `RULE005` (scoped agent fails
  `requires declare`). Codes `RULE006`-`RULE099` are reserved for future
  closed-predicate extensions. Codes `RULE100`+ are reserved for any
  future open-expression-language evolution.
- Example `146_declarative_project_lint_rule` proves the rule primitive
  with one happy-path `render_contract` case covering two composer agents
  plus one `compile_fail` case per shipped `RULE###` code.
- Curated `doctrine-learn` gains `references/rules.md` teaching the closed
  predicate set, the shipped diagnostics, and the canonical authoring form.
- Curated `agent-linter` gains `AL990 Project Lacks An Enforcement Rule For
  Shared Inheritance Invariant` so audits flag role classes whose shared
  ancestor is enforced by hand-authored discipline only.
- VSCode tmLanguage grammar highlights the `rule` declaration plus the
  `scope`, `assertions`, `requires`, `forbids`, `agent_tag`, `role_class`,
  `file_tree`, `declare`, and `message` keywords.
- Carrier-mode review-driven agents may now declare `final_output.review_fields:`
  as an explicit opt-in to structural binding validation on the single
  carrier output. The compiler runs the same field-binding and
  semantic-output-binding checks that split mode runs. `E500` still fires
  for authoring `review_fields:` on a non-review agent; unknown-field
  bindings on the carrier surface as `E299` via the shared binding
  validator.
- Example `135_review_carrier_structured` proves the carrier-mode opt-in
  and includes a compile-fail fixture for an unknown bound field.
- Example `137_role_home_shared_rules_split` and a new
  `LANGUAGE_DESIGN_NOTES.md` section recommend the stdlib pattern of
  splitting always-on `shared_rules:` from role-specific
  `how_to_take_a_turn:` on an abstract role home.
- Output record bodies may include a `via review.on_accept.route` or
  `via review.on_reject.route` clause inside a `next_owner:` field body.
  The clause is a compile-time structural assertion: it proves the field
  is bound to the resolved review route without requiring a literal
  `{{TargetAgent}}` interpolation. The prose on the shared carrier stays
  layer-neutral, so one shape can back multiple critics whose
  `on_reject` routes differ. A new compile code `E317` fires when the
  named section does not match the branch that resolved the route, or
  when more than one `via` clause appears in one override body.
- Example `136_review_shared_route_binding` proves the shared-carrier
  pattern with two critic agents that share one output declaration,
  plus compile-fail fixtures for `E317` (section mismatch) and `E496`
  (missing `via` and missing literal interpolation still fails loud).
- Output shapes may declare a `selector:` block with
  `mode <field_name> as <Enum>` and bodies may then use
  `case EnumType.member:` blocks to inline role-specific lines.
  Concrete agents bind the selector with a new `selectors:` field
  (`selector_name: EnumType.member`). The compiler resolves dispatch at
  compile time so each agent's emitted shape support only shows lines
  that apply to its bound member. New compile codes `E318` (shape-side:
  malformed selector, wrong enum in a case, overlapping cases, or
  non-exhaustive cases) and `E319` (agent-side: missing or mismatched
  selector binding).
- Example `138_output_shape_case_selector` proves the pattern with
  three agents (`WriterProducer`, `WriterCritic`, `WriterComposer`)
  that share one output declaration but emit role-specific field notes,
  plus compile-fail fixtures for `E318` (non-exhaustive cases and
  `case` without `selector:`) and `E319` (missing agent binding).
- Example `140_typed_gates_symbol_reference` proves the typed-gate
  teaching loop: a schema contract with a typed `gates:` block, a review
  body that rejects and accepts on `contract.NAME` identities, failing-
  gate prose that interpolates the same `contract.NAME` symbols, and a
  sibling `compile_fail` case that fires `E477` on a typo. The curated
  `doctrine-learn` reviews reference now includes a "Typed Gates,
  Declared Once, Referenced By Symbol" section pointing at the example,
  and the `agent-linter` finding catalog adds `AL245` for review gates
  authored as inline prose instead of typed contract gates.
- A `review_family` case body may now declare an `override gates:` block
  to carry a case-scoped gate delta against the shared review contract.
  The block accepts `add NAME: "Title"`, `remove NAME`, and
  `modify NAME: "Title"` clauses. The case `checks:` block still
  references the same `contract.NAME` symbols, now resolved against the
  per-case effective gate set. Two new compile codes fail loud on
  authoring mistakes: `E531` for a `remove` or `modify` of a gate the
  contract does not declare, and `E532` for an `add` (or duplicate
  `modify`) that collides with a name the effective gate set already
  carries. Existing programs without the block keep compiling unchanged.
- Example `141_review_case_gate_override` proves the per-case override
  pattern with one positive `render_contract` case (one shared review
  contract drives a `quick_path` case unchanged and a `full_path` case
  that removes one gate, adds another, and renames a third) plus two
  `compile_fail` cases that fire `E531` and `E532`. The curated
  `doctrine-learn` reviews reference now includes a `Per-Case Gate
  Override` section pointing at the example, and the `agent-linter`
  finding catalog adds `AL246 Per-Case Gate Delta Split Into Parallel
  Contracts` for two or more review cases that share one
  `review_family` and only differ in a small gate delta yet bind their
  own near-duplicate contract instead of using the override block.
- VSCode tmLanguage grammar now highlights the per-case gate override
  clauses (`add NAME: "..."`, `remove NAME`, `modify NAME: "..."`).
- `skill package` `host_contract:` now supports a typed `receipt`
  host-slot family. Author `receipt <slot_key>: "Title"` inside
  `host_contract:` with typed `<field_key>: <DeclaredType>` or
  `<field_key>: list[<DeclaredType>]` entries so the package owns the
  typed envelope it emits on every run. Receipt fields type with a
  declared `enum`, `table`, `schema`, or `document`. Receipt slots are
  exempt from the exact-once call-site bind requirement: the package
  owns its receipt envelope, so consuming skill entries do not re-bind
  receipt slots. Downstream consumers reference receipt fields through
  the skill binding, e.g. `<skill_binding_key>.receipt.<field_key>`.
  Three new compile codes fail loud on authoring mistakes: `E535` for
  a receipt body declared without fields or with duplicate field keys,
  `E536` for a dotted reference through a skill binding that names a
  field the receipt host slot does not declare, and `E537` for a
  receipt field typed with a name that is not a declared `enum`,
  `table`, `schema`, or `document`. `SKILL.contract.json` now records
  each receipt slot with its typed `fields` map so runtime hosts can
  validate the emitted envelope. Existing packages without a `receipt`
  slot keep compiling unchanged.
- Example `142_skill_host_receipt_envelope` proves the typed receipt
  envelope pattern with one positive `render_contract` case, one
  `build_contract` case that exercises the typed `fields` map in
  `SKILL.contract.json`, and two `compile_fail` cases that fire `E535`
  (empty receipt body) and `E537` (receipt field typed with an
  undeclared name). The curated `doctrine-learn` skills reference now
  includes a `Typed Receipt Envelope` section pointing at the example,
  and the `agent-linter` finding catalog adds
  `AL960 Process Evidence Emitted As Prose Not Typed Receipt` for
  skills that describe a run-by-run evidence envelope in prose instead
  of a typed `receipt` slot.
- VSCode tmLanguage grammar now highlights the `receipt` host-slot
  keyword.
- `output target` bodies may now declare `typed_as:` pointing at a
  declared `document`, `schema`, or `table`. The target carries the
  handoff-note family identity so downstream outputs that bind the
  target may omit a redundant `structure:` or `schema:` line, or state
  the matching family for clarity. The emitted output contract gains a
  `Typed As` row immediately after `Target` so downstream readers see
  the bound family directly. A new compile code `E533` fires when
  `typed_as:` resolves to an entity kind other than `document`,
  `schema`, or `table`, and `E534` fires when a downstream output's
  `structure:` or `schema:` family disagrees with the target's
  `typed_as:` family.
- Example `143_typed_handoff_note_identity` proves the typed
  handoff-note target with a positive `render_contract` case that
  verifies the new `Typed As` row, plus two `compile_fail` cases for
  `E533` (enum typed target) and `E534` (document family mismatch).
- Curated `doctrine-learn` outputs reference now includes a
  `Typed Handoff-Note Targets` section pointing at the example.
- VSCode tmLanguage grammar now highlights the `typed_as:` keyword,
  and the VSCode resolver navigates `typed_as:` refs to the bound
  `document`, `schema`, or `table` definition.
- A skill entry may now carry a canonical
  `mode CNAME = expr as <Enum>` statement. The production is the same
  `mode_stmt` shared with review cases, law matchers, and output-shape
  selectors, so one mode concept reaches across every surface that
  dispatches by enum. Use it to distinguish producer and audit uses of
  the same skill without authoring parallel skill declarations. Three
  new compile codes fail loud on authoring mistakes: `E540` for a mode
  `as` target that does not resolve to a declared enum, `E541` for an
  audit-mode skill entry that binds to an `output` or `final_output`
  host slot (audit-mode bindings stay read-only), and `E542` for a
  `CNAME` that is not a member of the declared enum.
- Example `144_skill_binding_producer_audit_mode` proves the pattern
  with one producer agent and one auditor agent sharing one skill
  declaration, plus four `compile_fail` cases that fire `E540`, `E541`,
  `E542`, and `E543`.
- `output shape` `selector:` statements now accept the canonical
  expr-based `mode CNAME = expr as <Enum>` form shared with the rest of
  the `mode_stmt` surface. Authors should write
  `mode role = selectors.role as WriterRole` instead of the enum-only
  shorthand. A new compile code `E543` soft-deprecates the enum-only
  form (`mode CNAME as <Enum>`) with a one-minor-bump timebox; the
  enum-only form will be removed at the next minor bump. Example
  `138_output_shape_case_selector` now uses the expr-based form on
  every case, and example `144` preserves one regression fixture on
  the enum-only form so the deprecation signal stays honest.

### Changed
- `E500` semantics: was "final_output review_fields may not be repeated on
  the review carrier"; now "`final_output.review_fields` is used in an
  invalid place". The carrier arm now validates bindings instead of
  rejecting the shape.
- Removed the example `106` compile-fail fixture that asserted the old
  E500 behavior. That constraint is no longer part of the language.

### Fixed
- Output shape selector identity now compares the resolved
  `(owner_module_parts, enum_name)` pair instead of the enum basename. A
  selector on `mod_a.WriterRole` no longer accepts a binding or case on a
  same-named `mod_b.WriterRole` from a different imported flow.
- Inherited output shapes now rebind `selector:` and every
  `case EnumType.member:` ref through the parent's module parts, so a
  child flow that `inherit`s a selector-backed shape compiles without
  spurious `E318` or cross-flow identity errors.
- `case` blocks that appear outside an output shape body and
  `via review.<section>.route` clauses that appear outside a `next_owner:`
  field body now fail loud (`E318` and `E317`) instead of being silently
  dropped at render.
- Duplicate and unknown selector bindings on an agent now fail loud with
  `E319` instead of silently matching the first entry.
- `examples/136_review_shared_route_binding` and
  `examples/138_output_shape_case_selector` manifests cover every new
  failure mode and the cross-flow and inherited-shape happy paths.

### Deprecated (language 5.3 -> 5.4)
- The enum-only `output shape` `selector:` form
  (`mode CNAME as <Enum>`) is soft-deprecated with a one-minor-bump
  timebox. Authors should migrate to the canonical
  `mode CNAME = expr as <Enum>` form shared with review cases, law
  matchers, and skill-binding modes. The grammar still accepts the
  enum-only form, but the validator now raises `E543` when it appears.
  The form will be removed at the next minor bump.

### Breaking (language 4.1 -> 5.0)
- One canonical form for closed field vocabularies. On every field-shaped
  surface — `output schema` fields, readable `row_schema` and `item_schema`
  entries, readable table columns, and record scalars — declare `enum X:
  "..."` once and type the field body with `type: X`. The renderer emits
  one `Valid values: ...` line per typed field in declared order under a
  unified helper. The JSON-schema lowering path emits the same members as
  `enum`.
- Deleted the inline `type: enum` plus `values:` form that `output schema`
  fields once accepted.
- Deleted the legacy `type: string` plus `enum:` form that `output schema`
  fields once accepted.
- Tightened the field `type:` slot: names that are neither a builtin
  primitive nor a resolvable `enum` now fail loud with a new compile code
  `E320`. The message names the hit and suggests either declaring the
  enum or using a builtin primitive.
- Extended the typed `type:` slot to `row_schema`, `item_schema`, table
  columns, and record scalars. Glossary and label nodes (`properties`
  items and `definitions` items) stay prose-only by design.
- Example `139_enum_typed_field_bodies` ships the canonical form on a
  `row_schema` entry with `render_contract` and `compile_fail` cases.
- Migrated six shipped example prompts (`79/AGENTS.prompt`,
  `79/optional_no_example/AGENTS.prompt`,
  `79/invalid_invalid_example/AGENTS.prompt`, `85/AGENTS.prompt`,
  `90/AGENTS.prompt`, `121/AGENTS.prompt`) off the deleted forms onto the
  canonical `enum X` plus `type: X` form.

Use this section for work that is not public yet.

When you cut a public release:

1. Copy the release entry template below.
2. Replace the placeholders.
3. Move the real change notes into the new release section.
4. Leave `## Unreleased` at the top for the next cycle.

Public release entries must replace every placeholder before `make release-tag`
or `make release-draft` runs. The helper rejects placeholder compatibility
payload text and breaking releases with no real upgrade steps.

## v4.0.1 - 2026-04-18

Release kind: Non-breaking
Release channel: stable
Release version: v4.0.1
Language version: unchanged (still 4.0)
Affected surfaces: the emitted `AGENTS.flow.d2` and `AGENTS.flow.svg` node-id hashes produced by `emit_flow`, the `doctrine._compiler` indexing internals, and the flow-namespace test fixtures under `tests/`.
Who must act: downstream consumers that pin the exact byte content of emitted flow diagrams across machines and CI.
Who does not need to act: authors writing `.prompt` files, runtime consumers of emitted Markdown or contract JSON, and users of the stable `doctrine` Python import path.
Upgrade steps: (1) install `doctrine-agents==4.0.1` from your package index; (2) re-emit any checked-in `AGENTS.flow.d2` / `AGENTS.flow.svg` build references so their node-id hashes match the new reproducible identity.
Verification: `uv run --locked python -m unittest tests.test_release_flow tests.test_package_release && make verify-package && make verify-examples && make verify-diagnostics`
Support-surface version changes: package metadata 4.0.0 -> 4.0.1; Doctrine language version unchanged at 4.0; distribution name `doctrine-agents` unchanged.

### Changed
- Made `emit_flow` node-id hashes reproducible across machines by hashing
  each flow's path relative to its prompt root instead of the absolute
  filesystem path. Re-emitted the three shipped example build references
  whose hashes were baked against a local absolute path.

### Fixed
- Collapsed the three `WeakKeyDictionary` module globals in
  `doctrine/_compiler/indexing.py` onto `IndexedUnit` so unit state lives
  on the unit itself, eliminating hidden cross-session state with no
  author-visible behavior change.

## v4.0.0 - 2026-04-18

Release kind: Breaking
Release channel: stable
Release version: v4.0.0
Language version: 3.0 -> 4.0
Affected surfaces: Doctrine import language, flow-boundary ownership, package metadata, import diagnostics, first-party `doctrine-learn` teaching refs and public install trees, the numbered example corpus, and docs that teach imports and namespace ownership.
Who must act: authors using same-flow imports, authors relying on relative imports, authors crossing flow boundaries without `export`, downstream readers who learned the old import story from shipped docs or examples, and release operators who install `doctrine-agents` by pinned package version.
Who does not need to act: authors whose flows already use bare same-flow refs and explicit cross-flow `export`, and users who only consume emitted runtime docs without depending on old import authoring.
Upgrade steps: (1) install `doctrine-agents==4.0.0`; (2) delete same-flow imports and use bare refs inside one flow; (3) replace any remaining relative import with an absolute cross-flow import; (4) mark declarations `export` when another flow must read them; (5) rename sibling declarations that now collide inside one flat flow namespace; (6) refresh local examples and docs to the flow-root model.
Verification: `uv sync && npm ci && uv run --locked python -m unittest tests.test_package_release tests.test_release_flow && make verify-package && make verify-examples && make verify-diagnostics`
Support-surface version changes: Doctrine language 3.0 -> 4.0; package metadata 2.0.0 -> 4.0.0; distribution name `doctrine-agents` unchanged; docs and example corpus now teach flow-owned namespaces, `export`-gated cross-flow visibility, and retired same-flow plus relative imports; first-party `doctrine-learn` public install trees now mirror the flow-root teaching surface.

Old behavior: prompt files could be treated like module owners, relative
imports were still documented, same-flow imports were tolerated in examples,
and cross-flow visibility did not require an explicit `export` gate.
New behavior: a flow root owns one flat namespace, same-flow imports fail
loud with `E315`, cross-flow imports see only `export`ed declarations,
missing exports fail loud with `E314`, sibling declaration collisions fail
loud with `E316`, and `E306` is retired.
First affected version: v4.0.0

## v2.0.0 - 2026-04-17

Release kind: Breaking
Release channel: stable
Release version: v2.0.0
Language version: 2.2 -> 3.0
Affected surfaces: authored `output schema` language (authored `required` and `optional` retired; use `nullable`), emitted runtime Markdown layout (`## Outputs` now renders grouped contract tables, compacted Doctrine-owned surfaces, and drops `_ordered list_` and `_unordered list_` helper lines), emitted companion contracts (`AGENTS.contract.json` retired; `final_output.contract.json` gains additive top-level `route` and `io` blocks; emitted `schemas/<output-slug>.schema.json` is the sole structured-output wire contract; emitted `SKILL.contract.json` sidecars appear for host-bound skill packages), shipped example directory names (structured final-output examples renamed from `_json_schema` to `_output_schema`), structured `JsonObject` final-output authoring (example object now lives inside `output schema`, checked-in `.example.json` support files no longer read), Doctrine language (additive: output inheritance, first-class named `table`, omitted first-class IO wrapper titles, `delivery_skill:` on `output target`, provider-supplied prompt roots, runtime package imports and emit, workflow-root readable blocks, titleless readable lists, anonymous inline readable blocks, triple-quote escape, hyphenated code language, import aliases and symbol imports, grouped `inherit`, review-field identity shorthand, one-line IO wrapper refs, `self:` path roots, inline skill `package:`, package `host_contract:`, skill-entry `bind:`, package-scoped `host:`, `type: enum` plus `values:`, `route field` and `final_output.route:`, nullable route fields), first-party skill packages (`agent-linter` and `doctrine-learn`) with checked-in public install trees under `skills/.curated/`, diagnostics catalog (`E236`, `E237`, `E289`, `E306`–`E309`, `E312`), live docs (`AGENT_LINTER.md`, `AUTHORING_PATTERNS.md`, `DOCTRINE_LEARN.md`, `FAIL_LOUD_GAPS.md`, `THIN_HARNESS_FAT_SKILLS.md`, `WARNINGS.md`, `PRINCIPLES.md`), and VS Code extension language coverage.
Who must act: authors using `required` or `optional` inside `output schema` fields or route fields (fails loud with `E236` and `E237` in 2.0.0); downstream consumers of emitted `AGENTS.contract.json` (no longer written); downstream snapshot, parser, or scraper users of emitted `## Outputs` Markdown, the old `_ordered list_` or `_unordered list_` helper lines, or the old compiler-owned review-semantics and single-child `* Binding` wrappers; callers that read `<example>.example.json` sidecars alongside structured final outputs; downstream users referencing the renamed structured final-output example directories.
Who does not need to act: users consuming `schemas/<output-slug>.schema.json` wire shapes (string-enum wire shape unchanged), authors whose `.prompt` files already parse under 3.0, users of the stable `AL###` agent-linter catalog, users who do not rely on emitted-Markdown layout snapshots or the retired sidecar, and users of the stable `doctrine` Python import path.
Upgrade steps: (1) install `doctrine-agents==2.0.0` from the package index; (2) replace authored `required` and `optional` inside `output schema` fields and route fields with `nullable` where the field may be `null` (compile errors cite `E236` and `E237`); (3) stop reading emitted `AGENTS.contract.json` — read `final_output.contract.json` for final-output, review-control, and the new top-level `route` and `io` metadata, and read `schemas/<output-slug>.schema.json` for structured-output wire shape; (4) refresh downstream emitted-Markdown snapshots and parsers to the new `## Outputs` grouped-contract layout and updated Doctrine-owned surfaces (no `_ordered list_` or `_unordered list_` helper lines, compacted review-semantics and single-child `* Binding` wrappers); (5) move inline structured-final example objects into `output schema` and stop shipping `<example>.example.json` sidecars; (6) update any references to `*_json_schema` shipped example directories to their `*_output_schema` names; (7) optionally adopt the additive authoring forms (import aliases, grouped `inherit`, review-field identity shorthand, one-line IO wrapper refs, `self:`, inline skill `package:`, `host_contract:`, `bind:`, `type: enum` plus `values:`) — the older forms still compile.
Verification: `uv run --locked python -m unittest tests.test_package_release && make verify-package && make verify-examples && make verify-diagnostics`.
Support-surface version changes: Doctrine language 2.0 -> 3.0; package metadata 1.0.2 -> 2.0.0; distribution name `doctrine-agents` unchanged; `final_output.contract.json` gains additive top-level `route` and `io` blocks; emitted `schemas/<output-slug>.schema.json` is now the sole structured-output wire contract; emitted `AGENTS.contract.json` retired; emitted runtime Markdown layout updated for grouped `## Outputs`, compacted Doctrine-owned surfaces, and dropped helper kind lines; emitted `SKILL.contract.json` sidecars appear for host-bound skill packages; `skills/.curated/` checked-in public install trees added.

### Added
- Added the manifest-backed `125_multiline_escape_triple_quote` example and
  a diagnostic smoke check so triple-quoted literals may embed a literal
  `"""` sequence by escaping the first quote as `\"""`. All existing
  literals parse unchanged.
- Added the manifest-backed `126_hyphenated_code_language` example so
  readable `code` block `language:` values accept hyphens. Informal fence
  names like `prompt-fragment`, `shell-session`, or `js-jsx` now survive
  through the renderer without renaming the fence.
- Added the manifest-backed `127_inline_anonymous_readable_blocks` example
  so anonymous inline `code:`, `markdown:`, and `html:` blocks render bare
  inside document sections without requiring an authored key. Named blocks
  continue to parse unchanged.
- Refactored the two first-party skill packages (`skills/agent-linter/` and
  `skills/doctrine-learn/`) to author their reference bundles as Doctrine
  `document` declarations under `prompts/refs/*.prompt`, emitted to
  `references/<slug>.md` through the `skill package` `emit:` block. The
  public install trees under `skills/.curated/<name>/` are byte-identical
  to the previous raw-`.md` shape, so consumers see no change.
- Added a first-party `skills/doctrine-learn/` skill package, its
  `doctrine_learn_skill` and `doctrine_learn_public_skill` emit targets, and
  live docs at `docs/DOCTRINE_LEARN.md`. The skill is prompt-only and teaches
  Doctrine authoring end-to-end through twelve loadable references
  (principles, language overview, agents and workflows, reviews, outputs and
  schemas, documents and tables, skills and packages, imports and refs, emit
  targets, authoring patterns, examples ladder, verify and ship).
- Added a first-party `skills/agent-linter/` skill package, its
  `doctrine_agent_linter_skill` emit target, focused emit proof, and live
  docs for emit, install, and use.
- Added explicit `emit:` companion docs for `skill package`, plus package-
  local prompt imports from the `SKILL.prompt` source root so one skill can
  ship many prompt-authored `.md` files without path magic.
- Added package host binding for fat skills:
  - inline skill `package:`
  - package `host_contract:`
  - skill-entry `bind:`
  - package-scoped `host:` refs across the prompt-authored emitted tree
  - emitted `SKILL.contract.json` sidecars from `emit_skill` for host-bound
    packages
- Added the manifest-backed `124_skill_package_host_binding` example and
  focused unit and smoke proof for package host binding.
- Added a checked-in public install tree at `skills/.curated/agent-linter/`
  so `npx skills add .` discovers one supported public skill from the repo
  root.
- Added the high-value authoring wave: import aliases and symbol imports,
  grouped explicit `inherit { ... }`, bare identity shorthand on
  `review.fields`, `review override fields`, and
  `final_output.review_fields`, one-line first-class `inputs` / `outputs`
  wrapper refs, and `self:` on the existing `PATH_REF` surfaces.
- Added shipped fail-loud diagnostics `E306`, `E307`, `E308`, `E309`, and
  `E312` for that wave. `E310` stays reserved for the deferred grouped-
  override investigation, and `E311` stays reserved for a future dedicated
  IO-wrapper shorthand diagnostic.
- Added directory-backed runtime package imports that resolve
  `<module>/AGENTS.prompt` and let thin `AGENTS.prompt` build handles emit
  real runtime package trees.
- Added runtime-package emit support for package-root `AGENTS.md`, optional
  same-name sibling `SOUL.md`, and bundled peer files.
- Added direct `output[...]` declaration inheritance with explicit top-level
  `inherit` and `override` patching, plus fail-loud errors for missing,
  wrong-kind, cyclic, and parentless output patches.
- Added shipped corpus coverage for inherited outputs on ordinary output
  contracts, imported handoff reuse, `final_output:`, shared `route.*`
  semantics, and fail-loud output-inheritance cases.
- Added optional titles for `sequence`, `bullets`, and `checklist` readable
  blocks while keeping the authored key required for inheritance and refs.
- Added a shipped corpus example for titled and titleless ordered and
  unordered readable lists.
- Added omitted titles for first-class `inputs` and `outputs` wrapper sections
  when the wrapper body resolves to one direct declaration. The omitted wrapper
  lowers into that declaration's heading instead of adding a second heading.
  Ambiguous shapes such as multiple direct refs or keyed child sections fail
  loud instead of guessing.
- Added workflow-root readable blocks so workflows may own non-section
  readable blocks directly instead of wrapping them in a local section first.
- Added `115_runtime_agent_packages` as the generic checked-in runtime-package
  proof example.
- Added first-class named `table` declarations so documents can reuse one
  table contract with local `table key: TableRef` use sites while keeping
  inline tables and rendered Markdown unchanged.
- Added `116_first_class_named_tables` as the focused proof example for named
  table declarations.
- Added `117_io_omitted_wrapper_titles` as the focused proof example for
  omitted first-class IO wrapper title lowering.
- Added target-owned output delivery skill binding with
  `output target ... delivery_skill:` and the focused
  `118_output_target_delivery_skill_binding` proof example.
- Added provider-supplied prompt roots so embedding runtimes can pass named
  dependency-owned `prompts/` roots without adding install paths to host
  compile config.
- Added a canonical top-level `route` block to `final_output.contract.json`.
  It exposes compiler-resolved named-agent route targets for ordinary routed
  finals, `route_only`, `route_from`, and routed review finals. Harnesses
  should read this block instead of asking the model to copy the next owner
  into a private control field.
- Added first-class routed structured final outputs with `route field` plus
  `final_output.route:`. This lets one final-output field own the route
  choice keys, labels, named targets, and emitted runtime route metadata.
- Added additive `route.selector` metadata to `final_output.contract.json`
  so harnesses can find the selected route field without local reconstruction.
- Added an additive top-level `io` block to `final_output.contract.json`.
  It carries resolved `previous_turn_inputs`, emitted `outputs`, and
  `output_bindings` in the same public runtime contract file.
- Added `type: enum` plus `values:` as the preferred local inline enum form
  for `output schema` fields. Legacy `type: string` plus `enum:` still works
  in this first cut, and both forms lower to the same emitted string-enum
  schema shape.

### Changed
- Changed the public skill install story to one line:
  `npx skills add .`.
- Tightened the first-party `agent-linter` skill so it more clearly treats
  prompt bulk without reusable leverage as bloat and keeps safety guidance in
  the existing runtime-boundary family, without changing the stable `AL###`
  catalog or the saved proof schema.
- Changed package verification to include pinned `skills` CLI smoke tests for
  discovery and Codex install.
- Changed the public docs, teaching examples, and VS Code support to teach
  the preferred additive forms for imports, grouped `inherit`, review-field
  identity binds, first-class IO wrapper shorthand, and self-addressed
  addressable refs.
- Changed `output schema` authoring for the next language-major line. Use
  `nullable` when an output-schema field or route field may be `null`.
  Object properties still stay present on the wire on the current
  structured-output profile, so this change keeps the emitted wire shape the
  same while fixing the authored language.
- Changed `emit_docs`, `emit_flow`, corpus build-contract proof, and
  diagnostic smoke checks to share one runtime frontier instead of assuming
  root-only runtime emit.
- Changed `emit_skill` to write `SKILL.contract.json` beside `SKILL.md` only
  when a skill package has real host-binding truth.
- Clarified the release policy to prefer the next patch version for routine
  public work and keep minor bumps for real backward-compatible public
  additions or soft deprecations.
- Changed structured `JsonObject` final outputs to keep their example object
  inside `output schema`, make that `example:` block optional, validate it
  against the lowered OpenAI-compatible schema when present, and stop reading
  checked-in `.example.json` support files.
- Changed `emit_docs` to write `AGENTS.md` plus the real lowered
  `schemas/<output-slug>.schema.json` artifact for structured final outputs,
  plus `final_output.contract.json` for final-output and review-control
  metadata. Doctrine no longer emits `AGENTS.contract.json`.
- Changed emitted final-output companion contracts to include
  `route.exists: false` for unrouted final responses, so harnesses can consume
  one route contract shape for routed and unrouted turns. When a final output
  carries route semantics through a nullable `route field`, `route.exists`
  now stays `true` and `route.selector.null_behavior` says whether `null`
  means no handoff.
- Renamed the shipped structured final-output examples from `_json_schema` to
  `_output_schema` so the public corpus matches the approved feature story.
- Added `python -m doctrine.validate_output_schema --schema ...` as the
  built-in file validator for emitted structured-output schema files.
- Changed emitted ordinary `## Outputs` Markdown to one grouped contract block
  per output. Single artifacts now start with a `Contract | Value` table,
  `files:` outputs add an `Artifacts` table, and `structure:` now renders as
  one `Artifact Structure` section. Downstream emitted-Markdown snapshots or
  parsers will need to update.
- Changed emitted runtime Markdown to compact several Doctrine-owned surfaces.
  Simple `TurnResponse` ordinary outputs may now render as bullet contracts,
  summary-only output structures may render as `Required Structure:` lists,
  split review finals now use one short carrier note instead of a repeated
  review-semantics section, and compiler-owned single-child `* Binding`
  wrappers may collapse when they add no extra meaning. Downstream emitted-
  Markdown snapshots or parsers will need to update.
- Changed detailed readable list rendering to drop helper kind lines such as
  `_ordered list_` and `_unordered list_`. Titled lists keep their heading,
  and titleless lists render directly in the parent section.
- Moved the public release record fully onto `CHANGELOG.md`, signed tags, and
  matching GitHub releases. `docs/VERSIONING.md` now stays policy-only.
- Centralized package release metadata and package smoke proof so release
  prep, CI, and publish flows use the same repo-owned path.
- Moved source-checkout setup docs onto `make setup` and package smoke docs
  onto `make verify-package` to reduce repeated shell instructions.
- Made the package publish path require explicit `[tool.doctrine.package]`
  fields instead of falling back to code defaults.
- Added `tests.test_package_release` to the release worksheet proof path and
  added `make verify-package` to the PR checklist for package and publish
  work.
- Tightened the README, docs index, and contributing guide so they point back
  to `docs/VERSIONING.md` and `CHANGELOG.md` instead of becoming second
  release-policy owners.

### Removed
- Retired authored `required` and `optional` inside `output schema`,
  including output-schema route fields and route-field overrides. Doctrine
  still parses those spellings there only so it can raise targeted `E236` and
  `E237` upgrade errors.

### Fixed
- Fixed custom authored workflow slots such as `read_first` so workflows with
  root readable blocks no longer fail with `E901` during emit.
- Fixed emit-time previous-turn extraction so zero-config
  `RallyPreviousTurnOutput` now resolves through `final_output.route`, and
  workflow-root readable blocks no longer crash flow-graph collection on that
  path.
- Fixed emit-time previous-turn extraction so attached review outcome routes
  such as `review.on_reject -> Agent` now count as reachable predecessor
  edges for explicit `RallyPreviousTurnOutput` selectors.
- Fixed output-guard validation so ordinary `shape: JsonObject` input fields
  such as `RouteFacts.live_job` still work in workflow-law and route-only
  guards after previous-turn input validation tightened.

### Release Entry Template

```md
## vX.Y.Z - YYYY-MM-DD

Release kind: Non-breaking
Release channel: stable
Release version: vX.Y.Z
Language version: unchanged (still 2.0)
Affected surfaces: ...
Who must act: ...
Who does not need to act: ...
Upgrade steps: ...
Verification: ...
Support-surface version changes: none

### Added
- Describe backward-compatible user-facing additions.

### Changed
- Describe user-visible behavior or workflow changes.

### Deprecated
- Describe soft-deprecated public surfaces and early move guidance.

### Removed
- Describe removed public surfaces.

### Fixed
- Describe important fixes that matter to users or maintainers.

### YANKED
- Use this only when a bad public release was superseded later.
```

## v1.0.2 - 2026-04-14

Release kind: Non-breaking
Release channel: stable
Release version: v1.0.2
Language version: unchanged (still 1.0)
Affected surfaces: package-index installs, GitHub Trusted Publishing, and the public install docs.
Who must act: users installing Doctrine from PyPI or TestPyPI and maintainers publishing Doctrine to package indexes.
Who does not need to act: users running Doctrine from a source checkout and users of the `doctrine` Python module path or `[tool.doctrine.emit]` config surface.
Upgrade steps: Install `doctrine-agents==1.0.2` from the package index you use. Keep using `python -m doctrine.emit_docs` and the `doctrine` module path exactly as before.
Verification: Install `doctrine-agents==1.0.2` in a fresh venv and run `python -m doctrine.emit_docs --pyproject ... --target ...` from a temp project outside this repo.
Support-surface version changes: package metadata 1.0.1 -> 1.0.2; distribution name doctrine -> doctrine-agents

### Added
- Added the first public package-index rollout for Doctrine under the `doctrine-agents` distribution name.
- Added GitHub Trusted Publishing wiring for `testpypi` and `pypi`, including repo environments and gated publish workflow paths.

### Changed
- Kept the Python import path as `doctrine` while making the package-index install name explicit in the docs and README.
- Added a package-index smoke path that builds the wheel, installs it in a fresh environment, and compiles a temp project outside the repo root.

## v1.0.1 - 2026-04-14

Release kind: Non-breaking
Release channel: stable
Release version: v1.0.1
Language version: unchanged (still 1.0)
Affected surfaces: Python package metadata, the public release flow, and external package install compatibility.
Who must act: maintainers cutting Doctrine releases and users installing Doctrine through package resolvers that require `doctrine>=1.0.0,<2`.
Who does not need to act: users pinned to repo commits and users who are not consuming Doctrine as a Python package.
Upgrade steps: Install Doctrine v1.0.1. If you added a local `0.0.0` workaround, remove it and resolve against the released package again.
Verification: uv run --locked python -m unittest tests.test_release_flow && make verify-diagnostics
Support-surface version changes: package metadata 0.0.0 -> 1.0.1

### Changed
- Made the published package metadata line up with the released Doctrine 1.0 patch line.
- Taught the release flow to check `pyproject.toml` package metadata before tagging or drafting a public release.

### Fixed
- Restored clean downstream installs for dependents that correctly require `doctrine>=1.0.0,<2`.

## v1.0.0 - 2026-04-14

Release kind: Non-breaking
Release channel: stable
Release version: v1.0.0
Language version: unchanged (still 1.0)
Affected surfaces: Doctrine 1.0 language docs, manifest-backed corpus guidance, and the public release flow.
Who must act: maintainers cutting public releases and users adopting Doctrine from tagged releases.
Who does not need to act: users staying on unreleased commits and maintainers not cutting a release today.
Upgrade steps: No upgrade from an earlier public release is required. New users can start from README.md, docs/LANGUAGE_REFERENCE.md, and examples/01_hello_world.
Verification: uv sync && npm ci && uv run --locked python -m unittest tests.test_release_flow && make verify-examples
Support-surface version changes: none

### Added
- Shipped the first public Doctrine 1.0 release with the live language docs, compiler-backed AGENTS.md output flow, and the full manifest-backed example corpus.
- Added a repo-owned public release flow with `make release-prepare`, `make release-tag`, `make release-draft`, and `make release-publish`.

### Changed
- Moved versioning, release, and compatibility guidance into the canonical `docs/VERSIONING.md` and `CHANGELOG.md` pair.
- Clarified the public docs links for release history, support, security, and collaboration rules.

### Fixed
- Corrected the skill-package example range in `examples/README.md` to `95` through `103`.

### YANKED
- Superseded by v1.0.1 because `pyproject.toml` still advertised `0.0.0`, which broke package resolvers that correctly required the Doctrine 1.x line.
