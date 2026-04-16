---
title: "Doctrine - VS Code Extension Parity - Architecture Plan"
date: 2026-04-16
status: draft
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
deep_dive_pass_1: not started
external_research_grounding: not started
deep_dive_pass_2: not started
recommended_flow: deep dive -> phase plan -> consistency pass -> implement
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

- none needed beyond Doctrine's own shipped language and extension contract
- reject a language-server detour for this plan; the current product is a thin
  TextMate-plus-resolver extension and the parity gap is inside that surface

## 3.2 Internal ground truth (code as spec)

- Authoritative language truth:
  - `doctrine/grammars/doctrine.lark`
  - `docs/LANGUAGE_REFERENCE.md`
  - `examples/README.md`
  - shipped examples through `examples/121_nullable_route_field_final_output_contract`
- Authoritative extension behavior owners:
  - `editors/vscode/syntaxes/doctrine.tmLanguage.json` for highlighting
  - `editors/vscode/resolver.js` for document links and definition targets
  - `editors/vscode/extension.js` only for provider registration
  - `editors/vscode/tests/**` and
    `editors/vscode/scripts/validate_lark_alignment.py` for proof
  - `editors/vscode/package.json`, `editors/vscode/Makefile`, and
    `editors/vscode/scripts/package_vsix.py` for shipped artifact behavior
- Canonical owner path to reuse:
  - shipped language truth remains in `doctrine/` and the manifest-backed
    example corpus
  - editor parity work belongs inside `editors/vscode/`
  - no second grammar source of truth outside the TextMate grammar and no
    second navigation source of truth outside the resolver
- Adjacent surfaces tied to the same parity story:
  - `editors/vscode/README.md`
  - `editors/vscode/tests/unit/*.test.prompt`
  - `editors/vscode/tests/snap/examples/**`
  - `editors/vscode/tests/integration/suite/index.js`
  - `editors/vscode/tests/integration/run.js`
  - `editors/vscode/.vscodeignore`
- Compatibility posture:
  - preserve existing working extension behavior while making late shipped
    language surfaces work
  - keep ambiguous imports and unsupported built-ins fail-closed, matching
    current documented behavior
- Existing reusable patterns:
  - declaration-kind tables and named-ref resolution in `resolver.js`
  - focused syntax units plus integration assertions in `editors/vscode/tests`
  - repo-local install and smoke guidance in `editors/vscode/README.md`
- Duplicate or drifting paths relevant to this change:
  - generic keyword buckets that hide missing first-class declaration rules
  - README claims that outrun tests
  - source-tree integration proof that outruns packaged proof
- Behavior-preservation signals already available:
  - `cd editors/vscode && npm test`
  - `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`
  - `cd editors/vscode && make`
- Audit evidence already collected:
  - the source audit found concrete gaps on top-level `table`, inline
    `final_output:` blocks, top-level `render_profile`, and `delivery_skill:`
  - the source audit also found proof gaps: 57 snapshot example roots vs 122
    shipped roots, 45 integration-referenced example roots, README overclaim,
    and no packaged VSIX smoke path

## 3.3 Decision gaps that must be resolved before implementation

- none yet, with this draft recommendation:
  - implement full parity for all repo-discoverable shipped extension surfaces
  - explicitly leave emit-time provider roots that have no editor-side config
    contract out of scope for this plan
  - if you want editor support for those host-provided roots too, the plan will
    need one explicit discovery contract before implementation
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `editors/vscode/package.json` defines one `doctrine` language, one grammar,
  and one extension entrypoint.
- `editors/vscode/extension.js` only registers a document link provider and a
  definition provider.
