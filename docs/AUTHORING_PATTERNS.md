# Doctrine Authoring Patterns

This guide answers one question:
If you need to do this, do it this way in Doctrine.

Use this guide when you are porting a prose-heavy agent system into Doctrine,
or when you know the syntax exists but do not yet know which surface to pick.
Use [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md) for the exact declaration
rules. Use [../examples/README.md](../examples/README.md) for the full proof
ladder.

This guide is not a second syntax reference.
It is a porting guide.

## What To Preserve When You Port

Doctrine works best when you preserve five things:

- One current surface.
- One owner at a time.
- One semantic job per turn.
- One typed trust boundary on outputs.
- One shared home for shared doctrine.

If your old system spreads those truths across prose, side files, and host
state, port the truth first.
Do not port the clutter.

## Map The Source System Before You Write Syntax

Before you write Doctrine, answer these questions:

- Which roles are real runtime owners?
- Which artifact is current after each turn?
- Which turns produce work, and which turns only judge or route it?
- What must later owners trust from the output itself?
- What does the host need at the end: a durable comment, one final answer, or
  both?

If you cannot answer those questions yet, keep mapping.
Doctrine gets better as the flow model gets simpler.

## Choose The Turn Kind First

Most porting mistakes start here.
Choose the turn kind before you choose the local syntax.

- Producer turn: use `workflow`, and add `law:` only when the compiler must
  own currentness, preservation, invalidation, or route truth.
- Review turn: use `review`, and use `review_family` when several reviews share
  one scaffold.
- Control-only turn with `current none`: use `route_only`.
- Ordinary turn that still needs route truth on outputs: use
  `handoff_routing` with a `law:` block.
- Grounding protocol turn: use `grounding`.

Best anchors:
- [43_review_basic_verdict_and_route_coupling](../examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt)
- [70_route_only_declaration](../examples/70_route_only_declaration/prompts/AGENTS.prompt)
- [71_grounding_declaration](../examples/71_grounding_declaration/prompts/AGENTS.prompt)
- [91_handoff_routing_route_output_binding](../examples/91_handoff_routing_route_output_binding/prompts/AGENTS.prompt)

## Port By Semantic Job, Not By Old Headings

Start with the job the turn is doing now.
Do not start with the heading names in the old prompt tree.

### Producer turn

Use `workflow` when the turn is making or updating durable work.
Add `law:` only when the compiler must own currentness, preservation,
invalidation, or route semantics.

Use this when:
- the turn writes or updates the main artifact
- the turn needs narrow write scope
- the turn needs exact or structural preservation
- the turn may invalidate downstream work
- the agent may still need to reread one live ledger or file and make a plain
  judgment from that current state

Do not do this:
- Do not turn every producer turn into a review.
- Do not bury currentness or invalidation only in handoff prose.
- Do not force workflow-law or mode-selection syntax when the branch really
  lives in a human judgment over one live file or ledger.

Best anchors:
- [33_scope_and_exact_preservation](../examples/33_scope_and_exact_preservation/prompts/AGENTS.prompt)
- [36_invalidation_and_rebuild](../examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt)
- [38_metadata_polish_capstone](../examples/38_metadata_polish_capstone/prompts/AGENTS.prompt)
- [73_flow_visualizer_showcase](../examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt)
- [WORKFLOW_LAW.md](WORKFLOW_LAW.md)

### Review turn

Use `review` when the turn's job is to judge work, issue a verdict, name the
failing gates, and route honestly.
Use `review_family` when several reviews share the same comment contract,
shared checks, or case-selected scaffold.

Use this when:
- the turn is a critic, acceptance, or review lane
- verdicts and failing gates are first-class truth
- next-owner truth depends on review outcome
- downstream owners need review-carried currentness or mode

Do not do this:
- Do not model new review work with plain workflow prose plus manual verdict
  fields and routing sections.
- Do not clone the same review scaffold across many lanes when one
  `review_family` can own it once.

Best anchors:
- [57_schema_review_contracts](../examples/57_schema_review_contracts/prompts/AGENTS.prompt)
- [43_review_basic_verdict_and_route_coupling](../examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt)
- [49_review_capstone](../examples/49_review_capstone/prompts/AGENTS.prompt)
- [69_case_selected_review_family](../examples/69_case_selected_review_family/prompts/AGENTS.prompt)
- [REVIEW_SPEC.md](REVIEW_SPEC.md)

