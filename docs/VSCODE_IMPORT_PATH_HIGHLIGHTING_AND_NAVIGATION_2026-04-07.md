---
title: "Doctrine - VS Code Import Path Highlighting and Navigation - Architecture Plan"
date: 2026-04-07
status: active
fallback_policy: forbidden
owners: []
reviewers: []
doc_type: architectural_change
related:
  - editors/vscode/README.md
  - editors/vscode/package.json
  - editors/vscode/syntaxes/doctrine.tmLanguage.json
  - examples/03_imports/cases.toml
  - https://code.visualstudio.com/api/extension-capabilities/overview
  - https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide
  - https://code.visualstudio.com/api/references/vscode-api
---

# TL;DR

Outcome

- Make the Doctrine VS Code extension visibly distinguish import paths in `.prompt` files and support normal VS Code follow-definition behavior across the full Doctrine clickable surface: every compiler-resolved declaration ref plus the structural inheritance-key refs users navigate through in real prompt authoring.

Problem

- The runtime extension and full clickable resolver now ship in-repo, but the original highlight complaint still needs one live installed-VSIX scope-inspector pass to distinguish theme visibility from any remaining emitted-scope issue.

Approach

- Keep Doctrine language truth in `doctrine/` and treat editor work as an adapter layer. Reuse the shipped import-resolution, declaration-resolution, readable-ref, interpolation-root, and inheritance-key semantics instead of hard-coding a smaller editor-only subset, and make any highlighting changes only after separating tokenization problems from theme-visibility problems.

Plan

- Phases 1-6 now ship in code: raw imports, full direct declaration refs, readable/interpolation-root refs, and structural inheritance-key refs all navigate through the widened resolver. Phase 7 docs are updated in-repo, and one live scope-inspector/editor pass still remains as manual finalization.

Non-negotiables

