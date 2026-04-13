---
title: "Doctrine - First-Class Skill Package Authoring - Architecture Plan"
date: 2026-04-13
status: complete
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
or raw-markdown escape hatches. The solution must feel like a natural Doctrine
surface, not a bolted-on packaging mode that makes existing authored doctrine
or downstream consumers worse.

Problem

The shipped language already models reusable skill objects and agent-side skill
relationships, but the real skill ecosystems in `~/.agents/skills`,
`~/.codex/skills`, plugin bundles, and `example_agents/harvested/` depend on a
package layer Doctrine does not currently own: frontmatter metadata, sidecar
references, optional scripts, runtime-specific companion config, bundled
subagents, and exact relative-path layout rules.

Approach

Add a first-class skill-package layer above the current `skill` / `skills`
semantic layer. That package layer will own package metadata, the package
source root around `SKILL.prompt`, emitted `SKILL.md`, exact-path copy-through
for bundled source files, package-aware validation, and example-backed proof
for the representative package shapes found in the local and harvested
corpora. Keep the design additive and compatibility-safe: existing inline skill
authoring, current docs doctrine, and current `AGENTS.md`-oriented consumers
must not pick up new mandatory burdens just to preserve today's behavior.

Plan

Ground the full corpus and current Doctrine owner paths, design one canonical
package model and emit contract, audit every required compiler/emitter/docs
touchpoint, then implement broad support through language, validation,
emission, examples, and docs before running the relevant verification surfaces.
The shipped result should teach skill authoring well, with rich Doctrine-native
examples clearly inspired by the crosslinked real skills rather than a minimal
compliance slice.

Non-negotiables

- No second-class "import raw markdown and hope" path.
- No parallel skill authoring surface that splits truth between Doctrine and
  hand-authored package files.
- No lossy metadata dropping, sidecar flattening, or path normalization.
- No privileged compiler concept of `build_ref/`; that remains verifier-only
  example convention, not package architecture.
- Preserve existing inline `skill` / `skills` semantics and emitted `AGENTS.md`
  behavior.
- Do not introduce new mandatory constraints, config, or authoring boilerplate
  for downstream consumers who only rely on the current shipped doctrine.
- Treat docs and examples as first-class deliverables, not post-implementation
  cleanup.
- Prefer structure-preserving first-class support over converter scripts,
  packaging shims, or compatibility theater.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-13
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None. Fresh audit verified the approved Phase 4 docs/example obligations now
  ship in the current worktree:
  `docs/SKILL_PACKAGE_AUTHORING.md:1`,
  `docs/README.md:17`,
  `docs/LANGUAGE_REFERENCE.md:31`,
  `docs/EMIT_GUIDE.md:8`,
  `examples/README.md:28`,
  `examples/README.md:76`,
  and the final proof surfaces all passed:
  `make verify-examples`, `make verify-diagnostics`, and
  `cd editors/vscode && make`.

## Reopened phases (false-complete fixes)
- None. Fresh audit found no execution-side narrowing of the approved
  requirements, scope, acceptance criteria, or phase obligations to hide
  unfinished work.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-13
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-13
recommended_flow: deep dive -> external research grounding when needed -> deep dive again -> phase plan -> consistency pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions. External research remained optional for the first shipped slice because internal grounding plus both deep-dive passes resolved the architecture cleanly enough for phase planning.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine becomes the first-class source of truth for skill packages, then it
must be able to author and emit representative real-world skill package shapes
from the local and harvested corpora with no manual edits after emission, while
preserving existing inline skill semantics, not imposing new compatibility
costs on current downstream consumers, and keeping package validation fail-loud.
The resulting authoring surface should be elegant enough that it looks like the
obvious Doctrine-native way to write these skills.

## 0.2 In scope

- First-class language support for skill-package authoring, not only inline
  skill semantics inside agent programs.
- Package metadata support for the recurring frontmatter and runtime fields seen
  in the local corpora, including `name`, `description`, nested metadata, tool
  gates, versioning, and other required package-level fields.
- Package layout support for source-root bundle/copy semantics: files authored
  alongside `SKILL.prompt` in the package source tree emit under the same
  relative paths. Observed layouts such as `references/`, `reference/`,
  `scripts/`, `assets/`, `agents/openai.yaml`, plugin manifests, and
  skill-adjacent bundled agent surfaces matter as examples and proof cases, not
  as privileged compiler-owned directory families.
- Emission and validation rules that preserve exact relative paths, filenames,
  directory spelling, and file casing.
- Compatibility-preserving integration with existing shipped doctrine:
  current inline `skill` / `skills` authoring, current `AGENTS.md` emit
  behavior, and current downstream consumers remain valid without opting into
  the new package surface.
- Broad architectural convergence across the canonical Doctrine owner paths:
  grammar, parser, model, resolver, validator, compiler/display, emit surfaces,
  docs, and numbered examples.
- Proof via a representative example matrix drawn from the package shapes in
  `~/.agents/skills`, `~/.codex/skills`, plugin-contributed skills, and
  `example_agents/harvested/`.
- Explicit support for the representative skill families already visible in the
  corpus:
  - bare single-file skills such as [adapt](</Users/aelaguiz/.agents/skills/adapt/SKILL.md>),
    [arrange](</Users/aelaguiz/.agents/skills/arrange/SKILL.md>), and
    [polish](</Users/aelaguiz/.agents/skills/polish/SKILL.md>)
  - reference-heavy workflow skills such as
    [arch-step](</Users/aelaguiz/.agents/skills/arch-step/SKILL.md>),
    [project-flow](</Users/aelaguiz/.agents/skills/project-flow/SKILL.md>),
    [mobile-sim](</Users/aelaguiz/.agents/skills/mobile-sim/SKILL.md>), and
    [together-chat-completions](</Users/aelaguiz/.agents/skills/together-chat-completions/SKILL.md>)
  - script-backed skills with paired language entrypoints such as
    [together-chat-completions](</Users/aelaguiz/.agents/skills/together-chat-completions/SKILL.md>)
    and the Figma family under
    [~/.codex/skills](</Users/aelaguiz/.codex/skills>)
  - runtime-flagged skills such as
    [figma-create-new-file](</Users/aelaguiz/.codex/skills/figma-create-new-file/SKILL.md>)
    with `disable-model-invocation`
  - plugin-contributed skills with split metadata such as the GitHub plugin
    [plugin.json](</Users/aelaguiz/.codex/plugins/cache/openai-curated/github/fb0a18376bcd9f2604047fbe7459ec5aed70c64b/.codex-plugin/plugin.json>)
    plus
    [skills/github/agents/openai.yaml](</Users/aelaguiz/.codex/plugins/cache/openai-curated/github/fb0a18376bcd9f2604047fbe7459ec5aed70c64b/skills/github/agents/openai.yaml>)
  - orchestrator skills that bundle parallel subagents such as
    [legal-review](../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md)
    plus its companion agent files
  - reference-compendium and table-heavy domain skills such as
    [FHIR developer](../example_agents/harvested/openclaw-medical-skills/raw/skills/fhir-developer-skill/SKILL.md)
    and
    [search strategy](../example_agents/harvested/openclaw-medical-skills/raw/skills/search-strategy/SKILL.md)
- Exact preservation of the conventions these packages rely on today:
  frontmatter variants, `references/` and `reference/`, optional `scripts/`,
  optional `assets/`, optional `agents/openai.yaml`, plugin root manifests,
  install/update guidance, quick-routing sections, section-heavy rulebooks,
  cross-file relative links, and filename casing such as
  [REFERENCE.md](</Users/aelaguiz/.agents/skills/mobile-sim/references/REFERENCE.md>).
- A documentation and examples package that makes skill authoring a first-class
  public Doctrine story:
  - a canonical authoring guide for skill packages
  - language-reference coverage for the new package surface
  - emit-guide updates for package emission
  - a broad numbered example matrix with Doctrine-native skills clearly
    inspired by the crosslinked real packages while remaining generic

## 0.3 Out of scope

- Shipping a lossy converter, markdown blob import, or compatibility shim as a
  substitute for first-class package authoring.
- Inventing a second public authoring surface for skills outside Doctrine.
- General repo-wide support for every markdown instruction family
  (`AGENTS.md`, `CLAUDE.md`, etc.) unless that support is required to faithfully
  package a real skill bundle already in scope.
- Narrowing this effort to a tiny subset of simple `SKILL.md` files and calling
  that "full support."
- Shipping package support without the docs and examples needed to teach it
  cleanly.

## 0.4 Definition of done (acceptance evidence)

- Doctrine can author and emit a representative package matrix that covers at
  least the observed major shapes: bare `SKILL.md`, `SKILL.md` plus bundled
  relative files, common layouts such as `references/`, `reference/`,
  `scripts/`, `assets/`, runtime-specific companion config, plugin-style split
  metadata roots, a skill package that bundles its own agent-side companion
  surfaces, and path/case-preservation edge cases.
- The emitted package layout preserves required metadata, relative links,
  filename spelling, and case with no manual post-emit repair.
- Existing shipped inline `skill` / `skills` examples still compile and emit
  correctly.
- Existing downstream consumers who stay on the current inline skill and
  `AGENTS.md` path do not need new declarations, new config, or compatibility
  shims to preserve current behavior.
