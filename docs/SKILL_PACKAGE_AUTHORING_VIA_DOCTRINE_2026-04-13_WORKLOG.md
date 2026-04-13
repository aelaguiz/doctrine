# Worklog

Plan doc: [docs/SKILL_PACKAGE_AUTHORING_VIA_DOCTRINE_2026-04-13.md](./SKILL_PACKAGE_AUTHORING_VIA_DOCTRINE_2026-04-13.md)

## Initial entry
- Run started.
- Current phase: Phase 2 — Core package lowering and deterministic filesystem emission

## Phase 1 (Package source surface and shared target-plumbing foundation) Progress Update
- Work completed:
  - Added first-class `skill package` parsing, typed `metadata:` support for the initial scalar package fields, AST/model ownership, and indexed-unit package registration.
  - Added `CompilationSession.compile_skill_package()` and the package compile boundary for the primary package body.
  - Widened shared emit-target validation so `SKILL.prompt` is recognized without widening `emit_docs` or `emit_flow`.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/11_skills_and_tools/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/21_first_class_skills_blocks/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/22_skills_block_inheritance/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/60_shared_readable_bodies/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/07_handoffs/cases.toml` — PASS
- Issues / deviations:
  - None in this phase.
- Next steps:
  - Broaden typed metadata beyond the initial scalar set and continue the package filesystem work already started in Phase 2.

## Phase 2 (Core package lowering and deterministic filesystem emission) Progress Update
- Work completed:
  - Added `doctrine/emit_skill.py` for the minimal `SKILL.md` package tree.
  - Wired build-contract verification to dispatch `SKILL.prompt` targets through the new package emitter.
  - Landed `examples/95_skill_package_minimal` with a checked-in `SKILL.md` tree and a parser failure contract for unknown package metadata.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/95_skill_package_minimal/cases.toml` — PASS
- Issues / deviations:
  - This pass only covers the minimal package tree. `references/`, `scripts/`, `assets/`, and path/case edge families from the full Phase 2 checklist remain unfinished.
- Next steps:
  - Extend the package artifact/emitter path to source-root bundle discovery and exact-path copy-through, then land the next package gallery examples before the next audit cycle.

## Plan correction (source-root bundle model)
- User clarified that bundled package files should live in the prompt tree as ordinary source files, with compile/emit preserving their relative paths into the emitted package tree.
- The plan was updated to treat `references/`, `reference/`, `scripts/`, `assets/`, runtime/plugin files, and similar layouts as proof cases and examples, not privileged compiler-owned companion families.
- `examples/*/build_ref` remains verifier-only checked-in proof and must not become part of the compiler-facing package model or public authoring story.
- Phase 1 and Phase 2 are reopened against the corrected architecture.
- Next steps:
  - Rework package implementation toward source-root bundle discovery plus exact-path copy-through rooted at the directory that contains `SKILL.prompt`.

## Phase 1 and Phase 2 correction implementation update
- Work completed:
  - Removed the ordinary `reference`, `script`, and `asset` package declarations from the grammar, parser, model, and package compiler path.
  - Reworked skill-package compilation around the directory that contains `SKILL.prompt`: the package body still compiles to `SKILL.md`, and ordinary bundled non-`.prompt` files now emit under the same relative paths.
  - Added generic bundled-path validation for reserved `SKILL.md` collisions, source-root-relative path safety, and case-folding collisions instead of hard-coded family roots.
  - Reserved descendant directories that contain their own `.prompt` files as prompt-bearing subtrees so the main package does not copy those files through as ordinary bundle content.
  - Rebuilt `examples/96_skill_package_references`, `examples/97_skill_package_scripts`, and `examples/102_skill_package_path_case_preservation` around authored source-root files in the prompt tree instead of declaration-generated companions.
  - Moved the path/case negative proof for example `98` into a prompt-bearing subtree under `prompts/invalid/` so the main package build stays clean while the invalid package still proves the reserved-name collision.
