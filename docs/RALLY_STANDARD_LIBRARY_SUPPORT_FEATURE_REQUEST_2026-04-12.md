---
title: "Doctrine Feature Request - Shared Standard Library Imports Across Prompt Roots"
date: 2026-04-12
status: active
doc_type: feature_request
owners: ["aelaguiz"]
reviewers: []
related:
  - docs/LANGUAGE_REFERENCE.md
---

# Executive Summary

Doctrine already appears to have the semantic surface needed for a downstream
standard library built out of ordinary Doctrine source: imports, reusable
declarations, workflow law, review, route-only behavior, currentness, trusted
carriers, custom I/O declarations, and compiler-owned flow truth.

The remaining blocker is narrower.
Doctrine currently ties import resolution to the nearest `prompts/` tree.
That prevents a downstream repo from keeping flow-local entrypoints in one
authored home while keeping one canonical shared standard library in another.

This request asks only for the missing capability.
It does not ask Doctrine to become the runner, and it does not claim that
lifecycle semantics, review semantics, or machine-readable compiler truth are
missing today.

# Why This Matters

## 1. A real standard library needs one real source home

A downstream system with multiple flows needs one shared standard library that
is authored once, reviewed once, and evolved once.

If shared Doctrine modules can only be imported when they live under the same
local prompt root as each flow entrypoint, the downstream repo is pushed toward
bad compromises:

- copying shared source into each flow
- vendoring generated artifacts instead of authored Doctrine
- distorting repo layout around the current import boundary

Those are all source-ownership problems, not product problems.

## 2. Reuse should stay in Doctrine source form

The value of a standard library is not just that it exists.
The value is that downstream flows depend on the same authored declarations and
reuse them through normal Doctrine semantics.

If the only practical reuse model is copying or generated snapshots, the
downstream system no longer has one standard library.
It has many drifting copies.

## 3. This is a boundary-preserving request

The request is intentionally narrow because the Doctrine boundary is valuable.

Doctrine should remain:

- the authoring language
- the compiler
- the owner of generic source-level reuse

Doctrine should not become:

- the run directory model
- the session manager
- the scheduler
- the CLI runner
- the runtime adapter layer

The need here is not more runtime ownership.
The need is one missing source-composition capability.

# Problem Statement

Doctrine should make it possible for a concrete entrypoint under one authored
`prompts/` tree to depend on reusable `.prompt` modules that live in a separate
shared authored home elsewhere in the same downstream repo.

This is a feature request about what must be possible.
It does not require any specific syntax, packaging scheme, repo convention, or
compiler architecture.

# Existing Doctrine Strength This Builds On

This request is not claiming that Doctrine lacks the semantic model for a
downstream MVP standard library.
The shipped implementation already appears strong on the surfaces that such a
stdlib would use after the import boundary is removed:

- normal imports, declaration refs, composition, and selective inheritance
- workflow law, including `current artifact ... via ...`, `current none`,
  `stop`, and authored routing
- review semantics, including blocked outcomes, carried state, and next-owner
  routing
- route-only and grounding as dedicated declaration families
- custom `input source`, `output target`, and `output shape` declarations
- trusted carriers, guarded output readback, and `standalone_read`
- compiler-owned structured flow extraction and diagnostics

This request exists because those strengths are harder to reuse honestly across
multiple flows when shared Doctrine source cannot live in its own canonical
repo location.

# Requested Outcome

Doctrine should support one canonical shared standard-library location in a
downstream repo even when concrete flow entrypoints live under separate local
prompt trees elsewhere in that repo.

The request is satisfied by capability, not by implementation choice.

# Capability Requirements

## 1. Cross-root shared-module importability

Doctrine must make it possible for a concrete flow entrypoint to import normal
Doctrine modules that are not descendants of that entrypoint's local
`prompts/` root.

What must be possible:

- a downstream repo can keep flow-local entrypoints in one authored home and
  shared standard-library modules in another
- the shared standard library remains ordinary Doctrine source
- imported declarations from that shared location participate in normal
  Doctrine semantics such as refs, composition, inheritance, and compilation
- the model works for a real tree of shared modules, not only for one special
  file
- missing or invalid shared-module references fail loudly and specifically

What must not be required:

- copying shared source into each flow
- vendoring generated Markdown or other emitted artifacts as the reusable truth
- rewriting Doctrine source in a downstream preprocessor before compile
- flattening the downstream repo into one giant prompt tree just to satisfy an
  import limitation

## 2. One canonical authored stdlib location

Doctrine must make it possible for multiple flows to depend on one canonical
shared standard-library location directly.

What must be possible:

- shared declarations are authored once and reused across flows
- changes to shared declarations remain reviewable as source-owned Doctrine
  changes
- flows depending on the same shared module are not forced into copied semantic
  forks
- the downstream runner can treat the shared library as a stable authored
  dependency rather than a generated bundle

What must not be required:

- one repo layout per Doctrine limitation
- per-flow vendoring as the primary reuse model
- a second downstream authoring layer that reinterprets Doctrine before real
  compilation happens

## 3. Fail-closed support detection

A downstream repo must be able to rely on this capability explicitly and fail
closed when the active Doctrine version does not support it.

What must be possible:

- a downstream repo can state that its authored layout depends on this support
- unsupported use fails loudly rather than silently degrading into a different
  import model
- diagnostics distinguish missing capability support from ordinary authoring
  mistakes such as missing modules or invalid refs

What must not happen:

- silent fallback to copying or weaker resolution rules
- partial success that appears valid while changing the meaning of authored
  imports

## 4. Boundary preservation

The request is only satisfied if ownership stays clean.

Doctrine must continue to own:

- source-level authoring semantics
- compilation
- generic import and reuse behavior

The downstream runner must continue to own:

- run directories
- session state
- scheduling and wake behavior
- adapter launch contracts
- CLI commands
- runtime materialization details

This boundary is part of the acceptance criteria, not an afterthought.

# Acceptance Criteria

The request should be considered satisfied only when all of the following are
true:

- a downstream repo can keep flow-local prompt trees and a shared standard
  library as separate authored surfaces
- multiple flows can consume that shared library directly from Doctrine source
  without copying it into each flow
- imported shared modules participate in ordinary Doctrine composition and
  compilation
- missing support or invalid cross-root usage fails loudly and specifically
- the solution does not require Doctrine to become the downstream runner

# Explicit Non-Requirements

This request does not require:

- a specific syntax
- a specific repo layout for all Doctrine users
- a specific packaging mechanism
- a specific emit format
- new lifecycle primitives
- new review primitives
- new machine-readable compiler artifacts beyond what Doctrine already owns
- Rally-specific runtime files, run ledgers, or archive formats

# Why Workarounds Are Not Good Enough

The following are not acceptable substitutes:

- copying shared `.prompt` files into each flow
- vendoring generated artifacts as the reusable source of truth
- reshaping the downstream repo purely to satisfy the current import boundary
- inserting a downstream preprocessor that rewrites author-authored Doctrine
  before compile

Each workaround preserves short-term motion by sacrificing source ownership and
honest reuse.

# Decision Rule

This request is satisfied if a downstream repo can honestly do all of the
following while keeping Doctrine as the authoring language and compiler:

- maintain one real shared standard library in its own canonical repo location
- consume that library from multiple distinct flow entrypoints
- reuse the same authored Doctrine source without copying or vendoring it
- fail closed when the active Doctrine version does not support that layout

If any of those still requires copied source, generated snapshots, repo-shape
distortion, or a hidden preprocessing layer, the request is not yet satisfied.