Historical proof:
- [13_critic_protocol](../examples/13_critic_protocol/prompts/AGENTS.prompt)
  shows the older prose-heavy critic style.
  Keep it as history, not as the default for new work.

### Route-only turn

Use `route_only` when the real job is routing, repair, waiting, or publish
follow-up and no specialist artifact is current.
Use `handoff_routing` with a `law:` block when the turn stays ordinary but the
outputs need compiler-owned route truth.

Use this when:
- the turn honestly has `current none`
- the turn exists to route or stop
- the output needs `route.*`
- the selected route comes from a typed selector

Do not do this:
- Do not pretend a specialist artifact is current when it is not.
- Do not keep route truth only in prose when the compiler can own it.

Best anchors:
- [70_route_only_declaration](../examples/70_route_only_declaration/prompts/AGENTS.prompt)
- [89_route_only_shared_route_semantics](../examples/89_route_only_shared_route_semantics/prompts/AGENTS.prompt)
- [91_handoff_routing_route_output_binding](../examples/91_handoff_routing_route_output_binding/prompts/AGENTS.prompt)
- [92_route_from_basic](../examples/92_route_from_basic/prompts/AGENTS.prompt)
- [94_route_choice_guard_narrowing](../examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt)
- [WORKFLOW_LAW.md](WORKFLOW_LAW.md)

Historical proof:
- [30_law_route_only_turns](../examples/30_law_route_only_turns/prompts/AGENTS.prompt)
  shows the narrower older path before dedicated `route_only`.

### Grounding turn

Use `grounding` when the job is to keep a source-to-target grounding policy
explicit.

Use this when:
- the turn must say what grounding starts from
- some evidence is allowed and some is forbidden
- unresolved grounding may reroute the turn

Do not do this:
- Do not hide grounding policy inside generic role prose.
- Do not invent a side packet or hidden control channel for grounding.

Best anchors:
- [71_grounding_declaration](../examples/71_grounding_declaration/prompts/AGENTS.prompt)
- [WORKFLOW_LAW.md](WORKFLOW_LAW.md)

## Put Truth In The Right Place

Doctrine stays clean when each surface owns one kind of truth.

### Let prose teach the human job

Use `workflow` and ordinary readable sections for:
- read order
- role boundary
- process guidance
- skill usage guidance
- durable explanations meant for humans

Do not force those things into `law`, `review`, or output fields unless the
compiler needs to reason about them.

Best anchors:
- [12_role_home_composition](../examples/12_role_home_composition/prompts/AGENTS.prompt)
- [15_workflow_body_refs](../examples/15_workflow_body_refs/prompts/AGENTS.prompt)
- [16_workflow_string_interpolation](../examples/16_workflow_string_interpolation/prompts/AGENTS.prompt)

### Let the compiler own semantic truth

Use `law` or `review` for:
- current artifact or `current none`
- owned scope
- preserved truth
- invalidation
- review verdicts
- failing gates
- carried mode or trigger state
- selected route truth

Do not restate those truths by hand in prose and hope they stay aligned.

Best anchors:
- [31_currentness_and_trust_surface](../examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt)
- [36_invalidation_and_rebuild](../examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt)
- [33_scope_and_exact_preservation](../examples/33_scope_and_exact_preservation/prompts/AGENTS.prompt)
- [46_review_current_truth_and_trust_surface](../examples/46_review_current_truth_and_trust_surface/prompts/AGENTS.prompt)
- [47_review_multi_subject_mode_and_trigger_carry](../examples/47_review_multi_subject_mode_and_trigger_carry/prompts/AGENTS.prompt)

### Put portable downstream truth on outputs

Use explicit output fields plus `trust_surface`.
That is the downstream trust boundary.

Use this when:
- a later owner must trust the current artifact
- a later owner must trust invalidations
- a later owner must trust selected review or route readback

Do not do this:
- Do not treat `standalone_read` as a trust channel.
- Do not hide portable truth in prose only.
- Do not mirror every readable note field into typed state.
  Keep `trust_surface` small.
  Type only the fields later turns must trust mechanically.

