---
title: "Doctrine - First-Class Skill Package Authoring - Architecture Plan"
date: 2026-04-13
status: draft
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/EMIT_GUIDE.md
  - examples/11_skills_and_tools/prompts/AGENTS.prompt
  - example_agents/README.md
  - example_agents/markdown_agents.md
---

# TL;DR

Outcome

Doctrine gains first-class authoring, validation, and emission for real skill
packages, not just inline `skill` / `skills` semantics inside an `AGENTS.prompt`
program. A Doctrine-authored skill must be able to ship as a real package with
its `SKILL.md` and required companion surfaces, without manual post-processing
or raw-markdown escape hatches.

Problem

The shipped language already models reusable skill objects and agent-side skill
relationships, but the real skill ecosystems in `~/.agents/skills`,
`~/.codex/skills`, plugin bundles, and `example_agents/harvested/` depend on a
package layer Doctrine does not currently own: frontmatter metadata, sidecar
references, optional scripts, runtime-specific companion config, bundled
subagents, and exact relative-path layout rules.

Approach

Add a first-class skill-package layer above the current `skill` / `skills`
semantic layer. That package layer will own package metadata, companion-file
layout, emitted `SKILL.md`, path-preserving sidecars, package-aware validation,
and example-backed proof for the representative package shapes found in the
local and harvested corpora.

Plan

Ground the full corpus and current Doctrine owner paths, design one canonical
package model and emit contract, audit every required compiler/emitter/docs
touchpoint, then implement broad support through language, validation,
emission, examples, and docs before running the relevant verification surfaces.

Non-negotiables

- No second-class "import raw markdown and hope" path.
- No parallel skill authoring surface that splits truth between Doctrine and
  hand-authored package files.
- No lossy metadata dropping, sidecar flattening, or path normalization.
- Preserve existing inline `skill` / `skills` semantics and emitted `AGENTS.md`
  behavior.
- Prefer structure-preserving first-class support over converter scripts,
  packaging shims, or compatibility theater.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: not started
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine becomes the first-class source of truth for skill packages, then it
must be able to author and emit representative real-world skill package shapes
from the local and harvested corpora with no manual edits after emission, while
preserving existing inline skill semantics and keeping package validation
fail-loud.

## 0.2 In scope

- First-class language support for skill-package authoring, not only inline
  skill semantics inside agent programs.
- Package metadata support for the recurring frontmatter and runtime fields seen
  in the local corpora, including `name`, `description`, nested metadata, tool
  gates, versioning, and other required package-level fields.
- Package layout support for the recurring companion surfaces already present in
  the corpus: `SKILL.md`, `references/`, `scripts/`, `agents/openai.yaml`, and
  skill-adjacent bundled agent surfaces when they are part of a real skill
  package contract.
- Emission and validation rules that preserve exact relative paths, filenames,
  directory spelling, and file casing.
- Broad architectural convergence across the canonical Doctrine owner paths:
  grammar, parser, model, resolver, validator, compiler/display, emit surfaces,
  docs, and numbered examples.
- Proof via a representative example matrix drawn from the package shapes in
  `~/.agents/skills`, `~/.codex/skills`, plugin-contributed skills, and
  `example_agents/harvested/`.

## 0.3 Out of scope

- Shipping a lossy converter, markdown blob import, or compatibility shim as a
  substitute for first-class package authoring.
- Inventing a second public authoring surface for skills outside Doctrine.
- General repo-wide support for every markdown instruction family
  (`AGENTS.md`, `CLAUDE.md`, etc.) unless that support is required to faithfully
  package a real skill bundle already in scope.
- Narrowing this effort to a tiny subset of simple `SKILL.md` files and calling
  that "full support."

## 0.4 Definition of done (acceptance evidence)