- Public docs and manifest-backed proof make skill-package authoring part of the
  canonical Doctrine story rather than a side note.
- The shipped docs include a high-quality authoring guide and an example set
  large enough to teach the surface through realistic patterns, not just one
  toy happy path.
- The examples are clearly grounded in the crosslinked real skills, but
  distilled into generic Doctrine-native surfaces suitable for shipped truth.
- Relevant verification surfaces run green for the changed layers, or the plan
  records precisely why a specific proof surface did not need to change.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks or runtime shims.
- No dual source of truth between Doctrine source and emitted skill package
  files.
- No manual post-processing step required to make emitted skill packages usable.
- No path spelling or casing drift.
- No silent metadata loss.
- No hard-coded package-family whitelist for ordinary bundled files.
- No degradation of the current inline `skill` / `skills` language contract.
- No new mandatory authoring requirements for consumers who do not opt into
  skill-package authoring.
- Fail loud when a package shape is unsupported or authored inconsistently.

## 0.6 Docs And Examples North Stars

The feature is not complete when the compiler can technically emit packages. It
is complete when Doctrine has a clear, elegant public teaching story for skill
authoring.

North-star public artifacts:

- One canonical "author a real skill package" guide that starts from a minimal
  single-file skill and walks through companion files, metadata, package
  layout, and emit flow until the reader can ship a realistic package.
- One canonical language-reference surface for the package declarations and
  semantics, so authors do not have to reverse-engineer the feature from
  examples.
- One canonical emit story for package output layout, companion files,
  target/config behavior, and path-preservation guarantees.
- One broad numbered example gallery that teaches the main real-world package
  shapes through Doctrine-native examples rather than product-specific clones.
- One explicit grounding map that says which crosslinked real skill family each
  shipped example is distilling and what pattern it is meant to teach.
- One compatibility story that clearly tells existing Doctrine users when to
  stay on inline `skill` / `skills`, when to reach for package authoring, and
  what does not change for current `AGENTS.md` consumers.

North-star example families:

- minimal single-file package
- reference-heavy workflow/rulebook package
- script-backed package
- runtime-flagged package with companion metadata
- plugin-contributed package with split metadata roots
- bundled-subagent orchestrator package
- compendium-style domain package
- path/case preservation edge-case package

North-star quality bar:

- Every example should teach one main idea while still looking like a plausible
  real skill package.
- The examples should be recognizably inspired by the linked real skills, but
  generalized into generic Doctrine truth.
- The docs should make the elegant path obvious and the compatibility story
  boringly clear.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. An elegant, coherent, Doctrine-native package authoring surface over
   piecemeal or visibly bolted-on extensions.
2. Full-fidelity package authoring over partial or approximate support.
3. One canonical package model that can represent the real observed skill
   shapes without splitting truth across ad hoc files.
4. Preserve existing inline `skill` / `skills` semantics, current `AGENTS.md`
   emission behavior, and downstream consumer expectations unless they
   explicitly opt into the new package surface.
5. Exact path and metadata preservation with fail-loud validation.
6. Keep the public story example-first, well-documented, and generic even when
   grounded in messy real-world sources.

## 1.2 Constraints

- The scope is intentionally large and cross-cutting.
- The shipped truth still lives in `doctrine/` and the manifest-backed numbered
  corpus, so the feature must converge onto those owner paths instead of
  creating a sidecar packaging subsystem.
- The design should be additive: existing authoring and emitted surfaces should
  not become harder to use or more constrained merely because package authoring
  exists.
- Real skill packages vary by runtime and packaging convention; the design
  cannot collapse to only the easiest Codex-style happy path.
- Many skill packages rely on relative cross-file references and companion
  surfaces, so exact path preservation matters.
- Public examples and docs must stay generic rather than importing product
  names, internal skill slugs, or repo-specific jargon from harvested sources.
- The observed local corpora are already broad:
  - `~/.agents/skills` currently includes 64 packages spanning bare
    `SKILL.md`, `SKILL.md` plus `references/`, `SKILL.md` plus
    `references/` plus `scripts/`, scripts-only, agents-only, and path/case
    outliers.
  - `~/.codex/skills` adds system skills, the Figma family, optional assets,
    runtime flags, and `agents/openai.yaml`.
  - `~/.codex/plugins` adds plugin-root manifests plus package-local skill
    metadata layers.
  - `example_agents/harvested/` adds pressure from compact skills,
    compendium-style skills, bundled subagents, machine-readable taskflow files,
    multi-file prompt families, and skill registries.
- The plan must distinguish shipped proof from pressure material:
  manifest-backed numbered examples are proof, while the harvested bank and
  local skill corpora are grounding inputs and pressure tests.

## 1.3 Architectural principles (rules we will enforce)

- Package semantics are first-class Doctrine, not opaque markdown passthrough.
- Prefer one beautiful first-class surface over multiple special-case authoring
  escapes.
- Reuse and extend the current `skill` / `skills` semantic core instead of
  replacing it with a second concept.
- Emission owns package layout from one canonical source of truth.
- New package support is additive and opt-in for current consumers.
- Validation protects shipped behavior and package integrity, not repo-shape
  cosmetics.
- If a package needs runtime-specific companion metadata, model that honestly
  and fail loud when the author omits required pieces.
- Preserve operational structure and relative references exactly enough that a
  Doctrine-authored package can stand in for the real shipped skill.
- Prefer a bundle-first package filesystem model: ordinary companion files live
  in the package source tree and are copied through by exact relative path
  unless Doctrine explicitly owns their compilation semantics.
- Docs and examples are part of the feature surface, not commentary about it.

## 1.4 Known tradeoffs (explicit)

- First-class package support will increase language and emit complexity, but it
  buys correctness and removes the need for brittle packaging shims.
- A generalized package model risks becoming too abstract; the design must stay
  grounded in the observed corpus rather than inventing speculative ecosystem
  layers.
- Some runtime-specific package metadata will likely require typed extension
  points instead of one flat universal field map.
- A strong elegance bar may force narrower core abstractions plus explicit
  extension points rather than a single giant package declaration that tries to
  model everything directly.

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
- The current shipped "skills are supported" story is grounded in
  [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md),
  [examples/11_skills_and_tools/cases.toml](../examples/11_skills_and_tools/cases.toml),
  [examples/21_first_class_skills_blocks/cases.toml](../examples/21_first_class_skills_blocks/cases.toml),
  [examples/22_skills_block_inheritance/cases.toml](../examples/22_skills_block_inheritance/cases.toml),
  and
  [examples/60_shared_readable_bodies/cases.toml](../examples/60_shared_readable_bodies/cases.toml).
  That shipped truth covers inline skill declarations, reusable skills blocks,
  inheritance, and readable skill-entry bodies inside agent-oriented programs.
- The current emit story is grounded in [EMIT_GUIDE.md](EMIT_GUIDE.md),
  [examples/README.md](../examples/README.md), and the flow-emit proof under
  [examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.d2](../examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.d2)
  and
  [examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.svg](../examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.svg).
  That is currently an agent-entrypoint emit story, not a skill-package story.

## 2.2 What’s broken / missing (concrete)

- Doctrine does not yet have a first-class package layer for real skill
  authoring.
- There is no canonical way to author package metadata, sidecar layout, or
  runtime-specific companion files as Doctrine source.
- There is no package-aware validator that can protect path preservation,
  metadata completeness, required companions, or structure-preserving transfer.
- The current public docs can reasonably be read as "Doctrine supports skills,"
  but the shipped support stops at inline skill content inside agent programs.
- The current language and emit owner paths
  ([doctrine/grammars/doctrine.lark](../doctrine/grammars/doctrine.lark),
  [doctrine/parser.py](../doctrine/parser.py),
  [doctrine/model.py](../doctrine/model.py),
  [doctrine/emit_common.py](../doctrine/emit_common.py))
  do not yet expose a canonical package abstraction that emits a `SKILL.md`
  package tree with companions.
- Real package conventions that are not yet first-class include:
  - package-level frontmatter beyond inline skill metadata, such as
    `metadata.short-description`, `license`, `compatibility`, `version`,
    `keywords`, `measurable_outcome`, `allowed-tools`, and `metadata.author`
  - runtime flags such as `disable-model-invocation`
    ([figma-create-new-file](</Users/aelaguiz/.codex/skills/figma-create-new-file/SKILL.md>))
  - package-local agent metadata such as `interface.display_name`,
    `default_prompt`, `policy.allow_implicit_invocation`, and
    `dependencies.tools` inside `agents/openai.yaml`
  - plugin-root manifests such as
    [plugin.json](</Users/aelaguiz/.codex/plugins/cache/openai-curated/github/fb0a18376bcd9f2604047fbe7459ec5aed70c64b/.codex-plugin/plugin.json>)
    and
    [.app.json](</Users/aelaguiz/.codex/plugins/cache/openai-curated/github/fb0a18376bcd9f2604047fbe7459ec5aed70c64b/.app.json>)
  - companion layouts such as `references/`, `reference/`, `scripts/`,
    `assets/`, and path/case quirks such as
    [REFERENCE.md](</Users/aelaguiz/.agents/skills/mobile-sim/references/REFERENCE.md>)
  - orchestrator packaging where one skill ships with bundled role files, such
    as
    [legal-review](../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md)
    plus
    [legal-risks](../example_agents/harvested/ai-legal-claude/raw/agents/legal-risks.md)
    and
    [legal-compliance](../example_agents/harvested/ai-legal-claude/raw/agents/legal-compliance.md)
  - section and workflow conventions such as `When to use`, `When not to use`,
    `Non-negotiables`, `Workflow`, `Quick Routing`, `High-Signal Rules`,
    `Resource Map`, `Official Docs`, `Install`, `Skill Arguments`,
    `First move`, and `Output expectations`

