---
title: "Doctrine - Skill Package Multi-File Prompt Outputs - Architecture Plan"
date: 2026-04-16
status: complete
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/SKILL_PACKAGE_AUTHORING.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/EMIT_GUIDE.md
  - doctrine/_compiler/compile/skill_package.py
  - doctrine/_compiler/context.py
  - examples/58_readable_document_blocks/prompts/AGENTS.prompt
  - examples/95_skill_package_minimal/prompts/SKILL.prompt
  - examples/96_skill_package_references/prompts/SKILL.prompt
---

# TL;DR

## Outcome

Doctrine skill packages gain one explicit `emit:` block that lets `SKILL.prompt`
compile a root `SKILL.md` plus any number of companion `.md` files from prompt
authored `document` declarations.

This shipped cleanly into the later package host-binding work too.
`emit:` docs, bundled agent prompts, and the root package body now share one
package-scoped host-binding model instead of three local ones.

## Problem

Today `skill package` can emit only the root `SKILL.md`, raw bundled files, and
special-cased bundled agent prompts. Real skills therefore mix Doctrine-authored
root prompts with hand-authored Markdown companions, or they rely on path magic
that does not generalize cleanly.

## Approach

Keep `SKILL.prompt` as the single package entrypoint. Add a package-owned
artifact map on `skill package` that binds package-relative output paths to
`document` declarations. Keep raw file bundling unchanged. Reject hardcoded
`references/` behavior, reject prompt-subdir auto-discovery, and keep `SKILL.md`
implicit for backward compatibility.

Compatibility note:

- the later `host_contract:` and `bind:` feature layers onto this package tree
  without changing `emit:` syntax
- `host:` now works across the root package body, emitted docs, and bundled
  agent prompts when those prompt artifacts already support refs

## Plan

Research the current package emitter and document compiler paths, design one
clean `emit:` syntax and fail-loud contract, implement it in parser/model and
skill-package compile, add one or two focused corpus examples, then update the
package docs, language reference, emit guide, and tests together.

## Non-negotiables

- No hardcoded `references/` surface.
- No per-file compile targets in `pyproject.toml` for one skill package.
- No prompt-subdir auto-discovery or path magic.
- No regression to the current `SKILL.md` root package convention.
- No silent collisions with raw bundled files or compiled agent outputs.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-16
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

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine adds one explicit package-level `emit:` block on `skill package`,
then authors can keep one `SKILL.prompt` entrypoint and emit `SKILL.md` plus as
many companion `.md` files as they need from prompt-authored `document`
declarations, without hardcoding special directories, without widening
`pyproject.toml`, and without falling back to hand-authored Markdown for the
same package.

## 0.2 In scope

- Add a first-class `emit:` block on `skill package`.
- Keep `SKILL.prompt` as the one package entrypoint configured in
  `pyproject.toml`.
- Keep `SKILL.md` as the implicit root artifact for backward compatibility.
- Let each `emit:` entry map one package-relative `.md` output path to one
  `document` declaration.
- Allow those `document` declarations to live in any imported prompt module
  layout under the package source tree.
- Keep ordinary bundled non-prompt files copying through byte for byte.
- Keep the current `agents/**/*.prompt` behavior working unless later phases
  deliberately converge it onto the same artifact model.
- Update docs, tests, and examples together.

Exact target syntax to plan around:

```prompt
from refs.query_patterns import QueryPatterns
from refs.receipts_template import ReceiptsTemplate
from refs.runtime_and_commands import RuntimeAndCommands

skill package PokerKbInterface: "Poker KB Interface"
    metadata:
        name: "poker-kb-interface"
        description: "Ground poker wording and claims against books."

    emit:
        "references/query-patterns.md": QueryPatterns
        "references/receipts-template.md": ReceiptsTemplate
        "references/runtime-and-commands.md": RuntimeAndCommands

    "Use this skill when poker wording or concept grounding needs books-based proof."
    "Keep the root file short. Put the deeper procedure in the emitted docs."
```

Exact source-tree example to preserve in the North Star:

```text
prompts/
|-- SKILL.prompt
|-- refs/
|   |-- query_patterns.prompt
|   |-- receipts_template.prompt
|   `-- runtime_and_commands.prompt
|-- scripts/
|   `-- poker_kb.py
`-- agents/
    `-- openai.yaml
```

Exact emitted-tree example to preserve in the North Star:

```text
build/
|-- SKILL.md
|-- references/
|   |-- query-patterns.md
|   |-- receipts-template.md
|   `-- runtime-and-commands.md
|-- scripts/
|   `-- poker_kb.py
`-- agents/
    `-- openai.yaml
```

## 0.3 Out of scope

- Renaming the root artifact from `SKILL.md` to `SKILLS.md`.
- Hardcoding `references/`, `examples/`, `playbooks/`, or any other special
  directory name into the language.
- Auto-compiling every `.prompt` file found under a package subtree.
- Moving multi-file package ownership into `pyproject.toml`.
- Adding a second package entrypoint model.
- Adding a general-purpose macro or templating system.
- Solving every future bundled-agent convergence question in the same first cut
  unless the deeper pass proves that is the cleanest minimal shape.

## 0.4 Definition of done (acceptance evidence)

- A skill package can author the exact `emit:` syntax above and compile cleanly.
- The root package still emits `SKILL.md` from the `skill package` body.
- At least one companion `.md` file emits from a `document` declaration in an
  imported prompt module.