- Doctrine can author and emit a representative package matrix that covers at
  least the observed major shapes: bare `SKILL.md`, `SKILL.md` plus
  `references/`, `SKILL.md` plus `references/` plus `scripts/`, `SKILL.md` plus
  runtime-specific companion config, and a skill package that bundles its own
  agent-side companion surfaces.
- The emitted package layout preserves required metadata, relative links,
  filename spelling, and case with no manual post-emit repair.
- Existing shipped inline `skill` / `skills` examples still compile and emit
  correctly.
- Public docs and manifest-backed proof make skill-package authoring part of the
  canonical Doctrine story rather than a side note.
- Relevant verification surfaces run green for the changed layers, or the plan
  records precisely why a specific proof surface did not need to change.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks or runtime shims.
- No dual source of truth between Doctrine source and emitted skill package
  files.
- No manual post-processing step required to make emitted skill packages usable.
- No path spelling or casing drift.
- No silent metadata loss.
- No degradation of the current inline `skill` / `skills` language contract.
- Fail loud when a package shape is unsupported or authored inconsistently.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Full-fidelity package authoring over partial or approximate support.
2. One canonical package model that can represent the real observed skill
   shapes without splitting truth across ad hoc files.
3. Preserve existing inline `skill` / `skills` semantics and current
   `AGENTS.md` emission behavior.
4. Exact path and metadata preservation with fail-loud validation.
5. Keep the public story example-first and generic even when grounded in messy
   real-world sources.

## 1.2 Constraints

- The scope is intentionally large and cross-cutting.
- The shipped truth still lives in `doctrine/` and the manifest-backed numbered
  corpus, so the feature must converge onto those owner paths instead of
  creating a sidecar packaging subsystem.
- Real skill packages vary by runtime and packaging convention; the design
  cannot collapse to only the easiest Codex-style happy path.
- Many skill packages rely on relative cross-file references and companion
  surfaces, so exact path preservation matters.
- Public examples and docs must stay generic rather than importing product
  names, internal skill slugs, or repo-specific jargon from harvested sources.

## 1.3 Architectural principles (rules we will enforce)

- Package semantics are first-class Doctrine, not opaque markdown passthrough.
- Reuse and extend the current `skill` / `skills` semantic core instead of
  replacing it with a second concept.
- Emission owns package layout from one canonical source of truth.
- Validation protects shipped behavior and package integrity, not repo-shape
  cosmetics.
- If a package needs runtime-specific companion metadata, model that honestly
  and fail loud when the author omits required pieces.
- Preserve operational structure and relative references exactly enough that a
  Doctrine-authored package can stand in for the real shipped skill.

## 1.4 Known tradeoffs (explicit)

- First-class package support will increase language and emit complexity, but it
  buys correctness and removes the need for brittle packaging shims.
- A generalized package model risks becoming too abstract; the design must stay
  grounded in the observed corpus rather than inventing speculative ecosystem
  layers.
- Some runtime-specific package metadata will likely require typed extension
  points instead of one flat universal field map.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Doctrine already models `skill` declarations and agent-side `skills`
  relationships as first-class language constructs.
- The shipped examples prove inline skill semantics, inherited skill blocks, and
  shared readable bodies.
- The emit pipeline already produces runtime Markdown and companion contracts for
  agent entrypoints.
- The repo already curates a skill-heavy harvested bank explicitly to pressure
  Doctrine with real-world markdown-native skill patterns.

## 2.2 What’s broken / missing (concrete)

- Doctrine does not yet have a first-class package layer for real skill
  authoring.
- There is no canonical way to author package metadata, sidecar layout, or
  runtime-specific companion files as Doctrine source.
- There is no package-aware validator that can protect path preservation,
  metadata completeness, required companions, or structure-preserving transfer.
- The current public docs can reasonably be read as "Doctrine supports skills,"
  but the shipped support stops at inline skill content inside agent programs.

## 2.3 Constraints implied by the problem

- The fix must touch language, model, validation, emit surfaces, docs, and
  examples together.
- The package model must represent the real observed shapes well enough that the
  feature is clearly first-class rather than best-effort.
