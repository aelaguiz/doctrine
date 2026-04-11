# Documentation

Doctrine's live documentation is anchored in the shipped implementation under
`doctrine/` and the manifest-backed example corpus through
`examples/53_review_bound_carrier_roots`.

## Start Here

- [WHY_DOCTRINE.md](WHY_DOCTRINE.md): why the project exists and why the
  runtime stays Markdown
- [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md): the best starting point for
  the shipped declaration model, composition rules, refs, interpolation, and
  Markdown emission
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

## Repo Truth

- Shipped language truth lives in `doctrine/`.
- The example corpus is proof, not just illustration.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.

## Not Part Of The Live Docs Path

Dated proposals, plans, worklogs, and exploratory notes are intentionally
excluded from this index. They are not part of Doctrine's evergreen open
source documentation set.