- At least one example proves several companion docs in one package.
- The package emitter fails loud on:
  - non-`.md` output paths
  - invalid relative paths
  - collisions with `SKILL.md`
  - collisions with raw bundled files
  - collisions with compiled agent outputs
  - wrong-kind refs
  - missing refs
- Public docs teach the new package artifact model clearly and still explain the
  unchanged raw-bundle behavior.
- Relevant tests pass, plus the shipped example corpus passes for the affected
  surfaces.

## 0.5 Key invariants (fix immediately if violated)

- No hardcoded `references/` semantics.
- No prompt-subdir auto-discovery.
- No new package source of truth outside `SKILL.prompt`.
- No change to the current root `SKILL.md` convention in this feature.
- No dual authoring path where the same companion doc must exist in both prompt
  and raw Markdown form.
- No silent path collisions or overwrite behavior.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Keep the package surface explicit and small.
2. Let authors emit many prompt-authored docs from one skill package.
3. Reuse Doctrine's existing `document` surface instead of inventing a second
   Markdown mini-language.
4. Preserve the current raw bundled-file story.
5. Keep future convergence with bundled agent outputs possible.

## 1.2 Constraints

- The current package compiler emits only `SKILL.md`, raw bundle files, and a
  special bundled-agent path.
- `SKILL.md` is already the public root artifact convention across docs,
  examples, and emit code.
- `document` is already Doctrine's authored Markdown declaration surface.
- The repo docs currently teach raw bundled Markdown companions as the package
  pattern, so docs drift must be corrected in the same change.

## 1.3 Architectural principles (rules we will enforce)

- One package entrypoint, one package-owned artifact map.
- Explicit emitted artifacts beat path magic.
- `document` owns authored companion Markdown.
- Raw files stay raw bundle files.
- Fail loud on ambiguity and collisions.

## 1.4 Known tradeoffs (explicit)

- An `emit:` block adds one authored surface, but it removes the need for
  hand-authored Markdown companions in Doctrine-backed packages.
- Keeping `SKILL.md` implicit is slightly asymmetric, but it preserves the
  current public surface cleanly.
- Limiting the first cut to `document` outputs keeps the feature elegant, even
  if a later pass may want to unify bundled-agent prompt outputs too.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine skill packages currently have three behaviors:

- compile the root `skill package` body to `SKILL.md`
- copy non-prompt files through byte for byte
- special-case `agents/**/*.prompt` into compiled Markdown companions

## 2.2 What’s broken / missing (concrete)

- Prompt-authored companion docs outside the root `SKILL.md` have no first-class
  emit path.
- Real skills therefore mix Doctrine source with raw Markdown companions.
- The current docs teach raw source-root bundle files as the answer, which is
  workable but not the cleanest authoring story when the companion docs
  themselves want Doctrine structure and reuse.

## 2.3 Constraints implied by the problem

- The right fix must preserve `SKILL.md`.
- The right fix must not widen `pyproject.toml` into a per-package artifact map.
- The right fix must not depend on magic subdirectory discovery.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- Local downstream consumer evidence in `../psflows` — adopt as the motivating
  real-world shape, not as a language constraint:
  - prompt-authored skills such as
    `../psflows/skills/psmobile-lesson-poker-kb-interface/prompts/SKILL.prompt`
    already point at several companion docs under `references/*.md`
  - several other downstream skills still ship hand-authored `SKILL.md` plus
    raw Markdown companions under `references/` or `reference_excerpts/`
  - this proves the user need is real: one skill package often wants one short
    root doc plus several separately loadable Markdown companions

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/_compiler/compile/skill_package.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/compile/skill_package.py:44)
    — current package emit owns the source-root scan, root `SKILL.md`, raw
    bundle copy-through, and the special bundled-agent prompt path
  - [doctrine/_compiler/compile/skill_package.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/compile/skill_package.py:116)
    — only `agents/**/*.prompt` compiles into extra Markdown companions today
  - [doctrine/_compiler/context.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/context.py:189)
    — the compiler already exposes standalone readable-declaration compilation
    for `document`
  - [examples/58_readable_document_blocks/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/58_readable_document_blocks/prompts/AGENTS.prompt:3)
    — `document` already owns rich authored Markdown structure
  - [doctrine/_compiler/package_layout.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/package_layout.py:31)
    — package output registration, path normalization, and collision checking
    already exist and are the right enforcement boundary
- Canonical path / owner to reuse:
  - [doctrine/_compiler/compile/skill_package.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/compile/skill_package.py:173)
    — the skill-package compiler should own the new emitted-companion-doc map
  - [doctrine/_compiler/context.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/context.py:224)
    — `compile_readable_declaration("document", ...)` is the clean existing path
    for companion Markdown generation
- Adjacent surfaces tied to the same contract family:
  - [docs/SKILL_PACKAGE_AUTHORING.md](/Users/aelaguiz/workspace/doctrine/docs/SKILL_PACKAGE_AUTHORING.md:79)
    — package authoring guide currently teaches raw bundled Markdown as the
    normal story
  - `docs/LANGUAGE_REFERENCE.md` and `docs/EMIT_GUIDE.md` — both describe the
    current source-root package model and must stay aligned
  - `examples/95` through `103` — current skill-package example ladder; at
    least one or two examples need to move the public story forward
  - [tests/test_emit_skill.py](/Users/aelaguiz/workspace/doctrine/tests/test_emit_skill.py:18)
    and `tests/test_compile_diagnostics.py` — current proof surfaces for emit
    behavior and fail-loud package boundaries
  - [skills/agent-linter/prompts/SKILL.prompt](/Users/aelaguiz/workspace/doctrine/skills/agent-linter/prompts/SKILL.prompt:49)
    plus `skills/agent-linter/prompts/references/*.md` — Doctrine's own
    first-party skill package currently uses raw bundled Markdown companions
