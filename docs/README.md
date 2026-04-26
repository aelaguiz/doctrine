# Documentation

This page is Doctrine's live docs index.
Use `doctrine/` plus the manifest-backed example corpus as the shipped truth.
Use [VERSIONING.md](VERSIONING.md) for release rules, [../CHANGELOG.md](../CHANGELOG.md)
for the public release record, and [../CONTRIBUTING.md](../CONTRIBUTING.md)
for repo setup and proof commands.

## Start Here

- [VERSIONING.md](VERSIONING.md): the canonical versioning guide, release
  rules, and breaking-change policy
- [../CHANGELOG.md](../CHANGELOG.md): the portable public release history
- [../CONTRIBUTING.md](../CONTRIBUTING.md): repo setup, proof commands, and
  contributor workflow
- [WHY_DOCTRINE.md](WHY_DOCTRINE.md): why the project exists and why the
  runtime stays Markdown
- [../PRINCIPLES.md](../PRINCIPLES.md): authoring principles for thin
  context, loadable modules, and clean harness boundaries
- [THIN_HARNESS_FAT_SKILLS.md](THIN_HARNESS_FAT_SKILLS.md): Doctrine's durable
  read of the thin-harness, fat-skills rule and how to use it in reviews
- [AUTHORING_PATTERNS.md](AUTHORING_PATTERNS.md): the task-first guide for
  choosing the right Doctrine surface when you are porting or authoring real
  agent systems
- [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md): the shipped syntax and
  declaration reference for composition rules, refs, `output schema`,
  `route field`, `final_output.route:`, target-owned `delivery_skill:`,
  runtime packages, top-level `output[...]` inheritance, markdown emission,
  and `skill package`
- [SKILL_PACKAGE_AUTHORING.md](SKILL_PACKAGE_AUTHORING.md): canonical guide to
  `SKILL.prompt`, explicit `emit:` document companions, source-root package
  bundles, `SKILL.source.json`, package-scoped graph targets, `emit_skill`,
  and the package example gallery
- [EMIT_GUIDE.md](EMIT_GUIDE.md): configure emit targets, generate runtime
  Markdown, emit structured-output schema files, emit final-output, review,
  and route metadata, generate runtime-package and skill-package trees, emit
  checked graph bundles, verify skill and graph source receipts, generate
  workflow flow diagrams, and troubleshoot emit failures
- [../examples/README.md](../examples/README.md): the teaching and verification
  corpus, in order

## Feature Guides

- [AGENT_LINTER.md](AGENT_LINTER.md): install and use the bundled Doctrine
  Agent Linter skill for prompt, package, flow, and repo-slice audits
- [DOCTRINE_LEARN.md](DOCTRINE_LEARN.md): install and use the bundled
  Doctrine Learn skill to teach an agent end-to-end Doctrine authoring —
  principles, language, packaging, emit, and verification
- [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md): inputs, outputs,
  bindings, target-owned delivery skills, `final_output:`,
  `final_output.route:`, generated schema files, emitted route metadata,
  `trust_surface`, guarded output items, and portable truth
- [WORKFLOW_LAW.md](WORKFLOW_LAW.md): workflow law, currentness, scope,
  preservation, invalidation, and route-only turns
- [REVIEW_SPEC.md](REVIEW_SPEC.md): first-class `review`, contracts, verdict
  coupling, carried state, current truth, and inheritance

## Reference

- [COMPILER_ERRORS.md](COMPILER_ERRORS.md): stable parse, compile, and emit
  error codes
- [FAIL_LOUD_GAPS.md](FAIL_LOUD_GAPS.md): easy author mistakes the compiler
  still accepts today and should turn into clear compile errors
- [WARNINGS.md](WARNINGS.md): evergreen plan for a first-class compiler
  warning layer, including goals, non-goals, candidate families, and
  guardrails
- [LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md): design principles,
  guardrails, and current non-goals
- [LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md](LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md):
  use-case audit for first-class skill graph support
- [SKILL_GRAPH_LANGUAGE_SPEC.md](SKILL_GRAPH_LANGUAGE_SPEC.md):
  proposed Doctrine language support for typed skill graphs
- [EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md](EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md):
  active epic that decomposes the skill graph spec into shipped sub-plans
- [ARCH_RECEIPT_CORE_PACKAGE_BRIDGE_2026-04-26.md](ARCH_RECEIPT_CORE_PACKAGE_BRIDGE_2026-04-26.md):
  shipped sub-plan 1 — top-level `receipt` declarations, inheritance, and
  the `host_contract: receipt key: ReceiptRef` bridge
- [ARCH_STAGE_CORE_ROUTED_RECEIPTS_2026-04-26.md](ARCH_STAGE_CORE_ROUTED_RECEIPTS_2026-04-26.md):
  shipped sub-plan 2 — top-level `stage` declarations, skeletal
  `skill_flow` registration, and receipt route fields targeting `stage`,
  `flow`, and the closed `human`/`external`/`terminal` sentinel set
- [ARCH_SKILL_FLOW_CORE_2026-04-26.md](ARCH_SKILL_FLOW_CORE_2026-04-26.md):
  shipped sub-plan 3 — full top-level `skill_flow` body with `start:`,
  `approve:`, `edge`, `route:`, `kind:`, `when:`, `repeat`, `variation`,
  `unsafe`, and `changed_workflow:`, plus local DAG and route-binding
  checks. Graph closure across flows, graph policies, and graph emit stay
  in later sub-plans
- [ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26.md](ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26.md):
  shipped sub-plan 4 — top-level `skill_graph`, graph closure, graph JSON
  and Markdown emit, graph source receipts, `emit_skill_graph`, and
  `verify_skill_graph`
- [../CHANGELOG.md](../CHANGELOG.md): public release history and correction
  record
- [../editors/vscode/README.md](../editors/vscode/README.md): repo-local editor
  support for `.prompt` files

## Historical Context

The shipped docs above are the live reference path.
Dated plans, worklogs, audits, and draft proposals are not part of that path.
Some may stay in the repo while active work is still in flight. Once one is no
longer active, delete it after a restore-point commit and use git history if
you need the old context.

## Repo Truth

- Shipped language truth lives in `doctrine/`.
- The example corpus is proof, not just illustration.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- The shared emit registry drives configured agent-doc, skill-package, and
  flow builds, and `emit_flow` also supports direct quick-start entrypoints on
  the same prompts-root-aware pipeline.
- `AGENTS.prompt` and `SOUL.prompt` stay the agent-runtime entrypoints.
  `SKILL.prompt` is the skill-package entrypoint.
- Absolute imports may also span explicitly configured shared `prompts/`
  roots through `[tool.doctrine.compile].additional_prompt_roots`.
- Same-flow imports are retired. Sibling `.prompt` files already share one
  flat namespace under their flow root, so only real cross-flow boundaries use
  `import`.
- Inside `SKILL.prompt` packages, prompt files may also import from the local
  package source root. If a local module path collides with a repo-wide one,
  Doctrine fails loud.
- Emit and verification surfaces reuse shared compile sessions and preserve
  authored ordering even when batch compilation fans out across threads.
- `build_ref/` is verifier-owned checked-in proof, not part of the public
  authoring model.
