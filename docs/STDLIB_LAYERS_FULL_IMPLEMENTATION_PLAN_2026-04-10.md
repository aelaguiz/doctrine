---
title: "Doctrine - Standard Library Layers Full Implementation - Architecture Plan"
date: 2026-04-10
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/STDLIB_LAYERS.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/WORKFLOW_LAW.md
  - docs/SPEC_1_3_END_TO_END_IMPLEMENTATION_PLAN_2026-04-10.md
  - examples/README.md
  - example_agents/README.md
  - example_agents/harvested/index.md
  - doctrine/compiler.py
  - doctrine/verify_corpus.py
---

# TL;DR

## Outcome

Doctrine gets a real four-layer stack aligned to `docs/STDLIB_LAYERS.md`:
Layer 1 stays compiler and language semantics, Layer 2 becomes an authored-in-
Doctrine `doctrine.std` foundation for portable-truth coordination and generic
role-home defaults under one shared repo-level `prompts/` root, Layer 3
becomes public reference packs that prove stdlib sufficiency without becoming
the framework, and Layer 4 stays private application packs that import Layer 2
directly unless a concrete Layer 3 pack truly fits.

## Problem

The intended layering is currently spread across strong design prose, shipped
portable-truth examples, and a harvested `example_agents/` pressure bank, but
it is not yet implemented as one repo-wide architecture with clear owner
paths. Without an explicit implementation plan, Doctrine risks either widening
Layer 1 with unearned semantics or letting the first public or private pack
turn into a shadow standard library.

## Approach

Treat `docs/STDLIB_LAYERS.md` as the directional contract, but ground every
implementation choice in shipped Doctrine truth: `doctrine/`,
`docs/LANGUAGE_DESIGN_NOTES.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, and examples
`30` through `49`. Use `example_agents/` only as design pressure for
separation boundaries, especially around coordination and handoffs, role-home
defaults, scoped instruction layers, skills and capabilities packaging, and
domain-local output contracts. Build Layer 2 only from patterns already earned
by the language; implement the `doctrine.std.*` namespace under a shared
repo-level `prompts/` root that current import resolution can actually load;
keep code-review-like public packs in Layer 3; and keep private nouns and host
schemas out of Layer 2.

## Plan

1. Confirm the four-layer boundary and the Layer 2 v1 surface that current
   Doctrine examples actually earn.
2. Research the shipped corpus and selected example-agent use cases to decide
   which reusable patterns belong in Layer 2, which belong in a public Layer 3
   proving ground, and which must stay pack-local.
3. Deep-dive the current repo to define the canonical owner paths, target repo
   layout, migration list, and proof strategy for `doctrine.std` plus the
   first public reference pack.
4. Author the phased implementation plan that lands Layer 2 first, then public
   pack proof and extraction rules, then docs/example/editor alignment.
5. Implement with existing repo proof lanes: targeted manifests,
   `make verify-examples`, `make verify-diagnostics` when needed, and
   `cd editors/vscode && make` if editor surfaces change.

## Non-negotiables

- No new language surface in Layer 2 beyond what current Doctrine examples and
  docs already earn.
- Layer 2 is authored Doctrine, not hidden compiler magic, packet machinery,
  or a Lessons-shaped framework.
- Layer 4 should depend directly on Layer 2 by default; if Layer 3 discovers
  something generic, extract it downward instead of letting Layer 3 become the
  real framework.
- `law` decides current truth; `output` and `trust_surface` carry what the
  next owner can read and trust.
- `example_agents/` is design pressure only, never shipped language truth.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-10
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-10
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-10
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine implements `docs/STDLIB_LAYERS.md` faithfully, the repo will ship
a clearly separable Layer 2 standard library authored in ordinary Doctrine
source, plus the supporting docs, examples, and proof lanes needed to show
that:

- Layer 1 owns semantics and compiler behavior.
- Layer 2 owns reusable authored Doctrine for portable-truth coordination and
  generic role-home defaults.
- Layer 3 owns public domain packs that prove stdlib sufficiency without
  becoming the hidden framework.
- Layer 4 owns private packs that extend Layer 2 without redefining lower-
  layer meaning.

This claim is false if the resulting repo still needs private pack nouns to
explain Layer 2, still relies on unshipped language features, or still leaves
Layer 3 as the practical reusable foundation.

## 0.2 In scope

- Converge the intended four-layer stack in one canonical implementation plan.
- Use `docs/STDLIB_LAYERS.md` as the directional source for Layer 2, Layer 3,
  and Layer 4 boundaries.
- Ground the plan in shipped Doctrine truth:
  - `doctrine/`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/WORKFLOW_LAW.md`
  - examples `30` through `49`
- Determine the initial Layer 2 v1 module families and their owner paths.
- Determine the initial Layer 3 proving-ground shape, with code-review-style
  public packs as the leading candidate rather than a guaranteed outcome.
- Use selected `example_agents/` packages as use-case pressure for clear
  separability:
  - coordination and handoff contracts
  - skills and capability packaging
  - role decomposition
  - scoped instruction hierarchy
  - response/readback contract shape
- Include architectural convergence work required to avoid parallel public
  foundations, docs-only pseudo-frameworks, or duplicate truth about where
  reusable Doctrine behavior should live.

## 0.3 Out of scope

- Inventing new core syntax merely to make Layer 2 more convenient.
- Smuggling unsupported features into Layer 2 through convention, including:
  - packet primitives
  - floating obligation runtimes
  - nominal artifact calculus
  - `current status`
  - targetless routes
  - top-level reusable `law`
  - `runtime_tools`
  - fake host-input schemas that pretend to be compiler-enforced
- Promoting a generic Layer 2 `review/` module before the corpus proves it.
- Importing product names, proprietary role graphs, or private vocabulary into
  public stdlib surfaces.
- Treating `example_agents/` as shipped truth, proof, or direct source text to
  cargo-cult into Doctrine.

## 0.4 Definition of done (acceptance evidence)

The implementation governed by this plan is done when all of the following are
true:

- The repo has a real Layer 2 owner path under one shared repo-level
  `prompts/` root with module namespace `doctrine.std.*`, and the first agreed
  v1 module families are authored in ordinary Doctrine source.
- The first public-pack proving ground is clearly separated from Layer 2 and
  uses Layer 2 imports for generic coordination structure rather than becoming
  the hidden reusable framework.
- The docs that explain layering, language boundaries, and portable-truth I/O
  are aligned to the implemented structure rather than describing a future
  shape that the repo does not ship.
- The proof lanes named by the plan run successfully for the touched surfaces:
  targeted manifest-backed examples, `make verify-examples`,
  `make verify-diagnostics` when diagnostics change, and
  `cd editors/vscode && make` if editor surfaces change.
- Existing shipped behavior stays intact unless the plan explicitly widens
  Layer 1 and proves that widening with the smallest credible signal.