## 2.3 Constraints implied by the problem

- The fix must touch language, model, validation, emit surfaces, docs, and
  examples together.
- The package model must represent the real observed shapes well enough that the
  feature is clearly first-class rather than best-effort.
- Any implementation must preserve current shipped skill semantics while adding
  the package layer above them.
- The docs and example corpus must teach the new surface credibly enough that
  "How do I author a real skill package in Doctrine?" has a clear canonical
  answer.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

The strongest external grounding here is the already-curated harvested bank plus
the linked local skill corpora. Those sources should shape the package model and
the teaching story, but they do not become shipped truth directly.

- Compact single-file skills — adopt as proof that the smallest Doctrine-native
  package path must feel elegant and complete, not second-class; reject
  product-specific naming, branding, or runtime assumptions as shipped
  Doctrine truth.
  - [composition-patterns](../example_agents/harvested/vercel-agent-skills/raw/skills/composition-patterns/SKILL.md),
    [react-view-transitions](../example_agents/harvested/vercel-agent-skills/raw/skills/react-view-transitions/SKILL.md),
    [scientific-brainstorming](../example_agents/harvested/openclaw-medical-skills/raw/skills/scientific-brainstorming/SKILL.md)
- Reference-heavy rulebooks and compendia — adopt as proof that `SKILL.md`
  bodies plus sidecar references must be first-class and example-worthy; reject
  flattening these packages into one markdown blob or a raw import escape hatch.
  - [react-native-skills](../example_agents/harvested/vercel-agent-skills/raw/skills/react-native-skills/SKILL.md),
    [agent-browser](../example_agents/harvested/vercel-agent-browser/raw/skills/agent-browser/SKILL.md),
    [search-strategy](../example_agents/harvested/openclaw-medical-skills/raw/skills/search-strategy/SKILL.md),
    [fhir-developer-skill](../example_agents/harvested/openclaw-medical-skills/raw/skills/fhir-developer-skill/SKILL.md)
- Orchestrator skills with bundled subagents — adopt as proof that some real
  skill packages own companion agent surfaces and orchestration doctrine; reject
  leaking vendor- or source-specific orchestration assumptions into the core
  Doctrine language.
  - [legal-review](../example_agents/harvested/ai-legal-claude/raw/skills/legal-review/SKILL.md),
    [legal-clauses](../example_agents/harvested/ai-legal-claude/raw/agents/legal-clauses.md),
    [legal-risks](../example_agents/harvested/ai-legal-claude/raw/agents/legal-risks.md),
    [legal-compliance](../example_agents/harvested/ai-legal-claude/raw/agents/legal-compliance.md),
    [legal-terms](../example_agents/harvested/ai-legal-claude/raw/agents/legal-terms.md),
    [legal-recommendations](../example_agents/harvested/ai-legal-claude/raw/agents/legal-recommendations.md)
- Machine-readable and code-backed instruction packages — adopt as pressure for
  typed extension points, sidecar preservation, and script-backed package
  shapes; reject making arbitrary raw file families a mandatory first-slice core
  surface before the core `SKILL.md` package model is settled.
  - [CVE-2023-2283.yaml](../example_agents/harvested/seclab-taskflow-agent/raw/examples/taskflows/CVE-2023-2283.yaml),
    [Agent Tools v1.0.json](</Users/aelaguiz/workspace/doctrine/example_agents/harvested/system-prompts-and-models/raw/Cursor Prompts/Agent Tools v1.0.json>),
    [bull_researcher.py](../example_agents/harvested/tradingagents/raw/tradingagents/agents/researchers/bull_researcher.py)
- Multi-file prompt assemblies — adopt as pressure for exact path preservation
  and cross-file layout rules; reject widening first-slice scope to general
  multi-file markdown instruction repos beyond what real in-scope skill
  packages need.
  - [agent-prompt-security-monitor-for-autonomous-agent-actions-first-part.md](../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-security-monitor-for-autonomous-agent-actions-first-part.md),
    [agent-prompt-security-monitor-for-autonomous-agent-actions-second-part.md](../example_agents/harvested/claude-code-system-prompts/raw/system-prompts/agent-prompt-security-monitor-for-autonomous-agent-actions-second-part.md)
- Registry and discovery surfaces — adopt as pressure for public docs,
  discoverability, and example organization; reject making registry authoring or
  skill-directory indexing a prerequisite for first-class skill-package support.
  - [example_agents/harvested/index.md](../example_agents/harvested/index.md),
    [awesome-agent-skills/raw/README.md](../example_agents/harvested/awesome-agent-skills/raw/README.md),
    [patrickjs-awesome-cursorrules/raw/README.md](../example_agents/harvested/patrickjs-awesome-cursorrules/raw/README.md),
    [livekit-agents-js/raw/agents/README.md](../example_agents/harvested/livekit-agents-js/raw/agents/README.md)

The harvested bank remains pressure, not shipped proof. The governing bank
contracts are [example_agents/README.md](../example_agents/README.md),
[example_agents/harvested/README.md](../example_agents/harvested/README.md),
and [example_agents/markdown_agents.md](../example_agents/markdown_agents.md).

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/grammars/doctrine.lark](../doctrine/grammars/doctrine.lark) —
    current top-level declaration surface, including shipped `skill` and
    `skills` grammar.
  - [doctrine/parser.py](../doctrine/parser.py) and
    [doctrine/model.py](../doctrine/model.py) — current AST/model ownership for
    skill declarations and reusable skills blocks.
  - [doctrine/_compiler/resolve.py](../doctrine/_compiler/resolve.py),
    [doctrine/_compiler/validate.py](../doctrine/_compiler/validate.py),
    [doctrine/_compiler/compile.py](../doctrine/_compiler/compile.py), and
    [doctrine/_compiler/display.py](../doctrine/_compiler/display.py) —
    current resolution, validation, lowering, and readable render behavior for
    inline skill semantics.
  - [doctrine/emit_common.py](../doctrine/emit_common.py),
    [doctrine/emit_docs.py](../doctrine/emit_docs.py), and
    [doctrine/emit_contract.py](../doctrine/emit_contract.py) — current emit
    target registry, path layout rules, and compiler-owned emitted companion
    artifacts.
  - [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) and
    [examples/README.md](../examples/README.md) — current manifest-backed proof
    contract and corpus organization.
  - [docs/README.md](README.md),
    [docs/LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md), and
    [docs/EMIT_GUIDE.md](EMIT_GUIDE.md) — the live public documentation path
    that currently tells a skills story limited to inline `skill` / `skills`
    semantics and `AGENTS.prompt` / `SOUL.prompt` emission.
- Canonical owner path / boundary to reuse:
  - the new package surface must stay inside the existing Doctrine owner path
    from grammar -> parser/model -> `_compiler` -> emit, not in a sidecar
    packaging subsystem or a converter script outside `doctrine/`
  - public teaching truth must land in the live docs index and numbered example
    corpus, not only in `example_agents/` or one-off plan prose
- Existing patterns to reuse:
  - [examples/11_skills_and_tools/cases.toml](../examples/11_skills_and_tools/cases.toml),
    [examples/21_first_class_skills_blocks/cases.toml](../examples/21_first_class_skills_blocks/cases.toml),
    [examples/22_skills_block_inheritance/cases.toml](../examples/22_skills_block_inheritance/cases.toml),
    and [examples/60_shared_readable_bodies/cases.toml](../examples/60_shared_readable_bodies/cases.toml)
    — the current inline-skill proof surface that must stay green
  - [pyproject.toml](../pyproject.toml) plus
    [doctrine/emit_common.py](../doctrine/emit_common.py) — existing configured
    emit-target contract, currently limited to `AGENTS.prompt` and
    `SOUL.prompt`, which any package-emission design must either extend or keep
    orthogonal without breaking
  - [pyproject.toml](../pyproject.toml) currently configures shared emit-target
    proof for `example_07_handoffs`, `example_14_handoff_truth`,
    `example_36_invalidation_and_rebuild`,
    `example_73_flow_visualizer_showcase`, and
    `example_79_final_output_json_schema`, which is a useful anchor for how any
    widened package-emission story should coexist with the current emit
    registry
  - [examples/README.md](../examples/README.md) plus
    [doctrine/verify_corpus.py](../doctrine/verify_corpus.py) — the canonical
    example/manifest pattern to reuse for the future skill-package gallery
- Prompt surfaces / instruction-bearing contracts to preserve:
  - the current emitted runtime markdown surface in
    [doctrine/emit_docs.py](../doctrine/emit_docs.py) and
    [doctrine/renderer.py](../doctrine/renderer.py) — package authoring should
    extend Doctrine’s instruction-bearing model, not bypass it through raw
    markdown passthrough
  - the existing inline skill render contract proven by
    [examples/11_skills_and_tools/cases.toml](../examples/11_skills_and_tools/cases.toml)
    — the package layer must preserve this current public behavior for
    downstream users who do not opt in
