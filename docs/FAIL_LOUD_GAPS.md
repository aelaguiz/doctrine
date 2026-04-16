# Fail-Loud Gaps

Doctrine says fail loud is the default.
This doc lists easy author mistakes that the shipped compiler still accepts.
Each item below should become a clear compile error instead of a plausible
rendered result.

This list only covers gaps I could prove from shipped code or local probes.
Use [COMPILER_ERRORS.md](COMPILER_ERRORS.md) for errors that already exist.

## What Belongs Here

- The mistake is easy to make.
- The compiler accepts it today.
- The accepted result can mislead the author or a downstream reader.
- The right fix is a compile error, not a docs note or a runtime workaround.

## High-Risk Gaps

### Near-Miss Reserved Agent Field Typos Compile As Normal Authored Slots

- Surface: agent fields such as `workflow`, `analysis`, `skills`, `review`,
  `final_output`, `inputs`, `outputs`, and `handoff_routing`.
- Files: `doctrine/grammars/doctrine.lark`,
  `doctrine/_parser/workflows.py`, `doctrine/_compiler/constants.py`,
  `doctrine/_compiler/validate/__init__.py`,
  `doctrine/_compiler/naming.py`.
- Accepted today: `worklfow:` and `analysys:` compile as ordinary authored
  slots and render under normal-looking headings such as `Workflow` and
  `Analysis`.
- Why this is bad: one missing or swapped letter can drop real compiler
  semantics and still leave a believable runtime document.
- Should error like: `Unknown agent field 'worklfow' in agent Demo. Did you
  mean 'workflow'?`

### Duplicate Review Singleton Blocks Silently Replace Earlier Values

- Surface: top-level review config blocks such as `subject`, `subject_map`,
  `contract`, `comment_output`, `fields`, `selector`, and `cases`.
- Files: `doctrine/_parser/reviews.py`,
  `doctrine/_compiler/resolve/reviews.py`,
  `doctrine/_compiler/compile/review_contract.py`.
- Accepted today: a second copy of one of these blocks overwrites the first
  one. The review still compiles.
- Why this is bad: the author can silently change the reviewed subject,
  comment carrier, or field bindings just by repeating a block later in the
  same review.
- Should error like: `Review DraftReview defines 'subject' more than once.`

### Duplicate Law `mode` Bindings Silently Replace Earlier Mode Semantics

- Surface: repeated `mode name = ... as Enum` lines inside one active law
  scope.
- Files: `doctrine/grammars/doctrine.lark`,
  `doctrine/_parser/workflows.py`,
  `doctrine/_compiler/validate/routes.py`,
  `doctrine/_compiler/compile/workflows.py`.
- Accepted today: repeated `mode` lines with the same name compile. The later
  value wins in semantic lookups and render output.
- Why this is bad: later `match`, `when`, and `route_from` logic can silently
  switch to a different mode than the author expected.
- Should error like: `Duplicate law mode binding 'edit_mode' in workflow
  ModeAwareEdit.`

### Duplicate `route_only` Singleton Blocks Silently Replace Earlier Contract Parts

- Surface: `route_only` declarations with repeated `facts`, `when`,
  `handoff_output`, `guarded`, or `routes` blocks.
- Files: `doctrine/grammars/doctrine.lark`,
  `doctrine/_parser/reviews.py`, `doctrine/_model/workflow.py`,
  `doctrine/_compiler/resolve/agent_slots.py`.
- Accepted today: later singleton blocks overwrite earlier ones. The route-only
  declaration still compiles if the final stored shape looks complete.
- Why this is bad: one repeated block can silently change activation,
  handoff carrier, or the target route set.
- Should error like: `route_only RouteRepair defines 'facts' more than once.`

### Duplicate `grounding` Singleton Blocks Silently Replace Earlier Setup

- Surface: `grounding` declarations with repeated `source`, `target`, or
  `policy` blocks.
- Files: `doctrine/grammars/doctrine.lark`,
  `doctrine/_parser/reviews.py`, `doctrine/_model/workflow.py`,
  `doctrine/_compiler/resolve/agent_slots.py`.
- Accepted today: later singleton blocks overwrite earlier ones. The grounding
  declaration still compiles if the last version is complete enough.
- Why this is bad: one repeated block can silently change what gets grounded,
  where it binds, or which policy rules apply.
- Should error like: `grounding ClaimGrounding defines 'source' more than
  once.`

### Branch-Level `when` Drops The False Branch

- Surface: law branches written as `when expr:` with currentness or routing
  inside the nested body.
- Files: `doctrine/_compiler/validate/routes.py`,
  `doctrine/_compiler/validate/route_semantics_context.py`.
