# Examples

The examples are both the language teaching surface and the verification corpus.

Each numbered example may contain:

- `prompts/`: authored `.prompt` source
- `cases.toml`: manifest-backed proof used by `doctrine.verify_corpus`
- `ref/`: checked-in expected render or error output
- `build_ref/`: checked-in emitted tree output when the emit pipeline matters

Read the examples in numeric order. The sequence is intentional.

For the shipped workflow-law model behind examples `30` through `42`, start
with [../docs/WORKFLOW_LAW.md](../docs/WORKFLOW_LAW.md). For the shipped
review model behind examples `43` through `49`, start with
[../docs/REVIEW_SPEC.md](../docs/REVIEW_SPEC.md).

## Reading Order

- `01` through `06`: core agent and workflow syntax, imports, inheritance, and
  explicit patching
- `07` through `14`: authored slots, routing, typed inputs and outputs, skills,
  role-home composition, and handoff truth
- `15` through `20`: readable refs, interpolation, and richer authored prose
  surfaces
- `21` through `26`: first-class block reuse, inheritance, and abstract
  authored-slot requirements
- `27` through `29`: addressable nested items, recursive workflow paths, and
  enums for closed vocabularies
- `30` through `42`: active workflow-law proof for route-only turns, portable
  currentness, trust carriers, scope and preservation law, basis roles,
  invalidation, law reuse, output-owned guarded readback, and the route-only
  handoff capstones
- `43` through `49`: first-class `review` support for verdict coupling,
  blocked review, exact contract gates, portable current truth, carried mode
  and trigger state, review inheritance, and the full review capstone

## Workflow Law Ladder

The route-only ladder is staged on purpose:

- `30` introduces the narrow setup
- `40` and `41` split the local and reroute ownership outcomes on whether the
  next owner is still unknown
- `42` combines them into the full route-only handoff capstone

- `30_law_route_only_turns`: narrow route-only setup with `current none`,
  `stop`, and explicit reroute
- `31_currentness_and_trust_surface`: one current artifact plus emitted trust
  carriers
- `32_modes_and_match`: enum-backed modes, exhaustive `match`, and one current
  subject per branch
- `33_scope_and_exact_preservation`: narrow ownership with exact preservation
  and overlap checks
- `34_structure_mapping_and_vocabulary_preservation`: preserve non-exact truth
  such as structure, mapping, and vocabulary
- `35_basis_roles_and_rewrite_evidence`: comparison-only support and rewrite-
  evidence exclusions
- `36_invalidation_and_rebuild`: invalidation as a truth transition plus the
  rebuild pattern
- `37_law_reuse_and_patching`: named law subsections with explicit inheritance
  and override rules
- `38_metadata_polish_capstone`: the full integrated portable-truth model
- `39_guarded_output_sections`: output-owned keyed guarded sections, nested
  guarded readback, and output-guard namespace limits
- `40_route_only_local_ownership`: local-ownership branch of the route-only
  slice with `current none` when reroute is not justified
- `41_route_only_reroute_handoff`: explicit reroute branch of the route-only
  slice when the next owner is still unknown, paired with an emitted handoff
  comment contract plus routed `next_owner` agreement proof
- `42_route_only_handoff_capstone`: the full generic Slice A route-only
  handoff model with guarded conditional readback plus `standalone_read`
  guard-discipline proof

Examples `40` through `42` intentionally omit `trust_surface`. They are
route-only comment-schema readback for `current none` turns, not portable
current-truth carriers.

The route-only ladder now carries integrated structured proof for the two Slice
A coupling rules:

- `41` proves that a routed `next_owner` field must explicitly bind the routed
  target
- `42` proves that `standalone_read` cannot structurally reference guarded
  output detail

## Review Ladder

The review ladder begins right after the workflow-law capstones:

- `43_review_basic_verdict_and_route_coupling`: the smallest first-class
  `review`, one reviewed subject, one shared review contract, guarded
  `failing_gates`, and explicit accept/reject next-owner routing
- `44_review_handoff_first_block_gates`: handoff-first `block` gates,
  `blocked_gate`, and the rule that blocked review still emits one durable
  `changes_requested` comment
- `45_review_contract_gate_export_and_exact_failures`: exact exported
  `contract.<gate>` identities and faithful shared-contract `failing_gates`
- `46_review_current_truth_and_trust_surface`: review-owned `current artifact
  ... via Output.field`, trusted current truth, and currentness diagnostics
- `47_review_multi_subject_mode_and_trigger_carry`: subject sets, `subject_map`,
  carried `active_mode`, carried `trigger_reason`, and one next owner with
  different live current artifacts
- `48_review_inheritance_and_explicit_patching`: `abstract review`, `inherit
  fields`, inherited named review sections, and explicit child patching
- `49_review_capstone`: blocked review, exact contract gates, `support_only`,
  `ignore ... for rewrite_evidence`, `preserve`, multi-subject review,
  carried state, portable current truth, and current-none blocked outcomes in
  one capstone surface

That boundary is still honest. Doctrine validates structured interpolations and
output structure here; it still does not parse arbitrary free prose.

## Important Rules

- A checked-in ref file is not proof on its own. The manifest is the proof
  surface.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- Keep new examples narrow: one new idea at a time.
- Do not add a new language primitive just to paper over a bad example.
- Keep the corpus single-surface: shipped manifests should stay active proof,
  not advisory review lanes.

## Useful Commands

Verify the whole active corpus:

```bash
make verify-examples
```

Verify one example manifest:

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml
```

Emit configured example trees:

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth
```