- Existing grounding / tool / file exposure:
  - the local skill corpora under `~/.agents/skills`, `~/.codex/skills`, and
    `~/.codex/plugins`
  - the curated pressure bank under `example_agents/harvested/`
  - the repo-local docs and numbered examples that already define live truth
- Duplicate or drifting paths relevant to this change:
  - [docs/LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md) currently says Doctrine
    supports skills, but that shipped story is only the inline semantic layer
  - [docs/EMIT_GUIDE.md](EMIT_GUIDE.md) and
    [doctrine/emit_common.py](../doctrine/emit_common.py) currently define an
    emit story centered on `AGENTS.prompt` / `SOUL.prompt`, not real skill
    packages
  - the strongest examples of real package shapes currently live outside the
    numbered corpus, split between local home-directory skill trees and
    `example_agents/harvested/`
- Capability-first opportunities before new tooling:
  - extend the current Doctrine grammar/model/compiler/emit surfaces before
    inventing converter scripts, packaging shims, or repo-policing utilities
  - reuse the existing docs index and numbered example corpus as the teaching
    surface before inventing a parallel docs path
  - preserve existing emit/verify contracts where possible rather than adding a
    second proof harness for package authoring
- Behavior-preservation signals already available:
  - `make verify-examples` — keeps the shipped corpus green, including the
    current inline `skill` / `skills` story
  - targeted manifest runs such as
    `uv run --locked python -m doctrine.verify_corpus --manifest examples/11_skills_and_tools/cases.toml`
    — cheap preservation signal for the current skill surface
  - current emit-target proof via
    [pyproject.toml](../pyproject.toml) and the checked-in `build_ref/` trees —
    preservation signal for existing emit behavior if package emission widens
    the shared emit pipeline
- The current numbered corpus boundary is the live docs index and
  [examples/README.md](../examples/README.md), which run through
  `examples/103_skill_package_binary_assets`; avoid
  older doc text that still names an earlier boundary.
- Observed local package shapes that the architecture must cover include:
  - `~/.agents/skills` with 25 bare `SKILL.md` packages, 17 packages with
    `agents/openai.yaml` plus `references/`, 15 with those plus `scripts/`,
    3 reference-only packages, 2 singular-`reference/` packages, 1
    scripts-only package, and 1 agents-only package
  - path-layout outliers such as
    [critique/reference/personas.md](</Users/aelaguiz/.agents/skills/critique/reference/personas.md>),
    [frontend-design/reference/typography.md](</Users/aelaguiz/.agents/skills/frontend-design/reference/typography.md>),
    and
    [mobile-sim/references/REFERENCE.md](</Users/aelaguiz/.agents/skills/mobile-sim/references/REFERENCE.md>)
  - section conventions that recur heavily in the live corpus:
    `Workflow`, `When to use`, `When not to use`, `Non-negotiables`,
    `Reference map`, `First move`, `Output expectations`, `Quick Routing`,
    `High-Signal Rules`, `Resource Map`, and `Official Docs`
  - script conventions such as paired Python and TypeScript entrypoints in
    [together-chat-completions/scripts/](</Users/aelaguiz/.agents/skills/together-chat-completions/scripts>),
    controller/hook support in
    [arch-step/scripts](</Users/aelaguiz/.agents/skills/arch-step/scripts>),
    and package-local agent metadata in `agents/openai.yaml`
  - plugin-root metadata splits such as
    [plugin.json](</Users/aelaguiz/.codex/plugins/cache/openai-curated/github/fb0a18376bcd9f2604047fbe7459ec5aed70c64b/.codex-plugin/plugin.json>),
    [.app.json](</Users/aelaguiz/.codex/plugins/cache/openai-curated/github/fb0a18376bcd9f2604047fbe7459ec5aed70c64b/.app.json>),
    and
    [skills/github/agents/openai.yaml](</Users/aelaguiz/.codex/plugins/cache/openai-curated/github/fb0a18376bcd9f2604047fbe7459ec5aed70c64b/skills/github/agents/openai.yaml>)

## 3.3 Decision gaps that must be resolved before implementation

No unresolved plan-shaping design blockers remain for the first shipped slice.
Deep-dive pass 2 resolves the architecture as:

- package source entrypoint: `SKILL.prompt`
- package root declaration: top-level `skill package`
- package filesystem boundary:
  - the package source root is the directory that contains `SKILL.prompt`
  - `SKILL.prompt` compiles to `SKILL.md`
  - bundled sibling and descendant files copy through under the same relative
    paths unless Doctrine explicitly owns their compilation semantics
- additive shared emit-target registry: existing targets stay valid, package
  targets join the same registry by entrypoint filename rather than by a new
  required target-kind field
- dedicated package emitter: a sibling surface to `emit_docs`, not a retrofit
  shim inside it
- typed metadata boundary:
  - first-class typed package metadata stays narrow and covers only
    identity/discovery/compatibility fields repeated broadly enough to validate
    (`name`, `description`, `version`, `license`, `keywords`, `compatibility`,
    authors, tool dependencies)
  - instruction-bearing guidance stays in the main `SKILL.md` body, not in
    frontmatter metadata
  - runtime-, plugin-, and platform-specific companion files are bundled
    source-local files by default, not hard-coded package-family declarations
- canonical teaching set:
  - `docs/SKILL_PACKAGE_AUTHORING.md`
  - package-gallery examples `91` through `99`
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

Current skill support is split across these shipped owner paths:

- `doctrine/grammars/doctrine.lark`
  - top-level declarations currently include `skill_decl` and `skills_decl`,
    but no package declaration or companion-file surface
- `doctrine/parser.py` and `doctrine/model.py`
  - current typed ownership is `SkillDecl` plus `SkillsDecl`
  - there is no model type that owns package metadata, sidecar files, or a
    package filesystem tree
- `doctrine/_compiler/indexing.py`
  - indexes `skills_by_name` and `skills_blocks_by_name` alongside the rest of
    the language declarations
  - there is no package registry or package-lowering path
- `doctrine/_compiler/resolve.py`, `doctrine/_compiler/validate.py`,
  `doctrine/_compiler/compile.py`, and `doctrine/_compiler/display.py`
  - resolve inline skill refs and inherited `skills` blocks
  - compile the resolved skill surfaces into ordinary rendered markdown sections
- `doctrine/emit_common.py`, `doctrine/emit_docs.py`, and
  `doctrine/emit_contract.py`
  - own the configured emit-target contract and runtime markdown emission for
    concrete root agents
  - the shared target contract currently supports `AGENTS.prompt` and
    `SOUL.prompt` only
- `doctrine/verify_corpus.py` plus `examples/*/cases.toml`
  - own the manifest-backed proof story
  - package trees are not yet part of the numbered proof corpus