Best anchors:
- [31_currentness_and_trust_surface](../examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt)
- [39_guarded_output_sections](../examples/39_guarded_output_sections/prompts/AGENTS.prompt)
- [46_review_current_truth_and_trust_surface](../examples/46_review_current_truth_and_trust_surface/prompts/AGENTS.prompt)
- [51_inherited_bound_io_roots](../examples/51_inherited_bound_io_roots/prompts/AGENTS.prompt)
- [53_review_bound_carrier_roots](../examples/53_review_bound_carrier_roots/prompts/AGENTS.prompt)
- [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md)

### Use shared `route.*` instead of rebuilding route truth

When route semantics are live, read:
- `route.exists`
- `route.next_owner`
- `route.label`
- `route.summary`
- `route.choice.*` when `route_from` or `final_output.route:` makes that safe

When a harness needs to route the final response, read the top-level `route`
block in `final_output.contract.json`. When the route comes from a structured
final output, read `route.selector` too. Do not ask the model to copy that
same target into a private control field.

Do not do this:
- Do not duplicate route owner and route summary as manual output fields.
- Do not leave route reads unguarded when some branches may not route.

Best anchors:
- [87_workflow_route_output_binding](../examples/87_workflow_route_output_binding/prompts/AGENTS.prompt)
- [88_review_route_semantics_shared_binding](../examples/88_review_route_semantics_shared_binding/prompts/AGENTS.prompt)
- [89_route_only_shared_route_semantics](../examples/89_route_only_shared_route_semantics/prompts/AGENTS.prompt)
- [91_handoff_routing_route_output_binding](../examples/91_handoff_routing_route_output_binding/prompts/AGENTS.prompt)
- [93_handoff_routing_route_from_final_output](../examples/93_handoff_routing_route_from_final_output/prompts/AGENTS.prompt)
- [94_route_choice_guard_narrowing](../examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt)
- [119_route_only_final_output_contract](../examples/119_route_only_final_output_contract/prompts/AGENTS.prompt)
- [120_route_field_final_output_contract](../examples/120_route_field_final_output_contract/prompts/AGENTS.prompt)
- [121_nullable_route_field_final_output_contract](../examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt)

### Use `route field` on structured final output when the payload chooses the next owner

Use this when the final JSON itself should choose the next routed agent.

The clean path is:
- declare the choices on one `route field`
- bind `final_output.route:` to that field
- let Doctrine emit the runtime route contract

Do not do this:
- Do not duplicate the same route choice in a payload field and a second
  `route_from` table.
- Do not copy the next owner into a private payload control field for the
  harness.

Best anchors:
- [120_route_field_final_output_contract](../examples/120_route_field_final_output_contract/prompts/AGENTS.prompt)
- [121_nullable_route_field_final_output_contract](../examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt)
- [92_route_from_basic](../examples/92_route_from_basic/prompts/AGENTS.prompt)

### Use `final_output:` only for the turn-ending answer

`final_output:` is not your whole output model.
It marks the one `TurnResponse` output that ends the turn.

Port this by host need:

- Same carrier is also the final answer:
  keep one review carrier and end on that same output.
- Split but control-ready final answer:
  keep the durable review comment and end on a second output that binds the
  review fields the host needs.
- Split partial final answer:
  keep the durable review comment and end on a smaller final output that binds
  only part of the review state.

Do not do this:
- Do not point `final_output:` at a file output.
- Do not throw away the durable review carrier just because the host also
  wants a smaller final answer.

Best anchors:
- [78_final_output_and_side_artifacts](../examples/78_final_output_and_side_artifacts/prompts/AGENTS.prompt)
- [76_final_output_prose_basic](../examples/76_final_output_prose_basic/prompts/AGENTS.prompt)
- [79_final_output_output_schema](../examples/79_final_output_output_schema/prompts/AGENTS.prompt)
- [104_review_final_output_output_schema_blocked_control_ready](../examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt)
- [105_review_split_final_output_output_schema_control_ready](../examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt)
- [106_review_split_final_output_output_schema_partial](../examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt)

### Choose `schema` and `document` by artifact job