Behavior-preservation evidence for convergence work:

- Existing examples continue to verify unless the plan explicitly retires or
  rewrites them in the same run.
- Any reusable behavior extracted into Layer 2 remains provable through import
  use cases instead of only through docs prose.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks.
- No runtime shims.
- No new parallel public foundation outside the chosen Layer 2 owner path.
- No private pack nouns inside Layer 2.
- No Layer 3 pack acting as the real reusable framework.
- No example-agent product jargon imported into public Doctrine docs or code.
- No Layer 2 feature that depends on semantics the language does not already
  support.
- No silent behavior drift in examples, rendered output, or docs while
  extracting reusable structure.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Keep Layer 1 honest and small: only real language/compiler semantics live
   there.
2. Make Layer 2 the reusable public foundation, not Layer 3 or Layer 4.
3. Keep Layer 2 output-heavy, patch-friendly, and clearly generic.
4. Use real example-agent use cases to sharpen boundaries without cargo-
   culting their product shapes.
5. Keep proof, docs, and implementation aligned as shipped truth.

## 1.2 Constraints

- Doctrine is example-first and should only standardize patterns that the
  shipped corpus or core docs already earn.
- Current shipped semantics run through examples `30` through `49`, not a
  speculative next language tier.
- Layer 2 must be authored in existing Doctrine source, not simulated by
  prose-only conventions that hide missing core support.
- `example_agents/` is a curated source bank, not part of
  `doctrine.verify_corpus`.
- Verification should stay inside existing repo lanes unless a missing proof
  gap is real and specific.

## 1.3 Architectural principles (rules we will enforce)

- Reuse the canonical path; do not keep a docs-only pseudo-stdlib and a real
  stdlib side by side.
- Make layer ownership explicit on disk and in docs.
- Keep `law` as the semantic home for current truth and `output` as the trust
  carrier contract.
- Prefer downward extraction into Layer 2 over upward dependency from Layer 4
  into Layer 3.
- Keep public reusable surfaces generic, named, and patchable.
- Fail loudly when a desired Layer 2 abstraction needs unsupported core
  semantics.

## 1.4 Known tradeoffs (explicit)

- The first Layer 2 pass will likely keep some duplication because current
  Doctrine does not yet ship every abstraction that a richer library system
  might want.
- A public Layer 3 code-review pack is a strong candidate because it creates
  the right extraction pressure, but forcing it into Layer 2 too early would
  blur the layer boundary.
- `example_agents/` gives valuable pressure across skills, handoffs, and role
  splits, but each source carries product-local assumptions that must be
  stripped before anything becomes public Doctrine.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- `docs/STDLIB_LAYERS.md` already describes the intended four-layer direction
  and a concrete Layer 2 v1 shape.
- `doctrine/` owns the shipped parser, compiler, renderer, diagnostics, and
  verification behavior.
- Examples `30` through `49` prove the current workflow-law, portable-truth,
  route-only, and full review surfaces.
- `example_agents/` contains curated real-world instruction artifacts that
  pressure Doctrine toward clearer layering, handoffs, skills, and scoped
  behavior, but it is explicitly non-authoritative.

## 2.2 What is broken / missing (concrete)

- There is no implemented Layer 2 owner path yet.
- Reusable coordination and role-home patterns still live mostly as examples,
  design prose, or pack-shaped thought experiments.
- The repo does not yet clearly separate "public reusable authored Doctrine"
  from "public domain pack" and "private pack."
- The example-agent bank is useful pressure, but the repo does not yet have a
  disciplined extraction path from that pressure into Doctrine layer decisions.

## 2.3 Constraints implied by the problem

- The plan must preserve the current example-first language posture.
- It must distinguish architectural convergence from product creep.
- It must not use docs prose to fake a library that the repo cannot actually
  author, import, verify, and maintain.

# 3) Research Grounding (external + internal "ground truth")

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `example_agents/harvested/openai-agents-python/notes.md` — adopt the split
  between generic coordination surfaces, tools, handoffs, and result
  contracts; reject the SDK's typed runtime APIs as direct Doctrine stdlib
  shapes.
- `example_agents/harvested/openclaw-medical-skills/notes.md` — adopt skill-
  package discipline, required capability declarations, and narrow output
  packages as evidence that reusable capability surfaces and domain packs
  should stay separate; reject domain schemas, connectors, and medical jargon.
- `example_agents/harvested/ai-legal-claude/notes.md` — adopt narrow
  specialist-role and output-contract separation as pressure for Layer 3 and
  Layer 4 pack boundaries; reject legal disclaimers and report templates as
  stdlib material.
- `example_agents/harvested/cloudflare-agents/notes.md` and
  `example_agents/harvested/langgraph/notes.md` — adopt explicit scope
  hierarchy and package-local narrowing as evidence that a good layer stack
  removes ambiguity instead of collecting everything in one framework bucket.
