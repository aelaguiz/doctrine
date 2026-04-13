---
title: "Doctrine - Elegant Gap Closure - Architecture Plan"
date: 2026-04-12
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: phased_refactor
related:
  - docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/REVIEW_SPEC.md
  - docs/WORKFLOW_LAW.md
  - docs/COMPILER_ERRORS.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/SECOND_WAVE_LANGUAGE_NOTES.md
  - docs/INTEGRATION_SURFACES_SPEC.md
  - docs/README.md
  - examples/README.md
  - doctrine/compiler.py
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/diagnostics.py
  - editors/vscode/README.md
---

# TL;DR

## Outcome

Ship the same real Doctrine-side gap family that the current worktree is
trying to close, but do it in one elegant pass: one canonical policy owner for
law-target validation, direct support for guarded currentness where the repo
already advertises it, one human-facing render path for emitted prose, one
clean proof ladder in the examples, and one live docs story that matches the
shipped code.

## Problem

The current uncommitted work is mostly justified, but it is not shaped cleanly
enough yet. It spreads allowed-target rules across multiple compiler branches,
lets internal control-state wording leak into rendered AGENTS output, leaves
guarded review-outcome currentness supported on `route` but not on `current
artifact` / `current none` even though draft repo docs already show that
syntax, mixes real semantic completion with ad hoc copy edits, and leaves
scratch docs in the worktree next to the real implementation surface.

## Approach

Keep the feature scope, but refactor the implementation around explicit single
owners. Centralize law-target policy in the compiler, ship guarded review
currentness on `current artifact` / `current none` through the existing inline
guard shape, centralize human-facing sentence lowering for route-only and
related surfaces, then rebuild the proof set and live docs from that cleaned-up
implementation instead of carrying forward the current broad patch as-is.

## Plan

1. Freeze the exact semantic scope we are preserving from the current patch and
   reject accidental user-facing wording regressions.
2. Add direct guarded-currentness support for review-outcome `current artifact`
   and `current none` so blocked-gate review branches no longer need match
   boilerplate for a documented use case.
3. Refactor the compiler so law-target permissions and root-resolution rules
   come from one policy table instead of repeated local conditionals.
4. Restore clean human-facing emitted prose while keeping the same control-plane
   truth and fail-loud behavior.
5. Reconcile examples, diagnostics, and live docs around the cleaned-up owner
   path.
6. Run the full Doctrine verification ladder, including examples and editor
   checks where the touched surface requires them.

## Non-negotiables

- No scope cuts relative to the real semantic family the patch is trying to
  ship.
- No new declaration families, modes, or speculative architecture just to make
  the code "cleaner."
- No duplicate policy encodings for the same law-target rule.
- No forcing `match present(...)` boilerplate for guarded currentness if the
  existing law guard shape can honestly own that use case.
- No internal implementation jargon such as `current-none` leaking into
  human-facing emitted AGENTS prose.
- Examples, docs, diagnostics, and editor parity are part of done, not cleanup.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-12
Verdict (code): COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- None. Fresh `uv sync`, `npm ci`, `make verify-diagnostics`, and
  `make verify-examples` all passed against the current worktree.

## Reopened phases (false-complete fixes)
- None. Phase 5 can close again; the live `docs/WORKFLOW_LAW.md`
  ownership summary now matches the shipped compiler and diagnostics surface.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Use `$arch-docs` for broader scratch-artifact cleanup of
  `.doc-audit-ledger.md`, `diff.txt`, and `docs/big_ass_dump.md` once
  restore-point requirements are satisfied.
<!-- arch_skill:block:implementation_audit:end -->

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

Worklog: [docs/ELEGANT_DOCTRINE_GAP_CLOSURE_PLAN_2026-04-12_WORKLOG.md](/Users/aelaguiz/workspace/doctrine/docs/ELEGANT_DOCTRINE_GAP_CLOSURE_PLAN_2026-04-12_WORKLOG.md)

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If this plan is executed correctly, Doctrine will ship the same intended
semantic closure as the current dirty worktree, but with a cleaner architecture
and cleaner output:

- the compiler will have one obvious owner for law-target permission rules
- guarded review currentness on `current artifact` / `current none` will work
  directly where the repo already documents that shape
- emitted AGENTS prose will read naturally without losing control-plane truth
- every changed semantic will have manifest-backed proof in the numbered corpus
- live docs and diagnostics will describe the same surface the code ships

This claim is false if any of the following remain true:

- allowed target kinds are still duplicated across unrelated compiler branches
- the docs still advertise guarded currentness syntax that the parser rejects
- emitted output still exposes internal-state phrases instead of human-facing
  wording
