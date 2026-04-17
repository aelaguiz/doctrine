---
title: "Doctrine - Skill Package Host Bindings Without Markdown Bloat - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/THIN_HARNESS_FAT_SKILLS.md
  - docs/SKILL_PACKAGE_MULTI_FILE_PROMPT_OUTPUTS_2026-04-16.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/SKILL_PACKAGE_AUTHORING.md
  - docs/AUTHORING_PATTERNS.md
  - doctrine/_compiler/constants.py
  - doctrine/_compiler/resolved_types.py
  - doctrine/_compiler/compile/skill_package.py
  - doctrine/_compiler/context.py
  - doctrine/emit_skill.py
  - examples/122_skill_package_emit_documents/prompts/SKILL.prompt
  - examples/123_skill_package_emit_documents_mixed_bundle/prompts/SKILL.prompt
---

# TL;DR

## Outcome

Doctrine gets a first-class way for a whole skill-package prompt tree to bind
to parent agent surfaces strongly, so authors can move real procedure into fat
skills without repeating the same inputs, outputs, and final-output language in
thin agent homes.

## Problem

Today inline `skill` and `skills` are addressable inside `AGENTS.prompt`, but
`skill package` is a separate emit surface. Downstream authors can move method
into `SKILL.prompt`, and now also into prompt-authored emitted docs under
`emit:` or bundled `agents/**/*.prompt`, but the package tree cannot bind to
the host agent's typed surfaces. That leaves repeated host-specific glue in
inline skill bridges and agent bodies, which is exactly the kind of duplication
the thin-harness, fat-skills model should remove.

## Approach

Add one explicit package contract plus one explicit call-site bind, and make
that contract visible across every prompt-authored artifact the skill package
emits while keeping the binding metadata out of emitted Markdown by default:

- package-side `host_contract:` on `skill package`
- call-site `bind:` on skill entries inside `skills` blocks
- reserved `host:` refs across the prompt-authored emitted skill tree

Bind by reference, not by expansion. `SKILL.md`, emitted companion docs, and
bundled agent markdown stay lean. Typed truth lives in compiler-owned contract
data and fail-loud validation, not in copied prose.

## Plan

Add package discovery, package-side host-slot declarations, whole-tree `host:`
refs, and agent-side bind validation in one coherent feature. Then prove the
zero-bloat rule with manifest-backed examples and emit checks that show:

- `bind:` and `host_contract:` add zero required Markdown lines
- the same host contract works in:
  - the root `SKILL.prompt` body
  - `emit:`-compiled `document` outputs
  - bundled `agents/**/*.prompt` markdown outputs
- package refs fail loud when missing, mistyped, or over-broad
- the useful host surfaces that drive repeated IO prose now bind cleanly

## Non-negotiables

- No magical full parent scope.
- No parent prose expansion into `SKILL.md` or `AGENTS.md`.
- No new always-on Markdown bulk for correct usage.
- No hidden title inference or import-order tricks for package lookup.
- No soft fallback when a bind is missing, wrong, or category-wrong.
- No harness-owned state, scheduling, or tool orchestration in this feature.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-17
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None. Focused host-binding and emit suites passed, `make verify-diagnostics`
  passed, and `make verify-examples` passed on 2026-04-17.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-17
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-17
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine adds explicit host binding for `skill package` through a semantic
`host_contract:` plus call-site `bind:` plus reserved `host:` refs, then
downstream repos can move reusable process into `SKILL.prompt` and still talk
about the parent agent's typed surfaces with strong compile-time binding across
the whole prompt-authored skill tree, while emitted Markdown stays flat because
the binding data never renders as copied host prose.

## 0.2 In scope

- Add a package-side host-contract surface on `skill package`.
- Add a non-rendered package link on inline `skill` declarations so the agent
  compiler can find the target package contract without new import syntax.
- Add a non-rendered `bind:` block on skill entries inside `skills` blocks.
- Add reserved `host:` refs across every prompt-authored artifact the skill
  package emits:
  - root `SKILL.prompt` prose
  - `document` declarations compiled through `emit:`
  - bundled `agents/**/*.prompt` markdown outputs
- Support the host-surface families that remove the real repeated IO and
  result-carrier boilerplate:
  - `input`
  - `output`
  - `document`
  - `analysis`
  - `schema`
  - `table`
  - `final_output`
- Support child-path binding on those families when the bound target is
  already addressable in Doctrine today.
- Use one package host contract for the whole emitted skill tree. Do not make
  authors redeclare host slots inside emitted docs or bundled agent prompts.
- Fail loud on:
  - missing package links
  - unknown host slots
  - missing binds
  - extra binds
  - family mismatch
  - invalid child paths
- Keep `host_contract:` and `bind:` out of emitted Markdown by default.
- Once `package:`, `host_contract:`, and `bind:` exist, require no extra
  per-artifact opt-in. `host:` should just work in every prompt-authored
  emitted artifact the package already compiles.
- Keep one `host:` spelling across supported artifact kinds. Do not invent
  artifact-local variants of the same reference.
- Emit package contract data in a machine-readable sidecar so external tools
  do not need to reparse emitted Markdown to discover the binding contract.
- Update examples, emit checks, and public docs for the new surface.
- Allow internal compiler convergence where needed so inline skill and package
  binding reuse one canonical resolution and validation story.

## 0.3 Out of scope

- Free `parent.*` access from `SKILL.prompt`.
- Artifact-local `host_contract:` blocks in emitted docs or bundled agent
  prompts.
- Binding to arbitrary parent prose fragments, anonymous sections, or runtime
  state that Doctrine does not already model as a typed or addressable surface.
- Expanding host inputs, outputs, or documents into emitted Markdown.
- A new general macro system, export system, or repo-wide package import
  language.
- Runtime scheduling, tool routing, or harness memory behavior.
- Solving every future cross-surface reuse problem in the same feature.
- Raw bundled helper files such as `.py`, `.yaml`, or plain `.md`. They stay
  byte-preserved and never see package host context.
- Non-emitted prompt-bearing subtrees. If a prompt file is compiler-owned and
  not emitted into the package tree, it does not gain `host:` access in this
  feature.
- Review or route internals unless a later deep-dive proves they are needed
  for the same repeated-IO problem family.

## 0.4 Definition of done (acceptance evidence)

- A package-backed inline `skill` can declare which `skill package` it points
  to through a non-rendered semantic field.
- A `skill package` can declare host slots once and use them through `host:`
  refs across the whole prompt-authored emitted tree without rendering the
  contract block into Markdown.
- A skill entry can bind those slots to real host targets in the agent's own
  prompt graph once for the whole package tree without rendering the bind map
  into `AGENTS.md`.