- `editors/vscode/resolver.js` is the single custom navigation and indexing
  path. It is about 6455 lines long.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` is the sole highlighting
  grammar.
- `editors/vscode/scripts/validate_lark_alignment.py` is the only grammar-to-
  shipped-truth validator.
- `editors/vscode/tests/unit` holds focused syntax tests.
- `editors/vscode/tests/snap/examples` mirrors a subset of shipped examples.
- `editors/vscode/tests/integration` drives a staged extension-host smoke run.
- `editors/vscode/.vscodeignore` strips test and script files from the packaged
  extension.

## 4.2 Control paths (runtime)

Current highlight path:

1. VS Code loads `source.doctrine` from `package.json`.
2. TextMate highlighting uses `syntaxes/doctrine.tmLanguage.json`.
3. `language-configuration.json` provides comment and folding behavior.

Current navigation path:

1. `extension.js` registers providers for `language: doctrine`.
2. `resolver.js` indexes imports, declarations, body specs, and candidate
   sites.
3. Document links use import resolution.
4. Go-to-definition uses line-classification heuristics, declaration kinds, and
   body-spec traversal.

Current package path:

1. `npm test` runs unit, snapshot, and integration checks.
2. `package:vsix` then runs the validator and packages the VSIX.
3. The integration harness stages a source-tree copy, not the packaged VSIX.

## 4.3 Object model + key abstractions

- `resolver.js` uses declaration-kind enums, regex-based declaration parsing,
  keyed field maps, and container body specs.
- The resolver currently hard-codes `final_output` only as a scalar field ref.
- The resolver currently has no first-class declaration kind for `table`.
- `delivery_skill:` is not part of the keyed field maps.
- The TextMate grammar relies on a mix of first-class declaration patterns and
  generic keyword buckets.
- The validator mostly proves keyword presence and a narrow sample of regex
  matches.

## 4.4 Observability + failure behavior today

- `cd editors/vscode && npm test` passed during the audit on 2026-04-16.
- `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`
  also passed during the audit.
- Those green checks did not catch real shipped-surface drift.
- The README says the extension supports the full shipped clickable surface,
  which is currently stronger than the proof.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not a product UI change. The user-facing surface is the editor experience:

```text
.prompt file open in VS Code
├── tokens highlighted by tmLanguage
├── import paths Ctrl/Cmd-clickable
├── declaration refs go to definition
└── README smoke ladder tells users what should work
```
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/` and the shipped example corpus remain the source of truth.
- `editors/vscode/syntaxes/doctrine.tmLanguage.json` will explicitly model all
  shipped first-class declaration surfaces the extension claims to highlight.
- `editors/vscode/resolver.js` will explicitly model all repo-discoverable
  clickable surfaces the extension claims to navigate.
- `editors/vscode/tests/**` and
  `editors/vscode/scripts/validate_lark_alignment.py` will directly prove late
  shipped feature families.
- `editors/vscode/README.md` will only claim surfaces covered by those proofs.

## 5.2 Control paths (future)

Future highlight path:

1. Shipped declaration or field surface lands in `doctrine/`.
2. Matching first-class highlight rule lands in the TextMate grammar.
3. Validator and syntax tests assert the concrete declaration or field shape.

Future navigation path:

1. Shipped clickable surface lands in `doctrine/` plus examples.
2. Matching resolver kind or body-spec support lands in `resolver.js`.
3. Integration tests pin one real example of that surface.

Future package path:

1. Source-tree tests stay green.
2. Validator stays green with explicit surface assertions.
3. Packaged VSIX smoke proves the shipped artifact still exposes the core
   behavior the README documents.

## 5.3 Object model + abstractions (future)

- Add a first-class resolver declaration kind for `table`.
- Add explicit final-output child-body modeling instead of treating nested
  `output:` and `route:` lines as generic slot content.
- Add explicit keyed-field mapping for `delivery_skill:` to `skill`.
- Add explicit highlight coverage for top-level `render_profile`.
- Tighten shared declaration regexes so `route_only` and `grounding` match
  shipped grammar, not looser invented syntax.
- Add one small parity matrix or equivalent structured feature list inside the
  extension proof surface so new shipped forms have one clear place to be wired
  and tested.

## 5.4 Invariants and boundaries