- examples prove the behavior but live docs still tell a different story
- scratch docs or patch artifacts still compete with the canonical repo truth

## 0.2 In scope

- The Doctrine-side semantic family currently represented by the dirty worktree:
  schema-family-rooted preservation and ownership, grounding-aware preserve
  mapping, multiple `decision:` attachments on one concrete agent, wrapped
  comment-shape render-profile proof, guarded review currentness on
  `current artifact` / `current none`, route-only emitted wording, and related
  diagnostics/doc parity.
- Internal refactoring inside the canonical owners needed to make that work
  elegant rather than merely functional, especially around law-target policy and
  sentence lowering.
- Example prompt, manifest, and checked-in ref updates needed to keep the proof
  corpus aligned, including review/currentness examples that currently need
  `match` or nested `when` boilerplate to express blocked-gate branches.
- Live docs updates across `docs/README.md`, `docs/LANGUAGE_REFERENCE.md`,
  `docs/WORKFLOW_LAW.md`, `docs/COMPILER_ERRORS.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, and `examples/README.md` where the final
  shipped surface demands it.
- Repo-local VS Code follow-through if the touched surface changes syntax
  coverage, definition resolution, or the documented editor smoke ladder.
- Cleanup of non-authoritative scratch artifacts created during this patch
  family so they do not masquerade as live docs or plan truth.

Allowed architectural convergence scope:

- small internal compiler refactors that collapse duplicated law-target
  validation logic into one explicit policy layer
- small grammar/parser/model/compiler changes needed to let review-outcome
  `current artifact ... when ...` and `current none when ...` reuse the same
  inline guard shape that adjacent outcome statements already use
- small internal render-lowering refactors that keep route-only and skill/readback
  prose human-facing without changing the underlying semantics
- focused docs and example consolidation needed to keep one source of truth

## 0.3 Out of scope

- New language families beyond the semantics already implied by the current
  patch.
- Reopening the already-shipped broad `big_ass_dump` closure work outside the
  touched semantic family.
- Inventing a second conditional syntax for currentness instead of extending the
  existing law guard shape.
- Adding wrapper tooling, compatibility shims, or fallback behavior.
- Open-ended cleanup of unrelated docs or unrelated dirty-worktree files.
- Changing Doctrine's public authoring rules, such as "one new idea per
  example," to accommodate this refactor.

## 0.4 Definition of done (acceptance evidence)

The work is done when all of the following are true:

- one compiler-owned policy surface governs which law statements may target
  inputs, outputs, enums, schema families, schema groups, or grounding
  declarations
- guarded review-outcome `current artifact` and guarded `current none` compile
  and evaluate correctly in the shipped review surfaces that need them
- the final emitted route-only and skill/readback prose is human-facing and
  semantically faithful
- the changed example families render or fail exactly as intended through their
  manifests
- live docs and diagnostics describe the cleaned-up surface accurately
- `make verify-examples` passes
- `make verify-diagnostics` passes if diagnostics changed
- `cd editors/vscode && make` passes if editor-facing surfaces changed

Behavior-preservation evidence:

- targeted manifest runs for the changed examples before the final full corpus
  sweep
- unchanged neighboring examples in the same feature ladders still pass during
  the full corpus run

## 0.5 Key invariants (fix immediately if violated)

- No scope narrowing.
- No new parallel owner paths.
- No silent behavior drift while centralizing policy.
- No documented-but-unshipped currentness syntax left behind.
- No internal-state jargon in user-facing emitted prose.
- No scratch docs treated as shipped truth.
- Fail-loud boundaries stay intact.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve the real semantic behavior the patch is trying to ship.
2. Centralize the implementation so one reader can find the rule owner quickly.
3. Keep emitted AGENTS output natural and reader-facing.
4. Keep examples, docs, diagnostics, and editor signals aligned.
5. Avoid speculative module splitting or new abstraction layers that outgrow the
   actual problem.

## 1.2 Constraints

- Shipped truth lives under `doctrine/` plus manifest-backed examples.
- Public docs and examples must stay generic.
- The repo already has a broad phase-history doc set; this plan must not create
  a competing explanation of shipped behavior.
- `route` already accepts inline `when`, so guarded currentness should extend an
  existing local pattern rather than inventing a new branch form.
- Verification has to use the repo's normal ladder rather than bespoke audit
  scripts.

## 1.3 Architectural principles (rules we will enforce)

- One rule, one owner: each law-target rule should come from one compiler-owned
  policy surface.
- Human-facing rendering should be owned by deliberate lowering logic, not by
  whatever internal label happened to be convenient during compilation.
- Parser guards, compiler diagnostics, examples, and docs must describe the
  same contract.
- When the repo already advertises one narrow syntax shape and adjacent law
  statements already use it, prefer extending that shape over teaching a bulkier
  workaround as the canonical answer.
- Keep the refactor in the existing canonical files unless a smaller local
  helper extract becomes clearly necessary.

## 1.4 Known tradeoffs (explicit)

- A small amount of duplication may remain at the docs/example layer because
  each example still has to prove one idea clearly, but the compiler-level rule
  source must not stay duplicated.
- Restoring cleaner route-only wording may require a more explicit separation
  between internal control-state semantics and emitted human sentence lowering.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

The live repo already ships first-class `decision`, `grounding`,
`render_profile`, schema families/groups, and parser-level output attachment
guardrails. The current dirty worktree is extending that shipped baseline by
allowing more law-target roots, proving those roots in the corpus, and updating
docs/diagnostics accordingly. Separately, the repo's draft second-wave docs
already show guarded-currentness syntax on `current artifact` / `current none`,
but the shipped grammar/parser still reject that form.

## 2.2 What’s broken / missing (concrete)

- Law-target permissions are being encoded in multiple places inside
  `doctrine/compiler.py`.
- The route-only lowering currently uses internal wording
  (`Route-only current-none ...`) that is precise for implementers but awkward
  for emitted AGENTS prose.
- Guarded currentness is a real doc/grammar drift seam: `route ... when ...`
  ships, but `current artifact ... when ...` and `current none when ...` do not,
  despite draft repo docs already teaching that exact shape.
- The skill-readback copy change looks ad hoc instead of stemming from one
  stable doctrine choice about fail-loud missing-skill behavior.
- The examples and docs are being updated, but the work is not yet organized
  around one clean implementation story.
- Scratch artifacts such as `.doc-audit-ledger.md`, `diff.txt`, and the current
  `docs/big_ass_dump.md` worktree file are too close to the real docs surface.

## 2.3 Constraints implied by the problem

- We cannot "clean this up" by dropping the semantic extensions.
- We cannot make emitted output cleaner by hiding real control-plane truth.
- We cannot leave documented guarded-currentness syntax unsupported and call the
  language surface elegant.
- We cannot claim elegance if the examples and docs are just patched after the
  fact instead of rebuilt from the chosen owner path.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- None required for this stage — reject external expansion for now — this is a
  repo-convergence pass against shipped Doctrine grammar, parser, compiler,
  docs, and proof ladders rather than a new language-design search.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/grammars/doctrine.lark` — `current_review_artifact_stmt` and
    `current_review_none_stmt` currently sit beside guarded review-outcome
    routes, but shipped without optional inline `when`.
  - `doctrine/parser.py` — `current_review_artifact_stmt` and
    `current_review_none_stmt` originally built bare review currentness nodes
    with no `when_expr`.
  - `doctrine/model.py` — `ReviewCurrentArtifactStmt` and
    `ReviewCurrentNoneStmt` originally lacked `when_expr`, while nearby review
    outcome statements such as routes and match heads already carried it.
  - `doctrine/compiler.py` — `_branch_with_review_outcome_stmt`,
    `_resolve_review_expr_constant`, `_resolve_review_agreement_branch`, and
    `_render_review_outcome_item` are the canonical owners for review
    currentness selection, blocked-gate guard handling, and human-facing review
    sentence lowering.
  - `docs/SECOND_WAVE_LANGUAGE_NOTES.md` and
    `docs/INTEGRATION_SURFACES_SPEC.md` — both already show
    `current artifact ... when missing(blocked_gate)` and
    `current none when present(blocked_gate)`, so draft repo docs have drifted
    ahead of the shipped grammar.
  - `docs/REVIEW_SPEC.md` — the live review reference already anchors the
    review currentness ladders and points readers to the relevant review
    examples.
  - `examples/46_review_current_truth_and_trust_surface`,
    `examples/49_review_capstone`,
    `examples/68_review_family_shared_scaffold`, and
    `examples/69_case_selected_review_family` — the closest shipped proof homes
    for review-owned currentness and blocked-gate review scaffolds.
  - `examples/33_scope_and_exact_preservation`,
    `examples/34_structure_mapping_and_vocabulary_preservation`,
    `examples/52_bound_scope_and_preservation`,
    `examples/70_route_only_declaration`,
    `examples/71_grounding_declaration`, and
    `examples/74_decision_attachment` — the most relevant preservation,
    route-only, grounding, and decision proof ladders around the touched
    compiler policy.
  - `examples/11_skills_and_tools`,
    `examples/21_first_class_skills_blocks`, and
    `examples/22_skills_block_inheritance` — the emitted skill-home wording
    proof surfaces for the touched copy seam.