- Compatibility posture (separate from `fallback_policy`):
  - preserve existing contract — keep implicit root `SKILL.md`, keep raw
    bundled non-prompt files working, and add `emit:` as an additive package
    surface rather than replacing the current raw bundle model
- Existing patterns to reuse:
  - [doctrine/_compiler/package_layout.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/package_layout.py:50)
    — explicit path registration and collision checks
  - [doctrine/_compiler/context.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/context.py:189)
    — readable declaration compilation entrypoint
  - `CompiledSkillPackageFile` in the current skill-package compile path — the
    existing carrier for additional emitted package files
- Prompt surfaces / agent contract to reuse:
  - [doctrine/grammars/doctrine.lark](/Users/aelaguiz/workspace/doctrine/doctrine/grammars/doctrine.lark:837)
    — `skill package` currently owns only `metadata:` plus ordinary record
    items, so the new surface should extend that same package-local contract
  - `document` declarations already define authored Markdown semantics; the new
    feature should reuse that surface instead of inventing a second Markdown DSL
- Duplicate or drifting paths relevant to this change:
  - raw bundled companion docs in
    `skills/agent-linter/prompts/references/*.md` and multiple `../psflows`
    skills — today the repo and downstream consumers both model multi-file
    skills, but those companion docs fall outside Doctrine's prompt-authored
    package story
  - current docs teach raw bundled references as the main answer even though the
    compiler already has richer prompt-authored document machinery
- Capability-first opportunities before new tooling:
  - none needed beyond the existing compiler paths; this is a language and
    package-emit design change, not a place for new harnesses, parsers, or
    helper sidecars
- Behavior-preservation signals already available:
  - [tests/test_emit_skill.py](/Users/aelaguiz/workspace/doctrine/tests/test_emit_skill.py:18)
    — emit tree proof for first-party and synthetic package shapes
  - `tests/test_compile_diagnostics.py` — targeted fail-loud package diagnostics
  - `examples/95` through `103` plus `make verify-examples` — shipped
    manifest-backed package corpus

## 3.3 Decision gaps that must be resolved before implementation

- None. The North Star already locked the plan-shaping choices that mattered:
  - `emit:` is the block name
  - each entry maps one package-relative `.md` path to one `document`
    declaration
  - root `SKILL.md` stays implicit and preserved
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 Parse and model surface today

- `skill package` is still a very small authored surface in the shipped
  grammar. In `doctrine/grammars/doctrine.lark`, the body accepts only one
  optional `metadata:` block plus ordinary record items.
- `doctrine/_parser/skills.py` lowers that body into
  `SkillPackageBodyParts(items, metadata)`. It already rejects duplicate
  `metadata:` blocks.
- `doctrine/_parser/transformer.py` validates only four metadata keys:
  `name`, `description`, `version`, and `license`.
- `SkillPackageDecl` in `doctrine/_model/io.py` stores only `name`, `title`,
  `items`, and `metadata`. There is no typed place to remember any extra
  package-owned emitted artifacts.

## 4.2 Compile and emit flow today

- `doctrine.emit_skill.emit_target_skill()` is the only public skill-package
  emit path. It parses `SKILL.prompt`, builds one `CompilationSession`, calls
  `compile_skill_package()`, writes `SKILL.md`, then writes each extra
  `CompiledSkillPackageFile`.
- `CompilationContext._compile_skill_package_decl()` is the current canonical
  owner of the package output contract. It builds the root compiled section and
  asks `_compile_skill_package_bundle_files()` for the rest of the emitted
  tree.
- `_compile_skill_package_bundle_files()` scans the whole source root, creates
  one `PackageOutputRegistry` with `SKILL.md` pre-reserved, and then decides
  what else can emit.

## 4.3 Bundled-file ownership rules today

- Ordinary non-`.prompt` files bundle byte for byte when they live outside
  reserved prompt-bearing subtrees.
- `agents/**/*.prompt` is the only non-root prompt family that compiles into
  extra Markdown companions today. Each such prompt must define exactly one
  concrete agent.
- Any other descendant prompt-bearing directory is treated as compiler-owned.
  Its `.prompt` files do not bundle through raw, and the current source-root
  scan also skips ordinary files under that reserved subtree.
- This means prompt-authored companion docs under `refs/`, `references/`, or
  any other imported prompt module tree cannot emit today, even though the
  import graph itself already works.

## 4.4 Existing reusable compiler pieces

- `document` is already the shipped prompt-authored Markdown surface. It owns
  structure, inheritance, addressable blocks, and render-profile use.
- Cross-module document refs already resolve through the normal declaration-ref
  path in `doctrine/_compiler/resolve/refs.py`. The feature gap is not name
  resolution.
- `_compile_document_decl(decl, unit=...)` in the readable compiler already
  produces the exact `CompiledSection` shape that `render_skill_package_markdown`
  knows how to render.
- `register_package_output_path()` in
  `doctrine/_compiler/package_layout.py` already owns normalized package paths,
  case-fold collision checks, and reserved-path rejection. That is the right
  enforcement layer to reuse.

## 4.5 Failure behavior and public drift today

- Path collisions, unreadable bundled files, and invalid bundled-agent prompt
  shapes already fail loud as `E304`.
