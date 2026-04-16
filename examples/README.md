# Examples

The examples are both the language teaching surface and the verification
corpus.
They are also the main proof that Doctrine stays deterministic and tractable as
prompt graphs grow, because the shipped verify and emit surfaces reuse shared
compile sessions while keeping manifest and output ordering stable.

Each numbered example may contain:

- `prompts/`: authored `.prompt` source
- `cases.toml`: manifest-backed proof used by `doctrine.verify_corpus`
- `schema_version` inside `cases.toml`: the manifest format version, not the
  Doctrine language version
- `ref/`: checked-in expected render or error output
- `build_ref/`: checked-in emitted tree output when the emit pipeline matters,
  including compiled Markdown trees, emitted structured-output schema files,
  `SKILL.md` package trees, and target-scoped `.flow.{d2,svg}` artifacts.
  `build_ref/` is verifier-owned proof, not a compiler or authoring
  convention.

## How To Read The Corpus

- Read the examples in numeric order. The sequence is intentional.
- The manifest is the proof surface. A checked-in ref file is not proof on its
  own.
- `schema_version` is the manifest contract version. It is not the Doctrine
  language version.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- Checked-in `ref/AGENTS.md` files now render ordinary outputs as grouped
  contract tables. Single artifacts start with `Contract | Value`. `files:`
  outputs add an `Artifacts` table.
- Keep new examples narrow. One new idea per example is the design rule.
- Package examples `95` through `103` use `SKILL.prompt` and teach the
  source-root bundle model. They do not make `build_ref/` part of the public
  authoring story.
- Batch verification and emit commands are expected to stay scalable on this
  corpus without changing emitted language or manifest order.

## Learning Paths

Some bullets below cover broad ranges.
Some call out landmark examples inside those ranges.

- `01` through `06`: core syntax, sections, imports, inheritance, and explicit
  workflow patching
- `07` through `29`: authored slots, routing, inputs, outputs, skills, refs,
  interpolation, reusable blocks, addressable paths, and enums
- `30` through `42`: workflow law, currentness, trust carriers, preservation,
  invalidation, guarded output items, and route-only turns
- `43` through `49`: first-class `review`
- `50` through `53`: bound roots for workflow law and review carriers
- `54` through `67`: integration and readable-document surfaces for
  `analysis`, owner-aware `schema:` / `structure:` attachments, readable
  markdown documents and descendants, schema artifact inventories and reusable
  groups, shared readable block reuse, multiline code blocks, schema-backed
  review contracts, title-bearing identity projections for concrete agents and
  enum members, authored render profiles, compact `properties`, typed row/item
  schemas, semantic render-profile lowering targets, and late extension
  readable blocks such as raw `markdown`, `html`, `footnotes`, `image`, and
  structured nested table cells
- `68` through `75`: reusable review-family scaffolds, dedicated `route_only`
  and `grounding`, schema-group invalidation, the flow visualizer showcase,
  first-class `decision` attachments, and cross-root standard-library imports
- `73` and `74`: the flagship multi-agent flow visualizer showcase and the
  decision-attachment capstone for reusable candidate-pool readback
- `73`: the flagship multi-agent flow visualizer showcase with shared inputs,
  a route-first handoff lane, a routed return loop, a shared carrier output,
  and checked-in `.flow.{d2,svg}` artifacts
- `74`: first-class `decision` attachments with typed candidate-pool, ranking,
  rejection, sequencing-proof, and winner-selection obligations
- `75`: repo-level compile config plus cross-root standard-library imports
  proven across multiple entrypoints and fail-loud ambiguity/config cases
- `76` through `86`: optional `final_output:` designation, dedicated
  final-answer rendering, `output schema` JSON final answers, fail-loud
  invalid-target / wrong-kind cases, and review-driven final answers that may
  either reuse `comment_output` or split the review comment from a separate
  control-only final output, plus imported reusable review comment outputs
  that still bind local routed owners