Use `document` with `structure:` when the artifact is a readable markdown file
with declared sections and blocks.
Use `schema` when the artifact is a typed contract, gate surface, artifact
inventory, invalidation group, or schema-backed review contract.

Do not do this:
- Do not attach both `schema:` and `structure:` to the same markdown-bearing
  output.
- Do not use `document` where the real need is typed gates or artifact groups.

Best anchors:
- [55_owner_aware_schema_attachments](../examples/55_owner_aware_schema_attachments/prompts/AGENTS.prompt)
- [56_document_structure_attachments](../examples/56_document_structure_attachments/prompts/AGENTS.prompt)
- [57_schema_review_contracts](../examples/57_schema_review_contracts/prompts/AGENTS.prompt)
- [58_readable_document_blocks](../examples/58_readable_document_blocks/prompts/AGENTS.prompt)
- [63_schema_artifacts_and_groups](../examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt)

## Keep Large Repos Small And Honest

The most useful porting move is often subtraction.

### Share role-home law once

Put shared read order, turn discipline, handoff discipline, and note discipline
in one inherited layer.
Keep each role file about that role's job.

Do not do this:
- Do not restate the same read-first rules in every role.
- Do not make every role prompt re-explain the whole runtime.

Best anchors:
- [12_role_home_composition](../examples/12_role_home_composition/prompts/AGENTS.prompt)
- [37_law_reuse_and_patching](../examples/37_law_reuse_and_patching/prompts/AGENTS.prompt)
- [21_first_class_skills_blocks](../examples/21_first_class_skills_blocks/prompts/AGENTS.prompt)
- [23_first_class_io_blocks](../examples/23_first_class_io_blocks/prompts/AGENTS.prompt)
- [24_io_block_inheritance](../examples/24_io_block_inheritance/prompts/AGENTS.prompt)

When one child keeps several inherited keyed items unchanged, prefer grouped
`inherit { ... }`. Doctrine lowers it to the same explicit inherited
accounting it already uses for singular `inherit key`.

### Keep host facts thin

Bind the host state the agent truly needs.
Nothing more.

Good host facts are:
- narrow
- typed
- local to one semantic choice
- easy to replace with compiler-owned truth later
- sometimes just one real file or ledger input the next owner should reread
  directly

Bad host facts are:
- giant review state bags
- giant route state bags
- blobs that tell the agent what it should have reasoned itself

Do not do this:
- Do not let host facts become a second control plane inside Doctrine.
- Do not make the host decide review gates, route truth, and currentness all at
  once when Doctrine can own those semantics.
- If the host already has one shared ledger or current-state surface, bind that
  once instead of rebuilding the same state in many separate inputs.
- Do not assume `source: Prompt` is better than `source: File`.
  If the honest job is “read the current ledger again,” model that directly.

Best anchors:
- [70_route_only_declaration](../examples/70_route_only_declaration/prompts/AGENTS.prompt)
- [71_grounding_declaration](../examples/71_grounding_declaration/prompts/AGENTS.prompt)
- [92_route_from_basic](../examples/92_route_from_basic/prompts/AGENTS.prompt)

### Prefer one shared note contract over many near-clones

If producers, critics, and route-only turns all need the same kind of readable
handoff, share the output shape and the shared readable bodies.

Do not do this:
- Do not clone the same comment carrier for every lane unless the structure
  really changes.
- Do not force later readers to decode a different note shape on every handoff.

Best anchors:
- [23_first_class_io_blocks](../examples/23_first_class_io_blocks/prompts/AGENTS.prompt)
- [24_io_block_inheritance](../examples/24_io_block_inheritance/prompts/AGENTS.prompt)
- [60_shared_readable_bodies](../examples/60_shared_readable_bodies/prompts/AGENTS.prompt)

Use grouped `inherit { ... }` when a child keeps several inherited IO wrappers
unchanged before one local override.

### Keep skills semantic and keep runtime config elsewhere

Use inline `skill` and `skills` to describe capability meaning inside
`AGENTS.prompt` and `SOUL.prompt`.
Use `skill package` only when Doctrine must emit a real package tree.

Do not do this:
- Do not overload inline `skills` when the job is to ship `SKILL.md` plus a
  package tree.
