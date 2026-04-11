# Documentation

Doctrine's live documentation is anchored in the shipped implementation under
`doctrine/` and the manifest-backed example corpus through
`examples/57_schema_review_contracts`.
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
  bindings, `trust_surface`, guarded output sections, and portable truth
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

## Second-Wave Specs

These documents record the design rationale behind the shipped second-wave
language work. They remain useful architecture references, but evergreen truth
still lives in `doctrine/` and the manifest-backed examples.

- [ANALYSIS_AND_SCHEMA_SPEC.md](ANALYSIS_AND_SCHEMA_SPEC.md): first-class
  `analysis`, first-class `schema`, grammar, model, diagnostics, and example
  ladders
- [READABLE_MARKDOWN_SPEC.md](READABLE_MARKDOWN_SPEC.md): first-class
  `document`, readable block kinds, typed markdown rendering, and contract
  formatting rules
- [INTEGRATION_SURFACES_SPEC.md](INTEGRATION_SURFACES_SPEC.md): how the new
  surfaces fit with workflow law, review, outputs, `trust_surface`, current
  truth, and route/preservation semantics
- [LANGUAGE_MECHANICS_SPEC.md](LANGUAGE_MECHANICS_SPEC.md): inheritance,
  addressability, name resolution, diagnostics, compiler touchpoints, and
  acceptance-corpus planning
- [SECOND_WAVE_LANGUAGE_NOTES.md](SECOND_WAVE_LANGUAGE_NOTES.md): broader
  design space, deferred ideas, and explicit non-first-wave language surfaces

This split spec set supersedes `docs/big_pile_of_shit.md` as the durable
reference for the feature wave. That monolith remains useful as historical
design context, but it is intentionally not part of the evergreen docs path.

## Repo Truth

- Shipped language truth lives in `doctrine/`.
- The example corpus is proof, not just illustration.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- The shared emit registry now drives both compiled Markdown trees and
  target-scoped workflow data-flow artifacts.
- Emit and verification surfaces reuse shared compile sessions and preserve
  authored ordering even when batch compilation fans out across threads.

## Not Part Of The Live Docs Path

Dated proposals, plans, worklogs, and exploratory notes are intentionally
excluded from this index. They are not part of Doctrine's evergreen open
source documentation set. That includes exploratory monolith notes such as
`docs/big_pile_of_shit.md`.