- The compiler validates slot coverage, family compatibility, and child-path
  validity against the concrete bound host targets.
- A representative bound-skill example proves zero extra emitted Markdown
  lines from `host_contract:` and `bind:` themselves.
- `emit_skill` emits one package contract sidecar that records host refs per
  emitted artifact path for package discovery and external tooling.
- Public docs explain the feature in generic Doctrine terms and keep the
  thin-harness, fat-skills line clear.
- New examples and smoke checks prove success cases and fail-loud cases.

## 0.5 Key invariants (fix immediately if violated)

- No new parallel binding model for inline skills versus package-backed skills.
- No package binding feature that depends on copying host Markdown into the
  package.
- No root-only binding story that ignores emitted docs or bundled agent
  prompts.
- No per-artifact enable switches for package host binding.
- No implicit package lookup based on title text alone.
- No untyped or all-scope host access.
- No per-artifact host-contract duplication inside one package tree.
- No bind coverage gaps hidden behind best-effort or advisory fallback.
- No Markdown bloat from semantic-only binding declarations.
- No drift between package contract truth, agent bind truth, and any prompt-
  authored artifact emitted from the skill tree.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Keep emitted Markdown flat.
2. Make fat skills able to bind to host IO and result surfaces strongly.
3. Keep the feature explicit and fail loud.
4. Reuse current Doctrine addressable and contract machinery where it fits.
5. Keep the public story small and elegant.

## 1.2 Constraints

- `SkillPackageDecl` is a separate public surface today. It is not a readable
  or addressable root in the shipped resolver.
- `emit_target_skill` already writes one root `SKILL.md` plus every compiled
  package file, which today includes `emit:` docs, bundled agent markdown, and
  raw bundled files.
- Skill packages already have prompt-authored companion-doc outputs through
  `emit:` and prompt-authored bundled-agent outputs under `agents/**/*.prompt`.
- Bundled agent prompts compile in their own nested `CompilationSession`, so
  whole-tree host binding needs explicit context propagation. It does not fall
  out of the root package compile path automatically.
- Inline `skill` and `skills` are semantic and compact today. We must not turn
  their rendered form into a metadata dump.
- The real user pressure is repeated inputs, outputs, documents, and final
  output carriers, not import syntax.
- Package-backed binding needs a stable lookup path from `AGENTS.prompt` to
  `SKILL.prompt` without forcing a new import model into every agent file.

## 1.3 Architectural principles (rules we will enforce)

- Bind by reference, not by expansion.
- Keep package contracts semantic by default. Do not render them as prose.
- Make package lookup explicit.
- Keep host-slot vocabulary small and typed.
- Make authoring learnable in one pass:
  - declare `host_contract:` once
  - bind once at the consuming skill entry
  - use `host:` anywhere in the prompt-authored emitted package tree
- Do not require artifact-kind-specific setup when the package already emits
  that prompt-authored artifact family.
- Reuse current addressable child-path rules instead of inventing a second path
  language.
- Keep the agent home thin. Put reusable method in the package and exact host
  truth in typed binds.

## 1.4 Known tradeoffs (explicit)

- This adds authored syntax, but it removes larger repeated prose blocks.
- Explicit package links are one more authored field, but they avoid brittle
  slug-title inference.
- Zero Markdown growth means some truth must live in sidecars and compiler
  contracts instead of rendered prose.
- Full parity with every exotic addressable surface would overreach. The first
  cut should cover the families that actually kill the repeated IO boilerplate.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Inline `skill` declarations are readable semantic objects used inside
  `AGENTS.prompt` and `SOUL.prompt`.
- Inline `skills` blocks carry role-specific skill relationships and render
  compactly.
- `skill package` in `SKILL.prompt` is a separate package-emission surface.
- Downstream repos already use the thin bridge plus fat package pattern:
  - an inline skill bridge in `skills.prompt`
  - an agent skill entry in `AGENTS.prompt`
  - a real `SKILL.prompt` package for the heavy procedure
  - prompt-authored companion docs under `emit:`
  - sometimes bundled agent prompts under `agents/**/*.prompt`

## 2.2 What’s broken / missing (concrete)

- The package cannot declare typed host dependencies.
- The agent cannot bind host surfaces into the package contract.
- Package prose cannot refer to those host surfaces with compile-time checking.
- Authors repeat the same input, output, and final-output language in inline
  bridges and local agent prose because the reusable package cannot own it.

## 2.3 Constraints implied by the problem

- The solution must preserve the clean split between inline skill semantics and
  package emission.
- The solution must not solve the problem by inflating rendered Markdown.
- The solution must let agents keep small inline skill bridges while the
  package owns the real method.
- The compiler needs a real package lookup path once `bind:` is introduced.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- No external system is the primary spec here. Doctrine already has the right
  shape for the key rule: semantic surfaces for exact truth and rendered
  Markdown only where it earns its keep.
- The best external-style anchor is the repo's own thin-harness, fat-skills
  doctrine in `docs/THIN_HARNESS_FAT_SKILLS.md`.

## 3.2 Internal ground truth (code as spec)

- Package/object model:
  - `doctrine/_model/io.py`
  - `SkillPackageDecl` now carries `name`, `title`, `items`, `metadata`, and
    `emit_entries`
- Prompt-authored emitted artifact families in a skill tree today:
  - root `SKILL.prompt` body -> `SKILL.md`
  - `emit:` `DocumentDecl` refs -> companion `.md` files
  - bundled `agents/**/*.prompt` -> bundled agent markdown companions compiled
    in a nested `CompilationSession`
- Raw bundled helper files in the skill tree still copy through byte for byte.
- Inline skill addressability:
  - `doctrine/_compiler/resolved_types.py`
  - `ReadableDecl` includes `SkillDecl`, but not `SkillPackageDecl`
  - `AddressableRootDecl` includes `ReadableDecl` and `SkillsDecl`, but not
    `SkillPackageDecl`
- Readable and addressable registries:
  - `doctrine/_compiler/constants.py`
  - includes `skill declaration` and `skills block`
  - excludes `skill package`
- Skill-package emission path:
  - `doctrine/_compiler/compile/skill_package.py`
  - `doctrine/emit_skill.py`
  - current output already includes:
    - `SKILL.md`
    - `emit:` document companions
    - bundled agent markdown companions
    - raw bundled files
- Multi-file package compatibility anchor:
  - `docs/SKILL_PACKAGE_MULTI_FILE_PROMPT_OUTPUTS_2026-04-16.md`
  - `examples/122_skill_package_emit_documents`
  - `examples/123_skill_package_emit_documents_mixed_bundle`