- There is no authored surface for "extra package Markdown from prompt files,"
  so there is also no explicit fail-loud contract for missing refs, wrong-kind
  refs, or non-`.md` output paths in that area.
- Repo docs and first-party packages therefore teach raw bundled Markdown
  companions as the normal answer, while downstream packages in `../psflows`
  show that one short root doc plus several separately loadable companion docs
  is a real recurring need.

## 4.6 UI surfaces

- No UI work is in scope.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 Public authored surface

- `skill package` gains one optional `emit:` block.
- Each entry is one explicit mapping from a package-relative Markdown file path
  to one `document` declaration ref:
  `"relative/path.md": DocumentRef`
- The ref uses the normal `NameRef` family. Local documents, imported symbols,
  and module-qualified document refs should all work through the same resolver
  Doctrine already uses elsewhere.
- `SKILL.md` stays implicit and reserved. Authors never spell the root artifact
  in `emit:`.

## 5.2 Parser and model shape

- `doctrine/grammars/doctrine.lark` adds `package_emit_block` and
  `package_emit_item` beside `package_metadata_block`.
- The parser lowers `emit:` into explicit emit-entry parts that keep line and
  column data for diagnostics.
- `SkillPackageBodyParts` grows an `emit_entries` field so the rest of the
  package body stays unchanged.
- `doctrine/_model/io.py` adds a small typed owner such as
  `SkillPackageEmitEntry(path, ref, source_span)`, and `SkillPackageDecl`
  stores `emit_entries` beside `metadata` and `items`.
- More than one `emit:` block is a parse-time failure, matching the current
  `metadata:` rule.

## 5.3 Canonical compile path

- `doctrine/_compiler/compile/skill_package.py` stays the one canonical owner
  of skill-package artifact assembly.
- `_compile_skill_package_decl()` should assemble three artifact families in
  one package-output registry:
  1. implicit root `SKILL.md`
  2. explicit `emit:` companion docs compiled from `document`
  3. existing bundled-agent outputs plus ordinary raw bundled files
- Explicit emitted docs register their output paths before ordinary bundling
  runs. That preserves one collision model across emitted docs, bundled agents,
  and raw files.
- Each `emit:` entry resolves through the existing document-ref path and
  compiles through `_compile_document_decl(decl, unit=resolved_unit)`. No new
  public `CompilationSession` method or CLI surface is needed.
- Output ordering stays deterministic: authored `emit:` entries in authored
  order, then the existing source-root scan outputs in stable path order.

## 5.4 Compatibility and boundary rules

- This is additive. Existing skill packages that use only raw bundled files
  keep working unchanged.
- `agents/**/*.prompt` stays on its current special path in the first cut. This
  change does not try to unify bundled-agent prompts onto `emit:`.
- Non-agent prompt-bearing subtrees stay compiler-owned in the first cut. Their
  `.prompt` sources still do not bundle through raw, and the only new way they
  become emitted package files is explicit `emit:`.
- `pyproject.toml` still points at one `SKILL.prompt` entrypoint and does not
  learn per-file package output wiring.
- There is no path magic, no auto-discovery, no hardcoded `references/`
  meaning, and no manifest sidecar in this change.

## 5.5 Fail-loud contract

- Each `emit:` path must be a relative `/`-separated file path that ends in
  `.md`.
- `emit:` paths may not collide with implicit `SKILL.md`, compiled bundled
  agent outputs, ordinary bundled files, or other emitted companion docs.
- Missing, ambiguous, or wrong-kind refs fail through the existing declaration
  ref family instead of inventing a package-only lookup rule.
- `docs/COMPILER_ERRORS.md` should continue to describe path and bundle-shape
  failures under `E304`, widened so the wording covers explicit emitted-doc
  paths too.

## 5.6 Authoring posture after the change

- Use raw bundled `.md` files when the source really is raw Markdown or another
  byte-preserved asset.
- Use `document` plus `emit:` when the companion file wants Doctrine structure,
  imports, inheritance, or reusable addressable blocks.
- Keep `SKILL.md` thin. Put deeper method and reference material in emitted
  companion docs that the runtime can load only when needed.

## 5.7 UI surfaces