- No shipped declaration family should be "supported" only by a generic keyword
  bucket.
- No README claim without direct proof.
- No parity fix that changes Doctrine language behavior.
- No speculative editor platform work beyond current extension scope.
- No package artifact claim without at least one shipped artifact proof path.
- No duplicated feature mapping tables if one canonical list can own the same
  truth.

## 5.5 UI surfaces (ASCII mockups, if UI work)

```text
Author opens late-corpus .prompt file
├── declaration token is scoped correctly
├── nested refs are styled correctly
├── Ctrl/Cmd-click lands on the real definition
├── Go to Definition works on the same surface
└── README smoke step matches what the installed VSIX actually does
```
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Declaration highlighting | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | top-level declaration patterns | no top-level `table` or `render_profile` declaration rule | add first-class declaration patterns and tighten late declaration regexes | shipped language truth now includes these declaration forms | highlight contract matches shipped declarations | syntax unit tests, snapshot coverage, validator |
| Table navigation | `editors/vscode/resolver.js` | declaration kinds, declaration regexes, document table headers | no table declaration kind; named table headers treated like inline readable blocks only | add table declaration kind, table declaration parsing, and named table use-site handling | named tables are shipped and addressable | table roots and named table descendants become real navigation targets | example `116` integration and syntax coverage |
| Final output block navigation | `editors/vscode/resolver.js` | `final_output` body handling | only scalar `final_output: Name` is modeled | add block-form body spec and nested `output:` / `route:` handling | shipped final-output route surfaces are not actually modeled today | inline `final_output:` becomes first-class navigation surface | examples `120` and `121`, existing final-output tests |
| Delivery skill navigation | `editors/vscode/resolver.js` | keyed record field maps | `delivery_skill:` is not mapped to `skill` | map `delivery_skill:` to `skill` in output-target record bodies | shipped target-owned delivery binding is invisible in navigation | `output target` can navigate to delivery skills | example `118`, integration and maybe unit coverage |
| Late declaration proof | `editors/vscode/tests/unit/declarations.test.prompt` | declaration matrix | stops before `review_family`, `route_only`, `grounding`, `table`, `render_profile` | extend declaration matrix to late shipped forms | current proof misses first-class declaration growth | declaration support becomes directly pinned | unit syntax suite |
| Late output schema proof | `editors/vscode/tests/unit/io-blocks.test.prompt` and integration suite | route fields, nullable, selected final-output routes | baseline route-field syntax only | add direct proof for late structured-output surfaces and no-route variants | late shipped output surfaces now outrun proof | structured final-output route contract gets direct proof | examples `104`, `119`, `120`, `121` |
| Named table descendants | `editors/vscode/tests/integration/suite/index.js` | example-backed definition assertions | only older inline table descendants are pinned | add example `116` assertions for declaration root and named use-site descendants | named table support is currently unproved | integration path proves first-class named tables | integration suite |
| Late family examples | `editors/vscode/tests/integration/suite/index.js` | example coverage list | no direct coverage for examples `68`, `69`, `70`, `71` | add direct assertions for `review_family`, `route_only`, and `grounding` | current proof misses late declaration families | late family support gets direct example proof | integration suite |
| Validator depth | `editors/vscode/scripts/validate_lark_alignment.py` | keyword and sample assertions | mostly checks keyword presence and a narrow sample set | assert declaration patterns and feature-specific sample lines for late surfaces | current validator can pass while parity is wrong | validator proves structure, not just words | validator itself, maybe package path |
| Snapshot breadth | `editors/vscode/tests/snap/examples/**` | example tree coverage | 57 of 122 shipped example roots mirrored | add late examples by feature family where snapshots buy real signal | current snapshot surface underrepresents late shipped language | snapshots cover current shipped syntax families proportionally | snapshot suite |
| Packaged artifact proof | `editors/vscode/tests/integration/run.js`, `editors/vscode/scripts/package_vsix.py`, `.vscodeignore` | install path vs staged source tree | integration only stages the source tree copy | add one packaged smoke path or manifest audit | README tells users to install the VSIX | shipped artifact contract matches source-tree proof | package smoke, maybe `make` |
| Public contract | `editors/vscode/README.md` | support list and smoke ladder | claims exceed current proof | narrow or expand claims to match shipped proof, and add late example smoke steps | docs are part of the shipped extension contract | README becomes evidence-backed | docs review plus `make` |

