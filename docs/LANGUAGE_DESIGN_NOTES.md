# Language Design Notes

This document records Doctrine's durable language choices and guardrails.

For the shipped syntax and feature overview, use
[LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md). For the numbered proof corpus,
use [../examples/README.md](../examples/README.md).

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

## Shipped Boundaries

Doctrine's current shipped surface runs through the numbered corpus up to
`examples/53_review_bound_carrier_roots`.

That shipped surface includes:

- agent and workflow composition
- typed inputs, outputs, skills, and enums
- readable refs, addressable paths, and interpolation
- workflow law on `workflow`
- first-class `review`
- concrete-turn bindings and bound roots for law and review carriers

## Current Non-Goals

The language intentionally does not ship:

- a packet primitive
- a shadow trust channel separate from `output` plus `trust_surface`
- implicit merge by omission for inherited structure
- a second capability surface parallel to `skill`
- arbitrary free-prose parsing as semantics

When a new feature earns its place, the expected path is:

1. Add the language and compiler support in `doctrine/`.
2. Prove it in a focused example with manifest-backed verification.
3. Document it in the live docs set.