- Any implementation must preserve current shipped skill semantics while adding
  the package layer above them.

# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

The harvested bank already contains the strongest markdown-native skill-package
pressure we have locally. `research` should formalize adopt/reject reasoning for
the strongest sources rather than rediscovering them ad hoc.

## 3.2 Internal ground truth (code as spec)

- Current inline skill semantics live in
  `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
  `doctrine/model.py`, `doctrine/_compiler/resolve.py`,
  `doctrine/_compiler/validate.py`, `doctrine/_compiler/compile.py`, and
  `doctrine/_compiler/display.py`.
- Current runtime Markdown emission lives in `doctrine/emit_docs.py`,
  `doctrine/emit_contract.py`, and the docs/examples that prove them.
- Real package pressure is already present in the repo bank under
  `example_agents/harvested/` and in the local skill corpora outside the repo.

## 3.3 Decision gaps that must be resolved before implementation

- What the canonical package declaration surface should be, and how it composes
  with the existing `skill` / `skills` semantic layer.
- Which package metadata fields should be first-class typed declarations versus
  a typed extension surface.
- How emitted package layout should integrate with the current emit target
  registry and output conventions.
- How plugin-specific companion metadata and bundled subagent surfaces should be
  represented without polluting the core language with speculative platform
  branches.

# 4) Current Architecture (as-is)

## 4.1 On-disk structure

Current skill support is spread across the grammar, parser/model, compiler
resolution/validation/compile/display, emit surfaces, live docs, and numbered
examples. The real-world pressure corpus lives separately under
`example_agents/harvested/`.

## 4.2 Control paths (runtime)

Today the main control path is `AGENTS.prompt` authoring to parse -> resolve ->
validate -> compile -> emit runtime Markdown plus companion contract artifacts.
Skills participate as declarations inside that agent-oriented pipeline.

## 4.3 Object model + key abstractions

Doctrine already has first-class objects for `skill`, `skills`, skill entries,
inheritance, and resolved skill bodies. It does not yet have a corresponding
first-class package abstraction that owns `SKILL.md` package layout.

## 4.4 Observability + failure behavior today

The shipped compiler is fail-loud for current language and emit failures. There
is no equivalent package-layer diagnostic surface yet for skill-package-specific
authoring errors.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.

# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

To be hardened in `deep-dive`. Current expectation: Doctrine source will own one
first-class skill-package model that emits the actual package tree, including
`SKILL.md` and required companions.

## 5.2 Control paths (future)

To be hardened in `deep-dive`. Current expectation: package-oriented authoring
will flow through the same parse -> resolve -> validate -> compile -> emit
pipeline, with a package-aware emit surface layered alongside the current agent
emit story rather than outside it.

## 5.3 Object model + abstractions (future)

To be hardened in `deep-dive`. Current expectation: existing inline skill
semantics remain the reusable semantic core, while a new package layer owns
package metadata, companion surfaces, and emitted layout.

## 5.4 Invariants and boundaries

To be hardened in `deep-dive`. The target architecture must keep one source of
truth, fail loud on unsupported package shapes, preserve exact paths, and avoid
parallel authoring paths.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.

# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | `skill_decl`, `skills_decl`, top-level declarations | Supports inline skill semantics only | Add first-class package authoring syntax | Package authoring is not currently expressible | TBD in `deep-dive` | New parser/compiler proof plus preserved existing corpus |
| Parser / model | `doctrine/parser.py`, `doctrine/model.py` | skill-related AST/model nodes | Builds inline skill AST only | Add package-level AST/model surfaces | Package metadata and companions need typed ownership | TBD in `deep-dive` | Unit and manifest-backed proof |
| Resolver / validator | `doctrine/_compiler/resolve.py`, `doctrine/_compiler/validate.py` | skill resolution and diagnostics | Resolves inline skill content only | Add package-aware resolution and fail-loud validation | Need integrity checks for metadata, layout, and companions | TBD in `deep-dive` | Diagnostics plus example proof |
| Compiler / display / emit | `doctrine/_compiler/compile.py`, `doctrine/_compiler/display.py`, `doctrine/emit_docs.py`, `doctrine/emit_contract.py` | current Markdown emission path | Emits agent-oriented runtime docs | Emit real skill package layout and companion surfaces | Doctrine must author shipped packages, not just prose fragments | TBD in `deep-dive` | Emit verification for representative packages |
| Docs / examples | `docs/`, `examples/`, `example_agents/` | public language story and proof corpus | Skills documented as inline semantic layer | Add canonical package story and proof matrix | Public docs must match shipped capability | TBD in `phase-plan` | Relevant corpus verification |

## 6.2 Migration notes

- Canonical owner path is not yet resolved; `research` and `deep-dive` must
  identify the smallest coherent package-owning boundary in `doctrine/`.
- Likely required cleanup includes any public wording that implies full skill
  support while only describing inline skill semantics.
- Behavior-preservation evidence must explicitly cover the current inline
  `skill` / `skills` story.

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

This section will be authored by `phase-plan` after `research` and `deep-dive`.
The expected foundational slices are:

- corpus-grounded package model
- language / AST / validation support
- emit layout and companion-surface support
- examples, docs, diagnostics, and verification convergence

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest existing signal. Default to
1-3 checks total per meaningful phase. Keep manual verification for finalization
unless a specific package shape has no credible programmatic proof.

## 8.1 Unit tests (contracts)

- Parser/model/validator coverage for new package declarations, metadata, and
  fail-loud diagnostics.
- Small compiler/display tests where package lowering introduces new contracts.

## 8.2 Integration tests (flows)

- Manifest-backed example matrix covering the representative skill-package
  shapes.
- Emit-level proof that the generated package layout preserves required files,
  metadata, and relative references without post-processing.
- Preservation checks that keep existing inline `skill` / `skills` examples
  green.

## 8.3 E2E / device tests (realistic)

Not device work. Realistic end-to-end proof here means running the package emit
path and verifying the emitted tree against representative reference packages
without adding brittle repo-policing gates.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Roll out example-first. The public story should move from "inline skill support"
to "full skill-package authoring" only once the representative package matrix is
shipped and verified.

## 9.2 Telemetry changes

No product telemetry is assumed yet. The likely operational signal is improved
package-specific diagnostics and clearer emit failures, not runtime telemetry.

## 9.3 Operational runbook

- Update the live docs index and language reference when the feature is real.
- Ensure the relevant repo verification commands cover the new package proof
  surfaces.
- Keep `example_agents/` as pressure material, but promote the durable truth
  into the numbered corpus and live docs.

# 10) Decision Log (append-only)

## 2026-04-13 - Treat skill packages as first-class Doctrine output

Context

The requested change is broad: Doctrine should elegantly and fully support
authoring the real skills in the local corpora and harvested bank, not just
inline skill prose inside agent programs.

Options

- Keep the current inline `skill` / `skills` support and improve docs only.
- Add a converter or shim that packages raw markdown after the fact.
- Extend Doctrine with first-class skill-package authoring that owns metadata,
  layout, validation, and emitted files.

Decision

Plan around first-class skill-package authoring as the canonical target.
Prose-only improvements and post-processing shims are explicitly insufficient
for this request.

Consequences

- The scope necessarily touches grammar, model, validation, emit surfaces, docs,
  and examples.
- The plan must stay grounded in real package shapes from the local and
  harvested corpora.
- Existing inline `skill` / `skills` semantics become a preserved compatibility
  constraint, not a substitute for the package layer.

Follow-ups

- Run `research` against the observed skill corpus and current Doctrine owner
  paths.
- Resolve the canonical package declaration and emit contract in `deep-dive`.
- Build the authoritative phase plan only after those decisions are explicit.
