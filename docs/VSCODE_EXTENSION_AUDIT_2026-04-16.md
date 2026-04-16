---
title: "Doctrine - VS Code Extension Parity - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: parity_plan
related:
  - editors/vscode/README.md
  - editors/vscode/package.json
  - editors/vscode/extension.js
  - editors/vscode/resolver.js
  - editors/vscode/syntaxes/doctrine.tmLanguage.json
  - editors/vscode/scripts/validate_lark_alignment.py
  - editors/vscode/tests/integration/suite/index.js
  - doctrine/grammars/doctrine.lark
  - docs/LANGUAGE_REFERENCE.md
  - docs/EMIT_GUIDE.md
  - examples/README.md
---

# TL;DR

## Outcome

Bring the VS Code extension back into full parity with the shipped Doctrine
language for highlighting, click following, and proof-backed README claims.

## Problem

The extension still passes its current test suite, but it has drifted on newer
shipped language surfaces such as top-level `table`, inline `final_output:`
blocks, top-level `render_profile`, and `output target delivery_skill:`.

## Approach

Treat the shipped grammar and manifest-backed corpus as the source of truth.
Update `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
`editors/vscode/resolver.js`, and the extension proof surface together so every
claimed editor feature is both implemented and tested.

## Plan

1. Tighten the extension's source-of-truth boundaries and proof surface.
2. Add missing first-class support for named tables and top-level
   `render_profile`.
3. Add missing navigation support for inline `final_output:` blocks and
   `delivery_skill:`.
4. Expand tests, validator coverage, packaged smoke, and README claims so the
   extension only promises what it proves.

## Non-negotiables

- `doctrine/grammars/doctrine.lark` and the shipped corpus stay the language
  truth.
- No keyword-only parity theater. Claimed surfaces need real highlighting or
  navigation support plus proof.
- No new language server, hover, rename, or speculative editor platform work.
- No overclaim in `editors/vscode/README.md`.
- No silent drift between shipped docs, shipped examples, TextMate grammar,
  resolver behavior, and packaged extension behavior.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
external_research_grounding: not started
deep_dive_pass_2: done 2026-04-16
recommended_flow: deep dive -> deep dive again -> phase plan -> consistency pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If we align the VS Code extension to the shipped Doctrine grammar and late
example corpus, then the extension will correctly highlight and navigate the
full repo-discoverable shipped language surface, its README will stop
overclaiming, and `cd editors/vscode && make` will prove those claims through
real unit, snapshot, integration, validator, and packaging checks.

## 0.2 In scope

- Highlighting parity for shipped top-level declarations and late syntax forms,
  including `table`, `render_profile`, `review_family`, `route_only`, and
  `grounding`.
- Click following and go-to-definition parity for shipped repo-discoverable
  references, including named tables, inline `final_output:` bodies, route
  fields, and `delivery_skill:`.
- Resolver parity for repo-visible prompt roots and runtime-package shapes
  already supported by the compiler and documented by the extension.
- Tightening `validate_lark_alignment.py` so it proves real declaration and
  surface coverage, not just keyword presence.
- Growing `editors/vscode/tests/` so late shipped examples and feature families
  have direct coverage.
- Packaged extension proof for the VSIX path the README tells users to install.
- README and smoke-ladder updates so the public extension contract matches the
  proved surface.
- Limited internal convergence work inside `editors/vscode/` when needed to
  remove duplicated feature tables or other drift-prone hard-coded mappings.

## 0.3 Out of scope

- Adding a full language server.
- Adding completion, hover, rename, symbol search, or semantic diagnostics
  beyond the current extension contract.
- Changing Doctrine language behavior in `doctrine/` just to make the editor
  easier to implement.
- Runtime-only provider roots that exist only at emit-time and have no
  discoverable editor-side config contract in the repo today.
- Broad editor UX redesign beyond what is needed to keep current VS Code or
  Cursor install and smoke paths truthful.

## 0.4 Definition of done (acceptance evidence)

- The extension correctly highlights and navigates the shipped parity gaps
  already found in the audit:
  - top-level `table`
  - block-form `final_output:` with nested `output:` and `route:`
  - top-level `render_profile`
  - `output target delivery_skill:`
- The extension also directly proves late declaration families and late output
  surfaces from the shipped corpus, especially examples `64`, `68`-`71`,
  `104`, `116`, `118`, `119`, `120`, and `121`.
- `editors/vscode/scripts/validate_lark_alignment.py` fails if a shipped
  declaration or special surface is only present as a generic keyword.
- `cd editors/vscode && npm test` passes.
- `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`
  passes.
- `cd editors/vscode && make` passes after implementation.
- One packaged VSIX smoke path proves the shipped artifact still exposes the
  same core editor behavior as the source-tree test host.
- `editors/vscode/README.md` only claims surfaces that are implemented and
  directly proved.

## 0.5 Key invariants (fix immediately if violated)

- Shipped language truth stays in `doctrine/` plus the manifest-backed corpus.
- The TextMate grammar owns highlighting truth. The resolver owns navigation
  truth. The validator and tests own proof truth. README only reports proven
  truth.
- No first-class shipped declaration should exist only as a generic keyword in
  the TextMate grammar.
- No shipped clickable ref surface should rely on README claims without direct
  tests.
- No runtime shim or fallback that hides unsupported editor behavior.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Match shipped Doctrine truth before adding editor cleverness.
2. Fix concrete parity gaps before polishing broad maintainability.
3. Expand proof at the same time as implementation.
4. Keep the extension thin and local to current repo patterns.
5. Make README claims strictly evidence-backed.

## 1.2 Constraints

- The extension is intentionally lightweight today: one TextMate grammar, one
  custom resolver, and no language server.
- `extension.js` only wires document links and go-to-definition.
- `resolver.js` is large and hand-written, so drift risk is already high.
- The shipped corpus now reaches `121_nullable_route_field_final_output_contract`.
- Repo policy requires `cd editors/vscode && make` for changes under
  `editors/vscode/`.
- The worktree is dirty, so this plan must converge on canonical extension
  paths without relying on destructive cleanup.

## 1.3 Architectural principles (rules we will enforce)

- The shipped grammar and examples decide what the editor must support.
- Every claimed editor feature must have one canonical implementation path and
  one direct proof path.
- Prefer first-class declaration or field rules over generic keyword buckets and
  fallback regexes.
- Prefer explicit body-spec modeling over heuristic line scanning when the
  language now has a real structure.
- Keep package-install truth aligned with source-tree truth.

## 1.4 Known tradeoffs (explicit)

- Some resolver convergence work may widen beyond the four concrete gaps if
  that is the cleanest way to remove drift-prone duplicated mappings.
- Expanding proof will cost time now, but the current green suite already shows
  that cheap proof is not enough.
- A small structural split inside `resolver.js` may be warranted if that is the
  least risky way to make late-surface support maintainable. A speculative
  rewrite is not warranted.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The current extension has:

- language registration in `editors/vscode/package.json`
- provider wiring in `editors/vscode/extension.js`
- custom import and definition logic in `editors/vscode/resolver.js`
- TextMate highlighting rules in
  `editors/vscode/syntaxes/doctrine.tmLanguage.json`
- a validator in `editors/vscode/scripts/validate_lark_alignment.py`
- unit, snapshot, and integration tests in `editors/vscode/tests/**`
- packaging through `editors/vscode/Makefile` and `package:vsix`

The current suite is green, but the audit already proved that green status does
not mean current parity.

## 2.2 What’s broken / missing (concrete)

- Top-level `table` is shipped Doctrine, but the extension does not model it as
  a first-class declaration for highlighting or navigation.
- Inline `final_output:` bodies are shipped Doctrine, but the resolver does not
  model nested `output:` and `route:` lines as final-output metadata.
- Top-level `render_profile` is shipped Doctrine, but the TextMate grammar does
  not highlight it as a declaration.
- `delivery_skill:` is shipped on `output target`, but the resolver does not
  map it to `skill`.
- `route_only`, `grounding`, and `review_family` have partial support, but weak
  direct proof.
- The validator mostly checks whether keywords appear somewhere in regex text.
- The README claims a full shipped clickable surface that the proof does not
  support.
- The packaged VSIX path is not directly smoke-tested.

## 2.3 Constraints implied by the problem

- The fix must touch implementation, proof, and docs together.
- Late shipped examples need to become direct proof surfaces, not just audit
  references.
- Packaging must be treated as part of the contract because the README tells
  users to install the VSIX, not the source tree.
- Any convergence work inside `resolver.js` must preserve current working
  behavior on older surfaces.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- none needed beyond Doctrine's own shipped language and current extension
  contract
- reject a language-server detour for this plan; the repo already ships one
  TextMate grammar plus one resolver path, and the parity gap is inside that
  surface

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` - shipped language truth. It declares
    top-level `render_profile`, `table`, `route_only`, `grounding`, and
    `review_family`, plus block-form `final_output:` and
    `output target delivery_skill:`.
  - `docs/LANGUAGE_REFERENCE.md` - shipped contract for named tables,
    `render_profile`, `final_output.route:`, and `delivery_skill:`.
  - `editors/vscode/package.json` - one extension entrypoint, one grammar path,
    and the truthful command surface: `npm test` plus `package:vsix`.
  - `editors/vscode/extension.js` - the extension only registers document links
    and definition providers. There is no second navigation engine.
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json` - sole highlighting
    owner. It already groups `workflow|route_only|grounding`,
    `review|review_family`, and nested `final_output` fields, but it has no
    top-level declaration rule for `render_profile` or `table`, and
    `delivery_skill` only appears in a generic keyword bucket.
  - `editors/vscode/resolver.js` - sole navigation owner. It already has
    explicit declaration regexes for `review_family`, `route_only`,
    `grounding`, and `render_profile`, plus direct `render_profile` refs and
    readable table descendant handling. It still has no first-class top-level
    `TABLE` declaration kind, no `delivery_skill` field mapping, and no agent
    child-body spec for block-form `final_output:`.
  - `editors/vscode/scripts/validate_lark_alignment.py` - proof gate, but still
    mostly checks keyword presence across regex text plus a small fixed sample
    list. It does not yet assert first-class support for `table`,
    `render_profile`, `review_family`, `route_only`, `grounding`, or
    `delivery_skill`.
  - `editors/vscode/tests/integration/run.js` - extension-host test runner. It
    stages a source-tree copy and explicitly excludes `.vsix`, so current
    integration proof does not exercise the packaged artifact.
- Canonical path / owner to reuse:
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json` - highlight owner
  - `editors/vscode/resolver.js` - navigation owner
  - `editors/vscode/tests/**`, `editors/vscode/scripts/validate_lark_alignment.py`,
    `editors/vscode/package.json`, and `editors/vscode/scripts/package_vsix.py`
    - proof and packaging owner
- Adjacent surfaces tied to the same contract family:
  - `editors/vscode/tests/unit/declarations.test.prompt` - direct declaration
    proof is still missing `table`, `render_profile`, `review_family`,
    `route_only`, and `grounding`.
  - `editors/vscode/tests/unit/io-blocks.test.prompt` - already proves nested
    `final_output` syntax highlighting and should stay in sync with resolver
    parity.
  - `editors/vscode/tests/integration/suite/index.js` - direct integration
    proof covers example `64` `render_profile` refs and scalar `final_output:`,
    but it does not cover examples `68`, `69`, `70`, `71`, `116`, `118`,
    `119`, `120`, or `121`.
  - `editors/vscode/tests/snap/examples/**` - snapshot proof covers scalar
    `final_output:` and inline table surfaces, but named-table and late-family
    proof is still thin.
  - `editors/vscode/README.md` - public contract claims a full shipped
    clickable surface, including structured-final-output route surfaces.
  - `editors/vscode/.vscodeignore` and `editors/vscode/scripts/package_vsix.py`
    - the packaged VSIX strips tests and scripts, so packaged proof must use a
    real VSIX smoke path.
- Compatibility posture (separate from `fallback_policy`):
  - preserve existing working import and navigation behavior while extending the
    current contract to late shipped surfaces
  - keep ambiguous imports and unsupported built-ins fail-closed, matching the
    current extension behavior and README contract
- Existing patterns to reuse:
  - shared declaration grouping for `workflow|route_only|grounding` in both the
    TextMate grammar and resolver
  - shared declaration grouping for `review|review_family`
  - existing direct `render_profile` ref handling in analysis, schema, and
    document collectors
  - existing `readable_table_body` and descendant-path handling for inline
    document tables
  - existing nested `final_output` highlighting in the TextMate grammar and
    unit tests
- Duplicate or drifting paths relevant to this change:
  - top-level declaration support is split between first-class declaration
    regexes and generic keyword or readable-block buckets, which hides missing
    `table` and `render_profile` parity
  - README claims outrun direct proof
  - source-tree integration proof outruns packaged-artifact proof
- Capability-first opportunities before new tooling:
  - none needed; this is not a model-capability problem
  - parity work should extend the current TextMate and resolver owners instead
    of adding a language server or helper daemon
- Behavior-preservation signals already available:
  - `cd editors/vscode && npm test`
  - `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`
  - `cd editors/vscode && make`
  - current integration checks for imports, output inheritance,
    `render_profile` refs, and scalar `final_output:`

## 3.3 Decision gaps that must be resolved before implementation

- none from repo truth today
- Section `0.3` already leaves emit-time provider roots with no editor-side
  discovery contract out of scope for this plan
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `editors/vscode/package.json` declares one `doctrine` language, one grammar
  path, one entrypoint, and three test layers plus `package:vsix`.
- `editors/vscode/extension.js` is thin. It only registers
  `provideImportLinks` and `provideDefinitionLinks`.
- `editors/vscode/resolver.js` is the one real navigation engine. It owns
  import resolution, declaration indexing, keyed field mapping, child-body
  specs, addressable-path descent, and final definition lookup.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` is the only highlighting
  owner. Top-level patterns already cover `analysis`, `decision`, `schema`,
  `document`, `workflow|route_only|grounding`, `review|review_family`, and the
  `output` family, plus nested `final_output` fields.
- `editors/vscode/scripts/validate_lark_alignment.py` checks package wiring,
  keyword coverage, and a small fixed sample list.
- `editors/vscode/tests/unit/*.test.prompt` pins local token scopes.
- `editors/vscode/tests/snap/examples/**` mirrors a subset of shipped examples.
- `editors/vscode/tests/integration/suite/index.js` drives example-backed
  Ctrl/Cmd-click and Go to Definition assertions through
  `tests/integration/run.js`.
- `editors/vscode/scripts/package_vsix.py` and `editors/vscode/.vscodeignore`
  own the packaged VSIX shape.
- `editors/vscode/README.md` is the public contract for install, smoke, and
  claimed feature coverage.

## 4.2 Control paths (runtime)

Current highlight path:

1. VS Code loads `source.doctrine` from `package.json`.
2. TextMate highlighting walks the top-level `patterns` list in
   `doctrine.tmLanguage.json`.
3. Top-level declaration lines match first-class declaration regexes only when
   the grammar has an explicit pattern for that family.
4. Missing first-class declaration matchers fall back to generic keyword or
   readable-block rules, which can hide parity drift while still coloring part
   of the line.

Current navigation path:

1. `extension.js` registers providers for `language: doctrine`.
2. `provideImportLinks` in `resolver.js` resolves raw `import` and
   `from ... import` paths.
3. `provideDefinitionLinks` classifies the active line, collects candidate
   sites, and resolves each site against declaration indexes and addressable
   descendants.
4. Declaration indexing starts from `DECLARATION_DEFINITIONS`,
   `DECLARATION_KIND`, and `ADDRESSABLE_DECLARATION_KINDS`.
5. Body-aware descent depends on `getAgentChildBodySpec`,
   `getReviewChildBodySpec`, `getReadableChildBodySpec`,
   `keyedFieldToDeclarationKind`, and `keyedRecordFieldToDeclarationKind`.

Current package path:

1. `npm test` runs unit, snapshot, and integration checks.
2. `package:vsix` then runs the validator and packages the VSIX.
3. `tests/integration/run.js` stages a source-tree copy of the extension and
   explicitly excludes `.vsix`.
4. `.vscodeignore` strips tests, scripts, `Makefile`, and `node_modules` from
   the packaged extension.
5. The shipped package path is therefore not exercised by the extension-host
   integration runner.

## 4.3 Object model + key abstractions

- `resolver.js` has one declaration model:
  `DECLARATION_KIND`, `DECLARATION_DEFINITIONS`,
  `ADDRESSABLE_DECLARATION_KINDS`, and `SELF_ADDRESSABLE_DECLARATION_KINDS`.
- `DECLARATION_DEFINITIONS` already has explicit regexes for
  `review_family`, `route_only`, `grounding`, and `render_profile`, but it has
  no top-level `table` declaration row.
- `TOP_LEVEL_FIELD_REF_RE` handles scalar agent refs like
  `analysis:`, `decision:`, `skills:`, `inputs:`, `outputs:`, and
  `final_output: Name`.
- `KEYED_DECL_REF_RE` handles `source|target|shape|schema|structure|render_profile`,
  but not `delivery_skill`.
- `getAgentChildBodySpec` opens inline I/O blocks, patched I/O blocks, skills
  blocks, and authored slot bodies. It does not open a nested
  `final_output:` body.
- `getReadableChildBodySpec` already gives `table` a readable-body model for
  document-local table blocks, including columns, rows, and row bodies.
- `collectAnalysisBodySites`, `collectSchemaBodySites`, and
  `collectDocumentBodySites` already resolve direct `render_profile:` refs.
- The TextMate grammar mixes first-class declaration patterns with broad
  fallback keyword buckets. `delivery_skill` is only present in a generic
  keyword matcher today.
- The validator is mixed: it already pins some concrete surfaces such as
  `skill grounding`, scalar and block `final_output`, route fields, and inline
  readable `table` headers, but it still misses top-level `table`,
  top-level `render_profile`, `review_family`, `route_only`, `grounding`, and
  `delivery_skill`.

## 4.4 Observability + failure behavior today

- Ambiguous absolute imports fail closed today. The integration suite already
  asserts that no synthetic target is produced for an ambiguous import.
- Unsupported built-in roots stay unsupported. The README already documents that
  limit.
- The repo has three programmatic signals now:
  `cd editors/vscode && npm test`,
  `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`,
  and `cd editors/vscode && make`.
- Those signals can still miss first-class declaration drift, because keyword
  presence and source-tree integration are broader than real shipped parity.
- Current direct parity proof for this story is narrow:
  integration pins `render_profile` refs on example `64` and scalar
  `final_output:` on example `76`, but not the late-family and late-output
  examples this plan needs.
- The package path has no real installed-artifact behavior proof beyond
  successful packaging.
- The README claims a fuller clickable surface than the current direct proof
  can support.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not a product UI change. The user-facing surface is the editor experience:

```text
.prompt file open in VS Code
├── top-level declarations get the right token scopes
├── nested refs in bodies get the right token scopes
├── import paths Ctrl/Cmd-click into real files
├── Go to Definition lands on the real declaration or keyed descendant
└── README smoke steps tell the truth about the installed VSIX
```
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/` plus manifest-backed examples stay the only shipped language
  truth.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` stays the one highlight
  owner. Missing shipped declaration families are added there, not in a second
  grammar surface.
- `editors/vscode/resolver.js` stays the one navigation owner. Missing table,
  final-output-body, and `delivery_skill` parity is added there, not in a new
  parser or language server.
- `editors/vscode/tests/**`,
  `editors/vscode/scripts/validate_lark_alignment.py`,
  `editors/vscode/tests/integration/run.js`,
  `editors/vscode/scripts/package_vsix.py`, and
  `editors/vscode/.vscodeignore` together own proof for source-tree and package
  truth.
- `editors/vscode/README.md` stays the only public extension contract and is
  narrowed or expanded to match direct proof.

## 5.2 Control paths (future)

Future highlight path:

1. A shipped declaration or field surface appears in `doctrine/` plus examples.
2. The TextMate grammar gets a first-class declaration matcher or explicit
   field matcher when that is the real authored surface.
3. Unit syntax proof, snapshots where useful, and validator samples pin that
   exact line shape.

Future navigation path:

1. A shipped clickable surface appears in `doctrine/` plus examples.
2. `resolver.js` adds the missing declaration kind, keyed field mapping, or
   child-body spec on the current owner path.
3. Existing descendant logic is reused where possible instead of creating a
   second path model.
4. Integration tests pin one real example for the root and one real example for
   the descendant or nested field when the surface is structured.

Future package path:

1. Source-tree tests stay green.
2. Validator stays green with feature-specific surface assertions.
3. One packaged VSIX smoke path installs the generated VSIX into an isolated
   extension host and runs a narrow late-surface smoke suite against that
   packaged artifact.
4. `cd editors/vscode && make` remains the one truthful final repo command.

## 5.3 Object model + abstractions (future)

- Add `DECLARATION_KIND.TABLE` and wire it through the declaration index,
  addressable-declaration list, and any self-addressable list needed for table
  root and descendant navigation.
- Keep the existing `RENDER_PROFILE` declaration kind, but pair it with a
  first-class TextMate declaration matcher and validator samples.
- Extend `keyedRecordFieldToDeclarationKind` with `delivery_skill -> skill`
  inside output-target bodies.
- Extend `getAgentChildBodySpec` with an explicit `final_output_body`, then
  reuse existing keyed-field and path-resolution logic inside that body instead
  of heuristic scans.
- Reuse the current readable-table descendant model for named tables rather
  than creating a second table-path engine.
- Add one small structured parity matrix only if it reduces duplicate feature
  wiring. Keep it inside the current owner files. Do not create a second source
  of truth.

## 5.4 Invariants and boundaries

- One grammar owner. One resolver owner. One proof surface. No language server,
  no sidecar parser, and no second navigation engine.
- Preserve current fail-closed behavior for ambiguous imports and unsupported
  built-ins.
- Preserve current working older surfaces while adding late shipped surfaces.
- No first-class shipped declaration can rely on generic keyword fallback alone.
- No package claim without package proof.
- No README claim without direct proof.
- No parity fix may change Doctrine language behavior in `doctrine/`.

## 5.5 UI surfaces (ASCII mockups, if UI work)

```text
Author opens a late-corpus .prompt file
├── top-level declaration token is scoped correctly
├── nested field token is scoped correctly
├── Ctrl/Cmd-click lands on the real declaration or descendant
├── Go to Definition works on that same surface
└── installed VSIX matches the README smoke ladder
```
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Provider wiring | `editors/vscode/extension.js` | `activate`, `provideImportLinks`, `provideDefinitionLinks` | one thin registration point | preserve this thin shell; keep all parity work in current owners | avoids a second navigation engine | no new provider layer | existing integration host |
| Highlight declarations | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | top-level declaration patterns and include order | first-class patterns cover many families, but not top-level `table` or `render_profile` | add first-class declaration matchers for those families and keep include order honest | shipped language truth now includes those declarations | first-class declaration surfaces highlight as declarations | unit syntax, snapshots, validator |
| Highlight late families | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | grouped `workflow|route_only|grounding` and `review|review_family` rules | grouped rules exist, but direct proof is thin | preserve grouped rules and add direct proof for each shipped family | avoids drift inside grouped matchers | grouped declaration contract becomes directly pinned | declarations unit test, snapshots, validator |
| Highlight nested final output | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | `finalOutputField`, `finalOutputOutputField`, `finalOutputRouteField` | nested `final_output` syntax already highlights | preserve this surface while aligning resolver behavior to it | prevents highlight and navigation from drifting apart | nested final output remains a first-class authored surface | unit I/O syntax tests |
| Delivery-skill field | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | generic keyword bucket | `delivery_skill` is only present in a generic keyword matcher | keep the current field highlight path and add direct proof so the scope stays honest | the real known gap is navigation, but proof should still cover the field surface | field highlighting stays truthful to actual feature scope | validator, targeted syntax proof |
| Declaration index | `editors/vscode/resolver.js` | `DECLARATION_KIND`, `DECLARATION_DEFINITIONS`, `ADDRESSABLE_DECLARATION_KINDS`, `SELF_ADDRESSABLE_DECLARATION_KINDS` | explicit rows exist for `review_family`, `route_only`, `grounding`, `render_profile`, but not `table` | add `TABLE` and wire it through the current declaration index and addressable lists | named tables need a real root owner | top-level tables become real navigation roots | declarations unit proof, integration suite |
| Scalar agent refs | `editors/vscode/resolver.js` | `TOP_LEVEL_FIELD_REF_RE`, `keyedFieldToDeclarationKind` | scalar `final_output: Name` already resolves to `output` | preserve existing scalar behavior while adding structured-body support | older surfaces must not regress | scalar and block `final_output` both work | existing final-output tests, integration |
| Nested final-output body | `editors/vscode/resolver.js` | `getAgentChildBodySpec` and body-site collection | agent child-body logic does not open nested `final_output:` | add explicit `final_output_body` and route nested `output:` and `route:` through current keyed-field and path logic | block-form final output is shipped and currently under-modeled | nested final-output body becomes a real navigation container | unit I/O tests, examples `120` and `121` |
| Output-target delivery skill | `editors/vscode/resolver.js` | `KEYED_DECL_REF_RE`, `keyedRecordFieldToDeclarationKind` | no `delivery_skill -> skill` mapping today | add explicit mapping in output-target context | shipped delivery binding is invisible in navigation | `output target delivery_skill:` navigates to `skill` | example `118`, integration suite |
| Named-table descendants | `editors/vscode/resolver.js` | `getReadableChildBodySpec`, readable-table containers, declaration lookup | readable table descendants work for document-local tables, but top-level named-table declarations do not have a first-class root path | reuse current readable-table descendant engine once top-level `table` is indexed | avoids a second table-path model | named table declarations and named use sites share one path model | example `116`, snapshots, integration |
| Render-profile refs | `editors/vscode/resolver.js` | `collectAnalysisBodySites`, `collectSchemaBodySites`, `collectDocumentBodySites` | direct `render_profile:` refs already resolve in these bodies | preserve this path and broaden proof | existing owner path is correct | no new render-profile resolver path needed | example `64`, declarations/unit proof |
| Validator depth | `editors/vscode/scripts/validate_lark_alignment.py` | keyword scan plus fixed sample list | already samples `skill grounding`, nested `final_output`, route fields, and inline `table`, but can still pass while late declaration parity is wrong | add feature-specific declaration and field samples for `table`, `render_profile`, `review_family`, `route_only`, `grounding`, nested `final_output`, and `delivery_skill` | proof must fail for the right reason | validator proves structure, not just words | validator itself, `make` |
| Declarations unit proof | `editors/vscode/tests/unit/declarations.test.prompt` | declaration matrix | stops before late declaration families and new top-level forms | extend with `table`, `render_profile`, `review_family`, `route_only`, and `grounding` | first-class declaration support needs direct proof | declaration matrix matches shipped families | unit syntax suite |
| I/O unit proof | `editors/vscode/tests/unit/io-blocks.test.prompt` | nested `final_output`, route fields | baseline nested final-output syntax exists | add direct proof for the late structured-output cases that matter to navigation | current syntax proof is ahead of navigation proof | structured final-output route contract becomes direct proof | unit syntax suite |
| Integration coverage | `editors/vscode/tests/integration/suite/index.js` | example-backed definition assertions | current suite covers imports, older addressable paths, workflow law, review, `render_profile` refs, and scalar `final_output:` | add direct assertions for examples `68`, `69`, `70`, `71`, `116`, `118`, `119`, `120`, and `121` | late shipped families are still outside direct example proof | shipped late surfaces become example-backed | integration suite |
| Snapshot breadth | `editors/vscode/tests/snap/examples/**` | subset of shipped examples | snapshots cover older roots and some inline table/final-output cases | add late examples only where snapshot signal is real | keeps syntax proof broad without mirror spam | snapshot set stays proportional to shipped syntax | snapshot suite |
| Packaged artifact proof | `editors/vscode/tests/integration/run.js`, `editors/vscode/scripts/package_vsix.py`, `editors/vscode/.vscodeignore`, `editors/vscode/package.json` | source-tree test host vs packaged VSIX | integration host stages source tree and strips `.vsix`; package step only checks that packaging succeeds | add one packaged VSIX smoke path inside the current package flow | users install the VSIX, not the staged source tree | package contract is proved against the real artifact | package smoke, `make` |
| Public contract | `editors/vscode/README.md` | support list and smoke ladder | claims exceed direct proof and omit late parity smoke steps | narrow or expand claims to match proof and add late example smoke steps | docs are part of the shipped extension contract | README becomes evidence-backed | docs review, final `make` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - shipped language truth remains in `doctrine/` plus manifest-backed examples
  - highlight parity remains in `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - navigation parity remains in `editors/vscode/resolver.js`
  - proof remains in existing tests, validator, and package flow
- Deprecated APIs (if any):
  - none user-facing
  - internally, generic keyword-only declaration coverage should stop standing
    in for first-class declaration support where the language has a real
    declaration form
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - stale README claims that outrun proof
  - stale validator assumptions that keyword presence is enough
  - any duplicate feature wiring table introduced during implementation if one
    canonical list can own the same truth
- Adjacent surfaces tied to the same contract family:
  - `doctrine/grammars/doctrine.lark`
  - `docs/LANGUAGE_REFERENCE.md`
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json`
  - `editors/vscode/resolver.js`
  - `editors/vscode/tests/unit/*.test.prompt`
  - `editors/vscode/tests/snap/examples/**`
  - `editors/vscode/tests/integration/suite/index.js`
  - `editors/vscode/tests/integration/run.js`
  - `editors/vscode/scripts/validate_lark_alignment.py`
  - `editors/vscode/scripts/package_vsix.py`
  - `editors/vscode/.vscodeignore`
  - `editors/vscode/README.md`
- Compatibility posture / cutover plan:
  - preserve existing working covered surfaces
  - add missing late shipped surfaces on the same owner paths
  - keep ambiguous imports and unsupported built-ins fail-closed
  - no runtime bridge or compatibility shim is needed
- Capability-replacing harnesses to delete or justify:
  - none exist today
  - do not add a language server, sidecar parser, or helper daemon for this
    parity story
- Live docs/comments/instructions to update or delete:
  - `editors/vscode/README.md`
  - high-leverage resolver or validator comments only if new owner tables would
    otherwise be hard to follow
- Behavior-preservation signals for refactors:
  - `cd editors/vscode && npm test`
  - `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`
  - `cd editors/vscode && make`
  - late-example integration assertions once they land

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Declaration support | `editors/vscode/syntaxes/doctrine.tmLanguage.json`, `editors/vscode/resolver.js` | one explicit first-class owner per shipped declaration family the extension claims to support | prevents drift from generic keyword fallback | include |
| Structured-body navigation | `editors/vscode/resolver.js` | explicit child-body support for nested `final_output:` | prevents line-level heuristics from swallowing real structure | include |
| Table descent | `editors/vscode/resolver.js` | reuse one readable-table descendant engine for inline and named tables | avoids a second table-path model | include |
| Proof ownership | validator plus tests | feature-specific proof tied to late shipped examples | prevents false green confidence | include |
| Package truth | `editors/vscode/tests/integration/run.js`, packaging scripts, `.vscodeignore` | one packaged VSIX smoke path inside the current package flow | prevents source-tree-only confidence | include |
| Public contract | `editors/vscode/README.md` | only claim what current proof covers | prevents user-facing overclaim | include |
| Monolith cleanup | `editors/vscode/resolver.js` | small local consolidation if it removes duplicate feature wiring | lowers future drift without speculative rewrite | include only where needed |
| Emit-time provider roots | extension import resolution | runtime-host discovery contract | repo truth does not expose an editor-side discovery contract today | exclude |
<!-- arch_skill:block:call_site_audit:end -->

# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

<!-- arch_skill:block:phase_plan:start -->
## Phase 1 - Parity foundations and explicit declaration support

### Goal

Make the extension's feature tables honest and first-class for shipped
declaration surfaces before adding late navigation fixes.

### Work

This phase establishes one trustworthy parity base: real declaration rules for
late shipped forms, no hidden generic-keyword support masquerading as parity,
and proof surfaces that can fail for the right reason.

### Checklist (must all be done)

- Add first-class TextMate declaration coverage for top-level `table`.
- Add first-class TextMate declaration coverage for top-level
  `render_profile`.
- Tighten `workflow|route_only|grounding` declaration handling so it matches the
  shipped grammar instead of looser invented syntax.
- Extend declaration proof in `editors/vscode/tests/unit/declarations.test.prompt`
  to cover `table`, `render_profile`, `review_family`, `route_only`, and
  `grounding`.
- Tighten `validate_lark_alignment.py` so it asserts the real declaration
  patterns and not just shipped keyword presence.
- Add one small internal feature map or equivalent structured owner table if
  that is the cleanest way to stop duplicate feature wiring from drifting.

### Verification (required proof)

- `cd editors/vscode && npm run test:unit`
- `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`

### Docs/comments (propagation; only if needed)

- Add only high-leverage comments if the new feature table or declaration owner
  split would otherwise be non-obvious to later maintainers.

### Exit criteria (all required)

- Top-level `table` and `render_profile` highlight as declarations.
- Late declaration families have direct syntax proof.
- The validator fails if those declarations regress back to keyword-only
  coverage.

### Rollback

- Revert declaration and validator changes together if they destabilize older
  declaration highlighting.

## Phase 2 - Named table highlighting and navigation parity

### Goal

Make named tables behave like the shipped language says they behave, both at the
top-level declaration root and at the named document use-site.

### Work

This phase fixes the most concrete shipped parity gap: first-class named tables.
It should treat top-level `table` declarations and named `table local_key:
TableRef` document entries as real resolver surfaces.

### Checklist (must all be done)

- Add a first-class `TABLE` declaration kind or equivalent canonical resolver
  owner.
- Parse top-level `table` declarations into the resolver index.
- Recognize named document table use-sites such as
  `table release_gates: ReleaseGates required`.
- Make named table roots and descendants navigate through the same addressable
  path system the shipped docs promise.
- Add direct integration proof for example `116`.
- Add any snapshot coverage needed so named table syntax is visible in the
  extension proof tree.

### Verification (required proof)

- `cd editors/vscode && npm run test:integration`
- targeted syntax and snapshot checks that cover example `116`

### Docs/comments (propagation; only if needed)

- Update README smoke steps if named tables become a newly advertised surface.

### Exit criteria (all required)

- Top-level `table` is both highlighted and navigable.
- Named document table headers resolve to the real table declaration.
- Addressable named-table descendants from example `116` navigate correctly.

### Rollback

- Revert named-table resolver work if it breaks older inline table navigation.

## Phase 3 - Final output and delivery-skill navigation parity

### Goal

Make late output surfaces navigable with explicit structure instead of generic
fallbacks.

### Work

This phase covers block-form `final_output:` and `output target delivery_skill:`
because both are shipped structures that the resolver still treats too
generically today.

### Checklist (must all be done)

- Add an explicit child body for block-form `final_output:`.
- Resolve nested `output:` inside that body to the chosen `output`
  declaration.
- Resolve nested `route:` inside that body to the chosen route field.
- Add direct keyed-field resolution for `delivery_skill:` to `skill`.
- Add direct validator or syntax proof for nested `final_output:` field lines and
  `delivery_skill:` field lines so the field-surface contract stays honest.
- Add integration coverage for examples `118`, `120`, and `121`.
- Preserve existing scalar `final_output: Name` behavior.
- Preserve existing fail-closed behavior on unsupported built-in destinations
  and ambiguous roots.

### Verification (required proof)

- `cd editors/vscode && npm run test:integration`
- targeted unit coverage if new syntax classification needs it
- `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`

### Docs/comments (propagation; only if needed)

- Keep comments local to the final-output body model or keyed-field map if the
  new owner path would otherwise be unclear.

### Exit criteria (all required)

- Block-form `final_output:` surfaces navigate correctly.
- `delivery_skill:` navigates to the target skill.
- Nested `final_output:` and `delivery_skill:` field surfaces have direct proof.
- Examples `118`, `120`, and `121` have direct extension proof.

### Rollback

- Revert the final-output body and delivery-skill changes together if they
  destabilize older output navigation.

## Phase 4 - Late-family and late-output proof expansion

### Goal

Turn the late shipped corpus into direct extension proof so green checks mean
something again.

### Work

This phase expands proof breadth across the feature families the audit showed
are underrepresented: `review_family`, `route_only`, `grounding`, output
inheritance attachments, late route contracts, nullable route fields, and other
late shipped examples.

### Checklist (must all be done)

- Add direct integration assertions for examples `68`, `69`, `70`, and `71`.
- Add late structured-output parity proof for examples `104`, `119`, `120`, and
  `121`.
- Add targeted proof for output inheritance surfaces where current proof is too
  narrow, especially examples `108`, `110`, `111`, and `112`.
- Grow snapshot coverage by feature family where it adds real signal.
- Keep the suite lean: do not add random example mirrors that do not protect a
  concrete risk.

### Verification (required proof)

- `cd editors/vscode && npm test`

### Docs/comments (propagation; only if needed)

- None expected beyond test-local why-comments if a new regression would be hard
  to understand later.

### Exit criteria (all required)

- Late declaration families and late output surfaces named in this phase have
  direct extension proof.
- The suite stays lean enough to explain what each new test protects.
- Green test status now covers the late examples the README and shipped docs
  depend on.

### Rollback

- Revert only low-value proof growth if the suite becomes noisy or redundant.
  Keep any proof needed for the concrete parity fixes.

## Phase 5 - Packaged proof and public contract alignment

### Goal

Make the shipped VSIX and the README tell the same truthful story as the source
tree.

### Work

This phase closes the last parity gap between source-tree development and the
artifact users actually install.

### Checklist (must all be done)

- Add one packaged VSIX smoke path that installs the generated VSIX into an
  isolated extension host and can fail when packaging strips or misstates the
  shipped runtime files.
- Keep `.vscodeignore` aligned with the actual runtime contract.
- Update `editors/vscode/README.md` support claims so they match direct proof.
- Expand the README smoke ladder to include the late high-risk examples that are
  now directly supported.
- Ensure `cd editors/vscode && make` is the one truthful repo command for final
  extension verification.

### Verification (required proof)

- `cd editors/vscode && make`

### Docs/comments (propagation; only if needed)

- Update README only. Do not create extra point-in-time extension docs if the
  README can own the contract.

### Exit criteria (all required)

- The packaged VSIX path has one real smoke signal.
- That smoke signal runs against the generated VSIX, not the staged source tree.
- README claims are fully evidence-backed.
- The final extension verification command for this repo is truthful and green.

### Rollback

- Revert only README or packaged smoke changes if the implementation surface is
  not yet stable enough to support the stronger contract.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Keep `editors/vscode/tests/unit` as the focused declaration and syntax matrix.
- Add direct units for late declaration families and late syntax forms rather
  than relying on generic keyword buckets.
- Keep `validate_lark_alignment.py` as a contract check, but make it assert
  real feature patterns.

## 8.2 Integration tests (flows)

- Grow `editors/vscode/tests/integration/suite/index.js` with direct assertions
  for the late high-risk examples named in Section 7.
- Use shipped examples as proof inputs wherever possible instead of synthetic
  fixtures.
- Keep `cd editors/vscode && npm test` green throughout the implementation arc.

## 8.3 E2E / device tests (realistic)

- Add one packaged VSIX smoke path that runs against the generated artifact in
  an isolated extension host.
- Keep manual editor token inspection and Ctrl/Cmd-click smoke as finalization,
  not as the only proof.
- After code changes under `editors/vscode/`, run `cd editors/vscode && make`.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship as a repo-local extension improvement with no Doctrine language contract
  change.
- Keep existing supported surfaces working while adding late-surface parity.
- Only strengthen README claims once the proof is in place.

## 9.2 Telemetry changes

No telemetry changes are expected.

## 9.3 Operational runbook

- Build and verify with `cd editors/vscode && make`.
- If live editor behavior disagrees with tests, check installed VSIX version,
  then inspect editor scopes and definition targets using the existing README
  smoke steps.
- Keep packaged smoke in the same runbook once Phase 5 lands.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass

- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, TL;DR, Sections `0` through `10`
  - owner-path consistency across Sections `3`, `5`, `6`, and `7`
  - phase obligation coverage against migration notes, delete lists, and proof
    claims
  - verification and package-proof alignment across Sections `0`, `5`, `7`,
    `8`, and `9`
- Findings summary:
  - Phase `3` had one orphaned obligation: Section `6` required direct
    `delivery_skill` and nested `final_output` field proof, but Section `7`
    did not own that work explicitly enough.
  - Phase `5` and Section `8` left the package-proof shape too loose after the
    deep-dive decision to use a real VSIX smoke path.
- Integrated repairs:
  - Phase `3` now explicitly owns direct validator or syntax proof for nested
    `final_output:` and `delivery_skill:` field surfaces.
  - Phase `5` now states that the packaged smoke path installs the generated
    VSIX into an isolated extension host.
  - Section `8.3` now matches that packaged-smoke contract.
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

## 2026-04-16 - Treat shipped language truth as the extension contract

### Context

The source audit found real extension drift even though the current extension
checks were green.

### Options

- Keep the current extension contract centered on whatever the current tests
  happen to cover.
- Treat `doctrine/` plus the manifest-backed corpus as the source of truth and
  make the extension catch up.

### Decision

Treat shipped Doctrine language truth as the extension contract, and treat the
current extension suite as underpowered proof that must be strengthened.

### Consequences

- Implementation must touch code, proof, and docs together.
- README claims that outrun proof must be narrowed or the proof must be grown.
- Generic keyword-only coverage is no longer enough for first-class surfaces.

### Follow-ups

- Use this plan to drive deep dive, phase plan confirmation, and implementation.

## 2026-04-16 - Keep this plan inside the current extension scope

### Context

The user asked for exhaustive parity on highlighting and click following, but
the repo evidence still shows a thin TextMate-plus-resolver extension, not a
language-server product.

### Options

- Expand this plan into a language-server rewrite.
- Keep this plan focused on the existing extension surface and converge it to
  shipped truth.

### Decision

Keep the plan focused on the current extension surface: TextMate grammar,
resolver behavior, proof, packaging, and README truth.

### Consequences

- The plan can be exhaustive within the current product boundary without
  inventing new editor product scope.
- Resolver convergence is allowed where needed, but a speculative rewrite is
  not required.

### Follow-ups

- If this parity work reveals a genuine product limit that only a language
  server can solve, record that separately after the current parity story is
  clean.

## 2026-04-16 - Reuse current extension owners and add package proof in place

### Context

Deep-dive pass 1 showed that the current extension already has one clear owner
for each concern: the TextMate grammar for highlighting, the resolver for
navigation, and the existing test and package flow for proof.

### Options

- Add a second parser, language server, or helper daemon for late shipped
  surfaces.
- Extend the current grammar, resolver, tests, validator, and package flow in
  place.

### Decision

Extend the current owner paths in place. Do not add a second parser, language
server, or new navigation engine. Add packaged proof inside the current package
flow instead of inventing a second proof lane.

### Consequences

- Top-level declaration parity lands in `doctrine.tmLanguage.json`.
- Table, nested `final_output`, and `delivery_skill` parity lands in
  `resolver.js`.
- Package truth must be proved through the current package flow, not assumed
  from source-tree integration alone.

### Follow-ups

- Deep-dive pass 2 should keep this owner-path choice fixed and harden any
  remaining completeness gaps before `phase-plan`.

## 2026-04-16 - Use a real VSIX smoke path for package truth

### Context

The current extension-host runner stages a source-tree copy and explicitly
excludes `.vsix`, while `.vscodeignore` strips tests and scripts from the
packaged artifact. That leaves a real package-proof gap.

### Options

- Keep package proof as a manifest or file-shape audit only.
- Add a narrow smoke path that runs against the generated VSIX itself.

### Decision

Use a real VSIX smoke path inside the current package flow. Do not treat a
manifest-only audit as the main package-proof story for this plan.

### Consequences

- The package contract is proved against the artifact users install.
- Source-tree integration and package proof stay distinct and honest.
- Phase 5 should wire the smallest credible packaged smoke path, not a second
  broad integration harness.

### Follow-ups

- `phase-plan` should keep the package-smoke scope narrow and tie it to the
  late high-risk surfaces in this plan.

# Appendix B) Conversion Notes

- Converted the source audit report into the canonical `arch-step` artifact in
  place, per the user request.
- Re-homed the concrete audit findings into Sections 2, 3, 6, and 7.
- Preserved the source audit's key evidence: the four concrete parity gaps, the
  proof gaps, the coverage counts, and the recommended repair order.
- No Appendix A was needed because the source audit content was fully placed in
  the canonical structure.