- Inline skill-entry rendering path:
  - `doctrine/_model/workflow.py`
  - `SkillEntry` already carries record-body items, so `bind:` can live there
    as semantic metadata without inventing a new call-site container
  - `doctrine/_compiler/compile/agent.py`
  - `_compile_resolved_skill_entry` already strips `requirement` and `reason`
    into compact rendered output, which is the right precedent for a
    non-rendered `bind:`
- Separate nested-session boundary that must be handled explicitly:
  - `doctrine/_compiler/compile/skill_package.py`
  - bundled agent prompts compile in a fresh nested `CompilationSession`, so
    package host context has to be carried into that path deliberately
- Downstream pressure that proves the need:
  - `../psflows/flows/lessons/prompts/shared/skills.prompt`
  - `../psflows/flows/lessons/prompts/agents/section_architect/AGENTS.prompt`
  - `../psflows/skills/psmobile-lesson-section-architect-pipeline/prompts/SKILL.prompt`
  - the package owns the real method, but the host-agent IO truth still lives
    outside the emitted skill tree

## 3.3 Decision gaps that must be resolved before implementation

No architecture blocker remains beyond North Star confirmation. This plan
chooses these defaults as the implementation path:

- use explicit non-rendered `package:` on inline `skill` declarations
- use non-rendered `host_contract:` on `skill package`
- use non-rendered `bind:` on skill entries
- use one reserved package-scoped `host:` root across all prompt-authored
  emitted artifacts in the skill tree
- allow `host:` in:
  - authored interpolation everywhere those artifacts already allow
  - ordinary addressable/readable ref surfaces where the artifact family
    already accepts `Decl:path`
- keep the root `SKILL.prompt` body interpolation-only because record bodies do
  not accept bare `path_ref` lines today
- emit one `SKILL.contract.json` that records referenced host paths per emitted
  artifact path
- do not add an agent-side Markdown or contract dump in the first cut

If later deep-dive finds that external runtimes truly need emitted agent-side
skill-binding metadata, that should be an additive follow-up only if the
zero-Markdown rule still holds.
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)

<!-- arch_skill:block:current_architecture:start -->
## 4.1 On-disk structure

- Grammar and parser:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/_parser/skills.py`
  - `doctrine/_parser/parts.py`
- Model:
  - `doctrine/_model/io.py`
  - `doctrine/_model/workflow.py`
- Indexing and session:
  - `doctrine/_compiler/indexing.py`
  - `doctrine/_compiler/session.py`
- Resolver and compiler:
  - `doctrine/_compiler/constants.py`
  - `doctrine/_compiler/resolved_types.py`
  - `doctrine/_compiler/resolve/addressables.py`
  - `doctrine/_compiler/resolve/skills.py`
  - `doctrine/_compiler/compile/skill_package.py`
  - `doctrine/_compiler/compile/agent.py`
- Package layout:
  - `doctrine/_compiler/package_layout.py`
- Emit:
  - `doctrine/emit_skill.py`

## 4.2 Control paths (runtime)

1. `CompilationSession.compile_skill_package()` delegates to
   `CompilationContext.compile_skill_package()`, which chooses one
   `SkillPackageDecl` from `IndexedUnit.skill_packages_by_name` and compiles it
   through `_compile_skill_package_decl()`.
2. `_compile_skill_package_decl()` builds a package output registry with
   compiler-owned `SKILL.md`, renders the root package body through
   `_compile_record_support_items()`, compiles `emit:` documents through
   `_compile_skill_package_emitted_docs()`, and gathers bundled files through
   `_compile_skill_package_bundle_files()`.
3. `_compile_skill_package_emitted_docs()` resolves each `SkillPackageEmitEntry`
   to a `DocumentDecl`, compiles it through `_compile_document_decl()`, and
   renders companion Markdown with `render_readable_block()`.
4. `_compile_skill_package_bundle_files()` walks the package tree, preserves
   ordinary files byte for byte, skips prompt-owned reserved subtrees, and
   special-cases bundled `agents/**/*.prompt` files.
5. `_compile_skill_package_nested_prompt()` reparses each bundled agent prompt,
   creates a fresh nested `CompilationSession`, requires exactly one concrete
   agent, and renders that agent to a sibling `.md` file.
6. `emit_target_skill()` writes root `SKILL.md` first and then writes every
   compiled package file. There is no extra sidecar or package contract payload
   today.
7. Inline skill use stays separate:
   - `SkillDecl` lives in `IndexedUnit.skills_by_name`
   - `_resolve_skill_entry()` resolves only inline skill targets
   - `_compile_resolved_skill_entry()` renders `purpose`, `requirement`,
     `reason`, and extra skill prose, but it has no package-link or bind truth

## 4.3 Object model + key abstractions

- `IndexedUnit` is the canonical indexed lookup owner for:
  - `skills_by_name`
  - `skill_packages_by_name`
  - `skills_blocks_by_name`
- `SkillDecl` in `doctrine/_model/io.py` owns inline reusable skill semantics.
- `SkillEntry` in `doctrine/_model/workflow.py` owns a skill relationship at
  the call site.
- `SkillPackageDecl` in `doctrine/_model/io.py` owns root package prose,
  package metadata, and `emit_entries`.
- `ResolvedSkillEntry` carries:
  - `metadata_unit`
  - `target_unit`
  - `skill_decl`
  - authored entry items
  but no package contract or bind truth today.
- There is no current object that represents:
  - package host-slot requirements
  - one package-scoped host context shared across the emitted prompt tree
  - package-to-inline skill linkage
  - agent-side binding of host surfaces into a package
  - artifact-by-artifact host-ref inventory for the emitted skill tree

## 4.4 Observability + failure behavior today

- A package can enforce only current package-bundle rules today:
  - source path is required for package compilation
  - `emit:` outputs must end in `.md`
  - `emit:` refs must resolve to `DocumentDecl`
  - bundled prompt-bearing agent files must define exactly one concrete agent
  - output-path collisions fail through the package output registry
- A package still cannot declare or validate parent-agent dependencies today.
- A skill entry still cannot bind parent-agent declarations into a package
  today.
- If a downstream author wants the root package body, emitted companion docs, or
  bundled agent prompts to refer to host-agent truth, they must duplicate that
  truth outside the package or accept loose prose.
- `emit_target_skill()` emits no package contract sidecar, so external tooling
  has no machine-readable host-binding surface to read.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.
<!-- arch_skill:block:current_architecture:end -->

# 5) Target Architecture (to-be)

<!-- arch_skill:block:target_architecture:start -->
## 5.1 On-disk structure (future)

- Grammar additions in `doctrine/grammars/doctrine.lark`
- Parser updates in:
  - `doctrine/_parser/skills.py`
  - `doctrine/_parser/parts.py` for parser-owned host-contract and bind body
    parts that keep lowering explicit and typed
- Model additions in:
  - `doctrine/_model/io.py` for:
    - package host-slot contract types
    - inline skill package-link metadata
  - `doctrine/_model/workflow.py` for skill-entry bind metadata
- Indexing and session updates in:
  - `doctrine/_compiler/indexing.py`
  - `doctrine/_compiler/session.py`
- Resolver and contract updates in:
  - `doctrine/_compiler/resolved_types.py`
  - `doctrine/_compiler/resolve/addressables.py`
  - `doctrine/_compiler/resolve/refs.py`
  - `doctrine/_compiler/resolve/skills.py`
- Compile and emit updates in:
  - `doctrine/_compiler/compile/skill_package.py`
  - `doctrine/_compiler/compile/agent.py`
  - `doctrine/_compiler/package_layout.py`
  - `doctrine/emit_skill.py`

## 5.2 Control paths (future)

1. `SKILL.prompt` declares a semantic `host_contract:` block.
2. That one package host contract is automatically in scope for every
   prompt-authored artifact the package emits:
   - the root `SKILL.prompt` body
   - every `document` compiled through `emit:`
   - every bundled `agents/**/*.prompt` markdown output
   - with no artifact-local opt-in, no per-artifact contract block, and no
     alternate host-root spelling
3. `host:` participates in the same reference families the current artifact
   already supports:
   - authored interpolation everywhere
   - ordinary addressable/readable refs where the artifact family already
     accepts `Decl:path`
   - the root `SKILL.prompt` body stays interpolation-only because record bodies
     do not accept bare `path_ref` lines today
4. Package compile validates declared slot names and records referenced host
   paths per emitted artifact. Concrete child-path validity is checked later,
   after the slot is bound to a real host target.
5. Inline `skill` declarations can declare `package: "package-id"` as a
   semantic link to the package contract.
6. Agent skill entries can declare `bind:` to map package slots onto concrete
   host targets.
7. Package-id lookup is explicit and fail loud:
   - Doctrine checks visible package ids first through the current unit,
     visible imports, and imported symbols
   - if that set finds nothing, Doctrine scans other `SKILL.prompt`
     entrypoints under the active prompt roots
   - duplicate matches fail loud instead of guessing
8. Agent compile resolves the package link, loads the package contract, and
   validates one bind map for the whole emitted skill tree against the concrete
   host target family and path.
9. `host:` is resolved as a package-scoped synthetic root inside
   `resolve/addressables.py`; it does not turn `SkillPackageDecl` into a
   general readable or addressable root in the public registries.
10. Bundled agent prompt compilation inherits the same package host context
    through the nested-session path instead of defining a second local contract
    model.
11. Rendered Markdown stays compact:
  - `host_contract:` does not render into `SKILL.md`
  - `package:` does not render into inline skill output
  - `bind:` does not render into `AGENTS.md`
  - in standalone `SKILL.md`, `{{host:slot_key}}` renders to the slot title
  - in standalone `SKILL.md`, `{{host:slot_key.path.to.child}}` renders to
    `<slot title>:path.to.child`
  - emitted docs and bundled agent markdown use the same symbolic render rule
12. `SKILL.contract.json` becomes a compiler-owned sibling path in the same
    package output registry that already reserves `SKILL.md`, so sidecar
    emission cannot silently collide with raw bundled files or emitted docs.
13. `emit_target_skill()` writes `SKILL.contract.json` beside `SKILL.md` from
    compiled package truth, not by reparsing rendered Markdown.

## 5.3 Object model + abstractions (future)

Exact authored syntax in the first cut:

`SKILL.prompt`

```prompt
from refs.query_patterns import QueryPatterns

