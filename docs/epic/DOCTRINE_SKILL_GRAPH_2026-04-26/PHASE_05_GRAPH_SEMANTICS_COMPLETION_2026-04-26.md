---
title: "Doctrine - Graph semantics completion - Architecture Plan"
date: 2026-04-26
status: complete
fallback_policy: forbidden
owners: [Codex]
reviewers: [aelaguiz]
doc_type: architectural_change
related:
  - docs/EPIC_DOCTRINE_SKILL_GRAPH_2026-04-26.md
  - docs/SKILL_GRAPH_LANGUAGE_SPEC.md
  - docs/LESSONS_STUDIO_SKILL_GRAPH_AUDIT.md
  - docs/ARCH_SKILL_GRAPH_CLOSURE_EMIT_2026-04-26.md
  - doctrine/grammars/doctrine.lark
  - doctrine/_parser/parts.py
  - doctrine/_parser/skills.py
  - doctrine/_model/io.py
  - doctrine/_model/skill_graph.py
  - doctrine/_compiler/resolve/skills.py
  - doctrine/_compiler/resolve/skill_graphs.py
  - doctrine/emit_common.py
  - doctrine/emit_skill_graph.py
  - doctrine/verify_skill_graph.py
  - doctrine/skill_graph_source_receipts.py
  - doctrine/_verify_corpus/runners.py
  - pyproject.toml
  - docs/WARNINGS.md
  - docs/EMIT_GUIDE.md
  - docs/COMPILER_ERRORS.md
  - docs/WARNINGS.md
  - docs/SKILL_GRAPH_LANGUAGE_SPEC.md
  - examples/README.md
  - skills/doctrine-learn/prompts/SKILL.prompt
  - skills/doctrine-learn/prompts/refs/skill_graphs.prompt
---

# TL;DR

Restored the graph features that phase 4 cut out. Phase 5 now implements the
graph language and emit surface with `skill.relations:`, checked
`{{skill:...}}` refs, real warnings, `GRAPH.prompt`, receipt schema emit,
durable artifact symbols, richer audit metadata, graph-path repeats, and the
remaining graph policy and CLI seams. The final full-corpus proof and
full unit proof passed on 2026-04-26. The completion-after-repair critic
passed with no discovered items.

# 0) Holistic North Star

## 0.1 The claim

After this slice ships, Doctrine can author one graph from either
`SKILL.prompt` or `GRAPH.prompt`, emit and verify the full graph bundle
including receipt schemas, and treat relations, checked skill mentions, and
warning policies as live compiler-owned surfaces instead of deferred prose or
inert metadata.

## 0.2 In scope

- Top-level `skill.relations:` with closed relation kinds and `why:`.
- Relation resolution, graph-closure inclusion, and graph JSON or Markdown
  projection for reached skills.
- Checked `{{skill:Name}}`, `{{skill:Name.package}}`, and
  `{{skill:Name.purpose}}` interpolation in the graph-owned text surfaces that
  need compiler-backed skill naming.
- `require relation_reason` and `require checked_skill_mentions`.
- A real warning layer for graph work, including `W201` through `W211`.
- `GRAPH.prompt` as a supported graph entrypoint in emit, verify, and corpus
  proof.
- `receipt_schema_dir` graph emit plus graph source-receipt and verify support
  for emitted receipt schemas.
- Direct graph emit parity for `--graph`, `--view`, and `--diagram` selectors
  where they point at graph views.
- Policy relaxers `allow unbound_edges` and `dag allow_cycle "Reason"`.
- Close any remaining repeat `over:` gap between the shipped local
  enum/table/schema path, the shipped graph-set path, and the spec's
  input-or-field-path story if the current code still lacks it.
- Docs, examples, diagnostics, versioning, and `skills/doctrine-learn` for the
  shipped phase-5 surface.

## 0.3 Out of scope

- Any edit in `../lessons_studio`.
- The `../lessons_studio` migration that would convert the studio repo to this
  graph surface.
- Runtime scheduling, memory, or tool-orchestration behavior.

## 0.4 Definition of done

- The next examples after `159_skill_graph_policy` prove the restored graph
  surface:
  - `160_skill_graph_relations_mentions`
  - `161_skill_graph_policy_allowances`
  - `162_skill_graph_negative_cases`
  - `163_skill_graph_authoring_metadata`
  - `164_skill_graph_artifacts`