- No UI work is in scope.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar | `doctrine/grammars/doctrine.lark` | `skill_package_body`, new `package_emit_block`, new `package_emit_item` | `skill package` accepts only `metadata:` plus record items | Add one optional `emit:` block with per-entry `"path.md": DocumentRef` items | The public syntax has no package-owned artifact map today | `emit:` is one explicit package block; each entry is one relative `.md` path to one `document` ref | `tests/test_parser_source_spans.py`, `tests/test_emit_skill.py`, corpus examples |
| Parser support | `doctrine/_parser/parts.py` | `SkillPackageBodyParts` plus new emit-part carriers | Only metadata survives parser lowering | Add emit-entry part objects with line and column data; thread `emit_entries` through body parts | Later diagnostics need exact authored sites | `SkillPackageBodyParts(items, metadata, emit_entries)` | `tests/test_parser_source_spans.py` |
| Parser lowering | `doctrine/_parser/skills.py`, `doctrine/_parser/transformer.py` | `skill_package_body`, `package_emit_block`, `package_emit_item`, `_skill_package_metadata` | Duplicate `metadata:` is rejected; there is no `emit:` lowering | Reject duplicate `emit:` blocks, lower entry refs and path strings, keep source spans | Parser should own authored shape errors before compile | One optional `emit:` block; source spans point at exact bad entry or duplicate block | `tests/test_parser_source_spans.py`, targeted parse/compile-negative tests |
| Model | `doctrine/_model/io.py`, `doctrine/model.py` | `SkillPackageDecl` and new emit-entry type exports | `SkillPackageDecl` stores only root prose items plus metadata | Add typed emit-entry storage and re-export it from `doctrine.model` | Compiler needs a real artifact map, not ad hoc tuples | `SkillPackageDecl(..., emit_entries=...)` | Emit tests, diagnostics tests |
| Compiler assembly | `doctrine/_compiler/compile/skill_package.py` | `_compile_skill_package_decl()`, `_compile_skill_package_bundle_files()`, new emit helpers | Builds root `SKILL.md`, bundled-agent markdown, and raw bundled files only | Compile explicit emitted docs, register all package outputs in one registry, keep bundled-agent and raw-bundle rules intact | One canonical owner path prevents parallel emit logic | Root `SKILL.md` + explicit emitted docs + existing bundle families share one collision model | `tests/test_emit_skill.py`, `tests/test_compile_diagnostics.py`, `make verify-examples` |
| Package path rules | `doctrine/_compiler/package_layout.py` or skill-package-local wrapper in `skill_package.py` | `register_package_output_path()` use sites | Validates relative paths and collisions, but not skill-package-specific `.md` emit intent | Reuse existing registry for all artifact families; add explicit `.md` suffix check at the skill-package emit layer | Keep one path-validation engine and avoid a second path policy | Emitted document paths use the same reserved-path and case-fold rules as raw and bundled-agent files | `tests/test_compile_diagnostics.py`, `docs/COMPILER_ERRORS.md` |
| Emit CLI smoke | `doctrine/_diagnostic_smoke/emit_checks.py` | `run_emit_checks()` skill-package cases | Smoke checks cover source-root bundles, mixed `agents/` trees, and binary assets | Add an end-to-end temporary-project smoke case for explicit emitted docs | The public CLI needs proof, not just unit coverage | `emit_skill` writes emitted document files in the right tree without helper glue | `make verify-diagnostics` |
| Emit unit proof | `tests/test_emit_skill.py` | skill-package success tests | No success case proves `emit:` docs | Add success coverage for several emitted docs, stable returned paths, and coexistence with raw files and bundled agents | Protect the public output tree contract | One package can emit `SKILL.md` plus several prompt-authored `.md` companions | `make verify-package`, `python -m unittest tests.test_emit_skill` |
| Fail-loud diagnostics | `tests/test_compile_diagnostics.py` | skill-package bundle cases | Only path collision and bundled-agent collision are covered | Add non-`.md` path, invalid relative path, missing ref, wrong-kind ref, duplicate emitted path, and emitted-doc-vs-bundled-file collision cases | The new authored surface must fail loud on every wrong shape | Explicit emitted-doc misuse is part of the shipped bundle contract | Targeted diagnostics tests, `make verify-diagnostics` |
| Parser source spans | `tests/test_parser_source_spans.py` | new skill-package emit-node assertions | No parser proof for `emit:` entry spans | Add source-span assertions for `skill package` emit entries and duplicate-block sites | Good diagnostics need stable authored locations | `emit:` entries keep exact line and column data | `python -m unittest tests.test_parser_source_spans` |
| Public language docs | `docs/LANGUAGE_REFERENCE.md` | `## Skill Packages` and prompt-file overview | Describes only root `SKILL.md`, raw bundle files, and bundled-agent prompts | Document `emit:` syntax, `document`-ref semantics, explicit path rules, and the unchanged compiler-owned subtree rule | Shipped language docs must match the compiler | `skill package` now owns an optional `emit:` block | Docs readback plus corpus example cross-links |
| Package authoring guide | `docs/SKILL_PACKAGE_AUTHORING.md` | quick start, source-root model, bundled files, gallery, first-party package section | Teaches raw bundled Markdown companions as the main story | Teach the choice between raw bundled files and `document` + `emit:`; keep raw bundle examples as compatibility proof | Authors need the right mental model for package composition | Skill packages now have two valid companion-doc paths: raw bundle or explicit emitted `document` | Docs readback, example gallery updates |
| Emit guide | `docs/EMIT_GUIDE.md` | skill-package output layout and examples | Package output is described as `SKILL.md` plus bundled source-root files | Add explicit emitted-doc artifact family and mixed-package output examples | Output-tree docs must match real emit behavior | Skill-package output tree now includes explicit emitted `.md` companions when declared | Docs readback |
| Discovery docs | `docs/README.md`, `docs/AUTHORING_PATTERNS.md`, `examples/README.md` | skill-package blurbs, anchors, example gallery | Discovery text points readers only at the older source-root bundle story | Add the new examples and refresh skill-package blurbs so they mention explicit emitted docs | Readers should find the new feature without diff archaeology | Canonical skill-package examples expand beyond `95` through `103` | Docs readback, `make verify-examples` |
| Error catalog | `docs/COMPILER_ERRORS.md` | `E304` row | `E304` wording covers bundle paths, collisions, unreadable files, and bundled-agent shape only | Widen the wording so it also covers explicit emitted-doc path failures | Public error docs must stay exact | `E304` remains the package-output path and collision family | Diagnostics unit tests, smoke checks |
| Release truth | `docs/VERSIONING.md`, `CHANGELOG.md` | language-version and release notes guidance | Current release docs do not mention this feature | Update when implementation lands because this adds shipped public syntax | Public compatibility truth must match the shipped surface | Additive language feature; release notes and language-version guidance must say so | Release-flow docs alignment |
| Example proof | `pyproject.toml`, new `examples/122_*`, new `examples/123_*` | emit targets, manifests, build refs, prompts | No shipped example proves prompt-authored companion docs from `emit:` | Add one exact North Star example and one mixed-package compatibility example | The corpus should teach both the clean happy path and coexistence with the old bundle model | Example 1: imported `document` refs emit `references/*.md`; Example 2: emitted docs plus raw files and bundled agents coexist | `make verify-examples`, focused manifest verification |