skill package SectionPipelineSkillPackage: "Section Pipeline Skill"
    metadata:
        name: "section-pipeline-skill"
        description: "Run the section pipeline with strong host binding."

    emit:
        "references/query-patterns.md": QueryPatterns

    host_contract:
        input previous_turn: "Previous Turn"
        input issue_ledger: "Issue Ledger"
        document section_map: "Section Map"
        output issue_note: "Issue Note"
        output turn_result: "Turn Result"
        final_output final_response: "Final Response"

    "Read {{host:previous_turn}} before you start."
    "Use {{host:section_map.lesson_count_and_order.title}} when you write the map."
    "Emit through {{host:final_response}}."
```

Emitted companion document in `refs/query_patterns.prompt`

```prompt
document QueryPatterns: "Query Patterns"
    section summary: "Summary"
        "Ground each query against {{host:issue_ledger}}."
        "Keep {{host:section_map.lesson_count_and_order.title}} stable."
```

Bundled agent prompt in `agents/reviewer.prompt`

```prompt
agent Reviewer:
    role: "Review the package output."
    workflow: "Review"
        output: "Output"
            host:issue_note
        "Flag drift between {{host:issue_note}} and {{host:final_response}}."
```

Inline skill bridge in `AGENTS.prompt`

```prompt
skill SectionPipelineSkill: "section-pipeline-skill"
    purpose: "Run the section pipeline."
    package: "section-pipeline-skill"
```

Skill entry bind in `AGENTS.prompt`

```prompt
skills SectionSkills: "Skills"
    skill section_pipeline: skills.SectionPipelineSkill
        requirement: Required
        bind:
            previous_turn: inputs:previous_turn
            issue_ledger: inputs:issue_ledger
            section_map: SectionMapDocument
            issue_note: outputs:issue_note
            turn_result: outputs:turn_result
            final_response: final_output
