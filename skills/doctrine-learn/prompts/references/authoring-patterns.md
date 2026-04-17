# Authoring Patterns

Load this when you have a real authoring job but do not yet know which
Doctrine surface owns it. This file is a task-first chooser, not a second
syntax reference. It maps common jobs to the one surface that should own
them, then cites the shipped example to copy from.

Keep these rules in front of every choice:

- Typed truth beats prose truth. If the compiler can own an exact rule,
  let it.
- Always-on context is a budget. Every line must earn its keep.
- The harness owns runtime. Doctrine owns authoring.
- Fail loud. If you are about to write something the compiler will reject,
  stop and use the error path.

## Task-First Chooser

Each row names one real job, one Doctrine surface, and one shipped example
to copy.

- I need to add a new turn that runs after an existing one.
  Use `workflow` with `handoff_routing`. Add `law:` only when the compiler
  must own currentness, preservation, invalidation, or route truth.
  See `examples/07_handoffs` and
  `examples/91_handoff_routing_route_output_binding`.

- I need a reviewer that blocks the final answer until it passes.
  Use `review` with a review-driven `final_output:`. The reviewer owns the
  verdict and gates. The final output binds review semantics the host
  needs.
  See `examples/104_review_final_output_output_schema_blocked_control_ready`.

- I need a smaller control-ready final JSON that still points at a durable
  review comment.
  Split the final output. Keep `comment_output` durable. Bind only the
  review fields the host needs on the split final output.
  See `examples/105_review_split_final_output_output_schema_control_ready`
  and `examples/106_review_split_final_output_output_schema_partial`.

- I need the final answer to be typed JSON.
  Use `output schema` plus `final_output:`. Do not add `structure:` to a
  structured JSON final output.
  See `examples/79_final_output_output_schema`.

- I need to route the next turn from a typed field in the final JSON.
  Declare one `route field` on the output schema. Bind
  `final_output.route:` to that field. Let Doctrine emit the runtime route
  contract.
  See `examples/120_route_field_final_output_contract`.

- I need a route field that may be null when no handoff happens.
  Use a nullable `route field`. That is how "no handoff on this turn" is
  modeled.
  See `examples/121_nullable_route_field_final_output_contract`.

- I need a route-only turn that has no current artifact.
  Use `route_only` with honest `current none`. Read shared `route.*` on
  guarded outputs. Do not pretend a specialist artifact is current.
  See `examples/70_route_only_declaration` and
  `examples/89_route_only_shared_route_semantics`.

- I need a route-only turn whose final response carries runtime route
  metadata.
  Use `route_only` with `final_output:`. Doctrine emits canonical route
  metadata in `final_output.contract.json`.
  See `examples/119_route_only_final_output_contract`.

- I need the workflow law itself to pick the next owner from a typed
  selector.
  Use `route_from` on workflow law. The selector must resolve to a scalar
  enum-compatible field.
  See `examples/92_route_from_basic`.

- I need shared `route.*` readback on an ordinary workflow output.
  Use `handoff_routing` with route-facing outputs. Read `route.next_owner`,
  `route.label`, and `route.summary` under guards when some branches do
  not route.
  See `examples/87_workflow_route_output_binding` and
  `examples/91_handoff_routing_route_output_binding`.

- I need to teach the runtime my agent's law.
  Write a `workflow` with a `law:` block. Use it for currentness, scope,
  preservation, invalidation, and route truth. See the workflow law guide
  at `docs/WORKFLOW_LAW.md`. Capstone example:
  `examples/38_metadata_polish_capstone`.

- I need a reviewer that reuses one scaffold across many cases.
  Use `review_family`. Pick the case with an enum-backed selector. Keep
  shared gates and comment shape in one scaffold.
  See `examples/68_review_family_shared_scaffold` and
  `examples/69_case_selected_review_family`.

- I need reusable capability I can call from many agents.
  Use `skill`. Keep `purpose` short. Use titleless `bullets` or
  `checklist` inside `use_when`, `provides`, or `does_not` when that field
  is really a list.
  See `examples/11_skills_and_tools` and
  `examples/21_first_class_skills_blocks`.

- I need a reusable package I can ship as a real tree.
  Use `skill package` with `SKILL.prompt`. Bundle agents, references, and
  scripts from the source-root model.
  See `examples/95_skill_package_minimal` and
  `examples/100_skill_package_bundled_agents`.