- `example_agents/harvested/vercel-agent-browser/notes.md` and
  `example_agents/harvested/sentry-mcp/notes.md` — adopt reusable
  coordination/readback contracts, capability boundaries, and fail-loud
  quality gates as pressure for Layer 2 coordination outputs and capability
  surfaces; reject browser/auth/OAuth/MCP product specifics.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `docs/STDLIB_LAYERS.md` defines the intended four-layer direction and a
    concrete Layer 2 v1 candidate surface, but it is still design direction,
    not shipped implementation truth.
  - `docs/LANGUAGE_DESIGN_NOTES.md` is the language-decision anchor: Doctrine
    is example-first, `workflow` is the semantic home,
    `12_role_home_composition` earned the basic role-home shell,
    `21_first_class_skills_blocks` earned first-class skills blocks,
    `23_first_class_io_blocks` and `24_io_block_inheritance` earned reusable
    IO blocks, `29_enums` earned first-class closed vocabularies, and examples
    `30` through `42` earned the workflow-law family.
  - `docs/AGENT_IO_DESIGN_NOTES.md` fixes the I/O boundary: `output` is the
    one produced-contract primitive, `trust_surface` is the portable-truth
    carrier, and packet-like machinery is explicitly non-shipped.
  - `docs/WORKFLOW_LAW.md` fixes the portable-truth mental model: `law`
    decides what is true now, `output` plus `trust_surface` decide what the
    next owner can read and trust, and route-only readback stays outside
    `trust_surface`.
  - `doctrine/compiler.py::_resolve_prompt_root()` and
    `doctrine/compiler.py::_load_module()` define a hard implementation
    constraint: prompt imports resolve under the nearest `prompts/` root only.
    A real shared stdlib therefore needs one shared prompt root or explicit
    import-resolution work; a literal `doctrine/std/*.prompt` tree is not
    importable today by itself.
  - `doctrine/verify_corpus.py::_load_case()` already supports
    `cases[].prompt` overrides. Manifest-backed proof can therefore target a
    shared-root stdlib or public-pack entrypoint without rewriting the current
    numbered-corpus manifest model.
  - `pyproject.toml` plus `doctrine/emit_docs.py` already support arbitrary
    `AGENTS.prompt` and `SOUL.prompt` entrypoints for emitted-doc proof.
    Shared stdlib and public-pack emit targets can therefore use the existing
    build lane.
  - `examples/12_role_home_composition/prompts/AGENTS.prompt` and
    `examples/13_critic_protocol/prompts/AGENTS.prompt` prove the reusable
    role-home shell, `read_first`, `how_to_take_a_turn`, specialization, and
    outputs grouping patterns that Layer 2 can extract generically.
  - `examples/21_first_class_skills_blocks/prompts/AGENTS.prompt`,
    `examples/23_first_class_io_blocks/prompts/AGENTS.prompt`, and
    `examples/24_io_block_inheritance/prompts/AGENTS.prompt` prove first-class
    `skills`, `inputs`, and `outputs` blocks plus explicit inheritance and
    patching.
  - `examples/29_enums/prompts/AGENTS.prompt` proves the reusable enum
    surface.
  - `examples/32_modes_and_match/prompts/AGENTS.prompt`,
    `examples/35_basis_roles_and_rewrite_evidence/prompts/AGENTS.prompt`,
    `examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt`,
    `examples/37_law_reuse_and_patching/prompts/AGENTS.prompt`, and
    `examples/38_metadata_polish_capstone/prompts/AGENTS.prompt` prove the
    `CurrentHandoff`, `RewriteRegime`, trust-carrier, named-law-subsection,
    and integrated portable-truth patterns that the stdlib direction wants to
    package.
  - `examples/39_guarded_output_sections/prompts/AGENTS.prompt` strengthens
    the "output-heavy before workflow-heavy" direction by proving keyed,
    output-owned guarded sections without inventing a second semantic plane.
  - `examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt`
    through `examples/49_review_capstone/prompts/AGENTS.prompt` prove review
    as a shipped Doctrine surface, but that evidence is still too
    review-shaped to justify a generic Layer 2 review module.
  - `example_agents/README.md` and `example_agents/harvested/index.md` are the
    authority for how the example-agent bank should be used: harvest-and-
    distill material only, never shipped Doctrine truth.
- Canonical path / owner to reuse:
  - Layer 1 stays in `doctrine/` plus the manifest-backed numbered corpus.
  - The cleanest Layer 2 physical owner path is one shared repo-level
    `prompts/` root with module namespace `doctrine.std.*`, concretely
    `prompts/doctrine/std/**`, because that satisfies the current prompt-root
    import model without widening language semantics.
  - The corresponding Layer 3 physical owner path should be
    `prompts/doctrine/packs_public/**`, with module namespace
    `doctrine.packs_public.*`.
- Existing patterns to reuse:
  - `examples/03_imports/prompts/AGENTS.prompt` plus
    `doctrine/compiler.py::_resolve_prompt_root()` and `_load_module()` —
    Python-like module naming under one prompt root.
  - `examples/12_role_home_composition/prompts/AGENTS.prompt` and
    `examples/13_critic_protocol/prompts/AGENTS.prompt` — generic role-home
    shell plus role-local overrides.
  - `examples/21_first_class_skills_blocks/prompts/AGENTS.prompt` —
    first-class skills grouping without a parallel runtime-tools surface.
  - `examples/23_first_class_io_blocks/prompts/AGENTS.prompt` and
    `examples/24_io_block_inheritance/prompts/AGENTS.prompt` — explicit,
    patchable IO blocks that suit Layer 2 outputs and inputs.
  - `examples/29_enums/prompts/AGENTS.prompt` — small, stable reusable enums.
  - `examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt`,
    `examples/35_basis_roles_and_rewrite_evidence/prompts/AGENTS.prompt`,
    `examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt`, and
    `examples/38_metadata_polish_capstone/prompts/AGENTS.prompt` — trust-
    surface carrier families that should become explicit Layer 2 output
    families rather than repeated example-local declarations.
  - `examples/37_law_reuse_and_patching/prompts/AGENTS.prompt` and
    `examples/38_metadata_polish_capstone/prompts/AGENTS.prompt` — named `law`
    subsection conventions and explicit override points.
  - `doctrine/verify_corpus.py::_load_case()` and `pyproject.toml` emit
    targets — shared-root proof and build lanes without a new harness.
- Duplicate or drifting paths relevant to this change:
  - `docs/STDLIB_LAYERS.md` repeatedly sketches a literal `doctrine/std/**`
    on-disk path, but the current compiler only imports within one `prompts/`
    root. The semantic namespace and the physical authored-source path are
    therefore drifting today.
  - `CurrentHandoff`, `RewriteRegime`, coordination handoff outputs, and
    portable-truth law conventions are repeated across examples `32`, `35`,
    `37`, and `38`, plus `docs/STDLIB_LAYERS.md`, but do not yet exist as one
    reusable stdlib source of truth.
  - Generic role-home guidance is repeated across examples `12` and `13`, and
    related private-pack pressure appears in
    `docs/LESSONS_PROSE_BUCKETS_2026-04-10.md` and the `BAD_LESSONS_*` docs.
    That is extraction pressure, but those private nouns must not leak into
    Layer 2.
  - Review pressure is split across `docs/REVIEW_SPEC.md`,
    `docs/FULL_REVIEW_SPEC_IMPLEMENTATION_PLAN_2026-04-10.md`, and
    examples `43` through `49`. The pressure is real, but it is still too
    early to bless a generic Layer 2 review module.
  - `example_agents/**` and the Lessons-related prose-bucket docs are valuable
    pressure surfaces, but they are also the easiest place for public Doctrine
    layering to accidentally absorb product-local vocabulary.
- Capability-first opportunities before new tooling:
  - Use a shared repo-level `prompts/` root plus manifest `prompt` overrides
    and emit-target entrypoints before changing import semantics, inventing a
    pack loader, or adding a second module-resolution system.
  - Use already-earned first-class blocks, explicit patching, enums, and named
    `law` subsections before inventing workflow parameters, output inheritance,
    or pseudo-runtime abstractions to make the stdlib look "cleaner."
- Behavior-preservation signals already available:
  - targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
    runs
  - `make verify-examples`
  - `make verify-diagnostics` only if compiler or diagnostics wording changes
  - targeted `uv run --locked python -m doctrine.emit_docs --target ...` for
    shared-root stdlib or public-pack build proof

## 3.3 Open questions (evidence-based)

- Should the first public proving pack be `code_review`, or is there a
  narrower public domain that proves Layer 2 separation more cleanly?
  Evidence needed: which candidate pack reuses coordination outputs,
  role-home defaults, and portable-truth conventions without importing private
  nouns.