## Migration notes

* Canonical owner path / shared code path:
  `doctrine/_compiler/compile/skill_package.py` stays the one owner of
  skill-package artifact assembly. `doctrine/_compiler/package_layout.py`
  stays the shared path and collision engine. `document` ref resolution and
  document compilation stay on their current shared compiler paths.
* Deprecated APIs (if any):
  None. This is additive and does not retire the current raw bundled-file
  contract.
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  No code path should be deleted in the first cut. The stale docs wording that
  frames raw bundled Markdown as the only answer for companion docs must be
  rewritten. Do not delete raw bundle support or the bundled-agent special case.
* Adjacent surfaces tied to the same contract family:
  `docs/LANGUAGE_REFERENCE.md`, `docs/SKILL_PACKAGE_AUTHORING.md`,
  `docs/EMIT_GUIDE.md`, `docs/AUTHORING_PATTERNS.md`, `docs/README.md`,
  `examples/README.md`, `docs/COMPILER_ERRORS.md`, `docs/VERSIONING.md`,
  `CHANGELOG.md`, `pyproject.toml`, `doctrine/_diagnostic_smoke/emit_checks.py`,
  and the skill-package example gallery.
* Compatibility posture / cutover plan:
  Additive cutover only. Existing raw bundled Markdown, scripts, runtime
  metadata, plugin metadata, binary assets, and bundled-agent prompts keep
  working. New prompt-authored companion docs opt in through `emit:`. No bridge
  layer or migration shim is approved.
* Capability-replacing harnesses to delete or justify:
  None. This is compiler work. Do not add helper scripts, special package
  manifests, or runtime-side loaders to compensate for missing compiler support.
* Live docs/comments/instructions to update or delete:
  Update the skill-package docs, emit guide, language reference, discovery
  docs, example index, compiler error catalog, and release docs listed above.
* Behavior-preservation signals for refactors:
  Keep existing skill-package proof green, especially
  `96_skill_package_references`, `100_skill_package_bundled_agents`, and
  `103_skill_package_binary_assets`. Add new proof examples for explicit
  emitted docs. Keep `tests/test_emit_skill.py`,
  `tests/test_compile_diagnostics.py`, and
  `doctrine/_diagnostic_smoke/emit_checks.py` green.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Skill-package docs | `docs/LANGUAGE_REFERENCE.md`, `docs/SKILL_PACKAGE_AUTHORING.md`, `docs/EMIT_GUIDE.md`, `docs/AUTHORING_PATTERNS.md`, `docs/README.md`, `examples/README.md`, `docs/COMPILER_ERRORS.md` | Teach one explicit package-artifact model: implicit root `SKILL.md`, optional `emit:` docs, existing raw bundle rules | Prevent docs from teaching contradictory companion-doc stories | include |
| Existing raw-bundle proof | `examples/96_skill_package_references` | Keep raw bundled Markdown as compatibility proof, not as the only package-doc story | The new feature is additive; raw bundle behavior still needs shipped proof | exclude |
| Existing bundled-agent proof | `examples/100_skill_package_bundled_agents`, `doctrine/_compiler/compile/skill_package.py` bundled-agent branch | Do not fold bundled-agent prompts into `emit:` in this change | Avoid turning one clean feature into a larger package-artifact rewrite | defer |
| First-party dogfooding | `skills/agent-linter/prompts/SKILL.prompt`, `skills/agent-linter/prompts/references/*.md` | Future dogfood move from raw bundled docs to `document` + `emit:` where it clearly helps | The package is a strong future adopter, but converting it now would mix compiler work with a large authoring rewrite | defer |
| Release truth | `docs/VERSIONING.md`, `CHANGELOG.md` | Treat this as a shipped additive language feature when it lands publicly | Prevent release docs from lagging behind the syntax change | include |
| Runtime packages | `emit_docs` runtime-package surfaces | Do not copy the `skill package emit:` design onto runtime packages in this change | Runtime packages are a separate public surface with different root-artifact rules | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Parse and type the package artifact map

Status: COMPLETE

* Goal:
  Add the public `emit:` authored surface and store it as typed package data
  without changing package compilation yet.
* Work:
  This phase locks the new surface at the grammar, parser, and model boundary
  so later compiler work can assume one stable representation instead of
  reverse-engineering raw parser output.
* Checklist (must all be done):
  - Extend `doctrine/grammars/doctrine.lark` so `skill package` accepts one
    optional `emit:` block whose entries are `"relative/path.md": DocumentRef`.
  - Add parser parts for emitted-doc entries with line and column data.
  - Thread emitted-doc entries through `SkillPackageBodyParts`.
  - Add a typed emitted-doc entry model and store `emit_entries` on
    `SkillPackageDecl`.
  - Re-export the new type through `doctrine/model.py`.
  - Reject duplicate `emit:` blocks at parse time, matching the current
    `metadata:` behavior.
  - Add parser source-span coverage for `emit:` entries and duplicate-block
    failure sites.