- Focused unit tests lock parser or model shape, relation resolution, checked
  mention interpolation, graph warning emission, `GRAPH.prompt` target
  plumbing, and receipt-schema emit or verify.
- `docs/SKILL_GRAPH_LANGUAGE_SPEC.md`, `docs/EMIT_GUIDE.md`,
  `docs/WARNINGS.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md`, and
  `skills/doctrine-learn` tell the same story as the code.
- The implementation worker runs the focused manifests, the touched unit tests,
  `make verify-diagnostics`, `make verify-examples`, `make verify-package`,
  and `uv run --locked python -m unittest discover tests`.
- The completion-after-repair critic passed after the full proof and
  same-scope public-doc repair.

## 0.5 Key invariants

- No existing hard error becomes a warning unless an explicit graph policy says
  so.
- Relations, checked mentions, and warnings must all come from one resolved
  graph. Emit code must not re-parse raw strings to rebuild graph truth.
- `GRAPH.prompt` must reuse the same compile and emit plumbing as other
  supported entrypoints. Do not fork the loader.
- Receipt schemas and source receipts must stay deterministic and must not
  escape the target output root.
- `skills/doctrine-learn` and public docs must say exactly which warning and
  policy behavior ships in phase 5.

# 1) Epic Requirement Coverage

| Remaining requirement | Phase 5 disposition | Later owner |
| --- | --- | --- |
| Top-level `skill.relations:` language | Owned here | - |
| Closed relation kinds plus target resolution | Owned here | - |
| `require relation_reason` and `W210` | Owned here | - |
| Graph closure, contract, and query JSON projection for relations | Owned here | - |
| Checked `{{skill:Name}}` refs plus `.package` and `.purpose` projections | Owned here | - |
| `require checked_skill_mentions` and `W204` | Owned here | - |
| Real warning engine and warnings `W201` through `W211` | Shipped here | - |
| `GRAPH.prompt` entrypoint support | Owned here | - |
| `receipt_schema_dir` emit and verify | Owned here | - |
| Direct `emit_skill_graph` selector parity for `--view` and `--diagram` | Owned here | - |
| `allow unbound_edges` and `dag allow_cycle "Reason"` | Owned here | - |
| Repeat `over:` parity for graph-owned input or field-path sources | Shipped here | - |
| Public docs and `skills/doctrine-learn` for every phase-5 feature | Shipped here | - |
| `artifact` or durable-target declaration | Shipped here | - |
| Stage `entry`, `repair_routes`, and `waiver_policy` | Shipped here | - |
| Skill inventory metadata including aliases | Shipped here | - |
| Manual-only/default-flow metadata warning | Shipped here | - |
| Final exhaustive docs, examples, and release-truth closure for the full restored feature set | Shipped here | - |

# 2) Problem Statement

## 2.1 What ships today

Doctrine already ships the strict graph core through examples `150` through
`159`:

- top-level `receipt`, `stage`, `skill_flow`, and `skill_graph`
- graph closure, graph emit, and graph verify
- graph-set late binding on the graph compile path
- strict graph policies such as `require edge_reason`,
  `require durable_checkpoint`, `require route_targets_resolve`, and
  `require stage_lane`
- graph JSON, graph Markdown views, D2, SVG, Mermaid, and graph source
  receipts

## 2.2 What was missing or cut before this pass

- `skill.relations:` was missing from the grammar, model, resolver, and emit
  surface.
- Graph warning keys were accepted as inert metadata, but there was no live
  warning engine or shipped warning codes.
- Checked `{{skill:...}}` refs did not exist, so `require checked_skill_mentions`
  could not be real.
- Graph emit followed the older entrypoint boundary. `GRAPH.prompt` was not
  supported.
- Graph emit did not write `receipt_schema_dir`, and graph receipts did not
  track those files.
- Policy relaxers such as `allow unbound_edges` and `dag allow_cycle "Reason"`
  had been cut from the shipped slice.
- The audit named Doctrine-side authoring gaps that had no owner after phase 4
  narrowed the graph scope. This pass restored the Doctrine-side gaps that fit
  the graph surface, including durable artifacts and audit metadata.

## 2.3 Why restore this now

The epic currently reads like graph work is almost done, but the authoritative
spec and audit still name compiler-owned features that are absent from code.
Leaving them out would turn a temporary phase boundary into fake product truth,
and `skills/doctrine-learn` would teach that fake boundary as if it were the
language.