- Should human-facing stdlib reference docs live only under `docs/`, or should
  a small authored-source README live adjacent to `prompts/doctrine/std/**` as
  well? Evidence needed: what keeps the docs map clear without creating two
  competing truth surfaces.
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)

<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

The current layering story is split across four real repo surfaces:

- `doctrine/`
  - owns the shipped grammar, parser, model, compiler, renderer, diagnostics,
    verification harness, and emit pipeline
- `examples/`
  - each numbered example keeps its own local `prompts/` root under
    `examples/<N>_*/prompts/`
  - imports resolve inside that local root, which makes the examples strong
    semantic proof units but not a shared library workspace
- `docs/`
  - holds the living language and architecture notes, including
    `docs/STDLIB_LAYERS.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
    `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/WORKFLOW_LAW.md`, and review-facing
    pressure docs
- `example_agents/`
  - holds curated external pressure cases, notes, and candidate tests

What is missing today:

- no repo-level shared `prompts/` root
- no `doctrine.std.*` authored module namespace
- no `doctrine.packs_public.*` authored module namespace
- no stdlib conformance examples that compile against one shared library root

## 4.2 Control paths (runtime)

The current authored-source control path is:

`parse_file()` -> nearest `prompts/` root via `_resolve_prompt_root()` ->
module resolution via `_load_module()` -> `compile_prompt()` ->
render/verify/emit downstream.

Three practical consequences follow from that:

- Existing numbered examples are intentionally isolated proof packages.
- Shared authored-source modules do not yet exist because there is no shared
  prompt root for them to live under.
- The repo already has the proof/build hooks needed for a shared-root stdlib:
  `doctrine.verify_corpus` can point a manifest at any prompt file via
  `cases[].prompt`, and `doctrine.emit_docs` can emit from arbitrary
  entrypoints declared in `pyproject.toml`.

## 4.3 Object model + key abstractions

The current language already owns the abstractions Layer 2 most needs:

- `workflow`, `law`, and `trust_surface`
- first-class `skills`, `inputs`, and `outputs` blocks
- explicit inheritance and patching
- first-class enums
- route-only currentness, mode selection, scope, evidence, invalidation, and
  named `law` subsections

The current language does not yet ship the extra abstractions a more ambitious
library layer might want:

- output inheritance
- workflow parameters
- top-level reusable `law`
- a typed host-handoff schema beyond current input conventions
- packet-like coordination primitives

That means the raw semantic substrate for Layer 2 is real, but the library has
to be explicit, output-heavy, and patch-friendly rather than elegant through
unsupported shortcuts.

## 4.4 Observability + failure behavior today

Current proof and failure behavior is clear:

- missing modules fail loud when they are not present under the current prompt
  root
- `make verify-examples` is the main behavior-preservation signal
- `make verify-diagnostics` exists if compiler-facing wording changes
- `doctrine.emit_docs` plus `pyproject.toml` emit targets already prove some
  built outputs
- `cd editors/vscode && make` exists for editor-surface changes

What is missing:

- no stdlib-specific conformance lane
- no shared-root build proof for library modules or public packs
- no existing import consumer that proves a real repo-level stdlib boundary

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not UI work. The user-facing surfaces here are:

- authored `.prompt` modules
- compiled `AGENTS.md`
- docs explaining the layer boundary
- manifests proving the intended import and composition behavior
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)

<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

The future structure should separate physical authored-source layout from the
module namespace cleanly:

```text
doctrine/
  ...                     # Layer 1 semantics and compiler truth

prompts/
  doctrine/
    std/
      coordination/
        enums.prompt
        inputs.prompt
        outputs.prompt
        workflows.prompt
      portable_truth/
        workflows.prompt
      role_home/
        workflows.prompt
    packs_public/
      code_review/
        enums.prompt
        inputs.prompt
        outputs.prompt
        workflows.prompt
        AGENTS.prompt

examples/
  50_stdlib_coordination/
    cases.toml
  51_stdlib_role_home_and_portable_truth/
    cases.toml
  52_public_code_review_pack/
    cases.toml