- Do not split one semantic skill rule across many prompt files and a second
  config surface unless that second surface is truly runtime-only.
- Do not launder stable shared runtime rules through many local prompts.
  Put repo-wide rules once in a shared import, base owner, or shared skill.

Authoring tip:
- Keep `purpose` short and direct.
- When `use_when`, `provides`, `does_not`, or a similar field is really a
  list, use a titleless `bullets` or `checklist` block inside that field.
  That keeps emitted Markdown compact and easy to scan.

Best anchors:
- [11_skills_and_tools](../examples/11_skills_and_tools/prompts/AGENTS.prompt)
- [21_first_class_skills_blocks](../examples/21_first_class_skills_blocks/prompts/AGENTS.prompt)
- [95_skill_package_minimal](../examples/95_skill_package_minimal/prompts/SKILL.prompt)
- [100_skill_package_bundled_agents](../examples/100_skill_package_bundled_agents/prompts/SKILL.prompt)
- [SKILL_PACKAGE_AUTHORING.md](SKILL_PACKAGE_AUTHORING.md)

### Keep the prompt tree modular

Split by family, contract, shared role-home, and outputs.
Import shared doctrine where it is used.
Keep `emit_flow` entrypoints separate when the family needs a graph view.
Use `import ... as ...` when a module prefix is repeated a lot.
Use `from ... import ...` when one declaration is the only thing you need.
Keep `import module` when you still want the module path to stay visible.

Do not do this:
- Do not put every owner, contract, skill, and output into one mega-file.
- Do not make readers reconstruct the family graph from scattered owners if one
  checked flow entrypoint would make it clear.

Best anchors:
- [03_imports](../examples/03_imports/prompts/AGENTS.prompt)
- [75_cross_root_standard_library_imports](../examples/75_cross_root_standard_library_imports/flow_alpha/prompts/AGENTS.prompt)
- [73_flow_visualizer_showcase](../examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt)

## Common Upgrades

When you port older Doctrine or prose-heavy agent systems, these upgrades pay
off fast.

### Upgrade old prose review protocols to `review`

Old shape:
- workflow prose
- manual verdict fields
- manual review routing

Better shape:
- `review`
- typed `fields`
- compiler-owned verdict and route truth

Use:
- [13_critic_protocol](../examples/13_critic_protocol/prompts/AGENTS.prompt)
  as the old proof
- [43_review_basic_verdict_and_route_coupling](../examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt)
  as the minimal upgrade
- [49_review_capstone](../examples/49_review_capstone/prompts/AGENTS.prompt)
  as the real target

### Upgrade embedded route-only law to `route_only`

Old shape:
- route-only branches mixed into general workflow law

Better shape:
- dedicated `route_only`
- honest `current none`
- guarded route-aware outputs

Use:
- [30_law_route_only_turns](../examples/30_law_route_only_turns/prompts/AGENTS.prompt)
- [70_route_only_declaration](../examples/70_route_only_declaration/prompts/AGENTS.prompt)

### Upgrade manual route fields to shared `route.*`

Old shape:
- output fields that restate next owner and route summary by hand

Better shape:
- compiler-owned `route.*`
- guarded output reads
- `route_from` when one typed selector chooses the route
- `final_output.contract.json` as the runtime route contract when a harness
  needs to dispatch the next turn

Use:
- [87_workflow_route_output_binding](../examples/87_workflow_route_output_binding/prompts/AGENTS.prompt)
- [91_handoff_routing_route_output_binding](../examples/91_handoff_routing_route_output_binding/prompts/AGENTS.prompt)
- [119_route_only_final_output_contract](../examples/119_route_only_final_output_contract/prompts/AGENTS.prompt)
- [92_route_from_basic](../examples/92_route_from_basic/prompts/AGENTS.prompt)
- [94_route_choice_guard_narrowing](../examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt)

### Upgrade one overloaded comment into comment plus `final_output:`

Old shape:
- one giant comment that must be both durable record and control answer

Better shape:
- durable `comment_output`
- separate `final_output:` only when the host really needs it

