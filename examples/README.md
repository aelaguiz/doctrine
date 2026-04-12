# Examples

The examples are both the language teaching surface and the verification
corpus.
They are also the main proof that Doctrine stays deterministic and tractable as
prompt graphs grow, because the shipped verify and emit surfaces reuse shared
compile sessions while keeping manifest and output ordering stable.

Each numbered example may contain:

- `prompts/`: authored `.prompt` source
- `cases.toml`: manifest-backed proof used by `doctrine.verify_corpus`
- `ref/`: checked-in expected render or error output
- `build_ref/`: checked-in emitted tree output when the emit pipeline matters,
  including compiled Markdown trees and target-scoped `.flow.{d2,svg}`
  artifacts

## How To Read The Corpus

- Read the examples in numeric order. The sequence is intentional.
- The manifest is the proof surface. A checked-in ref file is not proof on its
  own.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- Keep new examples narrow. One new idea per example is the design rule.
- Batch verification and emit commands are expected to stay scalable on this
  corpus without changing emitted language or manifest order.

## Learning Paths

- `01` through `06`: core syntax, sections, imports, inheritance, and explicit
  workflow patching
- `07` through `29`: authored slots, routing, inputs, outputs, skills, refs,
  interpolation, reusable blocks, addressable paths, and enums
- `30` through `42`: workflow law, currentness, trust carriers, preservation,
  invalidation, guarded output sections, and route-only turns
- `43` through `49`: first-class `review`
- `50` through `53`: bound roots for workflow law and review carriers
- `54` through `74`: second-wave integration surfaces for `analysis`,
  owner-aware `schema:` / `structure:` attachments, readable markdown
  documents and descendants, schema artifact inventories and reusable groups,
  shared readable block reuse, multiline code blocks, schema-backed review
  contracts, title-bearing identity projections for concrete agents and enum
  members, authored render profiles, compact `properties`, typed row/item
  schemas, semantic render-profile lowering targets, and late extension
  readable blocks such as raw `markdown`, `html`, `footnotes`, `image`, and
  structured nested table cells, plus `review_family`, case-selected review
  families, dedicated `route_only`, dedicated `grounding`, schema-group
  invalidation, and first-class `decision` attachments for candidate-pool,
  sequencing-proof, and winner-selection scaffolds
- `73` and `74`: the flagship multi-agent flow visualizer showcase and the
  decision-attachment capstone for reusable candidate-pool readback
- `73`: the flagship multi-agent flow visualizer showcase with shared inputs,
  a route-first handoff lane, a routed return loop, a shared carrier output,
  and checked-in `.flow.{d2,svg}` artifacts
- `74`: first-class `decision` attachments with typed candidate-pool, ranking,
  rejection, sequencing-proof, and winner-selection obligations

For the shipped workflow-law reference, use
[../docs/WORKFLOW_LAW.md](../docs/WORKFLOW_LAW.md). For the shipped review
reference, use [../docs/REVIEW_SPEC.md](../docs/REVIEW_SPEC.md).

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
| `34_structure_mapping_and_vocabulary_preservation` | Preserving structure, mapping, and vocabulary. |
| `35_basis_roles_and_rewrite_evidence` | Comparison-only support and rewrite-evidence exclusions. |
| `36_invalidation_and_rebuild` | Invalidation as a truth transition plus rebuild routing. |
| `37_law_reuse_and_patching` | Named workflow-law subsections and explicit law patching. |
| `38_metadata_polish_capstone` | Full workflow-law capstone with activation, currentness, preservation, invalidation, and reroute. |
| `39_guarded_output_sections` | Guarded output sections and nested guarded readback. |
| `40_route_only_local_ownership` | Route-only local-ownership branch with `current none`. |
| `41_route_only_reroute_handoff` | Route-only reroute branch when the next owner is still unknown. |
| `42_route_only_handoff_capstone` | Integrated route-only handoff capstone. |
| `43_review_basic_verdict_and_route_coupling` | Smallest first-class `review`. |
| `44_review_handoff_first_block_gates` | `block` gates and `blocked_gate`. |
| `45_review_contract_gate_export_and_exact_failures` | Exact contract gate export and faithful `failing_gates`. |
| `46_review_current_truth_and_trust_surface` | Review current truth on trusted output carriers. |
| `47_review_multi_subject_mode_and_trigger_carry` | Multi-subject review plus carried mode and trigger reason. |
| `48_review_inheritance_and_explicit_patching` | `abstract review` and explicit review patching. |
| `49_review_capstone` | Full review capstone with blocked review, exact gates, carried state, and current truth. |
| `50_bound_currentness_roots` | Bound roots for workflow-law currentness carriers. |
| `51_inherited_bound_io_roots` | Inherited bound I/O roots staying visible to workflow law. |
| `52_bound_scope_and_preservation` | Bound roots for ownership and preservation law. |
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
| `64_render_profiles_and_properties` | Authored `render_profile`, compact `properties`, and explicit readable `guard` shells. |
| `65_row_and_item_schemas` | Typed `item_schema:` / `row_schema:` descendants on readable list and table blocks. |
| `66_late_extension_blocks` | Explicit raw `markdown` / `html`, `footnotes`, `image`, and structured nested table cells. |
| `67_semantic_profile_lowering` | Semantic render-profile lowering for `analysis.stages`, `review.contract_checks`, and `control.invalidations`, plus document-attached profile inheritance through `output structure:`. |
| `68_review_family_shared_scaffold` | Dedicated `review_family` reuse with explicit inherited scaffold accounting. |
| `69_case_selected_review_family` | Case-selected `review_family` with exhaustive enum-backed cases. |
| `70_route_only_declaration` | Dedicated `route_only` lowered through the shipped route-only workflow-law path. |
| `71_grounding_declaration` | Dedicated `grounding` protocol with explicit policy and ordinary routing. |
| `72_schema_group_invalidation` | `schema.groups.*` invalidation expansion in authored group order. |
| `73_flow_visualizer_showcase` | Flagship multi-agent flow visualizer proof with shared inputs, a route-first handoff lane, a routed return loop, a shared carrier output, and checked-in `.flow.{d2,svg}` artifacts. |
| `74_decision_attachment` | First-class `decision` declarations plus concrete-agent `decision:` attachments for candidate-pool, sequencing-proof, and winner-selection scaffolds. |

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
uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase
```

Example `73_flow_visualizer_showcase` is the canonical checked-in flow
example. Its `build_ref/` tree includes both compiled Markdown and
`AGENTS.flow.{d2,svg}` proof artifacts.
