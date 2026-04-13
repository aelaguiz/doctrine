# Documentation

Doctrine's live documentation is anchored in the shipped implementation under
`doctrine/` and the manifest-backed example corpus through
`examples/90_split_handoff_and_final_output_shared_route_semantics`.
The shipped compiler stays fail-loud and deterministic while scaling to larger
prompt graphs through shared compile sessions and safe default batch
parallelism.

## Start Here

- [WHY_DOCTRINE.md](WHY_DOCTRINE.md): why the project exists and why the
  runtime stays Markdown
- [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md): the best starting point for
  the shipped declaration model, composition rules, refs, interpolation, and
  Markdown emission
- [EMIT_GUIDE.md](EMIT_GUIDE.md): configure emit targets, generate runtime
  Markdown, generate workflow flow diagrams, and troubleshoot emit failures
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
- [../editors/vscode/README.md](../editors/vscode/README.md): repo-local editor
  support for `.prompt` files

## Historical Design Context

The shipped docs above are the only live reference path. Earlier plans,
worklogs, audits, and one-off investigations are deleted after a restore-point
commit. If you need that old context, use git history.

The earlier second-wave draft specs, phase plans, and the implemented
`final_output` design proposal were deleted after restore-point commits once
their durable truth landed in the live docs and verified example corpus. Use
git history if you need that design-phase context.

## Repo Truth

- Shipped language truth lives in `doctrine/`.
- The example corpus is proof, not just illustration.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- The shared emit registry drives configured Markdown and flow builds, and
  `emit_flow` also supports direct quick-start entrypoints on the same
  prompts-root-aware pipeline.
- Absolute imports may also span explicitly configured shared `prompts/`
  roots through `[tool.doctrine.compile].additional_prompt_roots`, while
  relative imports stay rooted in the importing module's own `prompts/` tree.
- Emit and verification surfaces reuse shared compile sessions and preserve
  authored ordering even when batch compilation fans out across threads.

## Not Part Of The Live Docs Path

Dated proposals, plans, worklogs, and exploratory notes are intentionally
excluded from this index. They are not part of Doctrine's evergreen open
source documentation set. After a restore-point commit, delete them. Git
history is the archive.