```

Whole-tree compatibility rule in the first cut:

- The `bind:` map applies to the whole emitted skill tree, not only the root
  `SKILL.prompt` body.
- Authors learn one rule: declare once, bind once, then use `host:` anywhere
  the emitted prompt artifact already supports refs.
- `refs/*.prompt` documents emitted through `emit:` automatically see the same
  package host context. They declare no local `host_contract:`.
- Bundled `agents/**/*.prompt` outputs automatically see the same package host
  context. They also declare no local `host_contract:`.
- No emitted document or bundled agent declares its own enable switch,
  package link, or alternate `host_*` syntax.
- Raw bundled helper files never see host context because Doctrine preserves
  them byte for byte.

Bind-target syntax in the first cut:

- agent-relative bind roots:
  - `inputs:<local_key>`
  - `inputs:<local_key>.path.to.child`
  - `outputs:<local_key>`
  - `outputs:<local_key>.path.to.child`
  - `analysis`
  - `analysis:path.to.child`
  - `final_output`
  - `final_output:path.to.child`
- declaration-root bind refs:
  - `Decl`
  - `Decl:path.to.child`

Bind resolution rules in the first cut:

- `inputs`, `outputs`, `analysis`, and `final_output` are reserved bind roots.
- Those reserved roots resolve against the consuming concrete agent, not
  against the `skills` declaration file that authored the bind.
- Bare declaration refs still resolve through normal module/import rules from
  the authored `skills` declaration.
- Every slot declared in `host_contract:` must be bound exactly once in the
  first cut.
- No per-slot optionality ships in the first cut. If a package needs a host
  slot, the consuming skill entry must bind it.
- The one bind map satisfies every prompt-authored emitted artifact in the
  package tree.

Package lookup rules in the first cut:

- `package:` takes a string package id.
- That id matches `metadata.name` on the target `skill package`.
- If `metadata.name` is omitted, the id falls back to the `skill package`
  declaration key.
- Lookup is explicit and two-step:
  - Doctrine checks the current visible/imported package-id set first
  - if that set finds nothing, Doctrine scans other `SKILL.prompt`
    entrypoints under the active prompt roots
  - ambiguous matches fail loud
- A skill entry may not use `bind:` unless its target inline skill declares
  `package:`.

Render rules in the first cut:

- `host_contract:` does not render into `SKILL.md`.
- `package:` does not render into inline skill output.
- `bind:` does not render into `AGENTS.md`.
- Across all prompt-authored emitted artifacts:
  - `{{host:section_map}}` renders as `Section Map`
  - `{{host:section_map.lesson_count_and_order.title}}` renders as
    `Section Map:lesson_count_and_order.title`
  - bare `host:issue_note` renders through the same readable/addressable label
    path ordinary `Decl:path` refs already use for that artifact family
- At bind-validation time, Doctrine checks that the concrete bound target
  really supports the referenced child path.
- No emitted artifact gets extra Markdown lines just because it participated in
  host binding.

`SKILL.contract.json` shape in the first cut:

```json
{
  "contract_version": 1,
  "package": {
    "name": "section-pipeline-skill",
    "title": "Section Pipeline Skill"
  },
  "host_contract": {
    "previous_turn": {
      "family": "input",
      "title": "Previous Turn"
    },
    "issue_ledger": {
      "family": "input",
      "title": "Issue Ledger"
    },
    "section_map": {
      "family": "document",
      "title": "Section Map"
    },
    "issue_note": {
      "family": "output",
      "title": "Issue Note"
    },
    "turn_result": {
      "family": "output",
      "title": "Turn Result"
    },
    "final_response": {
      "family": "final_output",
      "title": "Final Response"
    }
  },
  "artifacts": {
    "SKILL.md": {
      "kind": "skill_package_root",
      "referenced_host_paths": [
        "previous_turn",
        "section_map.lesson_count_and_order.title",
        "final_response"
      ]
    },
    "references/query-patterns.md": {
      "kind": "document",
      "source": "refs.query_patterns.QueryPatterns",
      "referenced_host_paths": [
        "issue_ledger",
        "section_map.lesson_count_and_order.title"
      ]
    },
    "agents/reviewer.md": {
      "kind": "agent",
      "source": "agents/reviewer.prompt",
      "referenced_host_paths": [
        "issue_note",
        "final_response"
      ]
    }
  }
}
```

- `SkillPackageHostSlot`
  - slot key
  - display title
  - family
- `SkillPackageContract`
  - package id
  - package title
  - declared host slots
  - emitted-artifact host-ref inventory
- `SkillPackageLink`
  - inline skill declaration field that ties a semantic inline skill to a
    package contract by package id
- `SkillEntryBind`
  - call-site mapping from slot key to one concrete bind target ref
- `BoundSkillHostTarget`
  - resolved family
  - resolved concrete root
  - resolved child path
  - display label used for standalone package render
- `SkillPackageArtifactHostRefs`
  - emitted artifact path
  - artifact kind
  - source declaration or prompt
  - referenced host paths

These objects should be compiler-owned semantic truth. They should not be
modeled as rendered Markdown fields.

## 5.4 Invariants and boundaries

- `host_contract:` is semantic-only by default.
- `bind:` is semantic-only by default.
- `package:` is semantic-only by default.
- Package lookup is explicit through `package:`, not through title guessing.
- `host:` is a reserved package-scoped addressable/interpolation root available
  only inside prompt-authored artifacts emitted from a skill package.
- `host:` refs may point only to declared slots.
- No emitted artifact in the package tree may declare a second local
  `host_contract:`.
- Slot families may bind only to supported target families.
- Child-path validation must reuse Doctrine's current addressable rules.
- Standalone package render may use slot titles and literal child-path tails
  only. It may not expand bound host content.
- No copied host readable blocks appear anywhere in the emitted skill tree.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not UI work.
<!-- arch_skill:block:target_architecture:end -->

# 6) Call-Site Audit (exhaustive change inventory)

<!-- arch_skill:block:call_site_audit:start -->
## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Grammar | `doctrine/grammars/doctrine.lark` | skill-package and skill-entry grammar | no host-contract or bind syntax | add `host_contract:`, `package:`, and `bind:` grammar | feature entrypoints need first-class syntax | semantic-only package and bind fields | parser smoke, new examples |
| Parser | `doctrine/_parser/skills.py` | `skill_package`, `skill_entry`, inline `skill` | package and skill entry bodies are just ordinary record items | parse and lower semantic host and bind parts into typed model objects | compile phase needs structured truth, not ad hoc record scanning | typed host-slot and bind nodes | parser tests |
| Model | `doctrine/_model/io.py` | `SkillDecl`, `SkillPackageDecl` | inline skills have no package link; skill packages have no host-binding contract field | add inline skill package-link metadata, package host-contract model, and emitted-artifact host-ref inventory | package lookup and package truth belong on the package-facing model surfaces | `SkillPackageLink`, `SkillPackageHostSlot`, `SkillPackageArtifactHostRefs` | model consumers |
| Model | `doctrine/_model/workflow.py` | `SkillEntry` | no bind model | add typed bind data on skill entries | call-site bind truth belongs with the consuming relationship | `SkillEntryBind` | resolver and compile tests |
| Indexing | `doctrine/_compiler/indexing.py` | `IndexedUnit.skills_by_name`, `IndexedUnit.skill_packages_by_name` | indexing knows declaration names, but not package ids derived from `metadata.name` | add canonical package-id lookup and duplicate-id validation across the visible compile graph | explicit `package:` lookup must be fail loud and stable | canonical package-id resolution surface | indexing and compile tests |
| Resolve | `doctrine/_compiler/constants.py` | readable and addressable registries | no package-aware host namespace | add package host-ref handling without making skill packages general readable roots | keep categories clean while enabling package refs | reserved package-scoped `host:` namespace | ref-resolution tests |
| Resolve | `doctrine/_compiler/resolve/refs.py` | `_decl_lookup_targets()` family | current lookup works only on declaration names inside the visible compile graph | add package-id lookup that follows the same local-plus-imported visibility rules | package links should resolve with the same import and ambiguity rules as other Doctrine refs | package-id lookup helper | resolve tests |
| Resolve | `doctrine/_compiler/resolve/addressables.py` | addressable and interpolation resolver | only current declaration roots work | validate `host:` refs against package contract slots and record child paths across the root package body, emitted docs, and bundled agents | whole-tree prompt-authored package artifacts need compile-time checking | package host-ref resolution path | interpolation tests, readable-ref tests |
| Resolve | `doctrine/_compiler/resolve/skills.py` | skill-entry resolution | skill entries resolve only inline skill semantics | resolve package link and bind metadata at call site | strong host binding needs end-to-end validation | package-backed skill-entry resolution | bind validation tests |
| Context/session | `doctrine/_compiler/session.py`, `doctrine/_compiler/context.py` | root session plus nested bundled-agent session | bundled `agents/**/*.prompt` compile in a fresh nested session with no package host context | propagate one package host context through nested agent compilation and emitted-document compilation | root-only host binding would miss prompt-authored artifacts elsewhere in the skill tree | package host compile context | compile tests, mixed-tree examples |
| Package layout | `doctrine/_compiler/package_layout.py` | package output registry | registry reserves `SKILL.md` and current compiled outputs only | reserve `SKILL.contract.json` as a compiler-owned output path and keep collision rules fail loud | sidecar output should reuse the same package collision boundary as existing compiled outputs | compiler-owned sidecar path | emit smoke, collision tests |
| Compile | `doctrine/_compiler/compile/skill_package.py` | root package body, `emit:` docs, nested bundled agents | package compile has no host contract or artifact host-ref payload | omit `host_contract:` from Markdown, apply one host context across all emitted prompt artifacts, and build package contract payload with per-artifact refs | zero-bloat whole-tree package emit | `SKILL.contract.json` payload with `artifacts` map | emit smoke, example refs |
| Compile | `doctrine/_compiler/compile/agent.py` | `_compile_resolved_skill_entry` | renders all extra skill-entry fields except `requirement` and `reason` | consume `bind:` as semantic-only metadata and validate it against the whole package tree contract | zero-bloat agent emit | non-rendered bind metadata | agent emit checks |
| Emit | `doctrine/emit_skill.py` | `emit_target_skill` | emits `SKILL.md`, emitted docs, bundled agents, and raw files | also emit `SKILL.contract.json` with per-artifact host-ref inventory | external tools should not reparse emitted Markdown | package contract sidecar | emit smoke |
| Docs | `docs/LANGUAGE_REFERENCE.md` | skills and package sections | no host-binding story | document new syntax and zero-bloat rule | public surface must be clear | new language reference text | docs alignment |
| Docs | `docs/SKILL_PACKAGE_AUTHORING.md` | package guide | no host contract guidance | add package-side authoring rules | downstream authors need real guidance | host-contract guide | docs alignment |
| Docs | `docs/THIN_HARNESS_FAT_SKILLS.md` | design rule | no concrete package binding example | add one compact example and rule text | feature exists to serve this rule | durable design note | docs alignment |
| Proof | `examples/` | skill-package ladder | no package binding examples | add new manifest-backed examples for success and fail-loud cases, including mixed trees with `emit:` docs and bundled agents | feature needs shipped proof | new examples after `123` | `make verify-examples` |

## 6.2 Migration notes

- Canonical owner path:
  - package contract truth should live with `skill package`
  - call-site binding truth should live with the skill entry in the consuming
    agent
  - package host context propagation should stay in the skill-package compile
    and nested-session boundary, not in ad hoc per-artifact shims
- Adjacent surfaces that must move together:
  - grammar
  - parser
  - model
  - indexing
  - resolver
  - compile
  - package layout
  - session/context
  - `emit_skill`
  - docs
  - manifest-backed examples
  - emit smoke checks
- Compatibility posture:
  - additive public feature
  - no silent behavior change for existing skills or packages
  - no title-based package inference in the initial cut
  - preserve existing multi-file package outputs from `emit:` and bundled
    `agents/**/*.prompt`
- Deprecated APIs:
  - none in the first cut
- Delete list:
  - none in Doctrine
- Capability-replacing harnesses to delete or justify:
  - none in Doctrine
  - this feature should replace repeated host-IO prose and ad hoc package glue,
    not introduce expansion helpers, mirror package trees, or agent-side bind
    dumps
- Live docs/comments/instructions to update or delete:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/SKILL_PACKAGE_AUTHORING.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/THIN_HARNESS_FAT_SKILLS.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/SKILL_PACKAGE_MULTI_FILE_PROMPT_OUTPUTS_2026-04-16.md`
- Behavior-preservation signals:
  - all existing skill-package examples continue to emit the same Markdown
  - all existing inline skill examples continue to emit the same Markdown
  - `examples/122` and `examples/123` continue to emit the same file trees
    when no host-binding syntax is used
  - new semantic-only fields do not appear in rendered output

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Package lookup | `doctrine/_compiler/indexing.py`, `doctrine/_compiler/context.py` | one canonical package-id lookup path for `package:` | avoids split lookup rules between compile, resolve, and emit code | include |
| Ref visibility | `doctrine/_compiler/resolve/refs.py`, `doctrine/_compiler/resolve/skills.py` | package-id lookup follows existing visible/imported-unit rules | avoids inventing a second import-visibility model just for package-backed skills | include |
| Package outputs | `doctrine/_compiler/package_layout.py`, `doctrine/emit_skill.py` | reserve compiler-owned sidecar paths in the same package output registry as `SKILL.md` | avoids silent path collisions and special-case emit logic | include |
| Mixed package outputs | `doctrine/_compiler/compile/skill_package.py`, `examples/122_*`, `examples/123_*` | one package-scoped host context across every prompt-authored emitted artifact | avoids root-only host binding and keeps multi-file skill packages coherent | include |
| Downstream fat skills | `../psflows/skills/**/prompts/SKILL.prompt`, `../psflows/flows/**/AGENTS.prompt` | replace repeated host-IO prose with package contract plus bind once Doctrine ships | real downstream pressure exists, but it is not Doctrine implementation scope | defer |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