- Accepted today: branch collection expands the guarded body but does not keep
  the implicit `expr == false` fallthrough branch. The law can then look total
  when it is not.
- Why this is bad: unguarded reads such as `route.next_owner` can compile even
  when runtime can fall through with no route at all.
- Should error like: `Non-total workflow law: branch guarded by
  'when RouteFacts.should_route' leaves an active fallthrough path without
  currentness or route.`

### Dynamic `match` And `route_from` Selectors Are Only Shallow-Checked

- Surface: `match` selectors and `route_from` selectors that do not resolve
  through the happy-path enum binding shape.
- Files: `doctrine/_compiler/validate/routes.py`,
  `doctrine/_compiler/resolve/law_paths.py`.
- Accepted today: `match` only gets full enum membership and exhaustiveness
  checks when the selector is a one-part mode ref. If `else` is present, bad
  explicit arms can slip through without validation. `route_from` only proves
  that the selector path exists, not that it is a scalar enum-compatible
  field.
- Why this is bad: authors can think they wrote typed branching, but Doctrine
  can accept non-total or wrong-typed branch logic.
- Should error like: `match selector must resolve to one declared enum source
  and be exhaustive or include else`, and `route_from selector must resolve to
  a scalar field whose values are members of ProofRoute`.

### Guard Expressions Accept Literal Conditions

- Surface: `when` guards on outputs, readable blocks, and related conditional
  surfaces.
- Files: `doctrine/_compiler/validate/outputs.py`,
  `doctrine/_compiler/validate/readables.py`,
  `doctrine/_compiler/display.py`.
- Accepted today: string, number, and boolean literals pass guard validation.
  A probe with `when "sometimes":` compiled and rendered `Show this only when
  sometimes.`
- Why this is bad: a quoted value or stray literal looks like a real guard,
  but it has no typed compiler meaning.
- Should error like: `Guard condition must be a supported boolean expression,
  not a bare string literal, in output Plan.retry_note.`

### Guard Expressions Accept Unknown Helper Names And Wrong Helper Arity

- Surface: predicate-style calls in `when` guards and review conditions.
- Files: `doctrine/_compiler/validate/outputs.py`,
  `doctrine/_compiler/validate/readables.py`,
  `doctrine/_compiler/resolve/reviews.py`,
  `doctrine/_compiler/validate/review_gate_observation.py`,
  `doctrine/_compiler/display.py`.
- Accepted today: guard validation walks only the arguments. It never checks
  the helper name or its arity. Probes with `banana(CurrentIssue.missing)` and
  `present(CurrentIssue.missing, CurrentIssue.missing)` compiled and rendered
  as if they were valid conditions.
- Why this is bad: a typo or wrong call shape can look valid in the emitted
  prompt while the compiler stops reasoning about it.
- Should error like: `Unknown guard helper 'banana' in output Plan.retry_note`,
  or `present(...) takes exactly one argument in output Plan.retry_note.`

### Review Helper Refs Do Not Validate Gate Names Or Carried Field Names

- Surface: review condition helpers such as `failed(contract.gate)`,
  `passed(contract.gate)`, `present(field)`, and `missing(field)`.
- Files: `doctrine/_compiler/resolve/reviews.py`,
  `doctrine/_compiler/validate/review_gate_observation.py`.
- Accepted today: `failed(contract.clarty)` is treated like a normal boolean
  helper call even when the contract gate does not exist. `present(blocked_gte)`
  and `missing(blocked_gte)` are also accepted and quietly change the branch
  meaning instead of failing.
- Why this is bad: review logic can drift because of a typo in a gate or field
  name, while the compiler keeps rendering the condition as if it were valid.
- Should error like: `Unknown contract gate 'clarty' in review condition of
  DraftReview`, and `Unknown review semantic field 'blocked_gte' in review
  condition of DraftReview.`

### Mode Bindings Accept Non-Enum Expressions If They Are Not Constant

- Surface: `mode name = expr as Enum`.
- Files: `doctrine/_compiler/validate/routes.py`,
  `doctrine/_compiler/resolve/law_paths.py`.
- Accepted today: the compiler only checks the enum value when it can resolve a
  constant member. A probe with `mode edit_mode = Current.missing as EditMode`
  compiled cleanly.
- Why this is bad: authors can think a mode is enum-bound when the compiler has
  not proved that at all.
- Should error like: `Mode binding 'edit_mode' must resolve to an EditMode
  member or an enum-typed scalar source.`

### Review Semantic Bindings Are Checked For Liveness, Not Meaning

- Surface: review semantic bindings such as `verdict`, `reviewed_artifact`,
  `current_artifact`, `failing_gates`, and `blocked_gate`.
