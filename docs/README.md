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
- [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md): the best starting point for
  the shipped declaration model, composition rules, refs, interpolation, and
  Markdown emission, including `skill package`
- [SKILL_PACKAGE_AUTHORING.md](SKILL_PACKAGE_AUTHORING.md): canonical guide to
  `SKILL.prompt`, source-root package bundles, `emit_skill`, and the package
  example gallery
- [EMIT_GUIDE.md](EMIT_GUIDE.md): configure emit targets, generate runtime
  Markdown, generate skill-package trees, generate workflow flow diagrams, and
  troubleshoot emit failures
- [../examples/README.md](../examples/README.md): the teaching and verification
  corpus, in order

## Feature Guides

- [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md): inputs, outputs,
  bindings, `trust_surface`, guarded output items, and portable truth
- [WORKFLOW_LAW.md](WORKFLOW_LAW.md): workflow law, currentness, scope,
  preservation, invalidation, and route-only turns
- [REVIEW_SPEC.md](REVIEW_SPEC.md): first-class `review`, contracts, verdict
  coupling, carried state, current truth, and inheritance

## Reference

- [COMPILER_ERRORS.md](COMPILER_ERRORS.md): stable parse, compile, and emit
  error codes
- [LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md): design principles,
  guardrails, and current non-goals
- [../CHANGELOG.md](../CHANGELOG.md): public release history and correction
  record
- [../editors/vscode/README.md](../editors/vscode/README.md): repo-local editor
  support for `.prompt` files

## Historical Context

The shipped docs above are the live reference path.
Old plans, worklogs, audits, and draft proposals are not part of that path.
After a restore-point commit, delete them and use git history if you need the
old context.

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
  roots through `[tool.doctrine.compile].additional_prompt_roots`, while
  relative imports stay rooted in the importing module's own `prompts/` tree.
- Emit and verification surfaces reuse shared compile sessions and preserve
  authored ordering even when batch compilation fans out across threads.
- `build_ref/` is verifier-owned checked-in proof, not part of the public
  authoring model.