- `87` through `94`: shared output-facing route semantics for ordinary
  workflow-law outputs, review comments, dedicated `route_only`,
  `handoff_routing` law, split review `final_output:` contracts, first-class
  `route_from`, output-selected handoff routing, and `route.choice` guard
  narrowing
- `95` through `106`: first-class skill-package authoring with `SKILL.prompt`,
  source-root bundle copy-through, runtime and plugin metadata roots, bundled
  agent companions, larger compendium trees, exact path and case
  preservation, binary assets, and review-native final-response metadata for
  carrier, split control-ready, and split partial review finals
- `107` through `116`: direct `output[...]` declaration inheritance, inherited
  output attachments, imported reusable handoff outputs, inherited
  `final_output:`, inherited shared `route.*` readback, fail-loud output
  inheritance errors, titled or titleless readable lists, workflow-root
  readable blocks, directory-backed runtime package emit, and first-class named
  table declarations
- `117`: omitted first-class IO wrapper titles lower one direct declaration
  and fail loud on ambiguous shapes

For the shipped workflow-law reference, use
[../docs/WORKFLOW_LAW.md](../docs/WORKFLOW_LAW.md). For the shipped review
reference, use [../docs/REVIEW_SPEC.md](../docs/REVIEW_SPEC.md).
For the task-first guide to choosing the right Doctrine surface, use
[../docs/AUTHORING_PATTERNS.md](../docs/AUTHORING_PATTERNS.md).
For the shipped skill-package authoring guide, use
[../docs/SKILL_PACKAGE_AUTHORING.md](../docs/SKILL_PACKAGE_AUTHORING.md).
For versioning and breaking-change guidance, use
[../docs/VERSIONING.md](../docs/VERSIONING.md).
For public release history, use [../CHANGELOG.md](../CHANGELOG.md).

## Corpus Index