# 3) Current Architecture And Change Seams

## 3.1 Code seams that own this work

- `doctrine/grammars/doctrine.lark`, `doctrine/_parser/parts.py`, and
  `doctrine/_parser/skills.py` own the authoring surface for top-level `skill`
  bodies and graph declarations.
- `doctrine/_model/io.py` and `doctrine/_model/skill_graph.py` own the raw and
  resolved model surface the compiler and emit code share.
- `doctrine/_compiler/resolve/skills.py` already resolves top-level skill refs
  and package links. It is the smallest owner path for direct skill relations.
- `doctrine/_compiler/resolve/skill_graphs.py` already owns graph closure and
  graph policy checks. It is the right owner for relation reachability, graph
  warnings, and policy-aware warning or error decisions.
- `doctrine/emit_common.py`, `doctrine/emit_skill_graph.py`,
  `doctrine/verify_skill_graph.py`, and `doctrine/skill_graph_source_receipts.py`
  own entrypoint support, graph emit, graph verify, and graph receipts.
- `doctrine/_verify_corpus/runners.py` and `pyproject.toml` own the manifest
  proof path for new graph entrypoints.

## 3.2 Architectural rules for implementation

- Add relation structure to `SkillDecl` instead of creating a graph-only skill
  shadow model.
- Keep non-fatal graph findings as data on the resolved graph path, not as
  swallowed exceptions or ad hoc print output.
- Reuse the existing resolved receipt lowering from skill emit when writing
  `receipt_schema_dir`.
- Keep checked skill mention interpolation opt-in and narrow. Do not add a
  blind repo-wide template pass.
- Use `GRAPH.prompt` as another supported entrypoint name. Do not create a
  second direct graph loader.

## 3.3 Resolved decisions

- Warning work ships graph-local first. The warning layer does not need to
  become repo-wide in the same slice.
- `allow unbound_edges` may only relax the graph compile path. Local
  `skill_flow` proof from phase 3 must stay strict by default.
- `dag allow_cycle "Reason"` must be explicit and authored. It is not a global
  "turn cycle checks off" switch.
- Repeat `over:` parity uses the graph path. Bare unresolved names still fail
  as missing graph sets. Dotted graph input or field-path names are kept as
  graph-path repeat sources.

# 4) Phase Plan

## Phase 1 - Language, model, and warning contract

Status: COMPLETE

Work:

- Extend top-level `skill` grammar with a `relations:` block and closed
  relation entries.
- Add relation model types to `SkillDecl` and the graph-resolved model surface.
- Add checked skill mention model support for the opt-in string or Markdown
  surfaces phase 5 touches.
- Add the remaining graph policy grammar and model surface:
  `allow unbound_edges` and `dag allow_cycle "Reason"`.
- Add a warning result carrier that can travel with resolved graph output
  without breaking existing error behavior.
- Add `GRAPH.prompt` to the supported entrypoint surface.

Done when:

- The parser and public model can represent relations, checked mentions, graph
  warning results, relaxed graph policies, and graph-only entrypoints without
  changing shipped phase-4 behavior yet.

## Phase 2 - Resolve, interpolate, and warn

Status: COMPLETE

Work:

- Resolve relation targets against top-level `skill` declarations.
- Extend graph closure so reached skills pull in declared relation facts.
- Implement checked skill mention interpolation for the graph-owned text
  surfaces that need compiler-backed skill naming.
- Implement the graph warning family `W201` through `W211`.
- Make `require relation_reason` and `require checked_skill_mentions` live.
- Make `allow unbound_edges` downgrade the missing-route-binding case from a
  hard failure to policy-aware graph warnings only on the graph compile path.
- Make `dag allow_cycle "Reason"` accept only explicit authored waivers.
- Close any still-open repeat `over:` parity gap if it can be done on the
  existing graph model.

Done when:

- One `compile_skill_graph()` call returns one resolved graph with relations,
  checked mention projections, warning data, and policy-aware validation.

## Phase 3 - Emit, verify, and schema closure

Status: COMPLETE

Work:

- Add `receipt_schema_dir` emit from the same resolved receipt facts the repo
  already lowers for skill contracts.
- Hash emitted receipt schemas in `SKILL_GRAPH.source.json` and verify them in
  `verify_skill_graph`.