- `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, and
  `examples/README.md`
  - are the live public teaching path
  - today they document inline skills and agent-entrypoint emission, not
    first-class skill-package authoring

Real package pressure exists outside that shipped truth boundary in:

- `~/.agents/skills`
- `~/.codex/skills`
- `~/.codex/plugins`
- `example_agents/harvested/`

Those surfaces pressure the design, but they are not compiler-owned proof today.

## 4.2 Control paths (runtime)

Today the main runtime paths are:

1. Source authoring:
   - `AGENTS.prompt` or `SOUL.prompt` is parsed with `parse_file(...)`
2. Compilation:
   - `CompilationSession` indexes top-level declarations
   - `SkillDecl` and `SkillsDecl` are resolved as part of agent or workflow
     compilation rather than as standalone package roots
3. Rendering:
   - `_compile_skills_field(...)`, `_compile_resolved_skills(...)`, and
     `_compile_resolved_skill_entry(...)` lower skill semantics into ordinary
     markdown sections such as `Purpose`, `Reason`, `Use When`, and other record
     prose
4. Emit:
   - `emit_docs` loads configured targets, compiles concrete root agents, and
     writes `<agent-slug>/AGENTS.md` plus `<agent-slug>/AGENTS.contract.json`
   - the emit contract is agent-oriented; there is no package-tree writer for
     `SKILL.md` plus companion files
5. Verification:
   - `verify_corpus` runs manifest-backed render, compile-fail, and emit checks
     against numbered examples
   - there is no package-emission proof matrix yet

Skills therefore participate today only as declarations inside an
agent-oriented control path. They are not currently a first-class emitted
artifact family.

## 4.3 Object model + key abstractions

The current abstraction split is:

- `SkillDecl`
  - one reusable capability object with a title and record-body metadata
- `SkillsDecl`
  - one reusable block of role-scoped skill relationships, inheritance, and
    section grouping
- `ResolvedSkillEntry`, `ResolvedSkillsBody`, and related compiler internals
  - the resolved semantic layer used during agent/workflow compilation
- `EmitTarget`
  - one configured emit target with `name`, `entrypoint`, `output_dir`, and
    `project_config`
  - currently bound to `AGENTS.prompt` / `SOUL.prompt` entrypoints only

What is missing is a first-class package abstraction that can own all of:

- package identity and frontmatter metadata
- the primary `SKILL.md` instruction body
- bundled filesystem entries and sidecar layout
- exact relative paths and filename casing
- package-specific validation and emit behavior

Right now Doctrine can describe skill semantics, but it cannot own the package
that real skill ecosystems actually ship.

## 4.4 Observability + failure behavior today

The current system is already fail-loud, but only for the existing surfaces:

- parser / compiler diagnostics cover invalid skill declarations, bad
  inheritance, wrong metadata kinds, and unresolved refs
- emit diagnostics in the `E50x` range cover missing targets, missing
  `pyproject.toml`, bad target entrypoints, and emit-path collisions
- `verify_corpus` surfaces manifest mismatches and checked-in ref diffs

There is no equivalent package-layer observability for:

- missing or malformed package metadata
- unsupported companion-file shapes
- path/case preservation failures
- plugin-companion contract mismatches
- package gallery drift between docs, examples, and emitted trees

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

The chosen architectural direction is:

- keep skill-package authoring inside the existing Doctrine owner path:
  grammar -> parser/model -> `_compiler` -> emit
- add one first-class package layer above the current `skill` / `skills`
  semantic core
- keep current `AGENTS.prompt` / `SOUL.prompt` emission intact for existing
  consumers
- add a dedicated package-emission path for real skill-package trees instead of
  forcing package output through the agent-doc emitter
- use `SKILL.prompt` as the package source entrypoint so package authoring stays
  inside the existing `.prompt` toolchain
- use a top-level `skill package` declaration as the concrete package root so
  the new surface is visibly a packaging layer for `skill`, not a second
  unrelated capability system

That future on-disk shape should look like:

- Doctrine source:
  - grammar additions for `SKILL.prompt` package entrypoints plus a top-level
    `skill package` declaration
  - parser/model additions for the package root plus package-source-root bundle
    ownership rooted at the directory that contains `SKILL.prompt`
  - `_compiler` additions for package resolution, validation, and lowering
  - shared emit-target plumbing widened so package targets can coexist with
    current agent targets without altering existing behavior
  - a dedicated package emitter module adjacent to the current emit surfaces,
    with current `emit_docs` and `emit_flow` behavior preserved
- Live docs:
  - `docs/README.md` exposes skill-package authoring as a first-class topic
  - `docs/LANGUAGE_REFERENCE.md` documents the package surface
  - `docs/EMIT_GUIDE.md` documents package emission
  - `docs/SKILL_PACKAGE_AUTHORING.md` teaches realistic package construction
- Numbered corpus:
  - examples `91` through `99` become the initial package gallery
  - current inline skill examples remain and continue proving legacy behavior
- Emitted package tree:
  - one package root emits `SKILL.md`
  - bundled source files emit under exact relative paths from the package
    source root
  - observed layouts such as `references/`, `reference/`, `scripts/`,
    `assets/`, `agents/openai.yaml`, and plugin-root metadata are preserved as
    authored conventions, not privileged compiler-owned roots

## 5.2 Control paths (future)

The future control path should be:

1. Package source authoring enters through a dedicated package-oriented
   Doctrine entrypoint surface named `SKILL.prompt` under the same
   `prompts/`-root-aware project model as the rest of the language.
2. Parsing and indexing register package declarations in the same compiler
   session model as existing declarations.
3. Resolution and validation:
   - the `skill package` root owns the primary skill body directly using the
     same record-body semantics and lowering rules that back `SkillDecl`
   - the compiler internally lowers that primary body through the existing
     semantic core instead of inventing a second capability model
   - validate package metadata completeness, source-root boundaries, reserved
     path collisions, prompt/file conflicts, path spelling, and casing
   - fail loud on unsupported package shapes rather than dropping data,
     rewriting layouts, or normalizing paths
4. Package lowering compiles one package artifact tree rooted at the
   `SKILL.prompt` directory, not just rendered prose.
5. Shared emit-target registry keeps one configured target list in
   `[tool.doctrine.emit.targets]`:
   - `emit_docs` accepts `AGENTS.prompt` and `SOUL.prompt`
   - the new package emitter accepts `SKILL.prompt`
   - `emit_flow` remains agent/workflow-oriented and continues to reject package
     entrypoints
6. A dedicated package emitter writes the package tree to disk by compiling
   recognized prompt-bearing files and copying the remaining bundled source
   files through under the same relative paths.
7. The numbered corpus and emit verification surfaces compare those emitted
   trees against checked-in proof.

The important boundary is that package emission is a sibling to the current
agent-doc emit flow, not a shim layered on top of it and not a replacement for
it.

## 5.3 Object model + abstractions (future)

The future model should keep this split:

- existing `SkillDecl` / `SkillsDecl`
  - remain the semantic core for reusable capability identity and role-scoped
    skill relationships
- new package-root abstraction
  - owns package metadata, primary `SKILL.md` content, the package source root,
    and emitted layout
  - lowers its primary body through the same underlying skill semantics rather
    than replacing them
- new package-bundle abstraction
  - represents bundled source-local filesystem entries relative to the package
    root rather than typed `reference` / `script` / `asset` declarations
  - distinguishes compiler-owned prompt-bearing files from ordinary copied
    files
- new compiled package artifact abstraction
  - owns a deterministic tree of output files with exact relative paths and
    case-sensitive filenames
- typed core metadata surface
  - covers identity/discovery/compatibility fields broad enough to validate
    across runtimes
- bundled extension files
  - carry runtime-specific surfaces such as `disable-model-invocation`
    sidecars, `agents/openai.yaml`, `.codex-plugin/plugin.json`, and
    `.app.json` as ordinary package-local files when Doctrine does not need to
    semantically interpret them
  - keep the first slice honest by typing only what the compiler actually owns
    and validating the rest through source-root and path-preservation rules

This keeps the existing semantic layer alive while making the package layer the
new emitted source of truth for real skill ecosystems.

## 5.4 Invariants and boundaries

The target architecture enforces these boundaries:

- one source of truth:
  - Doctrine source owns the package
  - emitted `SKILL.md` trees are generated artifacts, not parallel authored
    truth
- additive compatibility:
  - existing inline `skill` / `skills` authoring remains valid
  - current `AGENTS.md` emission remains valid
  - downstream users who do not opt into package authoring take on no new
    required config or boilerplate
- no fallback path:
  - no converter scripts
  - no raw markdown import escape hatch
  - no packaging shim that repairs emitted output after the fact
- one explicit source surface:
  - `SKILL.prompt` is the package entrypoint
  - `skill package` is the concrete package root
  - package authoring does not require an additional target kind flag,
    alternate file extension, or second docs taxonomy
- exact structure preservation:
  - preserve path spelling, directory names, casing, and relative links exactly
  - validate unsupported package layouts loudly
- bundle-first filesystem model:
  - ordinary bundled files are sourced from the package directory around
    `SKILL.prompt`, not from privileged companion declarations
  - observed directories such as `references/`, `reference/`, `scripts/`, and
    `assets/` are examples, not compiler-owned root families
- verifier boundary:
  - `examples/*/build_ref` is a corpus-proof convention only
  - it must not appear as a compiler-facing package concept or a public docs
    requirement
- docs/examples are part of the architecture:
  - the public teaching path must ship with the feature
  - the package example gallery is compiler-owned proof, not commentary
- first shipped slice is explicit:
  - `95_skill_package_minimal`
  - `96_skill_package_references`
  - `97_skill_package_scripts`
  - `98_skill_package_runtime_metadata`
  - `99_skill_package_plugin_metadata`
  - `100_skill_package_bundled_agents`
  - `101_skill_package_compendium`
  - `102_skill_package_path_case_preservation`
  - `103_skill_package_binary_assets`
- scoped ambition:
  - support real skill-package shapes first
  - do not widen into general support for every markdown instruction family
    unless required by an in-scope skill package

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | top-level declaration grammar near `skill_decl`, `skills_decl`, and entrypoint expectations | Supports inline skill semantics only; no package root or package-source-root semantics | Add `skill package` grammar while keeping bundled filesystem entries source-rooted instead of introducing hard-coded companion-family syntax | Package authoring is not currently expressible in Doctrine source | `SKILL.prompt` plus top-level `skill package` | Parser/compiler proof for new declarations plus legacy inline-skill preservation |
| Parser / model | `doctrine/parser.py`, `doctrine/model.py` | `SkillDecl`, `SkillsDecl`, declaration union, parser transforms | Builds inline skill AST only | Add package-root AST/model nodes, core package metadata nodes, and package-source-root bundle ownership rooted at the directory that contains `SKILL.prompt` | Package metadata, layout, and emitted tree need typed ownership without typing every copied file family | New package model layer above the existing semantic core | Unit coverage plus manifest-backed proof |
| Indexing | `doctrine/_compiler/indexing.py` | declaration registration and indexed-unit registries | Registers skills and skills blocks, but no package registry | Add package registration and canonical lookup paths | Compiler sessions need package ownership inside the existing pipeline | Indexed package registry owned by the same session model | Compiler/session coverage plus example proof |
| Resolver / validator | `doctrine/_compiler/resolve.py`, `doctrine/_compiler/validate.py` | skill resolution, inheritance, diagnostics | Resolves inline skill content only | Add package-aware resolution and fail-loud validation for metadata, source-root boundaries, reserved path collisions, prompt/file conflicts, and exact path/case preservation | Need integrity checks for real package shapes without inventing directory-family rules | Package validation contracts with exact preservation rules | Diagnostics plus package-matrix proof |
| Compiler / lowering | `doctrine/_compiler/compile.py`, `doctrine/_compiler/display.py` | inline skill lowering to rendered sections | Lowers skills only as agent/workflow markdown sections | Add package lowering to a compiled package artifact tree rooted at the `SKILL.prompt` directory, combining compiler-owned prompt outputs with copied bundled files | Doctrine must compile packages, not just prose fragments | New compiled package artifact contract | Compiler tests plus package emit proof |
| Shared emit target plumbing | `doctrine/emit_common.py`, `doctrine/project_config.py`, `pyproject.toml` contract | Shared emit-target config only understands `AGENTS.prompt` / `SOUL.prompt` | Widen shared target plumbing to recognize `SKILL.prompt` targets without adding a new required target-kind field | Package emission should reuse shared project/target conventions where credible | Additive target contract keyed by supported entrypoint filename | Emit-config tests plus legacy target preservation |
| Package emitter | `doctrine/emit_docs.py`, new `doctrine/emit_skill.py`, `doctrine/emit_contract.py` | `emit_docs` writes agent markdown and contract JSON only | Keep `emit_docs` semantics stable and add `emit_skill` as a sibling emitter for `SKILL.md` trees and companions | Avoid overloading the current agent-doc emitter while still sharing infrastructure | Dedicated package-emission path | Emit verification for representative package trees |
| Emit-flow and diagnostics surfaces | `doctrine/emit_flow.py`, `doctrine/diagnostics.py`, `docs/COMPILER_ERRORS.md`, `doctrine/diagnostic_smoke.py` | Flow and error surfaces assume only `AGENTS.prompt` / `SOUL.prompt` entrypoints | Update diagnostics and smoke coverage so package entrypoints widen shared emit plumbing without silently widening `emit_flow` semantics | Preserve honest user-facing errors and current flow boundaries | `emit_flow` remains agent/workflow-only; shared diagnostics mention `SKILL.prompt` where appropriate | Diagnostic smoke plus docs/error catalog proof |
| Package metadata / plugin manifests | package-local skill metadata plus plugin roots such as `agents/openai.yaml`, `.codex-plugin/plugin.json`, `.app.json` | Not part of the shipped Doctrine package model | Keep typed package metadata narrow and treat runtime/plugin files as bundled package-local source files by default unless Doctrine must semantically interpret them | Real skill ecosystems split metadata across these files today, but most do not need a dedicated language declaration to preserve them | Narrow typed metadata plus source-root bundle preservation | Package-matrix proof for runtime flags, implicit invocation policy, MCP dependencies, icons/assets, and plugin roots |
| Filesystem layout preservation | emitted package trees and relative links | No canonical package-tree emitter today | Add source-root discovery plus path-preserving package emission and validation for bundled files under arbitrary relative paths, including common layouts like `references/`, `reference/`, `scripts/`, `assets/`, bundled agents, and case-sensitive filenames | Real packages depend on exact paths, link targets, and filename spelling | Deterministic package-tree artifact contract | Reference-link proof plus path/case edge cases |
| Verification | `doctrine/verify_corpus.py`, `examples/*/cases.toml`, `examples/*/build_ref` | Verifies agent render/emit flows, not package trees | Extend corpus verification to cover package matrices and emitted package trees while keeping `build_ref` as proof-only convention rather than compiler architecture | Package support needs shipped proof, not plan prose only | Manifest-backed package verification contract | New package manifests plus preservation of current corpus |
| Editor support | `editors/vscode/resolver.js`, `language-configuration.json`, `syntaxes/doctrine.tmLanguage.json`, `scripts/validate_lark_alignment.py`, tests, `editors/vscode/README.md` | Editor support and docs assume the current shipped declaration and entrypoint set | Add `skill package` keyword coverage, `SKILL.prompt` entrypoint expectations, navigation support where applicable, and honest extension docs/tests | Prevent the editor from becoming stale live truth as the language grows | Updated editor grammar and docs aligned with shipped compiler grammar | `cd editors/vscode && make` plus targeted editor tests |
| Docs / examples | `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, `docs/SKILL_PACKAGE_AUTHORING.md`, `examples/README.md`, new numbered examples | Skills documented as inline semantic layer | Add canonical package story, dedicated authoring guide, package gallery, grounding crosswalk, and proof matrix | Public docs must match shipped capability and teach the new surface elegantly | Live docs path plus compiler-owned package gallery | Relevant corpus verification and docs coherence review |

Required docs/example work products under that last row:

- `docs/README.md`: update the live index so skill-package authoring is a first-class visible topic.
- `docs/LANGUAGE_REFERENCE.md`: define the package authoring surface and semantics.
- `docs/EMIT_GUIDE.md`: explain package emission, output layout, and target/config behavior.
- `docs/SKILL_PACKAGE_AUTHORING.md`: the canonical end-to-end authoring guide.
- `examples/README.md`: explain how to read the skill-package example gallery and what each example teaches.
- `examples/95_skill_package_minimal`: minimal single-file package.
- `examples/96_skill_package_references`: reference-heavy package.
- `examples/97_skill_package_scripts`: script-backed package.
- `examples/98_skill_package_runtime_metadata`: runtime-flagged package with companion metadata.
- `examples/99_skill_package_plugin_metadata`: plugin-style split metadata package.
- `examples/100_skill_package_bundled_agents`: bundled-subagent orchestrator package.
- `examples/101_skill_package_compendium`: compendium-style package.
- `examples/102_skill_package_path_case_preservation`: path/case edge-case package.

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - package authoring lives inside `doctrine/grammars` -> `doctrine/parser.py`
    and `doctrine/model.py` -> `doctrine/_compiler/*` -> shared emit plumbing
    plus a dedicated package emitter
  - no sidecar packaging subsystem and no post-emit repair path
- Likely required cleanup includes any public wording that implies full skill
  support while only describing inline skill semantics.
- Behavior-preservation evidence must explicitly cover the current inline
  `skill` / `skills` story.
- Migration must not impose new required declarations or config on existing
  inline-skill users or current `AGENTS.md`-only emit consumers.
- The migration plan must preserve the currently shipped inline skill proof in
  [examples/11_skills_and_tools](../examples/11_skills_and_tools),
  [examples/21_first_class_skills_blocks](../examples/21_first_class_skills_blocks),
  [examples/22_skills_block_inheritance](../examples/22_skills_block_inheritance),
  and [examples/60_shared_readable_bodies](../examples/60_shared_readable_bodies)
  while adding package authoring on top.
- Package-layout migration notes must explicitly address:
  `references/` versus `reference/`, optional `agents/openai.yaml`, optional
  `scripts/`, optional plugin manifests, and path/case preservation.
- `examples/*/build_ref` remains a verifier-owned checked-in artifact
  convention. It must not leak into the compiler contract, package source
  model, or public docs as if it were a user-authored directory.
- The package source model is source-root-relative: bundled files live beside
  `SKILL.prompt` in the prompt tree and compile/copy through under the same
  relative paths.
- If package support does not initially cover every pressure-family grammar
  from the harvested bank, the doc must say exactly which families are in the
  first shipped slice and which remain explicit follow-up rather than letting
  them disappear into vague scope language.
- Deprecated APIs (if any):
  - no legacy behavior is approved for removal in pass 1
  - current inline `skill` / `skills` and current `emit_docs` behavior are
    compatibility surfaces to preserve
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - stale live docs wording that overstates current skill-package support
  - any temporary converter, raw-markdown passthrough, or packaging shim created
    during implementation
- Capability-replacing harnesses to delete or justify:
  - markdown import shortcuts that bypass typed package ownership
  - repo-policing utilities whose only job is to assert docs or path hygiene
    instead of enforcing package boundaries in the compiler and emitter
- Live docs/comments/instructions to update or delete:
  - `docs/README.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
  - `editors/vscode/README.md`
  - numbered example descriptions and checked-in refs that become stale once the
    package gallery lands