<!-- arch_skill:block:phase_plan:start -->
## Phase 1 - Package contract and explicit package discovery

Status: COMPLETE

Goal

Give package-backed skills a typed host contract and give the agent compiler a
real way to find that contract for the whole emitted skill tree.

Work

Add the semantic package link and package-side host-slot contract first. Do
not touch rendering yet beyond making sure the new fields stay invisible.

Checklist (must all be done)

- Add grammar for:
  - inline skill `package:`
  - package `host_contract:`
- Add typed model support for package links, host slots, and artifact-level
  host-ref inventory.
- Resolve package-backed inline skills through explicit `package:` links.
- Reject missing or unknown package names when a feature path needs a package
  contract.
- Reject ambiguous visible package-id matches and duplicate visible package ids
  for `package:` lookup.
- Keep new semantic fields out of rendered Markdown.
- Define one package-host compile context that later phases can reuse for the
  root package body, emitted docs, and nested bundled agents.

Verification (required proof)

- parser tests for the new fields
- compile tests for:
  - missing package links
  - unknown package links
  - ambiguous visible package-id matches
- one example that uses `package:` without any host refs and proves no render
  drift

Docs/comments (propagation; only if needed)

- add one short code comment at the canonical package-lookup boundary if the
  new discovery rule is not obvious from the code alone