- Files: `doctrine/_compiler/validate/review_preflight.py`,
  `doctrine/_compiler/validate/review_agreement.py`,
  `doctrine/_compiler/validate/review_branches.py`.
- Accepted today: most checks only prove that the bound field is live on the
  right branches. They do not prove that the field can structurally carry the
  semantic value. A probe that bound `verdict` to an unrelated field compiled.
- Why this is bad: Doctrine can then treat the field as compiler-owned review
  truth even when the field shape does not match that truth.
- Should error like: `Review semantic field must structurally bind its semantic
  value in agent DraftReviewDemo review: verdict -> DraftReviewComment.analysis_performed.`

### `current artifact` And `invalidate` Carriers Are Checked For Existence And Trust, Not Payload Meaning

- Surface: `current artifact ... via ...` and `invalidate ... via ...` carriers
  in workflow law and reviews.
- Files: `doctrine/_compiler/validate/routes.py`,
  `doctrine/_compiler/resolve/reviews.py`.
- Accepted today: the compiler checks that the `via` path exists, is emitted,
  and is listed in `trust_surface`. It does not prove that the field actually
  carries the current artifact or invalidation set. A probe that bound
  `current artifact DraftSpec via ReviewComment.unrelated_note` compiled.
- Why this is bad: the trust surface can claim authority for the wrong field.
- Should error like: `current artifact carrier must structurally bind DraftSpec
  in workflow ReviewWorkflow: ReviewComment.unrelated_note.`

### `final_output` JSON Mode Inference Accepts Contradictory Shape Contracts

- Surface: `final_output:` plus output-shape `kind:` and `schema:` ownership.
- Files: `doctrine/_compiler/compile/final_output.py`,
  `doctrine/_compiler/resolve/outputs.py`,
  `doctrine/_compiler/validate/__init__.py`,
  `doctrine/_model/io.py`.
- Accepted today: bare builtin `JsonObject` without `schema:` downgrades to
  prose mode, and a named shape with `schema:` upgrades to JSON mode even if
  its `kind` is not `JsonObject`.
- Why this is bad: authors can write what looks like a structured final answer
  and get a prose contract, or write what looks like markdown and get a JSON
  contract.
- Should error like: `final_output using JsonObject must point at a named
  output shape with schema:`, and `output shape schema requires kind:
  JsonObject in output shape WeirdShape.`

### Structured JSON `final_output` Still Accepts `structure:`

- Surface: `final_output` outputs that already lower into a JSON contract.
- Files: `doctrine/_compiler/compile/outputs.py`,
  `doctrine/_compiler/compile/final_output.py`,
  `doctrine/_model/io.py`.
- Accepted today: the final-output path still resolves and renders `structure:`
  even when the final answer is already classified as structured JSON.
- Why this is bad: one compiled contract can demand JSON and a markdown
  document outline at the same time.
- Should error like: `structured JSON final_output cannot use structure: in
  output Reply.`

### Output-Schema Typing Does Not Reject Type-Incompatible Keywords Or Literals

- Surface: `output schema` fields, defs, enums, and const values.
- Files: `doctrine/_compiler/resolve/output_schemas.py`,
  `doctrine/_compiler/output_schema_validation.py`,
  `doctrine/_model/io.py`.
- Accepted today: the compiler lowers combinations such as `type: string` plus
  `minimum: 3`, `type: string` plus `const: 7`, or `type: integer` plus string
  enum members.
- Why this is bad: some constraints are silently ignored by JSON Schema, and
  some produce impossible schemas. Either way, the author thinks Doctrine is
  enforcing rules that it is not.
- Should error like: `Output schema field 'summary' in Payload cannot use
  minimum with type string.`

## Medium-Risk Gaps

### Config Declarations Ignore Extra Sections Instead Of Rejecting Them

- Surface: `input source` and `output target` declarations.
- Files: `doctrine/_compiler/validate/display.py`.
- Accepted today: `_config_keys_from_decl()` splits `required` and `optional`,
  then ignores every extra item. A probe with an extra `typo_section:` block
  compiled and the extra section vanished from the rendered contract.
- Why this is bad: a misspelled reserved section is silently dropped.
- Should error like: `input source Fancy uses unknown section 'typo_section'.
  Only 'required' and 'optional' are allowed.`

### The Same Config Key Can Appear In Both `required` And `optional`

- Surface: `input source` and `output target` declarations.
- Files: `doctrine/_compiler/validate/display.py`,
  `doctrine/_compiler/compile/outputs.py`.
- Accepted today: a key can appear in both sections. The compile path merges
  the labels with `{**required, **optional}` so the optional label wins for
  display, while the key still counts as required for completeness.
- Why this is bad: one authored key gets two meanings. The rendered contract
  can even show the wrong label for a required key.
