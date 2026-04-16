# Language Design Notes

This document records Doctrine's durable language choices and guardrails.

For the shipped syntax and feature overview, use
[LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md). For the numbered proof corpus,
use [../examples/README.md](../examples/README.md).
For release and compatibility policy, use [VERSIONING.md](VERSIONING.md).

## Core Principles

- Runtime compatibility matters. Doctrine keeps the runtime artifact as
  Markdown because existing coding-agent tools can already consume it.
- The structured `.prompt` source is the real maintenance surface.
- The language grows example-first. A feature is not really shipped until it
  lands in `doctrine/` and in the manifest-backed corpus.
- Reuse should happen through named declarations and explicit patching, not
  through hidden merge rules.
- Compiler-owned semantics are better than prose conventions for currentness,
  routing, preservation, and review state.
- Fail loud is the default. Doctrine prefers explicit diagnostics over silent
  fallback.

## Authoring Biases

- Prefer explicit typed declarations over magic strings.
- Prefer stable keys plus authored titles over implicit heading generation.
- Prefer first-class `skill` declarations over ad hoc script prose.
- Prefer small, focused examples that introduce one new idea at a time.
- Keep public docs and examples generic rather than importing product-specific
  jargon from other repos.

## Named Table Design

First-class `table` declarations follow Doctrine's normal named-type pattern.
The declaration owns the reusable table contract. The document use site owns
the local key and local rows. This is why the syntax is
`table release_gates: ReleaseGates`, not a generic `ref:` field or a path to a
table hidden inside another document. The compiler lowers named table use back
to the ordinary document table path, so rendering and inheritance stay the
same.

## Shipped Boundaries

Doctrine's current shipped surface is proven across the numbered corpus listed
in [../examples/README.md](../examples/README.md).
Keep the exact example boundary there so these design notes stay durable as
the corpus grows.

That shipped surface includes:

- agent and workflow composition
- typed inputs, outputs, skills, schemas, documents, render profiles, and
  enums
- readable refs, addressable paths, and interpolation
- workflow law, `handoff_routing`, `route_only`, and `grounding`
- first-class `review`, `review_family`, and review-driven `final_output`
- structured `final_output:` contracts through `output schema`, plus generated
  schema artifacts for `JsonObject` final answers
- concrete-turn bindings and bound roots for law and review carriers
- `analysis`, `decision`, owner-aware `schema:` / `structure:`, readable
  `document` blocks, first-class named `table` declarations, first-class
  schema artifacts/groups, multiline code blocks, schema-backed review
  contracts, and shared route semantics such as `route_from`
- title-bearing concrete-agent heads plus enum-member key/title/wire identity
  projections
- authored `render_profile`, compact `properties`, explicit readable guard
  shells, profile-sensitive semantic lowering targets, typed `item_schema:` /
  `row_schema:`, and explicit late readable extensions such as raw
  `markdown`, `html`, `footnotes`, `image`, and structured nested table cells
- first-class `skill package` authoring through `SKILL.prompt`

## Current Non-Goals

The language intentionally does not ship:

- a packet primitive
- a shadow trust channel separate from `output` plus `trust_surface`
- implicit merge by omission for inherited structure
- a second capability surface parallel to `skill`
- arbitrary free-prose parsing as semantics
- a generic readable-block `ref:` system

When a new feature earns its place, the expected path is:

1. Add the language and compiler support in `doctrine/`.
2. Prove it in a focused example with manifest-backed verification.
3. Document it in the live docs set.