- Tests run + results:
  - `uv sync` — PASS
  - `npm ci` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/95_skill_package_minimal/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/96_skill_package_references/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/97_skill_package_scripts/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/102_skill_package_path_case_preservation/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/11_skills_and_tools/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/21_first_class_skills_blocks/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/22_skills_block_inheritance/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/60_shared_readable_bodies/cases.toml` — PASS
  - `make verify-diagnostics` — PASS
- Issues / deviations:
  - Runtime/plugin/bundled-agent package families and examples `94` through `97` remain for the later phase.
  - Live public docs have not been updated yet, so the shipped documentation surface still lags the new package architecture.
- Next steps:
  - Continue into the Phase 3 slice: runtime/plugin package files, bundled-agent surfaces, diagnostics/editor convergence, and examples `94` through `97`.

## Phase 3 (Runtime/plugin companions, bundled agents, diagnostics, and editor convergence) Progress Update
- Work completed:
  - Added Phase 3 package-gallery targets and proof examples for runtime metadata, plugin metadata, bundled agent prompts, and the compendium slice in `examples/94` through `97`.
  - Extended package compilation so bundled agent prompts under `agents/**/*.prompt` emit compiled markdown companions under preserved relative paths, while nested prompt-bearing subtrees remain compiler-owned rather than copied as ordinary files.
  - Kept runtime/plugin files such as `agents/openai.yaml`, `.codex-plugin/plugin.json`, and `.app.json` on the source-root bundle path instead of inventing new typed file-family declarations.
  - Added package-specific diagnostic smoke for `emit_skill` bundle output and for `emit_flow` rejecting `SKILL.prompt` entrypoints.
  - Updated the compiler error catalog entry for `E510` so it reflects the emitter-specific entrypoint split instead of the old agent-only wording.
  - Updated the VS Code grammar, resolver, unit coverage, integration coverage, alignment rules, and editor README for first-class `skill package` / `SKILL.prompt` support.
- Tests run + results:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/98_skill_package_runtime_metadata/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/99_skill_package_plugin_metadata/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/100_skill_package_bundled_agents/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/101_skill_package_compendium/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/95_skill_package_minimal/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/96_skill_package_references/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/97_skill_package_scripts/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/102_skill_package_path_case_preservation/cases.toml` — PASS
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/11_skills_and_tools/cases.toml` — PASS
  - `make verify-diagnostics` — PASS
  - `cd editors/vscode && make` — PASS
- Issues / deviations:
  - The canonical public docs and package-gallery teaching path from Phase 4 are still missing.
  - The live docs index, language reference, emit guide, examples index, and dedicated package authoring guide still need to be updated before the feature is honestly complete.
- Next steps:
  - Move into the Phase 4 docs-and-gallery convergence slice so the live public story matches the now-shipped package implementation and proof matrix.

## Phase 4 (Public docs, example gallery, and final proof convergence) Progress Update
- Work completed:
  - Added `docs/SKILL_PACKAGE_AUTHORING.md` as the canonical end-to-end guide for `SKILL.prompt`, `skill package`, source-root bundle semantics, `emit_skill`, the package gallery, and the inline-skills-versus-package boundary.
  - Updated `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, and `examples/README.md` so the live public story now includes the shipped package surface instead of presenting the older agent-only emit path as the whole product story.
  - Made the docs explicit that bundled files come from the package source tree around `SKILL.prompt`, preserve relative layout on emit, and do not require a privileged `build_ref/` or companion-family authoring surface.
  - Added the generic public crosswalk from the package example gallery to the real skill-family shapes the feature is meant to support, without importing product-specific names or workflow jargon.
- Tests run + results:
  - `make verify-examples` — PASS
- Issues / deviations:
  - None in this slice so far. The next fresh audit should decide whether the full plan is now honestly complete.
- Next steps:
  - Hand back to the fresh implementation audit for the authoritative completeness verdict against the approved plan.