```

The public module namespace stays the one the direction doc wants:

- `doctrine.std.*`
- `doctrine.packs_public.*`

But the physical authored-source path lives under one repo-level `prompts/`
root because that is what the shipped compiler can import today.

Human-facing stdlib docs should stay under `docs/`, indexed from `docs/README.md`,
so the repo does not create two competing documentation homes.

## 5.2 Control paths (future)

The future runtime path should preserve current semantics and add a shared
authored-source root, not a second import system:

- Layer 1 remains `doctrine/` plus the numbered manifest-backed corpus.
- Layer 2 and Layer 3 authored modules compile under the repo-level
  `prompts/` root.
- New stdlib and public-pack proof examples stay under `examples/`, but their
  manifests may point at shared-root entrypoints through `cases[].prompt`.
- Emit proof for stdlib and public packs uses ordinary `pyproject.toml`
  entrypoints and `doctrine.emit_docs`.
- Existing numbered examples `01` through `49` remain the semantic substrate
  and do not need mass migration to shared-library imports in the first pass.

This deliberately avoids an initial import-resolution widening. If later work
wants existing local-root examples to import the shared stdlib directly, that
should be a separate explicit convergence decision, not hidden in the first
stdlib implementation.

## 5.3 Object model + abstractions (future)

Layer 2 v1 should be explicit and narrow:

- `doctrine.std.coordination.enums`
  - `RewriteRegime`
- `doctrine.std.coordination.inputs`
  - `CurrentHandoff` as a recommended host-coordination input convention, not a
    fake typed runtime packet
- `doctrine.std.coordination.outputs`
  - explicit output families such as `CoordinationComment`,
    `PortableTruthHandoff`, `ModeAwarePortableTruthHandoff`,
    `ComparisonPortableTruthHandoff`, `InvalidationPortableTruthHandoff`, and
    `PortableTruthHandoffFull`
- `doctrine.std.coordination.workflows`
  - only truly generic route-only coordination surfaces such as `RoutingOwner`
    and `RouteOnlyTurns`
- `doctrine.std.portable_truth.workflows`
  - portable-truth workflow conventions, named `law` subsection organization,
    and reference skeletons, not a giant generic framework
- `doctrine.std.role_home.workflows`
  - `HowToTakeATurn`
  - `CurrentTruthDiscipline`
  - `CoordinationReadbackDiscipline`
  - `SkillFirstSupport`

Layer 3 v1 should be a public proving pack, with `code_review` the leading
candidate because it reuses coordination carriers, role-home shells, explicit
review outputs, and route/verdict law without private nouns.

Layer 4 remains a boundary, not a shipped repo surface here:

- private packs import Layer 2 directly by default
- they may import Layer 3 only when there is a genuine domain fit
- any generic discovery in Layer 3 gets extracted downward into Layer 2

## 5.4 Invariants and boundaries

- Layer 2 must remain authored in existing Doctrine.
- Layer 2 must stay output-heavy before it becomes workflow-heavy.
- One shared repo-level `prompts/` root is the only shared authored-source
  boundary for Layer 2 and Layer 3 in this implementation.
- Existing numbered examples remain semantic proof anchors, not forced library
  migration targets.
- Public packs prove stdlib sufficiency; they do not become the reusable
  framework.
- Private nouns, private role graphs, and private host schemas stay out of
  Layer 2.
- Unsupported features stay deferred:
  - no output inheritance
  - no workflow parameters
  - no top-level reusable `law`
  - no packet layer
  - no fake typed handoff runtime
  - no targetless route or hidden registry layer
- Review stays Layer 3 in v1 until the corpus proves a generic Layer 2 review
  family strongly enough.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not UI work. The future user-facing surfaces are:

- importable `doctrine.std.*` and `doctrine.packs_public.*` prompt modules
- compiled `AGENTS.md` output emitted from shared-root entrypoints
- docs that explain the layer split honestly
- manifests that prove the shared-root import story and pack separation
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)

<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Layer 1 semantic owner | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, `doctrine/model.py`, `doctrine/compiler.py`, `doctrine/renderer.py`, `doctrine/verify_corpus.py` | grammar, AST, import resolution, compile, render, verify | Current Layer 1 already owns semantics and prompt-root module resolution. | Preserve the current semantic owner path; avoid widening language semantics unless a real stdlib blocker appears. | Keep Layer 1 honest and small. | No new syntax or hidden runtime layer for stdlib v1. | `make verify-examples`; `make verify-diagnostics` only if core wording changes. |
| Shared prompt root constraint | `doctrine/compiler.py` | `_resolve_prompt_root()`, `_load_module()` | Imports resolve only under the nearest `prompts/` root. | Reuse this constraint instead of fighting it: put shared Layer 2 and Layer 3 authored modules under one repo-level `prompts/` root. | Avoid a speculative import-system widening just to make stdlib possible. | Canonical authored-source roots are `prompts/doctrine/std/**` and `prompts/doctrine/packs_public/**`. | new shared-root manifests; `make verify-examples`. |
| Shared library source | `prompts/doctrine/std/**` | new stdlib modules | Absent. | Create the Layer 2 v1 module families using only already-earned language surfaces. | Repo currently has no reusable public authored foundation. | `doctrine.std.*` import namespace backed by ordinary prompt modules. | new manifests and emitted refs/builds. |
| Layer 2 coordination surface | `prompts/doctrine/std/coordination/**` | enums, inputs, outputs, workflows | Repeated today across examples `32`, `35`, `36`, `37`, and `38`, plus docs direction. | Extract the earned generic coordination families into named modules. | Remove repeated generic coordination doctrine from examples and future packs. | `RewriteRegime`, `CurrentHandoff`, coordination output families, route-only generic workflow surfaces. | new stdlib manifests; possibly targeted existing example checks for preservation. |
| Layer 2 role-home surface | `prompts/doctrine/std/role_home/workflows.prompt` | generic role-home defaults | Repeated today across examples `12`, `13`, and Lessons-pressure docs. | Extract only the generic role-home defaults into Layer 2. | Avoid pack-local repetition while keeping private nouns out. | `HowToTakeATurn`, `CurrentTruthDiscipline`, `CoordinationReadbackDiscipline`, `SkillFirstSupport`. | new role-home import manifests. |
| Layer 2 portable-truth conventions | `prompts/doctrine/std/portable_truth/workflows.prompt`, `docs/STDLIB_LAYERS.md`, live stdlib docs under `docs/` | named `law` subsection conventions and composition guidance | Proven today by examples `37` and `38` but only documented in design prose. | Codify the named subsection conventions and reference workflow patterns without inventing new syntax. | Public packs and private packs need stable override points. | Named portable-truth workflow conventions under `doctrine.std.portable_truth.*`. | new manifests; docs review. |
| Layer 3 public proving pack | `prompts/doctrine/packs_public/code_review/**` (tentative) | first public pack | Not implemented. Review pressure exists in docs and examples `43` through `49`, but that pressure is still domain-shaped. | Implement one public pack that proves Layer 2 sufficiency while keeping review-specific nouns local. | Prevent Layer 2 from guessing abstractions that should be earned by a public domain. | `doctrine.packs_public.code_review.*` import namespace. | new public-pack manifests and emit targets. |
| Existing numbered corpus | `examples/12_*`, `examples/13_*`, `examples/21_*`, `examples/23_*`, `examples/24_*`, `examples/29_*`, `examples/32_*`, `examples/35_*`, `examples/36_*`, `examples/37_*`, `examples/38_*`, `examples/39_*`, `examples/43_*` through `examples/49_*` | semantic substrate examples | These examples prove the patterns Layer 2 wants, but they are local prompt roots. | Preserve them as proof anchors; do not mass-migrate them to shared-root imports in the first stdlib pass. | Avoid turning the library bootstrap into a broad corpus rewrite. | Existing examples stay semantic substrate; new examples prove shared-root stdlib imports separately. | targeted preservation manifests; `make verify-examples`. |
| New conformance examples | `examples/50_*`, `examples/51_*`, `examples/52_*` | shared-root manifests | Absent. | Add manifest-backed examples whose `prompt` entries point at shared-root stdlib and public-pack entrypoints. | Real stdlib needs proof that imports, composition, and emitted outputs work from the canonical root. | Shared-root example manifests with `cases[].prompt` overrides. | targeted `verify_corpus`; `make verify-examples`. |
| Build proof | `pyproject.toml`, `doctrine/emit_docs.py` | emit targets | Emit targets currently cover only example entrypoints under local example roots. | Add shared-root stdlib and public-pack emit targets as needed. | Prove compiled docs for shipped reusable modules without new tooling. | Additional `tool.doctrine.emit.targets` for shared-root entrypoints. | targeted `emit_docs` runs; maybe `build_contract` manifests. |
| Live docs | `docs/STDLIB_LAYERS.md`, `docs/README.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/WORKFLOW_LAW.md`, `examples/README.md` | layer and portable-truth explanations | Current docs explain the direction but not the final shared-root implementation path. | Rewrite touched live docs so they describe the shipped Layer 2 and Layer 3 boundary honestly. | Avoid a docs-only pseudo-stdlib or contradictory owner-path story. | One layer story across docs, prompts, and proof examples. | docs review; `make verify-examples` when example docs change. |
| Review-facing docs | `docs/REVIEW_SPEC.md`, `docs/FULL_REVIEW_SPEC_IMPLEMENTATION_PLAN_2026-04-10.md`, `examples/43_review_basic_verdict_and_route_coupling/**` through `examples/49_review_capstone/**` | review pressure surfaces | Real pressure exists, but the review family remains domain-shaped even after the shipped proof ladder. | Update only if the chosen public pack or extraction rules make them stale; otherwise keep them as pressure, not stdlib truth. | Prevent accidental early promotion of generic review semantics into Layer 2. | Review stays Layer 3 pressure in v1. | defer or targeted doc updates. |
| Example-agent bank | `example_agents/**` | notes, candidate tests, raw excerpts | Curated pressure only, non-authoritative. | Use as design-reference support only; do not turn it into a runtime or proof dependency. | Keep public Doctrine generic and example-first. | No new runtime contract. | no runtime tests. |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - Layer 1 semantics: `doctrine/`
  - Layer 2 authored modules: `prompts/doctrine/std/**`
  - Layer 3 public packs: `prompts/doctrine/packs_public/**`
- Deprecated APIs (if any):
  - None required for v1.
  - Existing example-local declarations such as `CurrentHandoff` and
    `RewriteRegime` remain valid semantic examples even after their generic
    Layer 2 counterparts ship.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - Do not keep a second shared authored-source root if `prompts/doctrine/std/**`
    ships.
  - Do not keep docs-only pseudo-modules that mirror shipped Layer 2 module
    names without being importable prompt files.
  - Delete any temporary vendored-copy proof setup if a shared-root proof lane
    replaces it.
- Capability-replacing harnesses to delete or justify:
  - no import-resolution rewrite in the first pass if shared-root examples and
    emit targets prove enough
  - no pack loader
  - no registry or discovery layer for stdlib modules
  - no packet runtime or fake typed handoff runtime
- Live docs/comments/instructions to update or delete:
  - `docs/STDLIB_LAYERS.md`
  - `docs/README.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/WORKFLOW_LAW.md`
  - `examples/README.md`
  - `pyproject.toml` emit-target comments or adjacent docs if shared-root build
    proof is added
- Behavior-preservation signals for refactors:
  - targeted shared-root manifest runs
  - targeted existing-example manifest runs for the substrate examples
  - `make verify-examples`
  - `make verify-diagnostics` if compiler or diagnostics wording changes
  - targeted `uv run --locked python -m doctrine.emit_docs --target ...`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Shared authored-source root | `doctrine/compiler.py::_resolve_prompt_root()`, `doctrine/verify_corpus.py::_load_case()`, `pyproject.toml` emit targets | Use one repo-level `prompts/` root plus manifest prompt overrides instead of inventing a second import system. | Prevents stdlib bootstrap from widening import semantics or duplicating modules per example. | include |
| Generic coordination carriers | `examples/32`, `35`, `36`, `37`, `38`; `docs/STDLIB_LAYERS.md` | Extract generic handoff inputs and output families into Layer 2. | Prevents repeated coordination doctrine from staying trapped in examples or public packs. | include |
| Generic role-home shells | `examples/12`, `13`; Lessons prose-bucket docs | Extract only the generic turn-discipline prose into Layer 2 role-home modules. | Prevents private-pack role-home language from becoming the hidden reusable default. | include |
| Named `law` subsection conventions | `examples/37`, `38`; `docs/WORKFLOW_LAW.md` | Standardize named subsection keys and override points in Layer 2 conventions. | Prevents each public or private pack from inventing incompatible portable-truth patch structure. | include |
| Shared review module in Layer 2 | `examples/43` through `49`, `docs/REVIEW_SPEC.md`, review plans | Promote review semantics into Layer 2 now. | The evidence is still domain-shaped and should stay in Layer 3 for now. | defer |
| Mass migration of existing numbered examples to shared-root imports | `examples/**` | Rewrite the current corpus to import Layer 2 directly. | Would widen scope from stdlib implementation into a corpus-structure rewrite. | defer |
| Import-resolution widening | `doctrine/compiler.py::_resolve_prompt_root()` | Add multi-root or workspace-wide import discovery immediately. | Not needed if shared-root entrypoints plus manifest overrides prove the stdlib cleanly. | defer |
| Private-pack implementation inside this repo | external or private pack trees, Lessons docs | Implement Layer 4 as a real pack in this public repo. | Violates the private-pack boundary and pulls private nouns into public truth. | exclude |
| Example-agent direct reuse | `example_agents/raw/**` | Import harvested wording or source trees directly into shipped stdlib or packs. | Would cargo-cult repo-local jargon and blur the source-bank boundary. | exclude |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

<!-- arch_skill:block:phase_plan:start -->
> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

Warn-first note:

- `external_research_grounding` is still not started in `planning_passes`.
- That does not block this phase plan because repo evidence is already strong
  enough to lock the owner path, the Layer 2 v1 surface, and the public-pack
  proof direction.
- If implementation uncovers a real ambiguity that current repo evidence
  cannot settle, stop and route that gap through `external-research` before
  widening the authored-source or import path.

## Phase 1 — Shared-root Layer 2 foundation

Status: COMPLETE

* Goal:
  Create the canonical shared authored-source root for stdlib work and ship the
  first Layer 2 coordination modules without widening language semantics.
* Work:
  - Create the repo-level shared prompt root for public authored modules:
    `prompts/doctrine/std/**`.
  - Implement `doctrine.std.coordination.enums`,
    `doctrine.std.coordination.inputs`, and
    `doctrine.std.coordination.outputs` using only already-earned surfaces.
  - Keep module names aligned to the public namespace `doctrine.std.*`.
  - Do not widen `doctrine/compiler.py::_resolve_prompt_root()` unless the
    shared-root proof strategy fails.
  - Add the first shared-root conformance example manifest that proves a real
    import of the Layer 2 coordination modules through `cases[].prompt`.
* Verification (smallest signal):
  - targeted `verify_corpus` runs for the new shared-root stdlib coordination
    example manifest(s)
  - targeted preservation runs for existing substrate examples `23`, `24`,
    `29`, `32`, `35`, `36`, `37`, and `38` as needed
* Docs/comments (propagation; only if needed):
  - add one short note at the canonical import-root boundary if the shared-root
    strategy would otherwise be easy to misread later
* Exit criteria:
  - shared-root stdlib modules compile and import through the canonical
    namespace `doctrine.std.*`
  - no new language semantics or import-discovery layer was required
  - the first conformance manifest proves the shared-root pattern honestly
* Rollback:
  - remove the shared-root stdlib scaffolding if the proof lane exposes a real
    import-model blocker that cannot be solved without broader semantic
    widening

## Phase 2 — Role-home and portable-truth stdlib extraction

Status: COMPLETE

* Goal:
  Ship the generic Layer 2 role-home and portable-truth conventions that the
  corpus already earns, while keeping Layer 2 explicit and patch-friendly.
* Work:
  - Implement `prompts/doctrine/std/role_home/workflows.prompt` with the
    generic role-home defaults.
  - Implement `prompts/doctrine/std/portable_truth/workflows.prompt` with named
    subsection conventions and reference workflow patterns.
  - Add shared-root conformance examples that prove:
    - role-home import and specialization
    - portable-truth import plus named `law` subsection override points
  - Keep the v1 surface explicit:
    - no workflow parameters
    - no output inheritance
    - no top-level reusable `law`
* Verification (smallest signal):
  - targeted `verify_corpus` runs for the new Layer 2 role-home and
    portable-truth manifests
  - targeted preservation runs for substrate examples `12`, `13`, `37`, `38`,
    and `39`
* Docs/comments (propagation; only if needed):
  - update live docs where they would otherwise keep describing the Layer 2
    surface as design-only
* Exit criteria:
  - Layer 2 now carries the generic role-home and portable-truth surfaces
    without private nouns
  - import/patch examples prove the intended override model
  - no unsupported core feature was smuggled in to make the modules feel more
    abstract than the language allows
* Rollback:
  - revert the extracted modules if they depend on unshipped semantics or if
    the conformance examples can only pass by duplicating private-pack logic

## Phase 3 — Public Layer 3 proving pack

Status: COMPLETE

* Goal:
  Implement one public proving pack that demonstrates Layer 2 sufficiency
  without turning review or another domain into the hidden reusable framework.
* Work:
  - Implement the first public pack under
    `prompts/doctrine/packs_public/<pack>/**`, with `code_review` as the
    default candidate.
  - Keep domain nouns, domain outputs, and domain workflows local to the pack.
  - Import Layer 2 directly for generic coordination, portable-truth, and
    role-home structure.
  - Record every extracted-generic candidate that should move downward into
    Layer 2 instead of staying trapped in the pack.
  - Keep any still-domain-shaped review abstractions out of Layer 2.
* Verification (smallest signal):
  - targeted shared-root manifests for the public pack
  - at least one emitted-doc proof target for the public pack if the pack is
    meant to ship readable compiled output
* Docs/comments (propagation; only if needed):
  - update review-facing docs only if the chosen public pack would otherwise
    leave them stale or contradictory
* Exit criteria:
  - the public pack proves that Layer 2 is real and reusable
  - Layer 3 did not become the reusable foundation
  - any newly discovered generic pieces are named for downward extraction
* Rollback:
  - revert the pack if it can only work by pulling private nouns into Layer 2
    or by forcing unearned review abstractions into the core library layer

## Phase 4 — Docs, proof, and build alignment

Status: COMPLETE

* Goal:
  Make the live docs, manifests, and emitted-build proof tell the same layer
  story as the shipped modules.
* Work:
  - Update:
    - `docs/STDLIB_LAYERS.md`
    - `docs/README.md`
    - `docs/LANGUAGE_DESIGN_NOTES.md`
    - `docs/AGENT_IO_DESIGN_NOTES.md`
    - `docs/WORKFLOW_LAW.md`
    - `examples/README.md`
  - Add or update shared-root emit targets in `pyproject.toml` when stdlib or
    public-pack build proof is required.
  - Add any missing `build_contract` or render-contract proof that is required
    to keep emitted outputs honest.
  - Delete any docs-only pseudo-module path or temporary shared-root shim that
    the implementation no longer needs.
* Verification (smallest signal):
  - targeted manifest runs for the new shared-root examples
  - targeted `doctrine.emit_docs --target ...` runs for stdlib/public-pack
    build proof
* Docs/comments (propagation; only if needed):
  - keep the docs map and any new README notes aligned to the shipped owner
    paths
* Exit criteria:
  - live docs describe the shipped stdlib and public-pack layout honestly
  - no conflicting physical-path story survives in docs
  - build proof follows the same authored-source root and module namespace
* Rollback:
  - revert doc/build alignment changes that outrun the shipped modules or keep
    stale paths alive

## Phase 5 — Final verification and cleanup

Status: COMPLETE

* Goal:
  Prove the full stdlib-layer implementation end to end and remove stale
  parallel paths.
* Work:
  - run `uv sync`
  - run `make verify-examples`
  - run `make verify-diagnostics` only if compiler or diagnostics changed
  - run `cd editors/vscode && make` only if editor surfaces changed
  - confirm there is exactly one shared authored-source root for Layer 2 and
    Layer 3
  - confirm the public docs no longer imply a literal `doctrine/std/*.prompt`
    path if the shipped physical path is the shared-root `prompts/` layout
* Verification (smallest signal):
  - `make verify-examples`
  - `make verify-diagnostics` when needed
  - `cd editors/vscode && make` when needed
* Docs/comments (propagation; only if needed):
  - clean up any final stale comments or docs references discovered during the
    verification pass
* Exit criteria:
  - the full shipped corpus still passes
  - the new shared-root stdlib and public-pack proof lanes pass
  - there is no docs-only pseudo-stdlib and no second shared authored-source
    root
* Rollback:
  - reopen the earliest failing phase and revert only the latest convergence
    layer that introduced the regression instead of adding fallbacks
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Prefer manifest-backed example cases that directly prove Layer 2 exports,
  pack imports, and preserved portable-truth behavior.
- If the work changes diagnostics, run `make verify-diagnostics`.
- Avoid new proof machinery unless an existing lane cannot catch a real risk.

## 8.2 Integration tests (flows)

- Run `make verify-examples` for any implementation that changes shipped
  behavior, example imports, or rendered outputs.
- Use shared-root import-based example flows, via manifest `prompt` overrides
  when needed, to prove that Layer 2 is real authored doctrine and not just
  copied prose.
- Add targeted `doctrine.emit_docs --target ...` proof when shipped stdlib or
  public-pack compiled output is part of the changed surface.

## 8.3 E2E / device tests (realistic)

- No device surface is expected for the core layer split itself.
- If the implementation changes VS Code grammar, navigation, or highlighting,
  run `cd editors/vscode && make`.
- Keep any manual compile/render smoke short and finalization-oriented.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- No runtime fallback rollout is allowed.
- Roll forward in layer order: shared-root Layer 2 foundation, role-home and
  portable-truth extraction, public-pack proving ground, then docs/proof/build
  follow-through.
- Delete or rewrite stale live truth surfaces in the same run when a layer
  decision becomes shipped reality.

## 9.2 Telemetry changes

No telemetry changes are obvious yet. If implementation introduces any new
verification or compile-time reporting for stdlib imports, capture that during
`deep-dive` rather than assuming it now.

## 9.3 Operational runbook

- Keep `doctrine/` as the semantic owner.
- Keep Layer 2 import surfaces documented where authors will actually use them.
- Keep `example_agents/` in the design-reference lane and out of runtime truth.

# 10) Decision Log (append-only)

## 2026-04-10 - Treat `docs/STDLIB_LAYERS.md` as directional contract, not shipped truth

### Context

The repo already has a strong stdlib-layer direction doc, a shipped workflow-
law corpus, and a curated `example_agents/` source bank. The user asked for a
detailed plan to fully implement the stdlib layering according to that
direction and to use example-agent use cases to keep the layers clearly
separable.

### Options

- Treat `docs/STDLIB_LAYERS.md` as already authoritative and plan directly from
  it.
- Ignore `docs/STDLIB_LAYERS.md` and derive a fresh layering model from code
  and examples alone.
- Use `docs/STDLIB_LAYERS.md` as the directional target, but ground every
  implementation decision in shipped Doctrine truth and treat `example_agents/`
  as pressure only.

### Decision

Use `docs/STDLIB_LAYERS.md` as the directional contract, but keep shipped
Doctrine truth in `doctrine/`, the core docs, and manifest-backed examples as
the authority for what can actually be implemented now. Use `example_agents/`
only to sharpen separation boundaries and extraction rules.

### Consequences

- The plan can honor the user's intended Layer 2 direction without pretending
  the direction is already implemented.
- Research and deep-dive must explicitly distinguish "earned by current
  Doctrine" from "good future pressure."
- Layer 2 will be judged against both current language support and real
  cross-source use cases for clear separability.

### Follow-ups

- Confirm the North Star before moving into `research`.
- During `research`, turn the seeded example-agent pressures into adopted or
  rejected boundary rules.

## 2026-04-10 - Use a shared repo-level `prompts/` root for Layer 2 and Layer 3 modules

### Context

The direction doc repeatedly sketches `doctrine.std.*` and
`doctrine.packs_public.*` as the desired module namespaces, but the shipped
compiler resolves imports only under the nearest `prompts/` root. A literal
`doctrine/std/*.prompt` path would therefore not be importable by the current
module loader on its own.

### Options

- Change import resolution first so modules can live anywhere in the repo.
- Materialize the public module namespaces under one shared repo-level
  `prompts/` root that the current compiler can already load.
- Vendor stdlib modules into each proof example's local `prompts/` root.

### Decision

Use one shared repo-level `prompts/` root as the physical authored-source home
for Layer 2 and Layer 3:

- `prompts/doctrine/std/**`
- `prompts/doctrine/packs_public/**`

Keep the public module namespace as `doctrine.std.*` and
`doctrine.packs_public.*`, and use manifest `prompt` overrides plus ordinary
emit targets to prove the shared-root layout without widening import
semantics in the first pass.

### Consequences

- The repo can ship a real stdlib and public-pack layer without inventing a
  second import system.
- Existing numbered examples remain semantic substrate rather than becoming a
  mandatory migration project.
- Live docs must distinguish the public module namespace from the physical
  authored-source path honestly.

### Follow-ups

- Add shared-root conformance examples that prove stdlib imports directly.
- Revisit import-resolution widening only if later adoption work cannot be
  served by shared-root entrypoints and manifest `prompt` overrides.

## 2026-04-10 - Let manifest prompt overrides resolve from the repo root, while keeping refs example-local

### Context

Shared-root stdlib proof depends on manifest `default_prompt` and
case-specific `prompt` fields being able to point at
`prompts/doctrine/std/**` and `prompts/doctrine/packs_public/**`. The shipped
verifier previously resolved those prompt paths only relative to the owning
example directory, which made the shared-root layout compile honestly through
the compiler but fail to prove honestly through `verify_corpus`.

### Options

- Keep verifier prompt paths example-local and vendor shared-root entrypoints
  back into every example.
- Widen verifier prompt resolution for manifest-owned prompt entrypoints while
  leaving `approx_ref` and checked refs rooted in the owning example.
- Change compiler import semantics instead of fixing the verifier path
  mismatch.

### Decision

Resolve manifest `default_prompt` and case-level `prompt` entries under
`REPO_ROOT` in `doctrine/verify_corpus.py`, while keeping `approx_ref` and
other reference-material paths constrained to the owning example directory.

### Consequences

- Shared-root stdlib and public-pack examples can now prove the real shipped
  authored-source layout without vendored copies.
- Ref locality stays honest: checked render/build refs still live with the
  owning example.
- No compiler import widening or alternate prompt loader was required.

### Follow-ups

- Keep any future shared-root proof surfaces on manifest prompt overrides
  unless there is a real reason to widen the import model itself.

## 2026-04-10 - Keep generic coordination trust carriers unconditional in Layer 2 outputs

### Context

The first shared coordination outputs were intended to encode generic portable-
truth carrier families once, in Layer 2. During implementation, the shipped
guard rules from examples `39` and `49` mattered: ordinary output guards
cannot read imported input conventions and cannot read emitted output fields.

### Options

- Add new output-guard semantics so shared Layer 2 outputs can branch on input
  conventions or emitted fields.
- Duplicate coordination output families across each example or pack so every
  local caller can re-author its own guards.
- Keep the generic trust-carrier outputs explicit and unconditional, and let
  workflows plus `law` decide when a carrier is current or relevant.

### Decision

Keep the shared coordination carrier outputs unconditional in
`prompts/doctrine/std/coordination/outputs.prompt`, and express turn-specific
currentness through workflow/law structure rather than through output guards.

### Consequences

- Layer 2 stays output-heavy, explicit, and inside already-earned semantics.
- Shared coordination outputs remain reusable across route-only, portable-
  truth, and review-shaped packs without hidden guard coupling.
- The implementation does not invent a second semantic plane just to make the
  stdlib feel more abstract.

### Follow-ups

- If a future design wants more compact output branching, earn that in Layer 1
  first instead of hiding it in stdlib conventions.

## 2026-04-10 - Use examples `50` through `52` for stdlib proof lanes

### Context

The implementation plan originally sketched new stdlib proof examples in the
mid-40s. The shipped corpus already uses examples `43` through `49` for the
review ladder, so reusing those numbers would blur review truth with stdlib
conformance proof.

### Options

- Renumber the review ladder.
- Reuse the mid-40s and let stdlib proof examples collide conceptually with
  the review family.
- Start the shared-root stdlib and public-pack proof lanes at `50`.

### Decision

Use:

- `examples/50_stdlib_coordination`
- `examples/51_stdlib_role_home_and_portable_truth`
- `examples/52_public_code_review_pack`

### Consequences

- The shipped review ladder remains intact and easy to read.
- Shared-root stdlib proof sits clearly after the current Layer 1 example
  ladder instead of overlapping it.
- Docs, manifests, and emitted-build proof now reference one coherent set of
  example numbers.

### Follow-ups

- Keep future stdlib-layer proof examples above the current shipped ladder
  unless the example index is intentionally reorganized.