* Verification (required proof):
  - Run targeted parser coverage for the new syntax, including source spans.
* Docs/comments (propagation; only if needed):
  - No public docs move in this phase.
  - Add a short code comment only if the new parser part or model field would
    otherwise be hard to read.
* Exit criteria (all required):
  - `skill package` source can express the exact North Star `emit:` syntax.
  - `SkillPackageDecl` carries typed emitted-doc entries.
  - Duplicate `emit:` blocks fail before compile.
  - Parser source spans for emitted-doc entries are covered by tests.
* Rollback:
  - Revert the grammar, parser, model, and parser-test changes together.

## Phase 2 — Compile emitted documents on the canonical skill-package path

Status: COMPLETE

* Goal:
  Make `emit:` entries produce companion `.md` files through the existing
  document compiler path while preserving current package behavior.
* Work:
  This phase changes only the canonical package compiler path. It should reuse
  the existing document resolver and package-output registry instead of adding
  a second emit pipeline or any runtime-side helper layer.
* Checklist (must all be done):
  - Add a skill-package compile helper that resolves each `emit:` ref as a
    `document` declaration on the normal declaration-ref path.
  - Compile each resolved document through `_compile_document_decl(...)` and
    lower it into `CompiledSkillPackageFile`.
  - Register every explicit emitted-doc path in the same
    `PackageOutputRegistry` that already reserves `SKILL.md`.
  - Enforce the emitted-doc path contract at the skill-package layer:
    relative path, `/` separators, stays under the package root, and ends in
    `.md`.
  - Preserve current raw bundle behavior for non-prompt files.
  - Preserve the current bundled-agent prompt behavior under `agents/**/*.prompt`.
  - Preserve the current compiler-owned treatment of non-agent prompt-bearing
    subtrees.
* Verification (required proof):
  - Run targeted emit tests that compile one package with several emitted docs.
  - Run targeted diagnostics coverage for missing refs, wrong-kind refs,
    non-`.md` paths, invalid relative paths, and collisions.
* Docs/comments (propagation; only if needed):
  - Add a high-leverage code comment at the canonical package compile boundary
    if needed to explain artifact ordering or why non-agent prompt subtrees
    still stay compiler-owned.
* Exit criteria (all required):
  - One skill package can emit `SKILL.md` plus several prompt-authored
    companion `.md` files from `document` declarations.
  - Explicit emitted-doc paths share one collision model with `SKILL.md`,
    bundled-agent outputs, and raw bundled files.
  - Existing raw bundle and bundled-agent package proof still compiles on the
    same owner path.
  - No new emit CLI, helper script, shim, or sidecar is introduced.
* Rollback:
  - Revert the skill-package compiler changes and their targeted tests while
    leaving the parser/model work ready to re-land if needed.

## Phase 3 — Lock fail-loud behavior and end-to-end emit proof

Status: COMPLETE

* Goal:
  Make the new surface safe and observable with focused unit and smoke proof.
* Work:
  This phase hardens the failure contract and proves the public CLI path end to
  end. It is separate from the core compiler work so the feature cannot ship on
  a happy-path demo alone.
* Checklist (must all be done):
  - Extend `tests/test_emit_skill.py` with positive coverage for emitted docs,
    stable emitted paths, and coexistence with raw bundled files and bundled
    agents where appropriate.
  - Extend `tests/test_compile_diagnostics.py` with negative coverage for:
    non-`.md` paths, invalid relative paths, missing refs, wrong-kind refs,
    duplicate emitted paths, and emitted-doc collisions with bundled files or
    bundled-agent outputs.
  - Add or update one parser-oriented test file so emitted-doc source spans
    stay covered after the feature lands.
  - Add a temporary-project smoke case in
    `doctrine/_diagnostic_smoke/emit_checks.py` that runs through
    `emit_skill` and asserts the emitted document files exist in the expected
    tree.
  - Update `docs/COMPILER_ERRORS.md` so `E304` accurately describes the
    widened package-output path and collision family.
* Verification (required proof):
  - Run the touched unit tests for parser spans, emit behavior, and compile
    diagnostics.
  - Run `make verify-diagnostics`.
* Docs/comments (propagation; only if needed):
  - Keep `docs/COMPILER_ERRORS.md` aligned in this phase because the failure
    contract changes here.
* Exit criteria (all required):
  - Happy-path emit proof and fail-loud proof both exist for the new surface.
  - The public smoke checks cover explicit emitted docs through `emit_skill`.
  - `E304` public wording matches the implemented package-output rules.
* Rollback:
  - Revert the new diagnostics, smoke checks, and error-catalog wording if the
    implemented failure contract proves wrong.

## Phase 4 — Add shipped corpus examples and target wiring

Status: COMPLETE

* Goal:
  Add manifest-backed proof that teaches the clean path and the compatibility
  path.
* Work:
  This phase turns the feature into shipped corpus truth. It should prove both
  the exact North Star shape and coexistence with the older raw-bundle story,
  without rewriting existing compatibility examples.
* Checklist (must all be done):
  - Add one new example that uses the exact North Star pattern:
    `SKILL.prompt` plus imported prompt modules that define several `document`
    declarations emitted into `references/*.md`.
  - Add one new mixed package example that proves emitted docs can coexist with
    raw bundled files and, if useful, bundled-agent outputs without collision.
  - Add the new emit targets to `pyproject.toml`.
  - Add manifest cases, prompt sources, and checked-in `build_ref/` proof for
    the new examples.
  - Keep `examples/96_skill_package_references`,
    `examples/100_skill_package_bundled_agents`, and
    `examples/103_skill_package_binary_assets` as compatibility proof rather
    than rewriting them into the new feature.