- No second import resolver with different semantics.
- No silent fallback links to the wrong file or declaration.
- No new parallel editor path that bypasses shipped language truth in `doctrine/`.
- Keep extension tests, docs, and example-backed import behavior aligned.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-07
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. The repo-local extension now ships the widened resolver and extension-host proof surface for the full in-scope clickable contract.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None at code level. The remaining follow-up is human editor validation of token visibility and installed-VSIX behavior.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Rebuild and reinstall the VSIX locally, then run one live editor pass on `examples/03_imports/prompts/AGENTS.prompt` to inspect the import-path scope and confirm Cmd-click / Go to Definition behavior against the installed extension, as already recorded in [Section 7, Phase 3](/Users/aelaguiz/workspace/doctrine/docs/VSCODE_IMPORT_PATH_HIGHLIGHTING_AND_NAVIGATION_2026-04-07.md#L497).
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-07
external_research_grounding: done 2026-04-07
deep_dive_pass_2: done 2026-04-07
recommended_flow: phase plan -> implement -> audit implementation
note: Deep-dive has been refreshed for the expanded full-clickable scope; sync the phase plan before the next implementation pass.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

- If a user opens a `.prompt` file with the Doctrine extension active, import statement paths will have inspectable Doctrine token scopes, and Cmd-click or Go to Definition on every compiler-resolved Doctrine declaration ref plus every structurally resolved inheritance-key ref will jump to the correct local `.prompt` file, declaration header, or inherited source according to the same absolute and relative import rules, readable-ref ambiguity rules, and inheritance semantics used by the compiler, or fail loudly when unresolved.

## 0.2 In scope

- Understanding and fixing the VS Code editor experience around import path highlighting and follow-definition navigation for Doctrine source.
- The repo-local VS Code extension under `editors/vscode/`.
- Reusing or extracting import-resolution logic from `doctrine/parser.py`, `doctrine/model.py`, and `doctrine/compiler.py` when needed.
- Navigation support for the full clickable Doctrine surface:
  - import module paths
  - parent declaration refs in headers
  - authored-slot workflow refs and authored-slot overrides
  - workflow composition refs including `use` and override-based workflow refs
  - route target refs
  - top-level `skills`, `inputs`, and `outputs` block refs
  - inputs and outputs patch-parent refs
  - skill-entry refs
  - typed scalar declaration refs such as `source`, `target`, `shape`, and `schema`
  - standalone input and output declaration refs inside I/O bodies
  - standalone readable refs in workflow bodies
  - interpolation root refs inside strings
  - structural local-key refs such as `abstract`, `inherit`, and local-key `override`
- Extension tests, docs, packaging notes, and example coverage needed to keep the editor behavior aligned with shipped import semantics.
- Manual verification in VS Code or Cursor against the shipped examples that exercise those surfaces.

## 0.3 Out of scope

- Changing Doctrine language syntax or shipped import semantics.
- Adding unrelated language features such as completion, hover, rename, symbol search, or full language-server breadth unless research proves one is strictly necessary for the requested navigation surface.
- Non-editor compiler and renderer behavior beyond small extractions required to preserve a single import-resolution truth surface.
- Theme-wide color design outside the Doctrine token scopes relevant to this issue.
- Navigating arbitrary prose text that merely happens to match a declaration name.
- Navigating interpolation field-path segments after the declaration root such as the `source.path` part of `{{CurrentPlan:source.path}}`.
- Inventing synthetic editor targets for built-in input sources or built-in output targets unless the plan later names a concrete doc or virtual-document target.

## 0.4 Definition of done (acceptance evidence)

- A local Doctrine file in the import example can be inspected with VS Code's scope inspector to show the intended import-path token scopes.
- Cmd-click or Go to Definition flows on each in-scope ref family land on the correct file, declaration, or inherited source in the shipped examples that exercise that family, or fail loudly for unresolved or ambiguous references.
- The smallest credible automated signal exists for any new navigation-provider behavior, and existing grammar tests still pass.
- Docs tell users how to install or reinstall the VSIX and what editor behavior is supported.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks.
- Fail-loud when a target cannot be resolved.
- No dual sources of truth for import resolution.
- Do not regress shipped import grammar coverage.
- Do not silently reinterpret dotted names differently in editor and compiler.
- Keep editor support proportional; solve this issue with the smallest credible feature surface.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Exact parity with compiler import semantics.
2. User-visible import highlighting and follow-definition behavior that feels native in VS Code.
3. Clear separation between tokenization/theming concerns and navigation concerns.
4. Minimal extension surface area beyond what this issue needs.

## 1.2 Constraints

- Current extension now has a small runtime entrypoint plus `contributes.languages`, `contributes.grammars`, and language configuration, and manual finalization must keep that existing provider surface aligned with shipped compiler semantics.
- Current import-path highlighting is already covered by grammar unit and snapshot tests, so a reported "not highlighting" symptom may be tokenization drift, stale installed VSIX, or theme visibility rather than regex absence.
- The compiler resolves imports relative to the nearest `prompts/` root and current package, including multi-dot parent walks, and errors loudly on missing modules or walking above the root.
- The extension is packaged locally as a VSIX and must keep working in VS Code or Cursor builds compatible with `engines.vscode: ^1.105.0`.

## 1.3 Architectural principles (rules we will enforce)

- `doctrine/` remains the shipped language SSOT.
- Prefer shared pure logic or deliberate extraction over re-encoding compiler import semantics inside the extension.
- Declarative grammar owns lexical scopes; programmatic language features own click navigation.
- Navigation must fail loudly rather than guessing.
- Keep docs, tests, and examples synchronized with the supported editor surface.

## 1.4 Known tradeoffs (explicit)

- Broadening click navigation widens an existing runtime extension surface and test matrix rather than staying grammar-only.
- Import path "highlighting" may partly be a theming problem even when the grammar is correct, so the plan must distinguish visible styling from token classification before changing scopes.
- `DocumentLinkProvider` already owns raw import-path clicking, while `DefinitionProvider` owns declaration navigation; the remaining tradeoff is how far the definition surface should extend into readable and structural refs without inventing editor-only semantics.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- [editors/vscode/extension.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/extension.js#L10) now ships a real runtime entrypoint that registers a `DocumentLinkProvider` and `DefinitionProvider` for Doctrine files.
- [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L1) now owns one widened adapter path: import-path links, full direct declaration-ref lookup, readable declaration lookup for workflow bodies and interpolation roots, and structural key lookup for inherited owners.
- [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md#L5) now documents the full shipped clickable surface and the remaining explicit non-goals.
- [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L150) still supplies the lexical ranges for import paths, interpolation roots, route targets, `use`, `inherit`, `override`, patch-parent refs, keyed refs, and standalone reference bodies.
- [editors/vscode/tests/integration/suite/index.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/suite/index.js#L8) now proves at least one positive case per shipped clickable family over the example corpus.
- [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L3107) still owns the actual import semantics, readable-registry meaning, and inheritance behavior the adapter mirrors.

## 2.2 What’s broken / missing (concrete)

- The remaining gap is manual, not architectural: one live scope-inspector and installed-VSIX pass is still needed to close the original "not highlighting" complaint with direct editor evidence.
- Built-in `source:` and `target:` names still intentionally do not navigate, and interpolation field-path segments after the declaration root still stay out of scope.
- The repo now needs the artifact and any manual finalization notes to stay aligned with the shipped full-clickable behavior.

## 2.3 Constraints implied by the problem

- The plan must separate three possible failure modes: bad tokenization, stale local VSIX or editor state, and theme-visible-but-not-distinct styling.
- Any navigation implementation must support both absolute and relative Doctrine import syntax, not just file-system-relative guesses.
- The shipped runtime path should remain the single adapter path: `package.json` -> `extension.js` -> `resolver.js`.
- The editor should keep failing loudly on unresolved or ambiguous targets instead of guessing.
- Manual live validation should still use the shipped examples that exercise imports, readable refs, interpolation roots, and inheritance-heavy navigation.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- [Language Extensions Overview](https://code.visualstudio.com/api/language-extensions/overview) and [Extension Capabilities Overview](https://code.visualstudio.com/api/extension-capabilities/overview) — adopt the declarative/programmatic split — syntax highlighting, comments, indentation, and grammar contributions are declarative, while follow-definition behavior belongs to programmatic language features.
- [Programmatic Language Features](https://code.visualstudio.com/api/language-extensions/programmatic-language-features) — adopt direct `vscode.languages.*` providers as the default widening path — official docs make direct provider registration first-class for narrow language features, so the remaining phases can extend the current provider pair instead of jumping straight to a full language server.
- [VS Code API: `registerDefinitionProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDefinitionProvider), [`DefinitionProvider`](https://code.visualstudio.com/api/references/vscode-api#DefinitionProvider), and [`LocationLink`](https://code.visualstudio.com/api/references/vscode-api#LocationLink) — adopt as the canonical follow-definition surface for declaration refs and structural local-key refs — this matches normal Go to Definition behavior and supports precise source and target ranges for both local and imported targets.
- [VS Code API: `registerDocumentLinkProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDocumentLinkProvider), [`DocumentLinkProvider`](https://code.visualstudio.com/api/references/vscode-api#DocumentLinkProvider), and [`DocumentLink`](https://code.visualstudio.com/api/references/vscode-api#DocumentLink) — keep only for raw import-path ranges — official docs make this the right narrow surface for clickable text that is not itself a declaration lookup.
- [Syntax Highlight Guide](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide) — adopt scope-inspector-first debugging and reject grammar-only conclusions about visible styling — official docs split tokenization from theming, so a path can be tokenized correctly and still not look visually distinct in the active theme.
- [Syntax Highlight Guide: Scope Inspector](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#scope-inspector) — adopt as the first debugging step for the highlight complaint — this is the official way to see emitted scopes and the theme rules that actually matched.
- [Semantic Highlight Guide](https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide) — reject semantic tokens as the next move for the open phases — they are a larger, layered surface and are not required to widen the current clickable coverage or to settle the import-path visibility complaint.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py#L75) — parses `import` into `ImportPath(level, module_parts)` and parses dotted declaration refs into `NameRef(module_parts, declaration_name)`.
  - [doctrine/parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py#L109) and [doctrine/parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py#L145) — parse inputs/outputs ref and patch forms plus authored-slot direct, abstract, inherit, and override forms.
  - [doctrine/parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py#L347) and [doctrine/parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py#L405) — parse workflow section refs, `use`, workflow inherit/override, skill-entry refs, skills inheritance, I/O inheritance, and `RecordRef` bodies.
  - [doctrine/model.py](/Users/aelaguiz/workspace/doctrine/doctrine/model.py#L40) — `NameRef`, `SectionBodyRef`, `RecordRef`, and `SkillEntry` are the core declaration-reference data structures the editor must mirror.
  - [doctrine/model.py](/Users/aelaguiz/workspace/doctrine/doctrine/model.py#L226) and [doctrine/model.py](/Users/aelaguiz/workspace/doctrine/doctrine/model.py#L252) — authored-slot refs and I/O fields define the direct declaration-ref and patch-parent surfaces the editor now mirrors.
  - [doctrine/model.py](/Users/aelaguiz/workspace/doctrine/doctrine/model.py#L291) and [doctrine/model.py](/Users/aelaguiz/workspace/doctrine/doctrine/model.py#L333) — `InputDecl`, `OutputDecl`, `OutputShapeDecl`, and `JsonSchemaDecl` define the file-backed declaration kinds the editor now targets.
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L554) — resolves authored-slot `WorkflowSlotValue` refs to workflow declarations.
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L681) and [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L801) — resolve I/O patch parents and standalone `RecordRef` bodies with fail-loud typed routing.
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2203) and [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2288) — resolve workflow body refs and interpolation roots through the same readable-declaration path.
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2322) — defines the ambiguity, missing-local, imported-missing, and workflow-not-readable rules for readable refs.
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L1556), [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L1680), and [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L1771) — implement inheritance merge and override semantics for I/O blocks, skills blocks, and workflows.
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L3107) and [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L3028) — resolve the `prompts/` root, absolute and relative imports, indexed units, and missing or cyclic import errors.
  - [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L150), [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L665), [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L722), [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L733), [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L770), [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L821), and [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L860) — the grammar already marks interpolation roots, route targets, `inherit`, `override`, patch-parent refs, keyed refs, and standalone reference bodies as distinct lexical surfaces.
- Canonical path / owner to reuse:
  - [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L554) and [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2322) — compiler-owned workflow, readable-ref, and inheritance semantics remain the policy owner and should not be redefined in editor-only logic.
  - [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L123) — this is now the canonical adapter boundary for mapping compiler semantics onto VS Code URIs, ranges, and file-backed declaration discovery.
  - [editors/vscode/extension.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/extension.js#L10) — the runtime provider registration surface is already in place and should remain the single package boundary while manual finalization closes the live-editor evidence gap.
- Existing patterns to reuse:
  - [editors/vscode/scripts/validate_lark_alignment.py](/Users/aelaguiz/workspace/doctrine/editors/vscode/scripts/validate_lark_alignment.py#L10) — existing alignment-guard pattern that treats the shipped Lark grammar and the VS Code grammar as coupled truth surfaces.
  - [editors/vscode/tests/unit/declarations.test.prompt](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/unit/declarations.test.prompt#L3) — direct lexical contract that import statements tokenise the path as a Doctrine reference scope.
  - [editors/vscode/tests/unit/standalone-reference-bodies.test.prompt](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/unit/standalone-reference-bodies.test.prompt#L8) — existing test surface for standalone and key-value reference tokenization beyond raw import statements.
  - [editors/vscode/tests/snap/examples/03_imports/prompts/AGENTS.prompt.snap](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/snap/examples/03_imports/prompts/AGENTS.prompt.snap#L25) — snapshot proof that import-path tokens currently exist in the shipped editor grammar.
  - [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L248) — the unified site-classification path is the canonical adapter surface for any future compiler-backed widening.
  - [editors/vscode/tests/integration/suite/index.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/suite/index.js#L59) — the extension-host definition assertions are the canonical place to add one positive proof per newly supported clickable family.
  - [examples/03_imports/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/03_imports/cases.toml#L4) — import-path and imported-module fixture for prompt-root resolution.
  - [examples/07_handoffs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/07_handoffs/prompts/AGENTS.prompt), [examples/09_outputs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/09_outputs/prompts/AGENTS.prompt), [examples/12_role_home_composition/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/12_role_home_composition/prompts/AGENTS.prompt), [examples/15_workflow_body_refs/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/15_workflow_body_refs/prompts/AGENTS.prompt), [examples/16_workflow_string_interpolation/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/16_workflow_string_interpolation/prompts/AGENTS.prompt), [examples/20_authored_prose_interpolation/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/20_authored_prose_interpolation/prompts/AGENTS.prompt), [examples/22_skills_block_inheritance/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/22_skills_block_inheritance/prompts/AGENTS.prompt), [examples/24_io_block_inheritance/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/24_io_block_inheritance/prompts/AGENTS.prompt), [examples/25_abstract_agent_io_override/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/25_abstract_agent_io_override/prompts/AGENTS.prompt), and [examples/26_abstract_authored_slots/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/26_abstract_authored_slots/prompts/AGENTS.prompt) — shipped fixtures that exercise the shipped declaration, readable, interpolation, and inheritance-key surfaces.
  - [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md#L26) and [editors/vscode/Makefile](/Users/aelaguiz/workspace/doctrine/editors/vscode/Makefile#L1) — existing build, install, and verify pattern for packaging and reinstalling the local VSIX.
- Duplicate or drifting paths relevant to this change:
  - [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L28) — the keyed-ref regexes, declaration-kind map, and unified classifier now define the shipped adapter surface and will be the first drift point if future compiler-backed refs are added.
  - [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md#L19) — the explicit non-goals list is now the main drift surface and should stay narrow and deliberate.
  - [editors/vscode/tests/integration/suite/index.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/suite/index.js#L59) — current extension-host coverage proves the shipped clickable families, so any future widening should add matching assertions instead of bypassing the suite.
  - [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md#L49) — the Remote SSH note still matters because stale local VSIX installation is a real source of false "not highlighting" or "click does nothing" reports even when repo code is correct.
- Capability-first opportunities before new tooling:
  - [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L150) — the shipped syntax families already have the lexical captures the runtime resolver needs, so future work should continue reusing those ranges instead of inventing semantic tokens or a parallel parser just to locate click targets.
  - [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L248) — explicit single-line forms such as authored-slot refs, `schema:`, patch parents, and override refs are now part of the shipped classifier and remain the natural extension point for any future compiler-backed widening.
  - [examples/15_workflow_body_refs/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/15_workflow_body_refs/cases.toml), [examples/16_workflow_string_interpolation/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/16_workflow_string_interpolation/cases.toml), [examples/20_authored_prose_interpolation/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/20_authored_prose_interpolation/cases.toml), [examples/24_io_block_inheritance/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/24_io_block_inheritance/cases.toml), and [examples/26_abstract_authored_slots/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/26_abstract_authored_slots/cases.toml) — the shipped corpus already contains fail-loud ambiguity, missing-ref, and inheritance cases that can anchor editor behavior without inventing synthetic semantics.
  - [Syntax Highlight Guide: Scope Inspector](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#scope-inspector) — the highlight complaint can still be settled with emitted-scope evidence before any further grammar churn.
- Behavior-preservation signals already available:
  - `cd editors/vscode && npm test` — preserves shipped TextMate grammar coverage, including import-path and dotted-ref tokenization.
  - `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py` — preserves alignment between the shipped Doctrine grammar and the VS Code grammar contribution.
  - `cd editors/vscode && make` — packages the extension, runs the integration suite, and remains the smallest end-to-end editor verification path after each editor change.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml` — preserves import semantics if import-resolution logic is extracted or otherwise touched under `doctrine/`.
  - `make verify-examples` — preserves shipped language behavior if any open phase ends up extracting compiler-side shared logic instead of staying purely editor-local.

## 3.3 Open questions (evidence-based)

- Resolved in `deep-dive`: standalone `RecordRef` navigation stays limited to typed `inputs` and `outputs` bodies for this plan, because [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L801) is the only shipped compiler-owned typed routing contract for record-body declaration refs.
- Resolved in `deep-dive`: interpolation navigation is root-only. `{{Ref:field.path}}` should make only the declaration root clickable, while field-path-segment navigation remains out of scope per [Section 0.3](/Users/aelaguiz/workspace/doctrine/docs/VSCODE_IMPORT_PATH_HIGHLIGHTING_AND_NAVIGATION_2026-04-07.md#L142).
- Resolved in `deep-dive`: structural local-key clicks should land on the immediate inherited owner, not the farthest ancestor, so the editor shows the actual merge boundary the author is editing against.
- Resolved in `deep-dive`: built-in `source:` and `target:` names remain intentionally non-clickable until the repo names a concrete file-backed or virtual-document destination, consistent with [Section 0.3](/Users/aelaguiz/workspace/doctrine/docs/VSCODE_IMPORT_PATH_HIGHLIGHTING_AND_NAVIGATION_2026-04-07.md#L143).
- Still requires live validation: whether the user-observed "not highlighting" symptom is stale VSIX state, theme visibility, or a real scope gap should be settled with one scope-inspector pass on `examples/03_imports` after reinstalling the packaged VSIX.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:external_research:start -->
# External Research (best-in-class references; plan-adjacent)

> Goal: anchor the plan in idiomatic, broadly accepted practices where applicable. This section intentionally avoids project-specific internals.

## Topics researched (and why)

- Navigation provider choice — the plan still needs the smallest VS Code-native surface that matches user expectation for Cmd-click and Go to Definition.
- Highlight visibility vs tokenization — the reported highlight issue can waste work if theme visibility is mistaken for tokenization drift.
- Runtime extension test strategy — adding editor runtime code will need a smallest-credible official verification path, not ad hoc UI harnesses.

## Findings + how we apply them

### Navigation Provider Choice

- Best practices (synthesized):
  - Use `DefinitionProvider` when the user expectation is standard "Go to Definition" behavior on a symbol-like reference.
  - Use `LocationLink[]` when precise origin and destination ranges matter.
  - Use `DocumentLinkProvider` when the clickable thing is a textual range that should open an internal or external resource directly, rather than behaving like a symbol definition.
- Recommended default for this plan:
  - Treat imported declaration refs and the remaining declaration-style surfaces as `DefinitionProvider` territory.
  - Keep raw `import` path text in `DocumentLinkProvider`; that surface is already shipped and should remain narrow.
  - Prefer direct provider registration over a full language server for the remaining phases too.
- Pitfalls / footguns:
  - Trying to get Cmd-click from TextMate grammar changes alone will fail because definition navigation is not a declarative grammar feature.
  - Using only `DocumentLinkProvider` for everything can undershoot normal VS Code "follow definition" expectations on symbol-like refs.
  - Jumping straight to an LSP would widen the implementation and test surface before the narrow provider approach is exhausted.
- Sources:
  - Programmatic Language Features — https://code.visualstudio.com/api/language-extensions/programmatic-language-features — official feature mapping for direct provider implementations.
  - VS Code API `registerDefinitionProvider` / `DefinitionProvider` / `LocationLink` — https://code.visualstudio.com/api/references/vscode-api — official contract for Go to Definition behavior and richer target ranges.
  - VS Code API `registerDocumentLinkProvider` / `DocumentLinkProvider` / `DocumentLink` — https://code.visualstudio.com/api/references/vscode-api — official contract for clickable document ranges.

### Highlight Visibility vs Tokenization

- Best practices (synthesized):
  - Separate tokenization from theming before changing a grammar.
  - Use the scope inspector to confirm emitted scopes and matched theme rules.
  - Prefer common TextMate scopes for better theme compatibility instead of inventing highly custom scope names unless necessary.
- Recommended default for this plan:
  - Treat scope-inspector evidence as the first gate before any grammar-scope retuning.
  - Keep the current common-scope strategy unless deep-dive finds a concrete coverage gap in the emitted scopes.
  - Validate the complaint on a built-in theme first so theme variance does not masquerade as grammar failure.
- Pitfalls / footguns:
  - A token can be classified correctly and still look visually flat in the active theme.
  - Switching to semantic tokens as a first move would add complexity without first proving TextMate scope output is insufficient.
  - New Doctrine-only scopes can reduce theme compatibility if existing common scopes were already adequate.
- Sources:
  - Syntax Highlight Guide — https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide — official explanation of tokenization vs theming.
  - Syntax Highlight Guide: Scope Inspector — https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#scope-inspector — official debugging workflow for emitted scopes and theme matches.
  - Semantic Highlight Guide — https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide — official explanation of semantic tokens as an additional, larger layer.

### Runtime Extension Test Strategy

- Best practices (synthesized):
  - Run extension integration tests inside the Extension Development Host with full VS Code API access.
  - Use the official `@vscode/test-cli` and `@vscode/test-electron` tooling for extension-host tests instead of bespoke runners.
  - Disable other installed extensions during debugging or test runs when isolation matters.
- Recommended default for this plan:
  - Keep existing grammar tests for lexical coverage.
  - Add a minimal official extension-host integration test layer only if runtime navigation code is introduced.
  - Prefer one or two focused navigation tests over a broad UI test suite, and run them with extensions disabled for determinism.
- Pitfalls / footguns:
  - Relying only on grammar tests will miss runtime provider regressions.
  - Debugging or running extension tests against a globally loaded extension set can hide or create false failures.
  - Building a custom UI harness before trying the official Extension Development Host path would be unnecessary ceremony.
- Sources:
  - Testing Extensions — https://code.visualstudio.com/api/working-with-extensions/testing-extension — official extension-host testing guidance.
  - Testing Extensions (`@vscode/test-cli`, `@vscode/test-electron`) — https://code.visualstudio.com/api/working-with-extensions/testing-extension — official recommended tools and quick setup.
  - Testing Extensions (`--disable-extensions`) — https://code.visualstudio.com/api/working-with-extensions/testing-extension — official guidance for isolating extension tests and debug runs.

## Adopt / Reject summary

- Adopt:
  - Prefer direct provider registration before any LSP move; this sharpens Section 5 and Section 7 toward a minimal runtime addition under `editors/vscode/`.
  - Default to `DefinitionProvider` for imported declaration refs and keep `DocumentLinkProvider` as a path-click supplement rather than the sole navigation surface.
  - Use scope-inspector-first debugging and built-in-theme validation before modifying TextMate scopes.
  - If runtime code is added, extend Section 8 toward official Extension Development Host integration tests with `@vscode/test-electron` and `--disable-extensions`.
- Reject:
  - Reject grammar-only fixes for Cmd-click behavior because official VS Code guidance places definition navigation in programmatic language features.
  - Reject semantic tokens as the first response to the highlight complaint because they widen the surface before the existing TextMate pipeline is exhausted.
  - Reject a full language server as the first move because the external guidance supports narrower direct providers for this scope.

## Open questions (ONLY if truly not answerable)

- None beyond the plan's existing evidence-based open questions in Section 3.3.
<!-- arch_skill:block:external_research:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- [doctrine/parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py#L75) and [doctrine/model.py](/Users/aelaguiz/workspace/doctrine/doctrine/model.py#L40) still define the shipped semantic shapes the editor must respect: `ImportPath`, `NameRef`, readable refs, authored-slot refs, patch-parent refs, and inheritance-key items.
- [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2697), [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2203), and [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L1556) own the real resolution contracts for direct declaration refs, readable refs, and structural inheritance semantics.
- [editors/vscode/package.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/package.json#L19) now ships a real runtime package boundary with `main`, `activationEvents`, unit/snapshot tests, and extension-host integration tests.
- [editors/vscode/extension.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/extension.js#L10) is a thin registrar for one `DocumentLinkProvider` and one `DefinitionProvider`.
- [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L123) is the only editor-side semantics adapter today. It owns prompt-root discovery from URIs, import scanning, full clickable-site classification, imported-module lookup, readable lookup, structural-key lookup, and declaration-header lookup.
- The verification surface is already split into three layers:
  - [editors/vscode/tests/unit/](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/unit) and [editors/vscode/tests/snap/](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/snap) prove lexical scopes
  - [editors/vscode/tests/integration/suite/index.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/suite/index.js#L20) proves the shipped full clickable contract
  - [examples/03_imports/cases.toml](/Users/aelaguiz/workspace/doctrine/examples/03_imports/cases.toml#L4) and the rest of `examples/` prove the language itself

## 4.2 Control paths (runtime)

- Packaging path is now `cd editors/vscode && make` -> `npm test` -> `scripts/validate_lark_alignment.py` -> `scripts/package_vsix.py`, with the generated VSIX reinstalled locally after each extension change.
- Runtime activation path is `package.json` -> [extension.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/extension.js#L10) -> `registerDocumentLinkProvider` and `registerDefinitionProvider`.
- Raw import-path flow is already stable:
  1. [provideImportLinks(...)](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L125)
  2. [getDocumentContext(...)](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L320)
  3. [collectImportEntries(...)](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L215)
  4. `DocumentLink` to the resolved `.prompt` URI
- Direct-definition flow is already stable for the shipped full surface:
  1. [provideDefinitionLinks(...)](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L147)
  2. [classifyDefinitionTarget(...)](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L248)
  3. [resolveRefTargetUri(...)](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L334)
  4. [findDeclaration(...)](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L349)
  5. `LocationLink` back to VS Code
- The widened control path now keeps one prompt-file index plus three lookup modes in one adapter: direct declaration refs, readable declaration refs, and structural inheritance-key refs.
- Remote-install behavior is still local-editor-side, as documented in [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md#L49), so stale local VSIX state remains a real explanation for mismatches between repo code and live editor behavior.

## 4.3 Object model + key abstractions

- The current adapter carries an indexed document state made of `DocumentContext`, normalized import entries, and a lightweight prompt index built from declaration headers and owner/body ranges.
- The widened adapter now models the full declaration-kind set, readable-registry lookup, interpolation-root ranges, and immediate-parent structural ownership in one file-backed resolver.
- The grammar already exposes most of the remaining lexical ranges, including interpolation roots, `inherit`, `override`, patch-parent refs, keyed refs, and standalone reference bodies, in [doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L150) through [doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json#L860).
- The adapter now explicitly tracks:
  - an indexed prompt declaration tree
  - an enclosing owner/body kind for the clicked line
  - a mirrored readable-declaration registry set
  - the immediate inherited source for `abstract`, `inherit`, and local-key `override`

## 4.4 Observability + failure behavior today

- Compiler behavior is still fail-loud and specific. Missing modules, missing imported declarations, readable-ref ambiguity, abstract-agent route misuse, and invalid inheritance all raise shipped Doctrine errors.
- Editor behavior now matches the planned code surface:
  - supported sites return precise `LocationLink` or `DocumentLink` targets
  - unresolved or ambiguous sites return `undefined` and do not guess
  - built-in input/output target names remain intentionally non-clickable
- Runtime observability exists now:
  - [tests/integration/suite/index.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/suite/index.js#L8) proves imports, direct declaration refs, readable refs, interpolation roots, and structural inheritance-key refs
  - live scope-inspector validation is still pending for the highlight complaint
- Grammar coverage and runtime coverage are now aligned for the shipped clickable surface; the remaining question is live token visibility in the installed editor theme.

## 4.5 UI surfaces (ASCII mockups, if UI work)

- No custom UI is expected. The relevant surface is the native editor experience on `.prompt` text.
- Current user-visible state is:
  - raw `import` paths click
  - direct declaration refs click across the full in-scope registry surface
  - standalone readable refs and interpolation roots click on the declaration root
  - structural `abstract`, `inherit`, and local-key `override` clicks land on the immediate inherited owner
  - built-in `source:` / `target:` names and interpolation field-path segments remain intentionally non-clickable
- The remaining inconsistency is only the still-unverified live theme visibility report, not missing navigation code.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep compiler semantics owned by `doctrine/`. Do not move import math, registry meaning, readable-ref ambiguity rules, or inheritance semantics out of the shipped language.
- Keep the runtime package boundary exactly where it is today:
  - [editors/vscode/package.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/package.json#L19) stays the manifest boundary
  - [editors/vscode/extension.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/extension.js#L10) stays a thin provider registrar
  - [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js#L123) stays the canonical editor adapter
- If the adapter needs internal decomposition, keep it as a local refactor under `editors/vscode/` with `resolver.js` remaining the exported façade. Do not introduce a new package, subprocess, or language-server boundary.
- Keep the existing integration harness under [editors/vscode/tests/integration/](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration) and widen it phase by phase over existing shipped examples rather than inventing editor-only fixtures.

## 5.2 Control paths (future)

- Raw `import` path text stays in the existing `DocumentLinkProvider`. That path is already correct and should remain narrow.
- Everything else in the full clickable contract stays in the existing `DefinitionProvider`, with the shipped definition flow organized around three explicit lookup modes over a shared prompt context and prompt index:
  1. `directDeclRef`
  2. `readableDeclRef`
  3. `structuralKeyRef`
- Future definition pipeline:
  1. build `PromptContext` for the current document: `promptRootUri`, `currentModuleParts`, and normalized import entries
  2. build or fetch a lightweight `PromptIndex` for the current document that records top-level declaration headers, parent refs, owner/body ranges, keyed entries, and interpolation-root ranges
  3. classify the clicked position into one of the supported site kinds
  4. resolve the target according to that site's contract
  5. return one precise `LocationLink` to the file-backed declaration header or inherited source line, or return no target rather than guessing
- Direct declaration-ref mode:
  - keeps the exact-registry model
  - covers authored-slot refs, override refs, workflow `skills` refs, patch-parent refs, `schema:`, and standalone I/O body refs
  - resolves target units only through the current file or imported modules, not arbitrary workspace search
- Readable-ref mode:
  - covers standalone workflow body refs and interpolation roots
  - mirrors [_resolve_readable_decl_lookup_unit(...)](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2568) and [_find_readable_decl_matches(...)](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L2579)
  - preserves compiler behavior for ambiguity, imported-module membership, workflow rejection, and abstract-agent rejection
- Structural-key mode:
  - covers `abstract`, `inherit`, and local-key `override` across workflows, skills blocks, I/O blocks, and authored slots
  - resolves through the immediate inherited owner that the current declaration or block is merging against
  - locates the keyed source line in that immediate parent body rather than skipping to a farther ancestor
- Runtime code should continue to use VS Code URIs and `openTextDocument`, not raw local-only file assumptions or shelling out to Python.

## 5.3 Object model + abstractions (future)

- The adapter should standardize around these internal contracts:
  - `PromptContext`
    - `promptRootUri`
    - `currentModuleParts`
    - normalized `importEntries`
  - `PromptIndex`
    - top-level declaration headers by kind and name
    - parent refs for inheritable declarations
    - owner/body ranges for workflows, skills blocks, I/O blocks, and agents
    - keyed entry locations within those bodies
    - interpolation root ranges inside authored prose surfaces
  - `DoctrineSite`
    - `importPathSite`
    - `directDeclRefSite`
    - `readableDeclRefSite`
    - `structuralKeyRefSite`
- Extend `DECLARATION_KIND` to cover every file-backed declaration family the full clickable contract needs:
  - `agent`
  - `workflow`
  - `skills`
  - `inputs`
  - `input`
  - `input_source`
  - `outputs`
  - `output`
  - `output_target`
  - `output_shape`
  - `json_schema`
  - `skill`
- Mirror the compiler's readable-declaration registry set from [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py#L199) inside the adapter rather than inventing a looser “search any declaration” rule.
- Keep the adapter deliberately narrow:
  - nearest `prompts/` root wins
  - leading-dot imports walk package parents exactly once per click resolution
  - imported refs only resolve through imported modules or the current module
  - structural key navigation only follows explicit parent or patch-parent ownership
  - built-in `source:` and `target:` names do not grow synthetic destinations in this plan
- Do not introduce a Python subprocess bridge, a language server, semantic tokens for navigation, or workspace-wide fuzzy search.

## 5.4 Invariants and boundaries

- Declarative grammar continues to own lexical scopes. Do not change `doctrine.tmLanguage.json` unless a scope-inspector pass proves the highlight complaint is a real emitted-scope problem rather than theme visibility or stale VSIX state.
- Runtime navigation should cover every compiler-resolved declaration ref surface plus structural inheritance-key refs. Unsupported click targets should remain unsupported only when there is no compiler-backed or inheritance-backed target to point at.
- Shipped today:
  - raw `import` paths
  - parent refs in declaration headers
  - authored-slot workflow refs and authored-slot overrides
  - workflow `use` targets, workflow override refs, and workflow `skills` refs
  - route targets
  - top-level `skills`, `inputs`, and `outputs` block refs
  - skill-entry refs
  - patch-parent refs
  - typed key-value refs for `source`, `target`, `shape`, and `schema`
  - standalone input and output declaration refs inside typed I/O bodies
  - standalone readable refs in workflow bodies
  - interpolation root refs inside strings
  - structural local-key refs such as `abstract`, `inherit`, and local-key `override`
- Scope choices locked in the shipped surface:
  - standalone `RecordRef` navigation stays limited to typed `inputs` and `outputs` bodies because that is the only shipped typed contract
  - interpolation is root-only; field-path segments after `:` stay non-clickable
  - structural local-key clicks land on the immediate inherited owner, not the farthest ancestor
  - built-in `source:` and `target:` names remain intentionally non-clickable until the repo names a concrete editor destination
- Explicit non-goals for the full clickable surface:
  - arbitrary prose words that merely match declaration names
  - interpolation field-path segment navigation after the declaration root
  - synthetic built-in source or target destinations without a concrete editor target
- No parallel paths: the canonical runtime path is `package.json` -> `extension.js` -> `resolver.js` -> VS Code providers. Do not keep an alternative subprocess, language server, or old narrow-classifier side path alive now that the unified site model exists.

## 5.5 UI surfaces (ASCII mockups, if UI work)

- The final editor surface should stay native to VS Code:
  - import paths look like Doctrine-scoped tokens under the scope inspector
  - Cmd-click on an `import` path opens the target `.prompt` file
  - Cmd-click or Go to Definition on any supported direct declaration ref lands on the correct declaration header
  - Cmd-click on a standalone readable ref or interpolation root lands on the same declaration family the compiler would read
  - Cmd-click on `abstract`, `inherit`, or local-key `override` lands on the immediate inherited owner that structurally provides that key
  - unsupported or unresolvable refs do not jump to guessed files or guessed names
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| VS Code runtime boundary | [editors/vscode/extension.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/extension.js) | `activate(context)` | Thin registrar for one document-link provider and one definition provider | Keep provider surface stable; only update imports or registration wiring if `resolver.js` is internally decomposed | The architecture should widen the shipped adapter, not add more provider types or a second runtime path | `extension.js` remains a thin façade over `resolver.js` exports | `cd editors/vscode && npm test`, `cd editors/vscode && make` |
| Navigation adapter | [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) | `DECLARATION_KIND`, `DECLARATION_PATTERNS`, `classifyDefinitionTarget`, `findDeclaration`, prompt-root/import helpers | Resolves the shipped full clickable surface through shared prompt context, prompt indexing, direct/readable/structural site classification, readable-registry lookup, and immediate-parent structural resolution | No code change required from the audit; keep this adapter as the only editor-side semantic boundary and only widen it if future compiler-backed surfaces are added | Full clickable parity converges here; drift elsewhere would recreate a second resolver | One `resolver.js` façade with shared `PromptContext`, `PromptIndex`, and `DoctrineSite` contracts | Extension-host integration suite; existing grammar tests stay green |
| Declaration header lookup | [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) | `findDeclaration(...)` and declaration regex table | Finds the full file-backed declaration set used by the shipped clickable contract, including `input`, `output`, and `json schema` | No code change required from the audit; keep keyed structural lookups landing on indexed source lines and top-level refs landing on declaration headers | Full direct-ref parity depends on this remaining exact-registry, not heuristic | `DeclarationKind` stays full-surface for file-backed declarations; keyed structural targets use indexed line ranges | Integration tests for `schema:`, standalone I/O refs, and structural inheritance keys |
| Readable-ref parity | [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) | readable lookup path in unified resolver | Standalone workflow body refs and interpolation roots resolve through the shipped readable-declaration mirror | No code change required from the audit; preserve compiler ambiguity, workflow rejection, and abstract-agent rejection rules exactly | Readable refs cannot safely devolve into generic name search | `readableDeclRefSite` resolves through imported/current units and readable registries only | Integration tests over `examples/15_workflow_body_refs`, `examples/16_workflow_string_interpolation`, and `examples/20_authored_prose_interpolation` |
| Structural inheritance parity | [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) | structural-key lookup in unified resolver | `abstract`, `inherit`, and local-key `override` resolve to the immediate inherited owner | No code change required from the audit; preserve immediate-parent key lookup across workflows, skills blocks, I/O blocks, and authored slots | Structural parity must keep using compiler-shaped ownership, not a second inheritance model | `structuralKeyRefSite` lands on the immediate inherited owner or abstract requirement | Integration tests over `examples/07_handoffs`, `examples/22_skills_block_inheritance`, `examples/24_io_block_inheritance`, `examples/25_abstract_agent_io_override`, and `examples/26_abstract_authored_slots` |
| Grammar surface | [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json) | interpolation, override, patch-parent, standalone-ref scopes | Emits the lexical ranges needed by the shipped clickable surfaces, with import-path highlighting still awaiting one live scope-inspector confirmation | No code change required from the audit; only make a narrow scope retune if manual editor evidence proves an emitted-scope gap | Grammar already supplies the lexical contract; navigation should not be forced back into the grammar | Grammar remains lexical-only, with no editor-side semantics hidden in scope names | Existing unit/snapshot suites if changed after live validation |
| Compiler / parser / model SSOT | [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py), [doctrine/parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py), [doctrine/model.py](/Users/aelaguiz/workspace/doctrine/doctrine/model.py) | typed `_resolve_*_ref` paths, readable registries, inheritance merge paths, semantic data model | Already define the policy the editor is trying to mirror | Preserve as SSOT; only extract a tiny pure helper or constant if implementation proves that is clearly cheaper than maintaining a second hard-coded copy | The editor must converge on shipped language truth, not fork it | No new runtime ownership under `doctrine/` | `make verify-examples` and targeted manifest verify if any `doctrine/` file changes |
| Runtime verification | [editors/vscode/tests/integration/suite/index.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/suite/index.js) | shipped extension-host assertion matrix | Covers imports, direct declaration refs, readable refs, interpolation roots, and structural inheritance keys across the shipped example corpus | No code change required from the audit; keep adding focused assertions only if future compiler-backed surfaces are introduced | Runtime regressions now live here, not just in grammar tests | One authoritative extension-host proof surface for full clickable parity | `cd editors/vscode && npm test`, `cd editors/vscode && make` |
| User-facing docs | [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md), [README.md](/Users/aelaguiz/workspace/doctrine/README.md) | README support matrix and repo blurb now describe the shipped full clickable surface and explicit non-goals | No code change required from the audit; keep docs aligned with the installed-VSIX manual validation result | Docs are now the main drift surface once runtime behavior broadens | README is the stable support contract for the finished extension surface | Manual finalization only |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/` continues to own import semantics and typed declaration meaning.
  - `editors/vscode/extension.js` remains the thin runtime registrar.
  - `editors/vscode/resolver.js` remains the only editor adapter, widened in place around shared context/index/site contracts.
  - Shared contract to preserve: nearest `prompts/` root, exact absolute and relative import normalization, imported-module membership checks, readable-registry ambiguity rules, and immediate-parent structural ownership.
- Deprecated APIs (if any):
  - None publicly. Do not reintroduce parallel “narrow slice” and “full parity” code paths side by side.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - None outstanding from the shipped implementation. Do not reintroduce a narrow-slice support matrix in [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md#L19).
  - Do not reintroduce dead first-cut classifier or declaration-map helpers in [resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js).
  - Do not keep a second navigation path alive, such as a subprocess resolver, speculative LSP stub, or workspace-wide fuzzy-search fallback.
- Capability-replacing harnesses to delete or justify:
  - A Python subprocess bridge is not the default architecture and would need explicit justification before implementation.
  - A language server is out of scope for this run and should not appear as a preparatory scaffold.
- Live docs/comments/instructions to update or delete:
  - [editors/vscode/README.md](/Users/aelaguiz/workspace/doctrine/editors/vscode/README.md)
  - [README.md](/Users/aelaguiz/workspace/doctrine/README.md)
  - Any inline code comments added at the navigation boundary must explain the compiler-ownership invariant rather than duplicate the whole resolver algorithm.
- Behavior-preservation signals for refactors:
  - `cd editors/vscode && npm test`
  - `cd editors/vscode && make`
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml` if import-resolution logic under `doctrine/` changes
  - `make verify-examples` if any `doctrine/` file changes outside the narrow import manifest path
  - `make verify-diagnostics` only if diagnostics change
  - One manual full-surface pass across the shipped example matrix at finalization

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Direct declaration refs | [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) direct site classifier + declaration map | unify all remaining exact-registry `NameRef` surfaces behind one direct-decl lookup mode | Prevents a second hand-maintained subset of “special clickable refs” from emerging | include |
| Readable registry parity | [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py) `_WORKFLOW_MENTION_REGISTRIES`, `_resolve_readable_decl` | mirror readable-declaration matching and ambiguity rules in the editor adapter | Prevents workflow-body and interpolation clicks from devolving into loose name search | include |
| Prompt indexing | [editors/vscode/resolver.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/resolver.js) current line-local classifier | promote line regexes into a shared prompt index with owner/body ranges and keyed entry locations | Readable and structural phases both need context beyond one isolated line | include |
| Structural key lookup | [doctrine/compiler.py](/Users/aelaguiz/workspace/doctrine/doctrine/compiler.py) authored-slot, workflow, skills, and I/O inheritance merge paths | navigate structural keys through immediate-parent ownership | Prevents local-key clicks from inventing a second inheritance model | include |
| Built-in source/target destinations | typed field handling | synthetic virtual docs for built-ins | Would invent a new product surface not backed by shipped files | exclude |
| Interpolation field-path segments | interpolation handling | per-segment field navigation after the root declaration | Adds product scope beyond the locked North Star | exclude |
| Grammar retune | [editors/vscode/syntaxes/doctrine.tmLanguage.json](/Users/aelaguiz/workspace/doctrine/editors/vscode/syntaxes/doctrine.tmLanguage.json) scope names | only revisit after live scope-inspector evidence | Prevents scope churn from masking a runtime architecture problem | defer |
| Semantic tokens or LSP | package-wide | wider editor architecture | Would add speculative infrastructure before the direct-provider path is exhausted | exclude |
| Python subprocess bridge | package-wide | shell out to `uv` or Python at click time | Creates an operational side path and remote-host coupling the direct JS adapter does not need | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with the smallest credible signal. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests (deletion checks, visual constants, doc-driven gates). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Runtime Scaffold And Import-Path Navigation

Status: COMPLETE

* Goal:
  Turn the grammar-only package into a minimal runtime extension with deterministic packaging and the smallest user-visible vertical slice: correct navigation on raw `import` paths.
* Work:
  Add `main`, `activationEvents`, runtime test wiring, and any required dev dependencies in `editors/vscode/package.json`.
  Add `editors/vscode/extension.js` and `editors/vscode/resolver.js` as the only new runtime code paths.
  Add an official extension-host integration test surface under `editors/vscode/tests/integration/` and wire it into `npm test` and `make`.
  Implement URI-based prompt-root discovery, current-module derivation, absolute and relative Doctrine import normalization, and raw `import` path range detection in the JS helper.
  Register a `DocumentLinkProvider` for raw import-path text and make it resolve only to exact `.prompt` module targets from the shipped Doctrine import rules.
  Add one short boundary comment in the resolver helper stating that compiler import semantics are the policy owner and the JS helper is an editor adapter.
* Verification (smallest signal):
  `cd editors/vscode && npm test`
  `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  Add the resolver-boundary comment only.
  Do not rewrite public docs yet; wait until the supported navigation surface is complete.
* Exit criteria:
  The packaged VSIX activates on Doctrine files.
  Absolute and relative import paths in `examples/03_imports` resolve to the correct module files.
  Existing grammar coverage stays green and the new extension-host path is part of normal package verification.
* Rollback:
  Revert the runtime entrypoint, integration harness, and manifest wiring together, restoring the package to a declarative-only state if scaffold or import-path behavior is not stable.

## Phase 2 — Typed Follow-Definition For Supported Import-Driven Refs

Status: COMPLETE

* Goal:
  Add Go to Definition for the first-cut typed ref set without widening into readable-ref ambiguity, interpolation handling, or local-section navigation.
* Work:
  Classify the supported typed ref sites: imported parent refs, `use` targets, route targets, and single-registry typed key-value refs such as `skills`, `inputs`, `source`, `target`, `shape`, and skill-entry targets.
  Map each supported site to an exact declaration kind or registry contract instead of a generic name search.
  Implement a `DefinitionProvider` that returns `LocationLink` targets for the correct declaration headers in the current or imported module.
  Keep standalone readable refs, interpolation refs, local section refs, and inline override refs explicitly deferred rather than partially guessing them.
  Add focused extension-host tests for at least one imported parent flow, one workflow `use` flow, one route target flow, and one typed key-value flow.
* Verification (smallest signal):
  `cd editors/vscode && npm test`
  `cd editors/vscode && make`
  `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml` only if any file under `doctrine/` changes during implementation.
* Docs/comments (propagation; only if needed):
  Add a short comment where the surface-kind to registry mapping lives if that dispatch would otherwise be non-obvious.
* Exit criteria:
  Supported typed refs navigate to the correct declaration headers.
  Deferred ref kinds are still explicitly unsupported rather than misresolved.
  No compiler or grammar regressions are introduced while the provider surface grows.
* Rollback:
  Revert the typed-ref mapping and `DefinitionProvider` registration while keeping Phase 1 scaffold and import-path navigation intact if the typed surface proves too broad or unstable.

## Phase 3 — Docs, Live Validation, And Any Proven Highlight Fix

Status: COMPLETE

* Goal:
  Finish the original user-facing problem by aligning docs with shipped behavior and only touching grammar scopes if live editor evidence proves the current emitted scopes are insufficient.
* Work:
  Rewrite `editors/vscode/README.md` to describe supported navigation, reinstall and reload steps, Extension Development Host usage, and scope-inspector debugging.
  Update the root `README.md` VS Code section if the package meaningfully expands beyond syntax highlighting.
  Rebuild and reinstall the VSIX locally, then validate `examples/03_imports` in VS Code or Cursor with the scope inspector and Cmd-click / Go to Definition.
  Only if the scope inspector proves a real emitted-scope gap, make the narrowest `doctrine.tmLanguage.json` adjustment needed and refresh the affected grammar snapshots or unit expectations.
  If implementation touched `doctrine/`, run the import corpus verify and update proof surfaces only where behavior preservation requires it.
  Implementation note: docs were updated during `implement`, but live scope-inspector and manual Cmd-click validation still need a human editor session.
* Verification (smallest signal):
  `cd editors/vscode && npm test`
  `cd editors/vscode && make`
  `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml` only if any file under `doctrine/` changes
  Manual finalization in VS Code or Cursor: inspect the import-path scope, Cmd-click a raw import path, and Go to Definition on one supported typed ref from `examples/03_imports`
* Manual QA (non-blocking):
  Reinstall the packaged VSIX in VS Code or Cursor, then run one live scope-inspector and Cmd-click pass against `examples/03_imports`.
* Docs/comments (propagation; only if needed):
  Delete or rewrite syntax-highlighting-only claims in `editors/vscode/README.md`.
  Sync the repo-root README extension blurb to the shipped behavior.
* Exit criteria:
  Live docs match the shipped extension behavior.
  The original highlight complaint has been resolved either by proving the current scopes are fine after reinstall/theme inspection or by landing a narrow grammar fix backed by tests.
  The final packaged VSIX behaves correctly on the supported import-driven surfaces.
* Rollback:
  Revert any unproven grammar retuning or doc claims that outstate shipped behavior, while keeping only the verified runtime navigation surface.

## Phase 4 — Remaining Direct Declaration Ref Coverage

Status: COMPLETE

* Goal:
  Close the remaining direct declaration-ref surfaces that already have an exact compiler-owned target but are still non-clickable in the editor.
* Work:
  Add authored-slot workflow refs and authored-slot override refs such as `read_first: SharedReadFirst` and `override read_first: ProjectLeadReadFirst`.
  Add workflow override refs, including override-based workflow targets and workflow `skills:` / `override skills:` refs.
  Add inputs and outputs patch-parent refs such as `inputs[BaseSectionInputs]` and `outputs[BaseSectionOutputs]`.
  Add typed `schema:` refs that target `json schema` declarations.
  Add standalone input and output declaration refs inside I/O bodies where context already constrains the registry exactly.
  Reuse existing resolver classification and declaration lookup helpers rather than introducing a second navigation path.
* Verification (smallest signal):
  `cd editors/vscode && npm test`
  `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  Extend the README support matrix only after this direct-ref parity lands.
* Exit criteria:
  Every direct declaration-ref site backed by an exact registry contract is clickable.
  Override syntax and patch-parent syntax no longer behave like second-class refs.
* Rollback:
  Revert any newly added surface classifier that guesses across multiple registries instead of routing through exact compiler-owned meaning.

## Phase 5 — Readable Refs And Interpolation Root Navigation

Status: COMPLETE

* Goal:
  Add navigation for the compiler's readable-declaration surfaces without weakening the existing fail-loud ambiguity contract.
* Work:
  Add standalone readable refs in workflow bodies by reusing the compiler's readable-declaration matching model and ambiguity behavior.
  Add interpolation root navigation for strings such as `{{CurrentPlan:source.path}}` by making the declaration root clickable while leaving field-path segment navigation out of scope.
  Add integration coverage for examples that exercise workflow body refs, string interpolation refs, and agent-mention-style readable refs.
  Keep the implementation rooted in compiler-owned declaration classes and ambiguity rules rather than heuristic name search.
* Verification (smallest signal):
  `cd editors/vscode && npm test`
  `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  Update the README support matrix to distinguish interpolation-root navigation from unsupported field-path-segment navigation.
* Exit criteria:
  Standalone readable refs and interpolation roots are clickable and fail loudly when the compiler would treat them as ambiguous or invalid.
  The editor does not guess on bare names that the compiler would reject.
* Rollback:
  Revert readable-ref handling if the implementation cannot preserve compiler ambiguity rules exactly.

## Phase 6 — Structural Inheritance-Key Navigation

Status: COMPLETE

* Goal:
  Add navigation for structural local-key refs that the compiler resolves through inheritance merge logic instead of `NameRef` syntax.
* Work:
  Add navigation for `abstract`, `inherit`, and local-key `override` sites across workflows, skills blocks, inputs blocks, outputs blocks, and authored slots.
  Make those clicks land on the inherited source entry or abstract requirement that structurally owns the key.
  Add focused integration coverage over inheritance-heavy examples such as workflow merge, handoffs, skills-block inheritance, I/O block inheritance, abstract-agent I/O override, and abstract authored slots.
  Keep the implementation fail-loud when a structural source cannot be identified uniquely.
* Verification (smallest signal):
  `cd editors/vscode && npm test`
  `cd editors/vscode && make`
* Docs/comments (propagation; only if needed):
  Document that these clicks navigate by inherited structural ownership rather than by declaration-name lookup.
* Exit criteria:
  Structural inheritance-key refs are clickable anywhere the compiler resolves them meaningfully.
  Local-key navigation does not introduce a heuristic parallel resolver.
* Rollback:
  Revert any structural-key navigation that cannot identify the inherited source deterministically.

## Phase 7 — Full-Surface Docs And Live Validation

Status: IN PROGRESS

Completed work:
- `editors/vscode/README.md` and the repo-root `README.md` already describe the shipped full-clickable surface and explicit non-goals.
- Re-entered `implement` after the implementation audit and confirmed there is no remaining code delta for this plan; the runtime surface, tests, and packaging path are already in place.
- Re-ran `uv sync` and `cd editors/vscode && make`, and packaged a fresh VSIX at `editors/vscode/doctrine-language-0.0.1775617708985.vsix`.

* Goal:
  Finalize the editor surface against the full clickable contract and re-run live validation over the real example matrix instead of the original import-only slice.
* Work:
  Rewrite the VS Code README support matrix to list the full clickable ref families and the remaining explicit non-goals.
  Docs were updated during the implementation pass and now describe the shipped full-clickable surface.
  Run one live editor validation pass across examples that cover imports, authored-slot refs, typed declaration refs, readable refs, interpolation roots, and structural inheritance keys.
  Only if the live pass still proves an emitted-scope problem, make the narrowest grammar retune needed and refresh the affected snapshots.
  Keep the root README aligned with the full clickable surface without duplicating the extension README.
* Verification (smallest signal):
  `cd editors/vscode && npm test`
  `cd editors/vscode && make`
  Manual finalization in VS Code or Cursor across `examples/03_imports`, `07_handoffs`, `09_outputs`, `15_workflow_body_refs`, `16_workflow_string_interpolation`, `20_authored_prose_interpolation`, `24_io_block_inheritance`, and `26_abstract_authored_slots`
* Manual QA (non-blocking):
  Reinstall `editors/vscode/doctrine-language-0.0.1775617708985.vsix`, then run the live scope-inspector and Cmd-click matrix across the examples listed above.
* Docs/comments (propagation; only if needed):
  Delete any README claim that still describes the current narrow slice as if it were the final scope.
* Exit criteria:
  The docs describe the full clickable contract truthfully.
  Live editor behavior matches the full in-scope surface.
* Rollback:
  Revert any doc claim or grammar retune that outstates verified behavior.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

- Avoid verification bureaucracy.
- Prefer the smallest existing signal.
- Default to 1-3 checks total.
- Do not invent new harnesses, frameworks, or scripts unless they are the cheapest credible guardrail.
- Keep UI and manual verification as finalization by default.
- For refactors, prefer behavior-preservation checks that survive restructuring.
- Do not create proof tests for deletions, visual constants, or doc inventories.
- Document tricky invariants and gotchas at the SSOT or contract boundary.

## 8.1 Unit tests (contracts)

- Keep existing `cd editors/vscode && npm test` grammar coverage green.
- Prefer a small extension-host or unit contract for resolver and navigation behavior over broad UI goldens.
- If runtime navigation code is added, use the official Extension Development Host test path with `@vscode/test-electron` instead of a custom runner.
- If any file under `doctrine/` changes while preserving import semantics, run `uv run --locked python -m doctrine.verify_corpus --manifest examples/03_imports/cases.toml`.
- Do not add tests that merely restate deleted paths or theme colors.

## 8.2 Integration tests (flows)

- Prefer one or two end-to-end editor flows around `examples/03_imports` if runtime navigation is added.
- Run those flows with other extensions disabled when determinism matters.
- Reuse shipped import fixtures instead of inventing synthetic ones.

## 8.3 E2E / device tests (realistic)

- Manual finalization check in VS Code or Cursor: open a `.prompt` file, inspect scopes on an import path, Cmd-click supported refs, and verify unresolved targets fail loudly.
- Keep manual UI checks non-blocking until finalization.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- This is a repo-local extension. Rollout means rebuilding the VSIX, reinstalling it locally, and reloading the editor window.
- Keep README install and refresh steps aligned with any new runtime behavior.

## 9.2 Telemetry changes

- None expected unless `deep-dive` finds an existing local logging or diagnostics surface worth reusing.

## 9.3 Operational runbook

- Primary runbook is local: build and install the VSIX, reload the editor, validate on `examples/03_imports`, and confirm unresolved targets fail loudly.

# 10) Decision Log (append-only)

## 2026-04-07 - Start from grammar-vs-navigation split

Context

- User reported that import paths do not look highlighted in VS Code and Cmd-click does not follow definitions.

Options

- Treat both symptoms as one grammar bug.
- Split the problem into tokenization/theming versus navigation contracts.

Decision

- Split the problem. Repo evidence already shows import-path token scopes exist, while navigation is absent because no runtime language feature is contributed.

Consequences

- The plan can stay minimal and avoid changing shipped language semantics.
- Research and implementation must validate live editor behavior before rewriting grammar scopes.

Follow-ups

- Use `research` to ground the exact VS Code feature contracts and likely minimum provider surface.

## 2026-04-07 - Keep compiler import resolution as SSOT

Context

- `doctrine/compiler.py` already resolves Doctrine absolute and relative imports from the `prompts/` root and current package.

Options

- Re-implement Doctrine import resolution independently in the editor.
- Reuse or extract the shipped resolver semantics for editor navigation.

Decision

- Treat compiler import resolution as the canonical truth and design editor navigation around it.

Consequences

- The plan avoids semantic drift between compile-time behavior and editor navigation.
- Any extension runtime code must either call shared logic or mirror it from a deliberately extracted pure helper.

Follow-ups

- `deep-dive` should identify the cleanest shared boundary.

## 2026-04-07 - Treat Cmd-click as a programmatic language feature

Context

- Official VS Code docs separate declarative language features like syntax highlighting from programmatic language features like Go to Definition, and the API exposes both definition and document-link providers.

Options

- Expect TextMate grammar changes alone to produce click navigation.
- Plan around a small programmatic provider surface.

Decision

- Assume grammar changes alone are insufficient for Cmd-click navigation and evaluate a definition or document-link provider in later stages.

Consequences

- The fix surface is broader than `tmLanguage` only but can still stay minimal.
- The repo may need runtime extension code and tests where none exist today.

Follow-ups

- `research` should choose the smallest provider surface that matches expected user behavior.

## 2026-04-07 - Prefer direct providers and official extension-host tests

Context

- External VS Code guidance clarifies that narrow programmatic language features can be implemented directly without a language server, and that runtime extension behavior should be tested in the Extension Development Host with the official test tooling.

Options

- Build the first navigation cut with direct providers plus minimal official extension-host tests.
- Jump directly to a full language server or a custom UI-heavy test harness.

Decision

- Prefer direct providers for the first navigation cut and, if runtime code is added, verify it with the official `@vscode/test-electron` Extension Development Host path.

Consequences

- The plan stays minimal and aligned with official VS Code guidance.
- Section 8 should favor a small integration layer over bespoke harnesses if runtime navigation is introduced.

Follow-ups

- `deep-dive` should map the exact provider split and choose the smallest new runtime entrypoint and test files under `editors/vscode/`.

## 2026-04-07 - Use a minimal JS adapter, not a subprocess or LSP

Context

- The extension needs runtime navigation, but the repo-local package has no existing JS or TS entrypoint and current Remote SSH docs already show how local-versus-remote execution details can create confusion.

Options

- Shell out to Python so the editor directly reuses compiler code at click time.
- Add a full language server and move navigation there.
- Add a minimal JS runtime entrypoint plus a narrow Doctrine navigation helper that mirrors only the compiler-owned import and typed-ref contract.

Decision

- Use a minimal JS runtime entrypoint with direct VS Code providers and a narrow URI-based Doctrine helper. Keep compiler semantics as the policy owner and do not add a subprocess bridge or LSP for the first cut.

Consequences

- The extension stays idiomatic to VS Code and avoids remote-host and environment coupling to `uv` or Python execution.
- The navigation helper must stay deliberately small, type-aware, and verified against shipped import fixtures so it does not become a second policy owner.

Follow-ups

- `phase-plan` should implement the direct-provider path and explicitly defer broader readable-ref, interpolation, and local-section navigation unless they become nearly free.

## 2026-04-07 - Stage import paths before broader ref coverage

Context

- The plan now has a clear runtime shape, but it still needs an execution order that delivers the user-reported import-path problem first without widening into every Doctrine reference surface.

Options

- Land broad typed navigation and possible grammar retuning in one large pass.
- Stage the work as runtime scaffold plus raw import-path navigation first, then typed follow-definition for the first-cut supported ref set, and only change grammar scopes if live scope-inspector evidence proves it is necessary.

Decision

- Use three phases: runtime scaffold plus import-path navigation, typed follow-definition for supported import-driven refs, then docs plus live validation with grammar changes only if the editor evidence requires them.

Consequences

- The plan gets an early vertical slice that proves URI and import semantics before broadening into more ref kinds.
- Grammar churn stays conditional instead of being treated as inevitable.

Follow-ups

- `implement` should preserve the explicit defers for standalone readable refs, interpolation refs, local section refs, and inline override refs unless they become nearly free without widening scope.

## 2026-04-07 - Ship direct providers with explicit defers

Context

- The minimal runtime extension and official extension-host test path were implemented under `editors/vscode/`, and the first typed-definition surface is now working against shipped example files.

Options

- Widen immediately into standalone readable refs, interpolation refs, local section refs, and inline override refs.
- Ship the verified direct-provider slice and keep the broader surfaces explicitly deferred.

Decision

- Ship the verified `DocumentLinkProvider` plus `DefinitionProvider` slice and leave the broader non-import-driven or ambiguity-prone surfaces deferred.

Consequences

- The extension now supports the requested import-path and import-driven navigation behavior without widening into a second resolver or speculative editor infrastructure.
- Manual live editor validation for scope inspector and Cmd-click behavior still remains as a final human check outside the headless test environment.

Follow-ups

- Run a live VS Code or Cursor pass on `examples/03_imports` before closing the plan completely, and only touch grammar scopes if that pass proves the current emitted scopes are insufficient.

## 2026-04-07 - Import paths need definition-provider parity and a stronger theme scope

Context

- Headless tests passed, but live editor use still reported flat import-path styling and no normal Cmd-click behavior on raw `import` lines after reinstall.

Options

- Keep import paths on document links only and treat the live report as editor variance.
- Add import-path handling to the `DefinitionProvider` and strengthen the import-path TextMate scope with a more theme-friendly standard scope while preserving the Doctrine reference scope.

Decision

- Add import-path definition targets and retune the import-path capture to include `entity.name.namespace.doctrine support.type.reference.doctrine`.

Consequences

- Raw `import` lines now participate in normal Go to Definition behavior instead of depending on link-only UX.
- Import paths keep the Doctrine-specific scope but gain a standard namespace scope that more themes are likely to render distinctly.

Follow-ups

- Reinstall the newly packaged VSIX and re-check `examples/03_imports` in the live editor.

## 2026-04-07 - Expand the plan from a narrow slice to full clickable parity

Context

- The initial plan intentionally shipped a narrow provider slice, but live usage confirmed that "imports plus a few typed refs" is not the desired end state. The requested behavior is the full clickable Doctrine surface.

Options

- Keep the plan locked to the current narrow slice and treat broader navigation as future work outside this artifact.
- Expand the plan so the remaining compiler-backed and structural ref surfaces become open phases in the same canonical artifact.

Decision

- Expand the plan. Keep Phases 1-3 as completed groundwork, then add explicit open phases for remaining direct declaration refs, readable/interpolation-root refs, structural inheritance-key refs, and final full-surface validation.

Consequences

- The implementation audit is no longer code-complete for the broadened plan.
- The plan now treats the current shipped slice as groundwork rather than the finish line.

Follow-ups

- Implement Phases 4-7 without inventing virtual built-in targets, field-path-segment navigation, or other product-scope expansions that the current language truth does not already require.

## 2026-04-07 - Widen the shipped adapter instead of rebuilding the extension

Context

- Phases 1-3 already shipped a real runtime boundary under `editors/vscode/`, but Sections 4-6 were still describing a pre-runtime architecture and had not specified how the remaining readable and structural phases should converge.

Options

- Treat Phases 4-7 as a second architecture effort with new provider types, a subprocess bridge, or a language-server boundary.
- Keep the existing provider pair and widen the current `resolver.js` boundary around shared prompt context, prompt indexing, direct declaration lookup, readable lookup, and structural key lookup.

Decision

- Keep `extension.js` and the current provider pair stable. Widen `resolver.js` in place as the one editor adapter, with three explicit lookup modes: direct declaration refs, readable declaration refs, and structural local-key refs. Structural clicks land on the immediate inherited owner, not a farther ancestor.

Consequences

- The remaining phases now converge on one runtime file boundary instead of growing a second resolver path.
- The open phase work is concentrated in `resolver.js`, the integration suite, and README support truth rather than another manifest or architecture rewrite.
- Research questions about generic `RecordRef` breadth, root-only interpolation clicks, built-in source/target behavior, and structural-target depth are now resolved for this artifact.

Follow-ups

- Refresh `phase-plan` only if the existing Phases 4-7 no longer match this unified resolver-centered architecture.
