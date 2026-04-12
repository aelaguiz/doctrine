# Documentation

Doctrine's live documentation is anchored in the shipped implementation under
`doctrine/` and the manifest-backed example corpus through
`examples/72_schema_group_invalidation`.
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
- [archive/README.md](archive/README.md): historical proposals, plans, and
  worklogs that are not part of the live docs path
- [../editors/vscode/README.md](../editors/vscode/README.md): repo-local editor
  support for `.prompt` files

## Phased Plan Set

These documents organize the second-wave language work into implementation
order. Each phase doc is self-contained, restates the prior-phase baseline it
needs, and groups the work that should be built together.

- [01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md](01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md):
  phase 1 typed-markdown foundation, first-class `document`, the readable block
  family, multiline strings, `structure:`, and the base renderer conversion
- [02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md](02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md):
  phase 2 `analysis`, `schema`, owner-aware `schema:` rules, schema
  artifacts/groups, output contracts, diagnostics, and proof ordering
- [03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md](03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md):
  phase 3 advanced readable-markdown surfaces such as `properties`, explicit
  guard shells, `render_profile`, typed row/item schemas, and later block
  extensions, now proved in `examples/64_*` through `examples/67_*`
- [04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md](04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md):
  phase 4 schema-backed review integration, review families, `route_only`,
  `grounding`, and control-plane convergence, now proved in `examples/68_*`
  through `examples/72_*`

## Historical Design Context

These documents remain in the repo as historical design context. They were the
raw design inputs that were turned into the phased plan set above. Keep them
for provenance and drafting history, not as the primary implementation-order
view or the canonical shipped reference.

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

The phased plan set supersedes the split drafting view as the implementation
sequence. Use the live reference set above plus the numbered examples for
current shipped behavior. Keep the legacy standalone specs only as background
context for how the second-wave design was decomposed.

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
source documentation set. For historical materials that are still worth
keeping in-repo, use [archive/README.md](archive/README.md).