- Extend graph contract or query JSON, and any graph Markdown view that needs
  it, to expose relations and warning facts.
- Add `GRAPH.prompt` target routing through emit, verify, and corpus runners.
- Add direct graph emit selectors for view- or diagram-scoped output where the
  spec names them.

Done when:

- Graph emit and verify work from `SKILL.prompt` or `GRAPH.prompt`, and the
  emitted graph tree includes the restored relation, warning, and schema
  surfaces with deterministic receipts.

## Phase 4 - Proof, docs, and doctrine-learn

Status: COMPLETE

Work:

- Add the new manifest-backed examples after `159_skill_graph_policy`.
- Add focused unit tests for relation parsing, warning derivation, checked
  mention interpolation, `GRAPH.prompt` support, and graph schema emit or
  verify.
- Update `docs/SKILL_GRAPH_LANGUAGE_SPEC.md`, `docs/EMIT_GUIDE.md`,
  `docs/WARNINGS.md`, `docs/COMPILER_ERRORS.md`, `examples/README.md`, and
  `skills/doctrine-learn`.
- Update `docs/VERSIONING.md` and `CHANGELOG.md` if the shipped public graph
  surface changes in a way those files treat as versioned truth.

Done when:

- A reader can learn the full shipped phase-5 graph surface from public docs
  and `skills/doctrine-learn` without being told a false phase-4 boundary.

# 5) Verification Plan

## 5.1 Focused manifest proof

Run the new focused manifests first, then the nearby graph regressions:

- `uv run --locked python -m doctrine.verify_corpus --manifest examples/160_skill_graph_relations_mentions/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/161_skill_graph_policy_allowances/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/162_skill_graph_negative_cases/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/163_skill_graph_authoring_metadata/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/164_skill_graph_artifacts/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/157_skill_graph_closure/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/158_skill_graph_emit/cases.toml`
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/159_skill_graph_policy/cases.toml`

## 5.2 Focused unit proof

- `uv sync`
- `npm ci`
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill`
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill`
- `uv run --locked python -m unittest tests.test_emit_skill_graph`
- `uv run --locked python -m unittest tests.test_verify_skill_graph`
- `uv run --locked python -m unittest discover tests`
- `make verify-diagnostics`

## 5.3 Full repo proof

- `make verify-examples`
- `make verify-package`

## 5.4 Repo boundary proof

- `git -C ../lessons_studio status --short`

Expected result: no new edits from this slice. If the worktree is already
dirty, record that plainly and confirm this phase did not touch it.

## 5.5 Actual proof results

All required commands passed on 2026-04-26:

- `uv sync`: passed. It resolved 8 packages and checked 8 packages.
- `npm ci`: passed. It installed 3 packages and found 0 vulnerabilities.
- Focused manifests for examples `160` through `164` and nearby graph
  manifests `157` through `159`: passed, 14/14 cases.
- `uv run --locked python -m unittest tests.test_emit_skill_graph tests.test_verify_skill_graph tests.test_skill_graph_semantics`: passed, 10/10 tests.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_skill`: passed, emitted 17 files.
- `uv run --locked python -m doctrine.emit_skill --target doctrine_learn_public_skill`: passed, emitted 17 files.
- `make verify-diagnostics`: passed.
- `make verify-package`: passed.
- `make verify-examples`: passed, 486/486 manifest cases.
- `uv run --locked python -m unittest discover tests`: passed, 581/581 tests.
- `git -C ../lessons_studio status --short`: passed with no output.
- Completion critic repair proof on 2026-04-26: `make verify-examples`
  passed, `make verify-package` passed,
  `uv run --locked python -m unittest discover tests` passed 581/581 tests,
  and `git -C ../lessons_studio status --short` returned no output after the
  public-doc and release-truth repair.
- Completion-after-repair critic on 2026-04-26: passed at
  `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z/critics/completion-after-repair/graph-semantics-completion/run-2026-04-26T21-27-52Z/verdict.json`
  with no discovered items.

# 6) Logs

## Orchestration Log

- 2026-04-26: Created from the scope-restore pass against the epic doc, the
  language spec, the lessons-studio audit, the shipped graph code, and
  examples `150` through `159`.
- 2026-04-26: This phase owns the cut graph semantics and the remaining
  Doctrine-side audit items. It should not leave a queued phase 6 for features
  that this repo can ship now.