- Canonical path / owner to reuse:
  - `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`,
    `doctrine/model.py`, and `doctrine/compiler.py` — the existing
    review/currentness pipeline should own guarded currentness directly.
  - `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`,
    `docs/REVIEW_SPEC.md`, and `docs/COMPILER_ERRORS.md` — the live public
    explanation path to sync once syntax and behavior are finalized.
  - `examples/README.md` plus the touched example families — the canonical
    teaching and proof path.
- Existing patterns to reuse:
  - `doctrine/grammars/doctrine.lark` — the existing inline `when` shape on
    review routes is the local currentness pattern to reuse instead of
    inventing a second conditional form.
  - `doctrine/parser.py` — `outcome_route_stmt` already shows the parser-side
    optional-`when_expr` pattern in review outcomes.
  - `doctrine/compiler.py` — `_render_law_stmt_lines` already knows how to
    prefix guarded sentences with human-facing `When ...` phrasing.
  - `doctrine/compiler.py` — the shared law-path resolver/validator flow is the
    canonical place to centralize allowed target kinds rather than repeating
    tuples in multiple validation branches.
- Prompt surfaces / agent contract to reuse:
  - n/a — this is compiler/language work, not a prompt-surface design task.
- Native model or agent capabilities to lean on:
  - n/a — this plan is not agent-capability limited.