## 6.2 Migration notes

- Canonical owner path:
  - shipped language truth lives in `doctrine/` plus the manifest-backed
    examples
  - editor parity logic lives in `editors/vscode/`
- Deprecated paths or behaviors:
  - generic keyword-only coverage for first-class declarations should be retired
    where a declaration rule is required
  - README overclaim should be retired in the same change set
- Delete list:
  - no whole-file deletes planned yet
  - delete or rewrite stale README claims and stale validator assumptions as
    part of implementation
- Adjacent surfaces that must move with the same parity story:
  - TextMate grammar
  - resolver
  - validator
  - unit tests
  - snapshot tests
  - integration tests
  - package smoke
  - README smoke ladder
- Compatibility posture:
  - preserve existing working behavior on already-covered surfaces
  - add missing late-surface support without breaking fail-closed behavior on
    ambiguous or unsupported imports
- Live docs/comments/instructions to update or delete:
  - `editors/vscode/README.md`
  - maybe `docs/README.md` only if the extension entry needs wording changes
- Behavior-preservation signals for refactors:
  - `cd editors/vscode && npm test`
  - `cd editors/vscode && uv run --locked python scripts/validate_lark_alignment.py`
  - `cd editors/vscode && make`

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Declaration support | `resolver.js` and `doctrine.tmLanguage.json` | one explicit first-class rule per shipped declaration family the extension claims to support | prevents drift from generic keyword fallback | include |
| Navigation ownership | `resolver.js` | explicit body-spec support for nested final-output and named table surfaces | prevents heuristic line scans from swallowing real structure | include |
| Proof ownership | validator plus tests | feature-specific samples tied to late shipped examples | prevents green suite false confidence | include |
| Public contract | `README.md` | only claim tested surfaces | prevents user-facing overclaim | include |
| Packaged proof | `run.js`, packaging path | at least one packaged VSIX smoke or manifest audit | prevents source-tree-only confidence | include |
| Monolith cleanup | `resolver.js` | small internal consolidation if needed to reduce duplicated feature tables | reduces future drift without speculative rewrite | include only where needed |
| Emit-time provider roots | extension import resolution | runtime-host root discovery | repo truth does not expose an editor-side discovery contract today | exclude for this plan unless user explicitly wants a new discovery contract |
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
- Add integration coverage for examples `118`, `120`, and `121`.
- Preserve existing scalar `final_output: Name` behavior.
- Preserve existing fail-closed behavior on unsupported built-in destinations
  and ambiguous roots.

### Verification (required proof)

- `cd editors/vscode && npm run test:integration`
- targeted unit coverage if new syntax classification needs it

### Docs/comments (propagation; only if needed)

- Keep comments local to the final-output body model or keyed-field map if the
  new owner path would otherwise be unclear.

### Exit criteria (all required)

- Block-form `final_output:` surfaces navigate correctly.
- `delivery_skill:` navigates to the target skill.
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

- Add one packaged VSIX smoke path or packaged manifest audit that can fail when
  packaging strips or misstates the shipped runtime files.
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

- Add one packaged VSIX smoke path or equivalent packaged artifact audit.
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

# Appendix B) Conversion Notes

- Converted the source audit report into the canonical `arch-step` artifact in
  place, per the user request.
- Re-homed the concrete audit findings into Sections 2, 3, 6, and 7.
- Preserved the source audit's key evidence: the four concrete parity gaps, the
  proof gaps, the coverage counts, and the recommended repair order.
- No Appendix A was needed because the source audit content was fully placed in
  the canonical structure.