* Verification (required proof):
  - Run focused manifest verification for each new example.
  - Run `make verify-examples`.
* Docs/comments (propagation; only if needed):
  - Update `examples/README.md` in the next phase when the full example gallery
    wording can move together.
* Exit criteria (all required):
  - The shipped corpus contains one exact emitted-doc example and one mixed
    compatibility example.
  - The repo emit target registry knows how to build both new examples.
  - Existing compatibility examples still prove raw bundles, bundled agents,
    and binary assets unchanged.
* Rollback:
  - Revert the new examples, manifests, targets, and `build_ref/` output as
    one unit.

## Phase 5 — Align public docs, release truth, and full verification

Status: COMPLETE

* Goal:
  Make the shipped docs, release surfaces, and repo-level proof all tell the
  same story as the compiler and examples.
* Work:
  This phase is the ship gate. It updates every live doc surface named in the
  call-site audit so the repo no longer teaches raw bundled Markdown as the
  only answer for companion docs, while still preserving that path as a valid
  compatibility option.
* Checklist (must all be done):
  - Update `docs/LANGUAGE_REFERENCE.md` to document `emit:` syntax, document-ref
    behavior, emitted-doc path rules, and the unchanged compiler-owned
    treatment of non-agent prompt-bearing subtrees.
  - Update `docs/SKILL_PACKAGE_AUTHORING.md` to teach when to use raw bundled
    files versus `document` plus `emit:`, and refresh the package gallery.
  - Update `docs/EMIT_GUIDE.md` to show the new skill-package output layout and
    mixed output trees.
  - Update discovery docs that mention skill packages:
    `docs/README.md`, `docs/AUTHORING_PATTERNS.md`, and `examples/README.md`.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for the shipped additive
    language feature.
  - Keep the North Star syntax and source-tree examples visible in the public
    docs where they best fit.
  - Run the repo-level verification required by the touched surfaces.
* Verification (required proof):
  - Run `python -m unittest tests.test_emit_skill`.
  - Run the touched targeted unit tests for parser spans and compile
    diagnostics.
  - Run `make verify-diagnostics`.
  - Run `make verify-examples`.
  - Run `make verify-package`.
* Docs/comments (propagation; only if needed):
  - This phase owns all live-doc and release-truth propagation listed in the
    call-site audit.
* Exit criteria (all required):
  - Public docs, examples, error catalog, and release docs all describe the
    same emitted-doc package model.
  - The repo verifies cleanly on the touched parser, emit, diagnostics,
    examples, and package-install surfaces.
  - No live doc still implies that raw bundled Markdown is the only way to ship
    companion docs from a skill package.
* Rollback:
  - Revert the doc and release-truth updates together, or revert the whole
    feature if the docs would otherwise describe behavior that is not shipped.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Existing signals to use

- `uv sync`
- `npm ci`
- focused unit tests for parser spans, emit behavior, and compile diagnostics
- `make verify-diagnostics`
- manifest-backed example verification for the new examples
- `make verify-examples` before closing the full change
- `make verify-package` before closing the full change because this touches the
  public skill-package emit surface and install proof

## 8.2 New targeted proof to add

- Parser-source-span proof for emitted-doc entries
- One success test for several emitted companion docs from `document`
  declarations.
- One or more fail-loud tests for bad output paths, wrong-kind refs, and path
  collisions.
- One end-to-end `emit_skill` smoke case for explicit emitted docs in a
  temporary project.

## 8.3 Manual readback

- Read emitted example trees to confirm the root `SKILL.md`, companion `.md`
  files, and raw bundled files all land in the right places.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout

- Ship as an additive language feature.
- Preserve the current raw bundle path so existing packages do not need to move
  immediately.

## 9.2 Ops / telemetry

- No runtime telemetry change is needed.

## 9.3 User-facing change note

- Doctrine skill packages can now emit prompt-authored companion Markdown files
  from `document` declarations by explicit package mapping.

# 10) Decision Log (append-only)

## 2026-04-16 - Initial North Star draft

- Chosen direction: explicit `emit:` block on `skill package`
- Rejected in North Star:
  - hardcoded `references:` feature
  - prompt-subdir auto-discovery
  - multi-target `pyproject.toml` package wiring
  - renaming the root artifact away from `SKILL.md`

## 2026-04-16 - Deep-dive architecture lock

- Keep `doctrine/_compiler/compile/skill_package.py` as the one canonical
  owner of package artifact assembly.
- Reuse the existing document-ref resolver and `_compile_document_decl(...)`
  path instead of adding a second public compile API.
- Keep `agents/**/*.prompt` on the current bundled-agent special path in the
  first cut.
- Keep non-agent prompt-bearing subtrees compiler-owned in the first cut. The
  only new way they become package files is explicit `emit:`.
- Keep raw bundled Markdown and other raw package files as a supported
  compatibility path. Do not convert that existing behavior into path magic or
  remove its proof examples.

## 2026-04-16 - Phase-plan sequencing lock

- Split the work into five phases so parser/model, compiler assembly,
  fail-loud proof, corpus proof, and public-doc alignment can each complete
  with their own verification.
- Keep bundled-agent convergence and first-party dogfooding out of the initial
  implementation phases.
- Treat `make verify-package` as required final proof because the public
  skill-package emit and install surface changes here.