Use:
- [82_review_final_output_prose_basic](../examples/82_review_final_output_prose_basic/prompts/AGENTS.prompt)
- [84_review_split_final_output_prose](../examples/84_review_split_final_output_prose/prompts/AGENTS.prompt)
- [85_review_split_final_output_output_schema](../examples/85_review_split_final_output_output_schema/prompts/AGENTS.prompt)
- [106_review_split_final_output_output_schema_partial](../examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt)

### Upgrade repeated local blocks to shared blocks

Old shape:
- each role restates the same skills, inputs, outputs, and note structure

Better shape:
- shared `skills`
- shared `inputs`
- shared `outputs`
- shared readable bodies and inherited blocks

Use:
- [21_first_class_skills_blocks](../examples/21_first_class_skills_blocks/prompts/AGENTS.prompt)
- [22_skills_block_inheritance](../examples/22_skills_block_inheritance/prompts/AGENTS.prompt)
- [23_first_class_io_blocks](../examples/23_first_class_io_blocks/prompts/AGENTS.prompt)
- [24_io_block_inheritance](../examples/24_io_block_inheritance/prompts/AGENTS.prompt)
- [60_shared_readable_bodies](../examples/60_shared_readable_bodies/prompts/AGENTS.prompt)

## Source Smell To Doctrine Move

Use this section when the old system feels wrong but you have not yet named the
replacement.

### The old critic flow is all prose and route text

Doctrine move:
- `review`
- then `review_family` if the scaffold repeats

Use:
- [13_critic_protocol](../examples/13_critic_protocol/prompts/AGENTS.prompt)
- [43_review_basic_verdict_and_route_coupling](../examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt)
- [49_review_capstone](../examples/49_review_capstone/prompts/AGENTS.prompt)

### The host tells the agent too much route and state truth

Doctrine move:
- `route_only` for honest control-only turns
- `route_from` for typed route selection
- `trust_surface` carriers for current truth

Use:
- [31_currentness_and_trust_surface](../examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt)
- [70_route_only_declaration](../examples/70_route_only_declaration/prompts/AGENTS.prompt)
- [92_route_from_basic](../examples/92_route_from_basic/prompts/AGENTS.prompt)

### The handoff says only `see file`

Doctrine move:
- real readback on the output contract
- trusted fields on `trust_surface`
- guarded sections when route or verdict changes what must be shown

Use:
- [39_guarded_output_sections](../examples/39_guarded_output_sections/prompts/AGENTS.prompt)
- [46_review_current_truth_and_trust_surface](../examples/46_review_current_truth_and_trust_surface/prompts/AGENTS.prompt)
- [88_review_route_semantics_shared_binding](../examples/88_review_route_semantics_shared_binding/prompts/AGENTS.prompt)

### Many outputs repeat the same delivery glue

Doctrine move:
- put the reusable capability in `skill`
- bind that skill once on `output target` with `delivery_skill:`
- keep each `output` focused on target, shape, structure, and requirement

Use:
- [118_output_target_delivery_skill_binding](../examples/118_output_target_delivery_skill_binding/prompts/AGENTS.prompt)

### One giant comment must be both record and host control answer

Doctrine move:
- keep `comment_output` durable
- add `final_output:` only when the host truly needs a second ending surface

Use:
- [104_review_final_output_output_schema_blocked_control_ready](../examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt)
- [105_review_split_final_output_output_schema_control_ready](../examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt)
- [106_review_split_final_output_output_schema_partial](../examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt)

## Best Example Sets

If you want the fastest path through the corpus, start here.

- Reuse and role homes:
  [12](../examples/12_role_home_composition/prompts/AGENTS.prompt),
  [21](../examples/21_first_class_skills_blocks/prompts/AGENTS.prompt),
  [23](../examples/23_first_class_io_blocks/prompts/AGENTS.prompt),
  [24](../examples/24_io_block_inheritance/prompts/AGENTS.prompt),
  [75](../examples/75_cross_root_standard_library_imports/flow_alpha/prompts/AGENTS.prompt)
- Producer truth and workflow law:
  [31](../examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt),
  [33](../examples/33_scope_and_exact_preservation/prompts/AGENTS.prompt),
  [36](../examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt),
  [38](../examples/38_metadata_polish_capstone/prompts/AGENTS.prompt),
  [72](../examples/72_schema_group_invalidation/prompts/AGENTS.prompt)