- Existing grounding / tool / file exposure:
  - `examples/*/cases.toml` manifests — direct narrow proof surface for semantic
    runs.
  - `make verify-examples` — full shipped corpus proof.
  - `make verify-diagnostics` — public diagnostic message proof when touched.
  - `editors/vscode/README.md` and `cd editors/vscode && make` — editor parity
    path when syntax or resolver behavior changes.
- Duplicate or drifting paths relevant to this change:
  - `docs/SECOND_WAVE_LANGUAGE_NOTES.md` and
    `docs/INTEGRATION_SURFACES_SPEC.md` — draft docs that currently promise
    guarded currentness syntax the shipped parser rejects.
  - `doctrine/compiler.py` — repeated `allowed_kinds=(...)` branches are a real
    internal drift risk for law-target policy.
  - `.doc-audit-ledger.md`, `diff.txt`, and `docs/big_ass_dump.md` — scratch
    worktree surfaces that must not compete with the live docs path once the
    implementation lands.
- Capability-first opportunities before new tooling:
- Extend the existing inline review `when` shape to `current artifact` and
  `current none` rather than standardizing `match present(...)` as the public
  workaround or inventing a second conditional syntax.
  - Reuse the existing manifest-backed example ladders instead of adding new
    harnesses.
- Behavior-preservation signals already available:
  - `examples/33_*`, `34_*`, `52_*`, `70_*`, `71_*`, and `74_*` — preserve
    law-target, route-only, grounding, and decision semantics while the
    compiler policy is centralized.
  - `examples/46_*`, `49_*`, `68_*`, and `69_*` — preserve review/currentness
    behavior while adding direct guarded-currentness syntax.
  - `docs/README.md`, `examples/README.md`, `docs/REVIEW_SPEC.md`, and
    `editors/vscode/README.md` — live explanation surfaces to cold-read after
    the code settles.

## 3.3 Decision gaps that must be resolved before implementation

- None. Repo evidence is sufficient for planning: guarded review currentness
  should ship via the existing inline `when` shape, and the remaining choices
  are internal structure questions rather than user-facing blockers.
<!-- arch_skill:block:research_grounding:end -->

# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Parser and grammar rules live in `doctrine/grammars/doctrine.lark`,
  `doctrine/parser.py`, and `doctrine/model.py`.
- Semantic validation and readable lowering live primarily in
  `doctrine/compiler.py`.
- Public contract docs live in `docs/`.
- Proof and teaching live in `examples/` through manifest-backed cases and
  checked refs.
- Editor parity lives under `editors/vscode/`.

## 4.2 Control paths (runtime)

- Parse-time rules reject duplicated or incompatible attachments such as
  `schema:` plus `structure:` on one output.
- Parse-time rules allow inline `when` on several law statements, including
  `route`, but not on `current artifact` or `current none`.
- Compile-time law-path validation determines which declaration families may be
  targeted by `own only`, `preserve exact`, `preserve mapping`, and
  `preserve vocabulary`.
- The same compiler pass also lowers certain semantic constructs into the
  human-facing AGENTS/readable output.
- Diagnostics map compile errors into stable public error codes and summaries.

## 4.3 Object model + key abstractions

- Law roots currently resolve through a common path-resolution flow, but the
  allowed kinds are chosen in multiple local branches.