- Behavior-preservation signals for refactors:
  - `make verify-examples`
  - targeted inline-skill manifests such as `examples/11_skills_and_tools`
  - current configured emit targets in `pyproject.toml`
  - diagnostic smoke coverage for emit-target and direct-entrypoint constraints
  - `cd editors/vscode && make`
  - new package-gallery emit and verification surfaces

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Shared emit infrastructure | `doctrine/emit_common.py`, `doctrine/project_config.py`, `pyproject.toml` emit contract | one additive shared target-plumbing story for agent and package emission | prevents a second config surface for package authoring | include |
| Existing skill semantics | `doctrine/model.py`, `doctrine/_compiler/resolve.py`, `doctrine/_compiler/compile.py` | keep `skill` / `skills` as the semantic core and layer package ownership above them | prevents duplicate capability models | include |
| Package filesystem model | package-root discovery, emit tree construction, docs/examples wording | source-root bundle/copy-through semantics instead of typed companion-family declarations | prevents overfitting example directory conventions into the language core | include |
| Live docs path | `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md` | treat package authoring as live docs truth rather than proposal-only truth | prevents package support from shipping without a canonical teaching path | include |
| Example proof path | `examples/README.md`, numbered examples, `doctrine/verify_corpus.py` | keep package proof in the numbered corpus, not only in harvested banks | prevents split truth between examples and external pressure material | include |
| Prompt entrypoint toolchain | `emit_common`, diagnostics, editor support, smoke tests | treat `SKILL.prompt` as a first-class shipped entrypoint | prevents drift between compiler, diagnostics, docs, and editor behavior | include |
| Harvested pressure sources | `example_agents/harvested/`, local skill corpora outside the repo | use as inspiration and pressure, not shipped proof | prevents cargo-culted product-specific examples | include |
| Converter or shim path | any future package converter or markdown passthrough helper | forbid shim-based architecture | prevents parallel package-authoring paths | include |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Package source surface and shared target-plumbing foundation