- 2026-04-26: Implementation restored relations, checked mentions, graph
  warnings, `GRAPH.prompt`, receipt schemas, view selectors, graph policy
  relaxers, graph-path repeats, skill inventory metadata, durable artifacts,
  and Doctrine Learn coverage.
- 2026-04-26: The user asked to stop after doc updates and not begin new
  coding. Full-corpus verification still needed a later explicit run.
- 2026-04-26: The user resumed the epic, corrected the automatic lane to Codex
  `gpt-5.5` xhigh for all roles, and asked to finish through the async
  automatic path. This plan stayed `implementing` until the final full-corpus
  proof passed.
- 2026-04-26: Final worker pass reconciled the spec, audit, code, examples,
  docs, and `skills/doctrine-learn`. It found one remaining Doctrine-side gap:
  `W205` branch coverage warning was named by the spec but not implemented.
  This pass added `warn branch_coverage_incomplete` on the graph path, proved
  it in example `161_skill_graph_policy_allowances`, refreshed Doctrine Learn,
  and ran the full required proof set. That made phase 5 ready for the
  completion critic.
- 2026-04-26: Completion critic verdict
  `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z/critics/completion/graph-semantics-completion/run-2026-04-26T21-07-57Z/verdict.json`
  returned `scope_change_detected` because `docs/LANGUAGE_REFERENCE.md`,
  `CHANGELOG.md`, and `docs/VERSIONING.md` still taught stale graph and release
  truth. This repair updated those docs, aligned `docs/README.md`, wrote the
  auto-run `repair-report.md`, and reran the required proof set cleanly.
- 2026-04-26: Completion-after-repair critic verdict
  `.arch_skill/arch-epic/auto/doctrine-skill-graph-2026-04-26/run-2026-04-26T20-50-49Z/critics/completion-after-repair/graph-semantics-completion/run-2026-04-26T21-27-52Z/verdict.json`
  returned `pass`. All checks passed, and there were no discovered items.

## Decision Log

- 2026-04-26: This phase restores features that phase 4 cut out. Do not
  silently narrow them again unless current code proves the spec or audit was
  wrong.
- 2026-04-26: Warning work ships graph-local first. Each shipped warning must
  point to one owner path and one likely fix path.
- 2026-04-26: `GRAPH.prompt` is a supported entrypoint name, not a second
  compile mode.
- 2026-04-26: `receipt_schema_dir` must reuse the existing resolved receipt
  lowering path. Do not build a second schema generator just for graphs.
- 2026-04-26: Repeat `over:` parity shipped as graph-path support for dotted
  input or field-path names. Bare unresolved names remain graph-set refs and
  still fail if the set is not declared.
- 2026-04-26: `skills/doctrine-learn` updates are required in this phase for
  every feature that ships. There is no separate phase 6 teaching sweep.
- 2026-04-26: The completion critic repair is same-scope documentation and
  release-truth alignment. It does not change the approved phase 5 product
  scope, and it does not edit `../lessons_studio`.

# 7) Acceptance Checklist

- [x] Top-level `skill` accepts `relations:` with the closed relation kinds.
- [x] Relation targets resolve, and reached-skill relations appear in graph
  closure and graph emit.
- [x] Checked `{{skill:Name}}`, `.package`, and `.purpose` interpolation ships
  on the graph-owned text surfaces that need it.
- [x] `require checked_skill_mentions` is live.
- [x] `W201` through `W211` are real compiler warnings, not inert metadata.
- [x] `GRAPH.prompt` is supported by emit, verify, and corpus proof.
- [x] `receipt_schema_dir` emits deterministic receipt schemas and records them
  in `SKILL_GRAPH.source.json`.
- [x] `allow unbound_edges` and `dag allow_cycle "Reason"` are live graph
  policies with explicit authored behavior.
- [x] Repeat `over:` parity is closed for graph sets and dotted graph paths.
- [x] The next graph examples after `159` prove the restored surface cleanly.
- [x] `docs/SKILL_GRAPH_LANGUAGE_SPEC.md` matches the shipped graph surface.
- [x] `skills/doctrine-learn` teaches the shipped phase-5 graph surface from
  source.
- [x] `make verify-examples` passes after the restored scope.
- [x] `uv run --locked python -m unittest discover tests` passes after the
  restored scope.
- [x] Completion-after-repair critic passed with no known scope drift outside
  the accepted `../lessons_studio` migration boundary.