- I need a package that reads host facts.
  Declare `host_contract:` once on the package. Point the inline skill at
  it with `package:`. Bind the host slots once at the consumer with
  `bind:`. Use `host:` inside the emitted prompt-authored package tree.
  See `examples/124_skill_package_host_binding`.

- I need a package that emits many readable documents.
  Use `skill package` with `emit:` document companions. Mix in bundled
  agent markdown, runtime metadata, and raw helpers when the package tree
  needs them.
  See `examples/122_skill_package_emit_documents` and
  `examples/123_skill_package_emit_documents_mixed_bundle`.

- I need to deliver one output through a reusable channel.
  Bind a delivery skill on the `output target`. Keep the output focused
  on target, shape, structure, and requirement.
  See `examples/118_output_target_delivery_skill_binding`.

- I need a readable markdown document with declared sections.
  Use `document` with `structure:`. Do not attach both `schema:` and
  `structure:` to the same output.
  See `examples/56_document_structure_attachments` and
  `examples/58_readable_document_blocks`.

- I need a typed contract, gate surface, or artifact inventory.
  Use `schema`. Group related artifacts with `artifacts:` and `groups:`.
  See `examples/57_schema_review_contracts` and
  `examples/63_schema_artifacts_and_groups`.

- I need one named table I can reuse across documents.
  Use a top-level `table` declaration. Local document table keys point at
  it without restating rows.
  See `examples/116_first_class_named_tables`.

- I need portable current truth the next owner can trust.
  Put the current artifact on the output and add a small `trust_surface`.
  Only type the fields the next owner must trust mechanically.
  See `examples/31_currentness_and_trust_surface` and
  `examples/46_review_current_truth_and_trust_surface`.

- I need to mark downstream work stale when a step changes it.
  Use `invalidate ... via ...` in workflow law. Keep the invalidation set
  on a trusted carrier field.
  See `examples/36_invalidation_and_rebuild`.

- I need to keep grounding policy explicit.
  Use `grounding`. Say what the source is, what targets it may bind, and
  which evidence is forbidden.
  See `examples/71_grounding_declaration`.

- I need to inherit a whole output and keep most of its parts.
  Use `output[Parent]` inheritance. Use grouped `inherit { ... }` when a
  child keeps several inherited items unchanged.
  See `examples/107_output_inheritance_basic` and
  `examples/108_output_inheritance_attachments`.

- I need to extend an imported reusable output before I bind it.
  Inherit the imported output. Add the local section. Then bind it on
  `outputs`.
  See `examples/109_imported_review_handoff_output_inheritance`.

- I need a workflow to own a readable block directly at the root.
  Put the readable block on the workflow root. You do not need to wrap
  it in a local section.
  See `examples/114_workflow_root_readable_blocks`.

- I need a short bulleted list without a title.
  Use a titleless readable list. Helper kind metadata lines drop when
  the list is detailed.
  See `examples/113_titleless_readable_lists`.

- I need a runtime agent package the harness can load.
  Use the thin build-handle pattern. Emit a package-root `AGENTS.md`, an
  optional sibling `SOUL.md`, and bundled peer files.
  See `examples/115_runtime_agent_packages`.

If none of these rows match your job, load
`references/language-overview.md` and pick the one surface that fits
before writing code.

## Composition Patterns

Doctrine stays small when you compose the right way.

### Named Types Beat Repeated Prose

- Extract a reused output shape into a named `output shape`.
- Extract a reused readable block into a shared body.
- Extract a reused skill into a top-level `skill`.

Do this when the same structure appears in two or more places. One fix
should land once.

### Grouped `inherit { ... }`

- When a child keeps several inherited keyed items unchanged before one
  local override, use grouped `inherit { ... }`.
- Doctrine lowers it to the same explicit inherited accounting it
  already uses for singular `inherit key`.

See `examples/24_io_block_inheritance`.

### `override` For Clear Replacement

- Use `override key: DeclRef` when the child replaces one wrapper with a
  new declaration and adds no local prose.
- Keep the multiline wrapper when the section still needs prose or more
  than one item.

See `examples/25_abstract_agent_io_override`.

### Share Role-Home Law Once

- Put shared read order, turn discipline, handoff discipline, and note
  discipline in one inherited role home.