- Review:
  [43](../examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt),
  [57](../examples/57_schema_review_contracts/prompts/AGENTS.prompt),
  [46](../examples/46_review_current_truth_and_trust_surface/prompts/AGENTS.prompt),
  [49](../examples/49_review_capstone/prompts/AGENTS.prompt),
  [68](../examples/68_review_family_shared_scaffold/prompts/AGENTS.prompt),
  [69](../examples/69_case_selected_review_family/prompts/AGENTS.prompt)
- Route truth:
  [70](../examples/70_route_only_declaration/prompts/AGENTS.prompt),
  [71](../examples/71_grounding_declaration/prompts/AGENTS.prompt),
  [87](../examples/87_workflow_route_output_binding/prompts/AGENTS.prompt),
  [91](../examples/91_handoff_routing_route_output_binding/prompts/AGENTS.prompt),
  [92](../examples/92_route_from_basic/prompts/AGENTS.prompt),
  [94](../examples/94_route_choice_guard_narrowing/prompts/AGENTS.prompt),
  [119](../examples/119_route_only_final_output_contract/prompts/AGENTS.prompt)
- Output contracts and final answers:
  [56](../examples/56_document_structure_attachments/prompts/AGENTS.prompt),
  [57](../examples/57_schema_review_contracts/prompts/AGENTS.prompt),
  [63](../examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt),
  [64](../examples/64_render_profiles_and_properties/prompts/AGENTS.prompt),
  [79](../examples/79_final_output_output_schema/prompts/AGENTS.prompt),
  [104](../examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt),
  [105](../examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt),
  [106](../examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt)
- Skill packages:
  [95](../examples/95_skill_package_minimal/prompts/SKILL.prompt)
  through
  [100](../examples/100_skill_package_bundled_agents/prompts/SKILL.prompt)

## Core Spine

If you want one short path through the guide, read these first:

- [12_role_home_composition](../examples/12_role_home_composition/prompts/AGENTS.prompt):
  shared role-home and real repo composition
- [38_metadata_polish_capstone](../examples/38_metadata_polish_capstone/prompts/AGENTS.prompt):
  full producer-turn law
- [49_review_capstone](../examples/49_review_capstone/prompts/AGENTS.prompt):
  full review semantics
- [69_case_selected_review_family](../examples/69_case_selected_review_family/prompts/AGENTS.prompt):
  reusable review scaffold at repo scale
- [70_route_only_declaration](../examples/70_route_only_declaration/prompts/AGENTS.prompt):
  honest control-only turn
- [91_handoff_routing_route_output_binding](../examples/91_handoff_routing_route_output_binding/prompts/AGENTS.prompt):
  route truth on ordinary outputs
- [55_owner_aware_schema_attachments](../examples/55_owner_aware_schema_attachments/prompts/AGENTS.prompt):
  schema ownership boundary
- [79_final_output_output_schema](../examples/79_final_output_output_schema/prompts/AGENTS.prompt):
  structured final answer
- [105_review_split_final_output_output_schema_control_ready](../examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt):
  durable review plus control-ready final JSON
- [119_route_only_final_output_contract](../examples/119_route_only_final_output_contract/prompts/AGENTS.prompt):
  emitted route contract metadata for a route-only final response
- [99_skill_package_plugin_metadata](../examples/99_skill_package_plugin_metadata/prompts/SKILL.prompt):
  when Doctrine is emitting a real package tree

## Where To Go Next

- Use [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md) when you already know the
  right surface and need the exact rules.
- Use [WORKFLOW_LAW.md](WORKFLOW_LAW.md) when the turn is a producer with real
  compiler-owned truth.
- Use [REVIEW_SPEC.md](REVIEW_SPEC.md) when the turn is a real review.
- Use [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md) when the question is
  about outputs, trust, schemas, structures, or `final_output:`.
- Use [SKILL_PACKAGE_AUTHORING.md](SKILL_PACKAGE_AUTHORING.md) when the job is
  to emit a real `SKILL.prompt` package tree.
- Use [../examples/README.md](../examples/README.md) when you want the full
  proof ladder in teaching order.