- `CurrentArtifactStmt` and `CurrentNoneStmt` currently have no inline guard
  slot, which is why the parser forces currentness branches into nested
  `when`/`match` forms.
- Schema-family support is represented as a synthetic internal target kind.
- Grounding declarations are resolved as addressable law targets only in the
  places that explicitly allow them.
- Human-facing route-only and skill text is emitted from compiler-owned strings
  rather than from a separate render policy registry.

## 4.4 Observability + failure behavior today

- The repo already has manifest-backed render and compile-fail proof.
- Compiler errors are stable enough to publish in `docs/COMPILER_ERRORS.md`.
- Editor parity is checked through the local VS Code extension build and test
  path.
- The current dirty worktree adds proof, but it does not yet make the owner
  story obvious enough for a cold reader.
- Draft second-wave docs already advertise guarded currentness on current
  statements, so the repo currently contains a real syntax promise drift.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not a UI task. The relevant reader-facing surface is emitted Markdown / AGENTS
output, which should stay natural and compact.

# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/compiler.py` remains the canonical semantic owner, but with one
  explicit law-target policy registry and one explicit sentence-lowering owner
  for the touched human-facing surfaces.
- `doctrine/parser.py` continues to own structural attachment bans and will also
  own the inline-guard parse shape for currentness statements.
- `docs/` and `examples/` are updated to follow the cleaned-up owner path.
- Non-authoritative scratch artifacts are deleted or otherwise removed from the
  live docs path.

## 5.2 Control paths (future)

- Each workflow-law statement kind will derive its allowed target families from
  one compiler-owned policy source.
- `current artifact` and `current none` will accept the same inline guard shape
  that adjacent guarded law statements already use.
- Law-path resolution will remain shared, but the statement-specific policy will
  no longer be scattered through unrelated branches.
- Route-only and related emitted prose will be lowered through clean
  human-facing sentence rules that preserve currentness semantics without
  rendering internal control-state terms directly.
- Diagnostics and public docs will be updated from the final chosen semantics,
  not from the temporary patch wording.

## 5.3 Object model + abstractions (future)

- Keep `SchemaFamilyTarget` or an equivalent internal representation only if it
  remains the cleanest way to model family-root law targets. Do not add a new
  user-facing declaration surface.
- `CurrentArtifactStmt` and `CurrentNoneStmt` should gain optional `when_expr`
  support rather than forcing a separate workaround-only construct.
- Introduce one internal policy mapping for law-target permissions keyed by
  statement family and, where needed, preserve-kind.
- Introduce one small compiler-local render helper for human-facing sentence
  shapes touched by this change set.

## 5.4 Invariants and boundaries

- Parser owns structural attachment validity.
- Parser and model own the inline-guard shape for currentness statements.
- Compiler owns semantic target validity and emitted sentence lowering.
- Examples own proof.
- Live docs own explanation.
- Editor tooling follows only when the shipped surface actually changes.
- No branch of the implementation may silently broaden product capability beyond
  the current semantic family.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable beyond emitted prose quality. The target reader experience is:

```text
Current artifact: Section Metadata.
Route to Draft Author.
This skill is required for this role.
```

And the target authored currentness shape is:

```prompt
current artifact lesson_plan via CriticVerdictAndHandoffOutput.current_artifact when missing(blocked_gate)
current none when present(blocked_gate)
```

not:

```text
Route-only current-none to Draft Author.
```

# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Guarded currentness syntax | `doctrine/grammars/doctrine.lark` | `current_artifact_stmt`, `current_none_stmt` | no inline guard clause on currentness statements | let currentness statements reuse the existing law guard shape | close real doc/grammar drift without adding new syntax families | optional inline `when` on currentness statements | `46`, `49`, `68`, `69` |
| Guarded currentness AST | `doctrine/model.py`, `doctrine/parser.py` | `CurrentArtifactStmt`, `CurrentNoneStmt`, parser builders | currentness statements carry no guard slot | add `when_expr` support and parse it cleanly | currentness needs to model the authored syntax directly | internal-only AST extension | `46`, `49`, `68`, `69` |
| Guarded currentness evaluation | `doctrine/compiler.py` | currentness branch compilation / validation | users must spell blocked-gate currentness through nested `when` or `match` | evaluate guarded currentness directly while preserving existing exclusivity checks | elegant support for the documented use case | same semantics, cleaner authored form | `46`, `49`, `68`, `69` |
| Law-target policy | `doctrine/compiler.py` | preserve / own / forbid validation branches around `_validate_path_set_roots` and `_validate_law_path_root` | allowed kinds are chosen in repeated local conditionals | centralize allowed-target policy in one compiler-owned mapping | prevent drift and make the owner obvious | internal-only policy registry | `33`, `34`, `52`, `71` |
| Law-path resolution | `doctrine/compiler.py` | `_resolve_law_path` plus schema-family / grounding handling | shared resolver works, but policy is spread around it | keep shared resolver, but drive it from one policy source | preserve semantics while simplifying the architecture | internal-only cleanup | `34`, `52`, `71` |
| Route-only lowering | `doctrine/compiler.py` | route-only lowering to `LawRouteStmt` labels | current dirty wording exposes `current-none` directly | lower to cleaner human prose while preserving semantics elsewhere | emitted AGENTS output should read naturally | emitted sentence change only | `70` |
| Skill required prose | `doctrine/compiler.py` | skill-purpose sentence emission | current dirty patch trims missing-skill wording ad hoc | make fail-loud missing-skill behavior intentional and consistent | avoid arbitrary copy drift | emitted sentence change only | `11`, `21`, `22` |
| Parser guard parity | `doctrine/parser.py` | output attachment validation | parser already bans `schema:` + `structure:` | keep this as the canonical structural owner and ensure docs match it | avoid compiler/docs mismatch | no new syntax | targeted parse coverage, docs |
| Diagnostics | `doctrine/diagnostics.py`, `docs/COMPILER_ERRORS.md` | `E351`, `E352`, `E355` and any touched messages | messages track current wording manually | align diagnostics to final chosen policy wording | public errors must match real rules | stable message updates only | diagnostics, `33`, `34`, `52`, `71` |
| Live docs | `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`, `docs/REVIEW_SPEC.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`, `docs/README.md` | live language explanation | current docs are partly updated by patch-local edits and do not yet own the guarded-currentness answer | sync docs to the final owner story | one live explanation path | docs only | cold read plus verify |
| Draft doc drift | `docs/SECOND_WAVE_LANGUAGE_NOTES.md`, `docs/INTEGRATION_SURFACES_SPEC.md` | draft examples that advertise unsupported syntax | docs already show guarded currentness on current statements | either update them to the shipped syntax or keep them accurate once the syntax ships | stop root-doc drift | docs only | manual cold read |
| Corpus proof | `examples/11_*`, `21_*`, `22_*`, `33_*`, `34_*`, `46_*`, `49_*`, `52_*`, `64_*`, `68_*`, `69_*`, `70_*`, `71_*`, `74_*` | manifests, prompts, refs | proof exists, but some additions are broad and patch-shaped and guarded currentness has no direct positive proof | keep one new idea per example and rebuild proof around final semantics | proof should teach and verify cleanly | manifests and refs only | targeted manifests, full corpus |
| Editor parity | `editors/vscode/README.md` and only if needed resolver/tests | second-wave smoke ladder | editor docs may lag final cleaned-up story | update editor-facing docs or code only where touched surface requires it | keep shipped surface explanation aligned | no speculative editor work | `cd editors/vscode && make` if touched |
| Scratch artifacts | `.doc-audit-ledger.md`, `diff.txt`, `docs/big_ass_dump.md` | non-authoritative patch residue | currently adjacent to real docs/worktree | delete or quarantine once no longer needed | avoid fake live truth | cleanup only | manual check |

## 6.2 Migration notes

- Treat the current dirty worktree as input, not as the target architecture.
- Preserve the semantic wins from the patch, but re-land them through the
  centralized owner path.
- Any docs or refs that still explain the temporary wording should be updated in
  the same implementation pass rather than left as historical residue.

# 7) Depth-First Phased Implementation Plan (authoritative)

## 7.1 Phase 1: Freeze the elegant target

Status: COMPLETE

Goal:

- lock exactly which parts of the current worktree are real semantic scope and
  which parts are accidental wording or scratch residue

Work:

- compare the dirty diff against the live current repo
- explicitly keep the semantic extensions that are in scope
- explicitly include guarded currentness on `current artifact` / `current none`
  as supported language work, not as a workaround-only doc note
- explicitly reject temporary emitted wording regressions and scratch artifacts
- record the final route-only and skill-copy doctrine choice before code edits

Verification:

- no code changes yet; produce one explicit keep/rewrite/delete matrix in the
  plan/worklog

Exit criteria:

- no ambiguity remains about what the elegant version is preserving

Rollback:

- n/a for the planning-only phase

Completed work:

- froze the implementation target against the existing dirty worktree instead
  of restarting from scratch
- kept the broad preservation/grounding/decision work already in flight
- corrected the guarded-currentness target to the documented review outcome
  surface
- accepted `missing(blocked_gate)` as the shipped parseable form instead of the
  unparseable draft `not present(blocked_gate)` spelling

## 7.2 Phase 2: Ship guarded currentness directly

Status: COMPLETE

Goal:

- make the documented guarded-currentness shape compile directly without forcing
  nested `match` or `when` boilerplate

Work:

- extend the grammar so `current artifact` and `current none` accept the
  existing inline guard clause shape
- extend the parser/model so currentness statements carry optional `when_expr`
- teach the compiler to evaluate guarded currentness directly while preserving
  existing exclusivity and currentness validation
- add positive and negative proof in the closest review/currentness example
  ladders

Verification:

- targeted manifest runs for `46`, `49`, `68`, and `69`

Exit criteria:

- a blocked-gate currentness branch can be expressed directly in authored syntax
  without changing the meaning of existing review/currentness rules

Rollback:

- revert guarded-currentness support without disturbing unrelated policy
  cleanup

Completed work:

- extended review outcome grammar, parser, and model to carry optional inline
  `when_expr` on `current artifact` and `current none`
- taught review outcome branch resolution to honor
  `present(blocked_gate)` / `missing(blocked_gate)` guards without producing
  mixed-currentness false positives
- lowered guarded review currentness into honest emitted `When ...` prose
- added direct positive proof in `46_review_current_truth_and_trust_surface`

## 7.3 Phase 3: Centralize semantic policy in the compiler

Status: COMPLETE

Goal:

- collapse duplicated law-target permission logic into one obvious owner path

Work:

- introduce the compiler-local policy mapping for statement kinds and allowed
  target families
- refactor validation branches to consult that mapping instead of hardcoding
  repeated tuples
- keep `SchemaFamilyTarget` and grounding support only as implementation
  details, not as new public surface

Verification:

- targeted manifest runs for ownership/preservation/grounding examples
- compile-fail coverage still trips the right errors

Exit criteria:

- one compiler reader can find the target-permission rules in one place

Rollback:

- revert only the centralization refactor if it causes semantic drift

Completed work:

- introduced `_LAW_TARGET_ALLOWED_KINDS` and `_PRESERVE_TARGET_ALLOWED_KINDS`
  as the compiler-owned law-target policy tables
- rewired the touched validation and overlap checks to read through those
  policy owners instead of repeating local tuples

## 7.4 Phase 4: Clean up human-facing emitted prose

Status: COMPLETE

Goal:

- keep the same control-plane truth while making emitted output read naturally

Work:

- centralize the touched sentence-lowering logic
- replace internal route-only phrasing with human-facing phrasing
- make the required-skill wording fail-loud and intentional rather than patchy
- update example refs that prove the final wording

Verification:

- targeted manifest runs for `11`, `21`, `22`, and `70`

Exit criteria:

- emitted AGENTS/readable surfaces are semantically faithful and reader-facing

Rollback:

- revert sentence-lowering cleanup without touching semantic policy if needed

Completed work:

- restored route-only emitted labels to human-facing `Route to ...` wording
- kept the shorter shipped required-skill sentence as the active emitted form
  while preserving fail-loud enforcement in code and proof surfaces

## 7.5 Phase 5: Rebuild proof, diagnostics, and live docs

Status: COMPLETE

Completed work:

- repaired the stale `docs/WORKFLOW_LAW.md` compiler-check bullet so it now
  matches the shipped `own only` contract for current artifacts, emitted output
  surfaces, and declared schema families

Goal:

- make the public proof and explanation surfaces match the cleaned-up code

Work:

- update affected manifests, prompts, and checked refs
- update diagnostics and `docs/COMPILER_ERRORS.md`
- update `docs/LANGUAGE_REFERENCE.md`, `docs/WORKFLOW_LAW.md`,
  `docs/REVIEW_SPEC.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/README.md`,
  and `examples/README.md`
- sync or explicitly reframe `docs/SECOND_WAVE_LANGUAGE_NOTES.md` and
  `docs/INTEGRATION_SURFACES_SPEC.md` so they no longer advertise an
  unshipped syntax shape
- update editor-facing docs or code only if the final surface requires it

Verification:

- targeted manifest runs across changed example families
- `make verify-diagnostics` if diagnostics changed
- `cd editors/vscode && make` if editor files changed

Exit criteria:

- code, proof, and docs all tell the same story

Rollback:

- revert docs/example parity changes that outpace the final code decision

Completed work:

- added the new guarded-currentness prompt/case in `46_*`
- synced `docs/SECOND_WAVE_LANGUAGE_NOTES.md` and
  `docs/INTEGRATION_SURFACES_SPEC.md` to the shipped `missing(blocked_gate)`
  spelling
- updated `docs/REVIEW_SPEC.md` and `examples/README.md` to reflect the new
  review currentness coverage

## 7.6 Phase 6: Full verify and cleanup

Status: COMPLETE

Goal:

- prove the elegant version end to end and remove temporary residue

Work:

- run repo-standard verification
- remove scratch artifacts that are no longer needed
- do one final code-vs-doc cold read on the touched surface

Verification:

- `uv sync`
- `npm ci`
- targeted `uv run --locked python -m doctrine.verify_corpus --manifest ...`
  for changed examples
- `make verify-examples`
- `make verify-diagnostics` when required
- `cd editors/vscode && make` when required

Exit criteria:

- the full corpus passes and no fake doc truth remains in the worktree

Rollback:

- revert only cleanup that accidentally removes still-needed historical context

Completed work:

- ran `uv sync`
- ran `npm ci`
- ran targeted manifest checks for `44`, `46`, `49`, `68`, `69`, and `70`
- ran `make verify-diagnostics`
- ran `make verify-examples`

Deferred:

- broader scratch-artifact cleanup remains a follow-through item for
  `arch-docs`; `docs/big_ass_dump.md` is still covered by repo doc-deletion
  safety and was not deleted in this implementation pass

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Fast proof during implementation

- run targeted manifests for touched ladders first:
  - `examples/11_skills_and_tools/cases.toml`
  - `examples/21_first_class_skills_blocks/cases.toml`
  - `examples/22_skills_block_inheritance/cases.toml`
  - `examples/33_scope_and_exact_preservation/cases.toml`
  - `examples/34_structure_mapping_and_vocabulary_preservation/cases.toml`
  - `examples/46_review_current_truth_and_trust_surface/cases.toml`
  - `examples/49_review_capstone/cases.toml`
  - `examples/52_bound_scope_and_preservation/cases.toml`
  - `examples/64_render_profiles_and_properties/cases.toml`
  - `examples/68_review_family_shared_scaffold/cases.toml`
  - `examples/69_case_selected_review_family/cases.toml`
  - `examples/70_route_only_declaration/cases.toml`
  - `examples/71_grounding_declaration/cases.toml`
  - `examples/74_decision_attachment/cases.toml`

## 8.2 Full repo proof before claiming done

- `uv sync`
- `npm ci`
- `make verify-examples`
- `make verify-diagnostics` if diagnostics changed
- `cd editors/vscode && make` if anything under `editors/vscode/` changed

## 8.3 Human cold-read checks

- cold-read emitted route-only output and confirm it sounds like instructions to
  a human, not compiler debug text
- cold-read one guarded-currentness review example and confirm the direct
  currentness syntax reads naturally and compiles without workaround branching
- cold-read one emitted skill home and confirm fail-loud missing-skill behavior
  is still explicit
- cold-read the live docs path and confirm it matches the changed examples

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout shape

This is a hard-cut repo change, not a staged production rollout. The real
rollout surfaces are code, examples, docs, and editor tooling in one commit
sequence.

## 9.2 Operational risks

- semantic drift during compiler cleanup
- docs claiming the cleaned-up story before proof lands
- leaving scratch artifacts around after the canonical doc/code path is settled

## 9.3 Telemetry / signals

- manifest-backed example passes are the primary signal
- stable diagnostics are the secondary signal
- VS Code extension build/tests are the editor parity signal when touched

## 9.4 Post-ship follow-through

- if this plan lands cleanly, hand broader historical-doc cleanup to
  `arch-docs` rather than folding a repo-wide docs sweep into the implementation
  phase

# 10) Decision Log (append-only)

- 2026-04-12: North Star confirmed by the user; `status` advanced from `draft`
  to `active` with no scope change.
- 2026-04-12: This plan preserves the semantic scope of the current dirty
  worktree; it does not authorize scope cuts for the sake of elegance.
- 2026-04-12: The elegant version should centralize policy inside the existing
  compiler owner path rather than add a new public abstraction layer.
- 2026-04-12: Guarded review currentness on `current artifact` /
  `current none` is in scope and should ship via the existing inline outcome
  guard shape rather than by teaching `match present(...)` as the canonical
  public workaround.
- 2026-04-12: The documented blocked-gate spelling is now
  `missing(blocked_gate)` / `present(blocked_gate)`; draft `not present(...)`
  examples were syntax drift and were corrected instead of broadening the
  expression grammar in the same pass.
- 2026-04-12: Broader scratch-doc cleanup is a post-ship docs task, not a
  reason to leave the language and proof work half-implemented.
- 2026-04-12: Human-facing emitted prose must not expose internal control-state
  jargon such as `current-none`.
- 2026-04-12: Examples, docs, diagnostics, and editor parity are part of the
  feature surface for this refactor.
- 2026-04-12: Scratch patch artifacts are non-authoritative and must not remain
  adjacent to the live docs path once implementation is complete.