- Keep each role file about that role's job.

See `examples/12_role_home_composition` and
`examples/37_law_reuse_and_patching`.

### Keep The Prompt Tree Modular

- Split by family, contract, shared role-home, and outputs.
- Use `import ... as ...` when a module prefix repeats a lot.
- Use `from ... import ...` when only one declaration is needed.
- Use `self:path` when the current declaration root is the prefix you
  keep repeating.

See `examples/03_imports` and
`examples/75_cross_root_standard_library_imports`.

## Anti-Patterns

These shapes compile but push against the principles. Fix them early.

### Copy-Paste Across Agents

- Do not restate the same skills, inputs, outputs, or note structure in
  every role.
- Move the shared shape into a top-level `skills`, `inputs`, or
  `outputs` block and inherit it.
- See `examples/21_first_class_skills_blocks` and
  `examples/23_first_class_io_blocks`.

### Prose Where Typed Truth Belongs

- Do not keep currentness, invalidation, verdicts, failing gates, or
  route owner in prose when the compiler can own them.
- Use `law`, `review`, `trust_surface`, and `route.*` instead.

### Harness Leakage

- Doctrine does not own runtime state, memory, scheduling, tools, or
  session control.
- If a rule is really about run state, put it in the harness. Do not
  smuggle it into `law` or output prose.

### Vague Names And Descriptions

- Do not name modules `helper`, `core`, or `misc`.
- Write a short description that says what the module is for, when it
  should load, and what problem it helps solve.
- Names and descriptions help a thin runtime resolver load the right
  module.

### One Giant Root Agent File

- Do not dump every owner, contract, skill, and output into one mega
  file.
- Do not make readers rebuild the family graph from scattered owners if
  one checked flow entrypoint would make it clear.
- Use separate modules and a flow entrypoint when the family needs a
  graph view. See `examples/73_flow_visualizer_showcase`.

### Duplicate Route Truth

- Do not copy `route.next_owner` into a private payload field so the
  harness can read it.
- Do not restate route owner and route summary as manual output fields.
- Read compiler-owned `route.*` instead.
  See `examples/87_workflow_route_output_binding`.

### Overloaded Comments

- One comment carrier should not be both a durable record and the host
  control answer when the host truly wants both.
- Keep `comment_output` durable. Add `final_output:` only when the host
  really needs a separate ending surface.
  See `examples/104_review_final_output_output_schema_blocked_control_ready`.

### Host Facts Pretending To Be Control

- Keep host facts narrow, typed, and local to one choice.
- Do not let host facts turn into a second control plane for review,
  route, or currentness.

## When To Split A File

The AGENTS.md rule: if a functional code file grows past about 500 lines,
split it unless there is a clear reason to keep it whole.

The same spirit applies to prompt modules. Split when:

- One module starts owning two or more families of truth.
- Inheritance becomes harder to read than a new module would be.
- Shared sections could move to a reusable block and drop repetition.
- The family graph is getting hard to follow at a glance.

Keep code files small and single-purpose. Prefer shared helpers and
reusable modules over one huge file that mixes many jobs.

## Plain Language Rule

Shipped bundled Markdown and agent replies must read at about a 7th grade
level.

- Use short sentences.
- Use common words.
- Use direct verbs.
- Split dense instructions into two sentences when that keeps the meaning
  clear.
- Keep Doctrine terms that carry exact meaning. Simplify the sentences
  around them.

Bad: "A downstream owner should be able to read this review alone and
understand the verdict, current artifact, and next owner."

Good: "This review should stand on its own. A downstream owner should
know the verdict, current artifact, and next owner."

## Related References

- `references/principles.md` — the nine principles and the thin-harness
  rule.
- `references/language-overview.md` — the shipped grammar shape and the
  core declaration vocabulary.
- `references/agents-and-workflows.md` — `workflow`, `handoff_routing`,
  and workflow law.
- `references/reviews.md` — `review`, `review_family`, and verdict
  coupling.
- `references/outputs-and-schemas.md` — `output schema`, `route field`,
  and `final_output:`.
- `references/skills-and-packages.md` — `skill`, `skill package`,
  `host_contract:`, and `bind:`.
- `references/examples-ladder.md` — the numbered corpus as a learning
  path.

**Load when:** the author has a real job to port and needs to pick between several plausible Doctrine surfaces.