Status: COMPLETE (audit verified shipped code and proof)

Goal

Land the first-class package authoring surface inside the existing Doctrine
pipeline without changing current inline `skill` / `skills`, `AGENTS.prompt`,
or `SOUL.prompt` behavior.

Work

- Extend `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
  `doctrine/model.py`, and `doctrine/_compiler/indexing.py` for `SKILL.prompt`,
  top-level `skill package`, core typed package metadata, package-source-root
  ownership rooted at the directory that contains `SKILL.prompt`, and a
  compiled package artifact skeleton.
- Widen shared target plumbing in `doctrine/emit_common.py`,
  `doctrine/project_config.py`, and the emit contract so `SKILL.prompt` joins
  `[tool.doctrine.emit.targets]` without a new required target-kind field.
- Add fail-loud package-aware validation and diagnostics for malformed package
  roots, source-root escape attempts, reserved path collisions, prompt/file
  conflicts, unsupported package metadata, and illegal path normalization or
  case folding.
- Preserve the current skill semantic core by lowering the package primary body
  through existing skill semantics rather than introducing a second capability
  model.

Verification (smallest signal)

- Targeted parser/model/compiler coverage for the new package-root nodes and
  invalid forms.
- One focused manifest-backed proof for
  `examples/95_skill_package_minimal/cases.toml`.
- Preservation check that the current inline-skill examples still pass on
  their existing manifests, especially `11`, `21`, `22`, and `60`.

Docs/comments (propagation; only if needed)

- Add narrow comments only at the package-root lowering boundary and shared
  target-plumbing invariants when the new ownership would otherwise be hard to
  recover from code alone.
- Update `docs/COMPILER_ERRORS.md` only when package diagnostics become
  user-visible in this phase.

Exit criteria

`SKILL.prompt` is recognized by shared target plumbing, `skill package`
parses/indexes/validates fail-loud, the package source-root model is explicit,
and the current agent-oriented emit path is still behavior-preserving for
existing consumers.

Rollback

Revert the package entrypoint, AST/model, and shared target-plumbing widening
as one slice, leaving the pre-existing agent-only path intact.

Completed work:

- added first-class `skill package` parsing, typed `metadata:` support for the
  initial scalar package fields, AST/model ownership, and indexed-unit package
  registration
- added `CompilationSession.compile_skill_package()` plus the package compile
  boundary that lowers the package body through the existing record/render
  helpers instead of inventing a second capability model
- widened shared emit-target validation to recognize `SKILL.prompt` while
  keeping `emit_docs` and `emit_flow` explicitly scoped to `AGENTS.prompt` and
  `SOUL.prompt`
- reworked the package owner model around the directory that contains
  `SKILL.prompt`, removed typed ordinary companion declarations, and switched
  package validation to generic source-root path, collision, and case-fold
  checks instead of hard-coded companion-family roots

## Phase 2 — Core package lowering and deterministic filesystem emission

Status: COMPLETE (audit verified shipped code and proof)

Goal

Compile and emit real package trees through a dedicated sibling emitter while
proving exact path, casing, and relative-link preservation for the core package
families.

Work

- Add the compiled package artifact/tree layer in `doctrine/_compiler/*` and a
  dedicated sibling emitter in `doctrine/emit_skill.py`.
- Implement deterministic `SKILL.md` generation plus source-root-relative
  copy-through for bundled files under arbitrary relative paths.
- Preserve path spelling, filename case, and relative links exactly; reject
  unsupported collisions or layout rewrites loudly instead of repairing them
  after the fact.
- Wire package-tree verification into `doctrine/verify_corpus.py` and land the
  foundational gallery examples:
  `95_skill_package_minimal`, `96_skill_package_references`,
  `97_skill_package_scripts`, and
  `102_skill_package_path_case_preservation`, where `references/`,
  `reference/`, `scripts/`, and `assets/` are example layouts rather than
  compiler-owned package families.

Verification (smallest signal)

- Targeted manifest-backed proof for examples `91`, `92`, `93`, and `98`.
- Direct emit checks that compare emitted trees and relative-link outputs
  against checked-in refs.
- Preservation check that `emit_docs` still produces unchanged agent refs for
  the existing corpus.

Docs/comments (propagation; only if needed)

- Keep internal emitter comments focused on shared target-plumbing and
  path-preservation boundaries only.
- Update any touched user-facing emit error/help surfaces so they describe the
  real package behavior rather than the old agent-only assumption.

Exit criteria

`emit_skill` emits deterministic package trees from the `SKILL.prompt`
source-root model, path/case-preservation proof exists in the numbered corpus,
and `emit_docs` still behaves as before.

Rollback

Revert the new package-emission path and package-tree proof while leaving the
current agent-doc emitter untouched.

Completed work:

- added the new `doctrine/emit_skill.py` sibling emitter for the minimal
  `SKILL.md` package tree
- wired `doctrine.verify_corpus` build-contract runs to dispatch `SKILL.prompt`
  targets through the new package emitter
- landed `examples/95_skill_package_minimal` with a checked-in `SKILL.md`
  reference tree and a parser failure contract for unknown package metadata
- extended package compilation and `emit_skill` to discover and copy bundled
  non-`.prompt` source-root files under preserved relative paths and exact
  filename casing
- landed `examples/96_skill_package_references`,
  `examples/97_skill_package_scripts`, and
  `examples/102_skill_package_path_case_preservation` to prove `references/`,
  `reference/`, `scripts/`, `assets/`, relative-link preservation, and
  path/case validation as representative layouts
- reserved nested prompt-bearing subtrees as compiler-owned follow-up work for
  Phase 3 instead of copying them through as ordinary bundled files

## Phase 3 — Runtime/plugin companions, bundled agents, diagnostics, and editor convergence

Status: COMPLETE (audit verified shipped code and proof)

Goal

Cover the remaining first-slice real package families and make the compiler,
diagnostics, smoke coverage, and editor tooling agree on the shipped package
surface.

Work

- Extend source-root package emission so runtime/plugin files such as
  `agents/openai.yaml`, `.codex-plugin/plugin.json`, `.app.json`, and the
  supported bundled-agent package surfaces can ship as bundled package-local
  files under preserved relative paths.
- Add any needed support for nested prompt-bearing companion surfaces while
  keeping ordinary copied files untyped unless Doctrine must semantically own
  them.
- Extend validation and diagnostics for runtime/plugin package contracts
  without widening `emit_flow` beyond its current agent/workflow boundary.
- Update `doctrine/diagnostic_smoke.py`, `docs/COMPILER_ERRORS.md`, and shared
  diagnostics so `SKILL.prompt` and `skill package` are first-class shipped
  surfaces where appropriate.
- Update the VS Code extension grammar, resolver, tests, alignment checks, and
  `editors/vscode/README.md` for the new entrypoint and declaration surface.
- Land the remaining first-slice gallery examples:
  `98_skill_package_runtime_metadata`,
  `99_skill_package_plugin_metadata`,
  `100_skill_package_bundled_agents`, and
  `101_skill_package_compendium`.

Verification (smallest signal)

- Targeted manifest-backed proof for examples `94` through `97`.
- `make verify-diagnostics` when diagnostics change.
- `cd editors/vscode && make` when editor surfaces change.
- Preservation check that `emit_flow` still rejects package entrypoints.

Docs/comments (propagation; only if needed)

- Update touched editor docs and the compiler error catalog in the same phase
  as the code changes that make them real.
- Add narrow comments only where runtime/plugin companion ownership would
  otherwise be difficult to infer from code.

Exit criteria

The full first shipped package-family matrix is supported, diagnostics and
editor tooling match compiler truth, and the flow-versus-package boundary is
explicit and tested.

Rollback

Revert runtime/plugin companion support, the associated diagnostics/editor
changes, and the dependent gallery examples while preserving the core package
emitter from Phase 2.

## Phase 4 — Public docs, example gallery, and final proof convergence

Status: COMPLETE (audit verified shipped docs and proof)

Goal

Make skill-package authoring teachable and shippable, not merely implemented,
by aligning the live docs path, the numbered gallery, and the final repo
verification story.

Work

- Author `docs/SKILL_PACKAGE_AUTHORING.md` as the canonical end-to-end guide.
- Update `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`,
  and `examples/README.md` so the public story matches the shipped surface and
  the example gallery teaches one new idea per example.
- Make the public story explicit that bundled files come from the package
  source tree around `SKILL.prompt`, preserve relative layout on emit, and do
  not require a privileged `build_ref` or companion-family authoring surface.
- Add the explicit grounding crosswalk from the linked real skill families to
  the generic Doctrine-native example gallery without importing product-specific
  names or workflow jargon into shipped docs.
- Tighten any remaining manifest refs, example prose, and live-doc wording so
  implementation, diagnostics, examples, and documentation say the same thing.
- Run the final relevant repo verification passes for the changed surfaces.

Verification (smallest signal)

- `make verify-examples`.
- `make verify-diagnostics` if diagnostics changed in the shipped slice.
- `cd editors/vscode && make` if editor surfaces changed in the shipped slice.

Docs/comments (propagation; only if needed)

- Delete or rewrite stale live docs wording that would otherwise keep the repo
  presenting inline skill support as the whole story.
- Keep the shipped examples and docs generic even when they are clearly
  inspired by the crosslinked real skill families.

Exit criteria

The live docs path is canonical, the numbered package gallery is rich enough to
teach real authoring, the final relevant verification passes are green, and no
touched live docs or editor docs are stale.

Rollback

Revert public claims, gallery examples, and guide updates that overstate
support if the final proof or docs/examples convergence is not yet real.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

Avoid verification bureaucracy. Prefer the smallest existing signal. Default to
1-3 checks total per meaningful phase. Keep manual verification for finalization
unless a specific package shape has no credible programmatic proof.

During implementation, prefer one targeted manifest-backed example per phase
while the surface is still moving, then finish with the repo-level checks that
match the changed surfaces: `make verify-examples`, `make verify-diagnostics`
when diagnostics changed, and `cd editors/vscode && make` when editor support
changed.

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
- Authoring examples should cover realistic distilled patterns from the linked
  real skills, not only minimal toy surfaces.
- The representative package matrix should include, at minimum:
  - a bare single-file skill
  - a reference-heavy rulebook skill
  - a script-backed skill with paired `.py` and `.ts` entrypoints
  - a runtime-flagged skill with package-local metadata
  - a plugin-style package with split metadata roots
  - a bundled-subagent orchestrator skill
  - path/case edge cases such as `reference/` and `REFERENCE.md`
  - at least one example each clearly inspired by the crosslinked `adapt`,
    `arch-step`, `mobile-sim`, `together-chat-completions`, Figma, GitHub
    plugin, `legal-review`, and medical-compendium skill families after
    Doctrine-native generalization
- The docs proof should cover, at minimum:
  - one canonical authoring guide for building a realistic package end to end
  - language-reference coverage for every shipped package declaration
  - emit-guide coverage for package layout and companion-file emission
  - examples index coverage that explains the skill-package gallery and its
    teaching purpose

## 8.3 E2E / device tests (realistic)

Not device work. Realistic end-to-end proof here means running the package emit
path and verifying the emitted tree against representative reference packages
without adding brittle repo-policing gates.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Roll out example-first. The public story should move from "inline skill support"
to "full skill-package authoring" only once the representative package matrix is
shipped, verified, and documented well enough to serve as the canonical
authoring guidance. Do not claim the feature is done if the implementation
exists but the docs and example story are still thin.

## 9.2 Telemetry changes

No product telemetry is assumed yet. The likely operational signal is improved
package-specific diagnostics and clearer emit failures, not runtime telemetry.

## 9.3 Operational runbook

- Update the live docs index and language reference when the feature is real.
- Add or expand dedicated skill-package authoring docs rather than burying the
  new surface in scattered notes.
- Publish a crosswalk from the linked real skill families to the shipped
  Doctrine-native example gallery so the inspiration is explicit and curated.
- Ensure the relevant repo verification commands cover the new package proof
  surfaces.
- Keep `example_agents/` as pressure material, but promote the durable truth
  into the numbered corpus and live docs.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: self cold read 1, self cold read 2, self-integrator
- Scope checked:
  - frontmatter, `# TL;DR`, `# 0)` through `# 10)`, `planning_passes`, and helper blocks
  - agreement across scope, owner path, migration/deletes, execution order, verification, rollout, and compatibility claims
- Findings summary:
  - the plan is now aligned end to end on the additive package-authoring goal, canonical owner path, package surface, and four-phase delivery order
  - the only material drift found in this pass was bookkeeping drift in `planning_passes` and an under-specified acceptance matrix in `# 0.4`
- Integrated repairs:
  - updated `planning_passes` so the recommended flow includes the required consistency pass and marks external research as optional when internal grounding already settled the first shipped slice
  - tightened `# 0.4 Definition of done` so the acceptance matrix explicitly includes plugin-style split metadata roots and path/case-preservation edge cases already required by the example slate
- Remaining inconsistencies:
  - none
- Unresolved decisions:
  - none
- Unauthorized scope cuts:
  - none
- Decision-complete:
  - yes
- Decision: proceed to implement? yes
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

## 2026-04-13 - Treat skill packages as first-class Doctrine output

Context

The requested change is broad: Doctrine should elegantly and fully support
authoring the real skills in the local corpora and harvested bank, not just
inline skill prose inside agent programs. The user also wants this done without
breaking the current shipped doctrine or creating new compatibility burdens for
downstream consumers who rely on today's inline skill and `AGENTS.md` behavior.

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
- Documentation quality and breadth of examples are part of the acceptance bar,
  not optional polish after the feature exists.

## 2026-04-13 - Keep package authoring inside the existing Doctrine pipeline

Context

Deep-dive pass 1 resolved the architectural boundary needed to avoid package
support becoming a bolt-on subsystem or a breaking rewrite.

Decision

- keep the new package surface inside the existing Doctrine owner path from
  grammar through compiler and emit
- preserve current `skill` / `skills` semantics as the compatibility semantic
  core
- keep current `emit_docs` behavior stable for agent docs
- add a dedicated sibling package-emission path for real `SKILL.md` package
  trees rather than overloading the existing agent-doc emitter
- treat live docs and the numbered example gallery as part of the shipped
  architecture, not follow-up polish

Consequences

- package emission should widen shared emit-target plumbing but stay additive
  for current consumers
- deep-dive pass 2 now needs to settle exact declaration syntax, package target
  configuration details, and typed-versus-extension metadata boundaries
- implementation must delete any shim-style fallback path if one appears during
  delivery

## 2026-04-13 - Use `SKILL.prompt` plus `skill package` as the concrete package surface

Context

Deep-dive pass 2 resolved the remaining architecture choices needed before
phase planning.

Decision

- package source entrypoint is `SKILL.prompt`
- package root syntax is top-level `skill package`
- shared emit-target registry stays unified under `[tool.doctrine.emit.targets]`
  and widens by supported entrypoint filename rather than a new required target
  kind
- package emission ships as a dedicated sibling command/module (`emit_skill`)
  rather than a retrofit mode inside `emit_docs`
- the canonical teaching path is `docs/SKILL_PACKAGE_AUTHORING.md` plus package
  gallery examples `91` through `99`

Consequences

- parser, diagnostics, docs, smoke tests, and editor tooling all need explicit
  updates for `SKILL.prompt` and `skill package`
- phase-plan can now sequence work without carrying unresolved architecture
  branches
- Section 3.3 is now clear for implementation planning on the first shipped
  slice

Follow-ups

- Build the authoritative phase plan against the now-settled package surface.
- Keep the controller on the canonical path through `consistency-pass` before
  implementation begins.

## 2026-04-13 - Treat bundled package files as source-root inputs, not typed companion families

Context

Implementation drift exposed an important design error: the plan had started to
overfit the repo's example and corpus conventions by treating
`references/`, `reference/`, `scripts/`, `assets/`, and similar layouts as if
they should be compiler-owned package families. That would make example
conventions feel like language law and would incorrectly elevate `build_ref/`
from verifier artifact to product concept.

Decision

- keep `SKILL.prompt` plus top-level `skill package` as the authoring surface
- define the package source root as the directory that contains `SKILL.prompt`
- compile `SKILL.prompt` to `SKILL.md`
- copy bundled sibling and descendant files through under the same relative
  paths unless Doctrine explicitly owns their compilation semantics
- treat observed layouts such as `references/`, `reference/`, `scripts/`,
  `assets/`, `agents/openai.yaml`, plugin manifests, and similar trees as
  important proof cases, not privileged root families in the core language
- keep `examples/*/build_ref` as verifier-only checked-in proof, not public or
  compiler-facing package architecture

Consequences

- the plan reopens Phase 1 and Phase 2 until the implementation matches the
  source-root bundle/copy-through model
- typed file-family declarations are no longer the approved first-slice
  direction for ordinary bundled package files
- docs and examples must teach relative source-root bundling and exact
  path-preserving emission as the canonical authoring story

## 2026-04-13 - Sequence delivery as foundation -> emit -> extension/tooling -> docs/proof

Context

`phase-plan` translated the settled architecture into one execution checklist.
The user explicitly wants the final result to be elegant, compatibility-safe,
and richly documented rather than a thin implementation with docs deferred.

Decision

- ship the work in four depth-first phases:
  foundation, core package emission, runtime/plugin/editor convergence, and
  public docs/example-proof convergence
- treat docs/examples as a final ship gate rather than optional cleanup after
  the code path exists
- keep each phase behavior-preserving for current inline skill and
  agent-oriented consumers

Consequences

- implementation can move aggressively inside canonical owner paths without
  inventing a second package-authoring subsystem
- final completion requires the docs and gallery to be as real as the code
- the later consistency pass can audit one concrete sequencing story instead of
  several plausible execution orders