| ID | Focus |
| --- | --- |
| `01_hello_world` | Smallest concrete agents, `role`, and inline `workflow` shapes. |
| `02_sections` | Titled workflow sections and section-key validation. |
| `03_imports` | Absolute and relative imports plus typed imported refs. |
| `04_inheritance` | Basic agent and workflow inheritance. |
| `05_workflow_merge` | Explicit inherited workflow patching and ordering. |
| `06_nested_workflows` | Nested workflow structure and the boundary between inline and named workflows. |
| `07_handoffs` | Authored workflow slots, next-owner routing, and explicit owner-change doctrine. |
| `08_inputs` | Basic typed `input` declarations. |
| `09_outputs` | Basic typed `output` declarations, targets, shapes, and `files` mode. |
| `10_routing_and_stop_rules` | Ordinary routing and stop guidance before workflow law. |
| `11_skills_and_tools` | First-class `skill` declarations and role-side skill references. |
| `12_role_home_composition` | Composing larger role homes from reusable parts. |
| `13_critic_protocol` | Structured critic-style doctrine before first-class `review`. |
| `14_handoff_truth` | Exact handoff truth across split prompt modules and emitted outputs. |
| `15_workflow_body_refs` | Readable declaration refs in workflow section bodies. |
| `16_workflow_string_interpolation` | Interpolation inside authored workflow prose. |
| `17_agent_mentions` | Concrete agent mentions and mention validation. |
| `18_rich_io_buckets` | Richer I/O record structure and readable contract buckets. |
| `19_emphasized_prose_lines` | `required`, `important`, `warning`, and `note` prose lines. |
| `20_authored_prose_interpolation` | Interpolation across more authored prose surfaces. |
| `21_first_class_skills_blocks` | Reusable top-level `skills` blocks. |
| `22_skills_block_inheritance` | Inheritance and patching for `skills` blocks. |
| `23_first_class_io_blocks` | Reusable top-level `inputs` and `outputs` blocks. |
| `24_io_block_inheritance` | Inheritance and patching for I/O blocks. |
| `25_abstract_agent_io_override` | Abstract agent I/O doctrine and concrete override rules. |
| `26_abstract_authored_slots` | Required authored slots on abstract agents. |
| `27_addressable_record_paths` | Addressable paths through record bodies. |
| `28_addressable_workflow_paths` | Addressable paths through recursive workflow structure. |
| `29_enums` | Closed vocabularies with top-level `enum`. |
| `30_law_route_only_turns` | Narrow route-only workflow-law setup with `current none`. |
| `31_currentness_and_trust_surface` | Portable current truth plus `trust_surface`. |
| `32_modes_and_match` | Enum-backed `mode` plus exhaustive `match`. |
| `33_scope_and_exact_preservation` | `own only`, `preserve exact`, and overlap checks. |
| `34_structure_mapping_and_vocabulary_preservation` | Preserving structure, mapping, and vocabulary across artifact and schema-family roots. |
| `35_basis_roles_and_rewrite_evidence` | Comparison-only support and rewrite-evidence exclusions. |
| `36_invalidation_and_rebuild` | Invalidation as a truth transition plus rebuild routing. |
| `37_law_reuse_and_patching` | Named workflow-law subsections and explicit law patching. |
| `38_metadata_polish_capstone` | Full workflow-law capstone with activation, currentness, preservation, invalidation, and reroute. |
| `39_guarded_output_sections` | Guarded output items and nested guarded readback. |
| `40_route_only_local_ownership` | Route-only local-ownership branch with `current none`. |
| `41_route_only_reroute_handoff` | Route-only reroute branch when the next owner is still unknown. |
| `42_route_only_handoff_capstone` | Integrated route-only handoff capstone. |
| `43_review_basic_verdict_and_route_coupling` | Smallest first-class `review`. |
| `44_review_handoff_first_block_gates` | `block` gates and `blocked_gate`. |
| `45_review_contract_gate_export_and_exact_failures` | Exact contract gate export and faithful `failing_gates`. |
| `46_review_current_truth_and_trust_surface` | Review current truth on trusted output carriers, including blocked-gate-guarded currentness. |
| `47_review_multi_subject_mode_and_trigger_carry` | Multi-subject review plus carried mode and trigger reason. |
| `48_review_inheritance_and_explicit_patching` | `abstract review` and explicit review patching. |
| `49_review_capstone` | Full review capstone with blocked review, exact gates, carried state, and current truth. |
| `50_bound_currentness_roots` | Bound roots for workflow-law currentness carriers. |
| `51_inherited_bound_io_roots` | Inherited bound I/O roots staying visible to workflow law. |
| `52_bound_scope_and_preservation` | Bound roots for ownership and preservation law, including emitted-output and schema-family roots. |
| `53_review_bound_carrier_roots` | Bound review carriers and carried review state. |
| `54_analysis_attachment` | Concrete-agent `analysis:` attachment, `prove`, and analysis-root addressability. |
| `55_owner_aware_schema_attachments` | Owner-aware split between `output shape.schema` and `output.schema`. |
| `56_document_structure_attachments` | Typed `structure:` attachments on markdown-bearing inputs and outputs. |
| `57_schema_review_contracts` | Schema-backed `review contract:` with exported schema gates. |
| `58_readable_document_blocks` | Rich readable document blocks render natively through `structure:`. |
| `59_document_inheritance_and_descendants` | Document inheritance plus keyed readable descendants on lists and tables. |
| `60_shared_readable_bodies` | Shared readable blocks on workflow sections, skill-entry bodies, and output bodies. |
| `61_multiline_code_and_readable_failures` | Multiline readable code blocks plus compile-negative readable validation. |
| `62_identity_titles_keys_and_wire` | Titled concrete-agent identities plus enum member key/title/wire projections. |
| `63_schema_artifacts_and_groups` | First-class schema `artifacts:` / `groups:` plus family-namespaced schema addressability. |
| `64_render_profiles_and_properties` | Authored `render_profile`, compact `properties`, explicit readable `guard` shells, and wrapped `CommentText` lowering. |
| `65_row_and_item_schemas` | Typed `item_schema:` / `row_schema:` descendants on readable list and table blocks. |
| `66_late_extension_blocks` | Explicit raw `markdown` / `html`, `footnotes`, `image`, and structured nested table cells. |
| `67_semantic_profile_lowering` | Semantic render-profile lowering for `analysis.stages`, `review.contract_checks`, and `control.invalidations`, plus document-attached profile inheritance through `output structure:`. |
| `68_review_family_shared_scaffold` | Dedicated `review_family` reuse with explicit inherited scaffold accounting. |
| `69_case_selected_review_family` | Case-selected `review_family` with exhaustive enum-backed cases. |
| `70_route_only_declaration` | Dedicated `route_only` lowered through the shipped route-only workflow-law path. |
| `71_grounding_declaration` | Dedicated `grounding` protocol with explicit policy, ordinary routing, and grounding-root preservation mapping. |
| `72_schema_group_invalidation` | `schema.groups.*` invalidation expansion in authored group order. |
| `73_flow_visualizer_showcase` | Flagship multi-agent flow visualizer proof with shared inputs, a route-first handoff lane, a routed return loop, a shared carrier output, and checked-in `.flow.{d2,svg}` artifacts. |
| `74_decision_attachment` | First-class `decision` declarations plus multiple concrete-agent `decision:` attachments, duplicate-ref rejection, and winner-selection scaffolds. |
| `75_cross_root_standard_library_imports` | Repo-level `[tool.doctrine.compile].additional_prompt_roots`, shared authored `prompts/` roots, multiple entrypoints, and fail-loud ambiguity/config proofs for cross-root imports. |
| `76_final_output_prose_basic` | Smallest prose `final_output:` designation with a dedicated final-answer render. |
| `77_final_output_optional_passthrough` | Omitting `final_output:` preserves ordinary output rendering. |
| `78_final_output_and_side_artifacts` | Final assistant messages stay separate from ordinary emitted artifacts. |
| `79_final_output_output_schema` | `output schema` JSON `final_output:` with payload preview and optional rendered example. |
| `80_final_output_rejects_file_targets` | `final_output:` rejects file-backed outputs. |
| `81_final_output_rejects_non_output_refs` | `final_output:` rejects refs that are not `output` declarations. |
| `82_review_final_output_prose_basic` | Review-driven prose `final_output:` may reuse `comment_output` as the dedicated final answer. |
| `83_review_final_output_output_schema` | Review-driven `output schema` JSON `final_output:` may reuse `comment_output` and keep review semantics on the same output boundary. |
| `84_review_split_final_output_prose` | Review-driven prose `final_output:` may split from `comment_output` while the separate final message still inherits review semantics. |
| `85_review_split_final_output_output_schema` | Review-driven `output schema` JSON `final_output:` may split from `comment_output` and end with a control-only final JSON result. |
| `86_imported_review_comment_local_routes` | Imported reusable `comment_output` declarations may still structurally bind local routed owners on the concrete review. |
| `87_workflow_route_output_binding` | Ordinary workflow-law outputs may read shared compiler-owned `route.*` semantics, and unguarded reads fail loudly when some branches do not route. |
| `88_review_route_semantics_shared_binding` | Review comments may combine review semantics and shared `route.*` semantics on the same emitted output. |
| `89_route_only_shared_route_semantics` | Dedicated `route_only` lowers onto the same shared `route.*` output surface. |
| `90_split_handoff_and_final_output_shared_route_semantics` | A durable review comment and a separate JSON `final_output:` may consume the same shared `route.*` truth without merging into one output. |
| `91_handoff_routing_route_output_binding` | `handoff_routing` may feed the same shared `route.*` semantics into ordinary outputs and `final_output:` when its `law:` block resolves the route. |
| `92_route_from_basic` | Workflow law may pick one routed owner from a typed selector with first-class `route_from`. |
| `93_handoff_routing_route_from_final_output` | `handoff_routing` may bind `final_output:` route owner truth from an emitted output with `route_from`. |
| `94_route_choice_guard_narrowing` | `route.choice` guards may narrow branch-specific route detail, while unguarded `route.summary` still fails loud. |
| `95_skill_package_minimal` | Smallest `SKILL.prompt` and top-level `skill package` surface. |
| `96_skill_package_references` | Ordinary bundled reference documents copied through from the package source root. |
| `97_skill_package_scripts` | Ordinary bundled script files copied through from the package source root. |
| `98_skill_package_runtime_metadata` | Runtime metadata roots such as `agents/openai.yaml` in the source-root bundle model. |
| `99_skill_package_plugin_metadata` | Plugin-style split metadata roots such as `.codex-plugin/plugin.json`, `.app.json`, and `agents/openai.yaml`. |
| `100_skill_package_bundled_agents` | Bundled `agents/**/*.prompt` modules that emit markdown companions while normal files in the same `agents/` tree still bundle. |
| `101_skill_package_compendium` | Larger source-root compendium and reference tree preservation. |
| `102_skill_package_path_case_preservation` | Exact path and case preservation plus negative collision proof. |
| `103_skill_package_binary_assets` | Bundled binary assets preserved byte for byte. |
| `104_review_final_output_output_schema_blocked_control_ready` | Same-output review JSON final responses may stay on the carrier and still report blocked review with no route. |
| `105_review_split_final_output_output_schema_control_ready` | Split review JSON final responses may bind review semantics and become control-ready. |
| `106_review_split_final_output_output_schema_partial` | Split review JSON final responses may bind only a partial review subset, and invalid `review_fields` placement still fails loud. |
| `107_output_inheritance_basic` | Smallest direct `output[...]` inheritance proof with one inherited section and one local extension. |
| `108_output_inheritance_attachments` | Inherited outputs may keep top-level attachments such as `render_profile:`, `trust_surface`, and `standalone_read`, and override them explicitly. |
| `109_imported_review_handoff_output_inheritance` | Imported reusable handoff outputs may be inherited and extended locally before they are bound through an `outputs` block. |
| `110_final_output_inherited_output` | `final_output:` may point at an inherited `TurnResponse` output and still render as the dedicated final answer. |
| `111_inherited_output_route_semantics` | Inherited outputs may keep shared `route.*` semantics after the compiler resolves the parent output. |
| `112_output_inheritance_fail_loud` | Output inheritance fails loud on missing inherited keys, patch-without-parent, unkeyed parents, and wrong-kind overrides. |
| `113_titleless_readable_lists` | Titled and titleless readable lists render cleanly, and detailed list blocks drop helper kind metadata lines. |
| `114_workflow_root_readable_blocks` | Workflow roots may own readable blocks directly without wrapping them in a local section first. |
| `115_runtime_agent_packages` | Thin build handles may emit imported runtime packages with package-root `AGENTS.md`, optional sibling `SOUL.md`, and bundled peer files. |
| `116_first_class_named_tables` | Top-level `table` declarations may be reused by local document table keys without changing rendered Markdown. |
| `117_io_omitted_wrapper_titles` | Omitted first-class IO wrapper titles lower one direct declaration and fail loud on ambiguous shapes. |
| `118_output_target_delivery_skill_binding` | Imported output targets may bind a delivery skill and render one clean `Delivered Via` contract row. |

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
uv run --locked python -m doctrine.emit_docs --target example_115_runtime_agent_packages
uv run --locked python -m doctrine.emit_skill --target example_95_skill_package_minimal
uv run --locked python -m doctrine.emit_skill --target example_100_skill_package_bundled_agents
uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase
uv run --locked python -m doctrine.emit_flow --target example_115_runtime_agent_packages
```

Example `73_flow_visualizer_showcase` is the canonical checked-in flow
example. Its `build_ref/` tree includes compiled Markdown and
`AGENTS.flow.{d2,svg}` proof artifacts.
Examples `95` through `103` are the canonical checked-in skill-package gallery.
Their `build_ref/` trees are expected emitted package proof, not public
authoring input.
Example `115_runtime_agent_packages` is the canonical checked-in runtime-package
build proof. Its `build_ref/` tree shows the thin build-handle pattern, one
package-root `AGENTS.md`, one optional sibling `SOUL.md`, and bundled peer
files.