Exit criteria (all required)

- Package-backed skill discovery is explicit and fail loud.
- `package:` and `host_contract:` do not render into Markdown.
- The package host context model is shaped once at the package root and is not
  redefined per artifact.
- Existing skill and skill-package examples still emit the same Markdown.

Rollback

Revert the new semantic fields and package lookup together. Do not leave a
half-implicit discovery path behind.

## Phase 2 - Host refs and bind validation

Status: COMPLETE

Goal

Make prompt-authored package artifacts able to talk about declared host slots
and make agent call sites bind those slots to real host surfaces with full
fail-loud checks across the whole emitted skill tree.

Work

Introduce reserved `host:` refs in the root package body, emitted docs, and
bundled agent prompts, plus a non-rendered `bind:` block on skill entries.
Validate concrete host bindings against the package contract and the actual
addressable host surface.

Checklist (must all be done)

- Add `host:` ref parsing and resolution for:
  - root package body
  - emitted `document` outputs
  - bundled `agents/**/*.prompt`
- Record referenced slot paths per emitted artifact in the package contract.
- Add `bind:` parsing and typed model support on skill entries.
- Require complete bind coverage for declared host slots.
- Reject extra bind keys.
- Validate slot-family compatibility.
- Validate child paths against the bound concrete target.
- Support `final_output` as a first-class bind family.
- Propagate package host context through the nested bundled-agent session path.

Verification (required proof)

- one success example for whole-surface binding
- one success example for child-path binding
- one success example for `final_output`
- one mixed-tree example where the same bind set covers:
  - the root `SKILL.prompt` body
  - one emitted document
  - one bundled agent prompt
- fail-loud examples for:
  - missing bind
  - extra bind
  - wrong family
  - invalid child path

Docs/comments (propagation; only if needed)

- add one short comment where `host:` refs are kept semantic and non-expanding,
  if that boundary is easy to miss in the resolver

Exit criteria (all required)

- A package can declare host slots and reference them in prose.
- Emitted docs and bundled agent prompts can use the same `host:` root without
  local contract duplication.
- A consuming agent can bind those slots to real host surfaces.
- Every invalid bind shape fails loud.
- `bind:` does not render into `AGENTS.md`.

Rollback

Revert the `host:` and `bind:` feature together. Do not keep one without the
other.

## Phase 3 - Zero-bloat render path and package contract emit

Status: COMPLETE

Goal

Keep emitted Markdown flat and make package contract truth available without
parsing visible Markdown anywhere in the emitted skill tree.

Work

Render package host refs through slot display labels only across the whole
emitted prompt tree. Emit one package contract sidecar with per-artifact host
refs. Do not add agent-side Markdown or contract dumps in the first cut.

Checklist (must all be done)

- Define how `{{host:slot_key}}` and `{{host:slot_key.path.to.child}}` render
  in:
  - `SKILL.md`
  - emitted document companions
  - bundled agent markdown companions
- Keep that rendering inline and compact.
- Emit `SKILL.contract.json` from `emit_skill`.
- Reserve `SKILL.contract.json` through the package output registry so path
  collisions fail loud.
- Put host-slot declarations and referenced host paths per emitted artifact in
  the sidecar.
- Keep `AGENTS.md` unchanged aside from existing authored skill prose.
- Prove that adding `host_contract:` and `bind:` changes no rendered Markdown
  lines by itself.

Verification (required proof)

- emit smoke checks for `SKILL.contract.json`
- collision tests for reserved `SKILL.contract.json` output paths
- example golden outputs that prove:
  - no `host_contract:` block appears in `SKILL.md`
  - no `bind:` block appears in `AGENTS.md`
  - correct host refs render as compact inline text only in the root package body,
    emitted docs, and bundled agents

Docs/comments (propagation; only if needed)

- document the zero-bloat rule clearly in the package and language docs

Exit criteria (all required)

- The clean path adds zero emitted Markdown lines from semantic binding data.
- `SKILL.contract.json` exists and matches the package contract truth.
- `SKILL.contract.json` carries per-artifact host refs for every prompt-authored
  emitted artifact that used `host:`.
- No agent-side sidecar is needed to satisfy the first-cut use case.

Rollback

Remove sidecar emission with the host-binding feature if the render path cannot
stay zero-bloat.

## Phase 4 - Public proof, docs, and release alignment

Status: COMPLETE

Goal

Ship the feature as a coherent public surface with proof and guidance.

Work

Add examples, smoke checks, docs, and release notes as one bundle.

Checklist (must all be done)

- Add manifest-backed examples for:
  - minimal host contract
  - whole-surface bind
  - child-path bind
  - mixed-tree bind across root package, emitted doc, and bundled agent
  - fail-loud invalid bind cases