- Should error like: `Config key 'url' is declared in both required and
  optional sections of input source Fancy.`

### Single-Artifact Output Target Config Values Are Display-Validated, Not Type-Validated

- Surface: ordinary `target:` config rows on one output artifact.
- Files: `doctrine/_compiler/compile/outputs.py`,
  `doctrine/_compiler/validate/display.py`.
- Accepted today: the compile path checks key presence, then formats any scalar
  value for display. A probe with `target: File` and `path: PlanDoc` compiled
  and rendered `Path | Plan Doc`.
- Why this is bad: a missing quote or mistaken ref silently changes a file
  destination into a humanized declaration label.
- Should error like: `Output target config 'path' must be a string literal in
  output PlanFile target.`

### Special Output Sections Only Get Semantics When They Happen To Be Section-Shaped

- Surface: `must_include`, `current_truth`, `standalone_read`, `support_files`,
  and `notes` inside `output`.
- Files: `doctrine/_compiler/compile/outputs.py`,
  `doctrine/_compiler/validate/outputs.py`.
- Accepted today: these keys only get special handling when they come through
  the exact expected shape. A probe with scalar `standalone_read:` or scalar
  `must_include:` compiled and rendered plain bullet lines instead of the
  intended contract sections.
- Why this is bad: misshaping a special section silently strips its special
  meaning and falls back to generic prose rendering.
- Should error like: `Output Plan uses 'standalone_read' with the wrong shape.
  Use a titled section body.`

### Guarded Output Detail Can Leak Into Unconditional Trust Or Support Text

- Surface: `trust_surface` items and support prose such as `notes:` that point
  at guarded output detail.
- Files: `doctrine/_compiler/validate/outputs.py`,
  `doctrine/_compiler/compile/outputs.py`.
- Accepted today: there is a special guarded-detail check for `standalone_read`
  only. The same kind of read can still appear unguarded in `trust_surface` or
  ordinary support prose.
- Why this is bad: downstream readers can be told to trust or mention a field
  that may not exist on the emitted output.
- Should error like: `Output support surface cannot reference guarded output
  detail without a matching guard in output Reply: extra.note.`

### Duplicate `trust_surface` Paths Compile As Repeated Trusted Facts

- Surface: repeated items in one `trust_surface:` block.
- Files: `doctrine/_compiler/compile/outputs.py`.
- Accepted today: repeated paths render as repeated trusted labels. A probe
  with two `current_artifact` items produced two identical trust-surface
  bullets.
- Why this is bad: duplicate trusted facts look sloppy at best and can hide a
  copy-paste mistake at worst.
- Should error like: `Duplicate trust_surface path in output Plan:
  current_artifact.`

### Duplicate Output File Paths Compile Inside One File Set

- Surface: `files:` entries on one `output`.
- Files: `doctrine/_compiler/compile/outputs.py`.
- Accepted today: two artifacts in the same file set can use the same `path:`.
  A probe with two entries targeting `same.md` compiled and rendered both rows.
- Why this is bad: the contract describes two artifacts but only one file path.
- Should error like: `Duplicate file path 'same.md' in output Bundle.`

### Special Output Tables Accept Duplicate Field Entries

- Surface: special record-style output sections such as `must_include` and
  `current_truth`.
- Files: `doctrine/_compiler/validate/outputs.py`,
  `doctrine/_compiler/compile/outputs.py`.
- Accepted today: repeating a key such as `summary` or `verdict` inside one of
  these sections compiles into duplicate table rows instead of a compile error.
- Why this is bad: the contract table can say two different things about the
  same logical field.
- Should error like: `Duplicate field key 'summary' in output Plan.must_include.`

### Duplicate Law Subsection Keys Are Accepted Once You Leave Parent Accounting

- Surface: new child-only `law` sections with the same key.
- Files: `doctrine/_compiler/resolve/workflows.py`,
  `doctrine/_compiler/validate/routes.py`.
- Accepted today: inherited law checks reject duplicate accounting for parent
  sections, but duplicate new subsection keys still compile.
- Why this is bad: law subsection keys are the stable identity for patching and
  later overrides. Two bodies should not claim the same key.
- Should error like: `Duplicate law subsection key in workflow ChildWorkflow:
  routing.`

## Shared Fix Themes

- Close reserved-key namespaces on surfaces that depend on exact keys for real
  semantics.
- Treat singleton blocks as unique unless the language explicitly says they
  merge.
- Validate guard, mode, `match`, and `route_from` expressions as closed
  semantic domains instead of best-effort prose.
- Prove binding meaning, not just field existence or branch liveness.
- When a gap is fixed, add the real shipped error to
  [COMPILER_ERRORS.md](COMPILER_ERRORS.md) and remove the gap from this doc.