- Update:
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/SKILL_PACKAGE_AUTHORING.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/THIN_HARNESS_FAT_SKILLS.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/SKILL_PACKAGE_MULTI_FILE_PROMPT_OUTPUTS_2026-04-16.md`
- Classify release-surface disposition explicitly in this phase:
  - if this implementation is also the current public release cut for the
    feature, update `docs/VERSIONING.md` and `CHANGELOG.md`
  - otherwise defer those two files explicitly to the release cut and do not
    treat them as implemented here
- Keep examples generic. Do not import downstream product names into shipped
  Doctrine docs.

Verification (required proof)

- `make verify-examples`
- relevant emit smoke checks
- any targeted unit tests added for grammar, resolver, or emit behavior

Docs/comments (propagation; only if needed)

- none beyond the public docs listed above

Exit criteria (all required)

- The new surface is proven in the corpus.
- The public docs tell one consistent story.
- The release surfaces are aligned if this phase ships the feature.

Rollback

Do not ship partial docs or proof. Revert the public surface if the feature is
not ready to support.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- parser tests for `package:`, `host_contract:`, and `bind:`
- resolver tests for `host:` refs across:
  - the root `SKILL.prompt` body
  - `emit:` companion docs
  - bundled `agents/**/*.prompt`
- validation tests for:
  - missing package link
  - unknown package
  - ambiguous visible package-id match
  - missing bind
  - extra bind
  - family mismatch
  - invalid child path
- emit tests for `SKILL.contract.json`
- package-output collision tests for reserved `SKILL.contract.json`

## 8.2 Integration tests (flows)

- manifest-backed examples that prove both success and fail-loud cases
- emitted Markdown golden checks that prove semantic binding fields do not
  render
- one representative mixed-tree package-backed skill example that proves the
  zero-bloat rule end to end across the root package body, emitted docs, and
  bundled agents

## 8.3 E2E / device tests (realistic)

Not needed beyond corpus and emit proof for the Doctrine repo itself. A real
downstream adoption pass in `psflows` is good follow-through after the Doctrine
feature ships, but it should not be the gating proof for Doctrine's own repo.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship as an additive language feature.
- Keep existing inline skill and skill-package authoring valid.
- Treat `docs/VERSIONING.md` and `CHANGELOG.md` as release-cut surfaces, not as
  silent implementation follow-through. Update them in the same phase only when
  this work is the current public release cut for the feature.
- Teach one small authoring pattern:
  - link the package once
  - declare the host contract once
  - bind once at the consuming skill entry
  - use `host:` across the emitted prompt tree
- Encourage adoption first where fat skills already exist and host-IO
  duplication is the real pain.

## 9.2 Telemetry changes

None in Doctrine itself.

## 9.3 Operational runbook

If a downstream repo wants the feature, it must:

1. declare an explicit `package:` link on the inline skill
2. declare package-side `host_contract:`
3. add call-site `bind:` where the skill is used
4. write host-aware text only with `host:` in prompt-authored package artifacts
5. keep prompt-authored package artifacts generic and typed instead of copying
   host IO prose

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter and `planning_passes`
  - `# TL;DR`
  - `# 0)` through `# 10)`
  - helper-block drift
  - Section 7 obligation coverage against Sections 5 and 6
- Findings summary:
  - one carried live-doc obligation was missing from Phase 4
  - release-surface disposition needed to be stated explicitly instead of left
    as a soft conditional
- Integrated repairs:
  - added `docs/SKILL_PACKAGE_MULTI_FILE_PROMPT_OUTPUTS_2026-04-16.md` to the
    Phase 4 docs update list
  - made Phase 4 release-surface handling explicit for
    `docs/VERSIONING.md` and `CHANGELOG.md`
  - aligned Section 9 rollout wording with that release-surface rule
  - tightened package-id lookup wording so fail-loud ambiguity and visible
    import behavior say the same thing in Sections 5, 7, and 8
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

## 2026-04-16 - Choose semantic host binding over parent-scope interpolation

Context

The requested use case is a thin inline bridge plus a fat reusable
`SKILL.prompt` package. The package needs strong host binding without becoming
a second agent file.

Options

- give `SKILL.prompt` free parent-agent scope access
- expand host surfaces into the package at emit time
- add explicit package-side contract plus call-site bind

Decision

Choose explicit package-side contract plus call-site bind.

Consequences

- the feature stays explicit and typed
- the package stays reusable
- the compiler can fail loud
- emitted Markdown can stay flat

Follow-ups

- keep the slot-family surface small in the first cut
- revisit extra host families only after real use proves they matter

## 2026-04-16 - Keep binding metadata out of rendered Markdown

Context

The ask explicitly wants no Markdown bloat, ideally zero new lines for correct
skill-to-agent binding usage.

Options

- render host contracts and bind maps into visible Markdown
- hide them in compiler-owned semantic data and sidecars

Decision

Hide binding data in semantic compiler truth and package sidecars. Render only
compact slot labels where prompt-authored emitted package artifacts actually
mention them.

Consequences

- `SKILL.md` and `AGENTS.md` stay small
- public docs need to explain the semantic-only rule clearly
- external tooling should read the sidecar instead of scraping Markdown

Follow-ups

- prove the zero-bloat rule with emitted golden outputs
- do not add agent-side sidecars unless a later use case really needs them

## 2026-04-17 - Make host binding package-scoped across the emitted prompt tree

Context

Doctrine already ships multi-file skill-package prompt outputs. A package can
emit prompt-authored companion docs through `emit:` and bundled agent prompts
through `agents/**/*.prompt`. A host-binding feature that only works in root
`SKILL.prompt` would leave the rest of that prompt tree behind and force more
local glue.

Options

- bind only the root `SKILL.prompt` body
- add per-artifact opt-in or local contract blocks
- make one package-scoped host context available across all prompt-authored
  emitted artifacts

Decision

Use one package-scoped host context across every prompt-authored emitted
artifact the package already compiles. Do not require per-artifact opt-in,
local contract duplication, or alternate host-ref syntax.

Consequences

- authors learn one small pattern instead of an artifact matrix
- emitted docs and bundled agents get full binding parity with the root
  package body
- nested bundled-agent compilation must receive package host context
  deliberately

Follow-ups

- keep raw bundled helper files out of scope
- prove mixed-tree success and fail-loud cases in the corpus

## 2026-04-17 - Reuse the existing package output registry for sidecar emission

Context

The feature needs one `SKILL.contract.json` sidecar, but skill packages already
have one compiler-owned package output registry that guards `SKILL.md`,
emitted docs, bundled agents, and raw bundled files against collisions.

Options

- write `SKILL.contract.json` ad hoc in `emit_target_skill()`
- reserve `SKILL.contract.json` in the existing package output registry and
  emit it from compiled package truth

Decision

Reserve `SKILL.contract.json` in the existing package output registry and emit
it from compiled package truth.

Consequences

- sidecar emission reuses the same collision boundary as other compiled package
  outputs
- emit code stays single-source instead of growing a second path-allocation
  rule
- package compile must return enough structured truth for sidecar emission

Follow-ups

- add emit smoke and collision tests for the reserved sidecar path

## 2026-04-17 - Make package-id lookup follow existing visible-import rules

Context

Inline skills need explicit `package:` lookup, but Doctrine already has one
ref-visibility model through local declarations, visible imported modules, and
imported symbols. A package-backed skill feature should not invent a second
visibility story.

Options

- resolve package ids through a separate repo-wide package scan
- resolve package ids through the current visible/imported-unit lookup model

Decision

Resolve package ids through the current visible/imported-unit lookup model, with
fail-loud ambiguity when more than one visible package id matches.

Consequences

- package-backed skills reuse Doctrine's current import and ambiguity rules
- the feature avoids a second discovery model just for packages
- package-id lookup needs a compiler-owned helper over indexed visible units

Follow-ups

- add resolve tests for local, imported, and ambiguous package-id cases
