---
title: "Doctrine - Compile Errors Exact Lines And Shared Pattern - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/COMPILER_ERRORS.md
  - doctrine/diagnostics.py
  - doctrine/_diagnostics/contracts.py
  - doctrine/_diagnostics/formatting.py
  - doctrine/_diagnostics/message_builders.py
  - doctrine/_compiler/session.py
  - doctrine/_compiler/indexing.py
  - doctrine/_compiler/support.py
  - doctrine/_parser/parts.py
  - tests/test_parse_diagnostics.py
  - tests/test_import_loading.py
  - examples/03_imports/cases.toml
---

# TL;DR

## Outcome

Doctrine compile errors point to the exact authored line to fix by default.
When a failure involves more than one authored site, the error shows one
primary line plus related lines that explain the conflict. The message also
says the real problem in plain language instead of making authors decode
internal compiler phrasing.

## Problem

Doctrine's formatter can already print line, column, source excerpt, hints,
and trace. But the compile surface almost never carries that data. In a local
review of 160 manifest-backed `compile_fail` agent cases, 0 had line-level
location, 152 had path-only location, and 8 had no `Location:` block at all.
The compile layer also rebuilds many diagnostics from free-form error strings,
which makes exact spans and richer context hard to express.

## Approach

Move compile diagnostics onto one structured contract that carries primary
source spans, related spans, clear detail text, and stable code/summary
fields. Thread authored source positions from parser-owned temporary parts
into the authored model and compile helpers. Then migrate every compile error
family to shared location-aware helpers so exact-line output becomes the
default behavior instead of an exception.

## Plan

1. Add a shared compile-diagnostic data contract with primary and related
   source locations.
2. Preserve source spans on the authored nodes and refs that later compile
   validation reads.
3. Audit and migrate every `CompileError` family across indexing, resolve,
   validate, compile, and project-config surfaces.
4. Prove the new behavior across manifest-backed compile-fail cases, targeted
   unit tests, and compiler-error docs.

## Non-negotiables

- Keep shipped error codes stable unless a real release-level reason says
  otherwise.
- Exact line, column, and excerpt are the default for authored compile
  failures.
- Multi-site conflicts must show both the line to change and the related line
  that caused the conflict.
- File-only compile locations are allowed only for truly global failures, and
  those errors must say plainly why no single authored line exists.
- Do not keep regex message parsing as the long-term default compile-diagnostic
  path.
- Parse errors must not regress while compile diagnostics improve.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
recommended_flow: confirm North Star -> research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine preserves authored source spans through the compile pipeline and
raises compile diagnostics from one structured helper pattern, then every
authored compile failure can identify the exact line to change, show related
lines when the failure spans more than one authored site, and explain the
problem in direct language. After this change, compile diagnostics should no
longer depend on parsing their own free-form message strings to recover
meaning.

## 0.2 In scope

- Exhaustively review the compile-error surface that reaches `CompileError`,
  including compiler entrypoints, indexing, import resolution, resolve,
  validate, compile, and compile-stage project-config failures.
- Define one shared compile-diagnostic contract for:
  primary source location, primary excerpt, related locations, detail, hints,
  trace, and low-level cause.
- Preserve authored line and column data on the nodes, refs, or equivalent
  shared span carriers that later compile validation can still see.
- Choose and document one shared policy for duplicates, kind mismatches,
  missing refs, import failures, output and review semantic failures, and
  other multi-site conflicts.
- Migrate compile raise sites so structured, location-aware diagnostics are
  the default authoring path.
- Update compiler error docs, diagnostic smoke coverage, and manifest-backed
  proof where the public error shape changes.
- Keep imported parse failures working with the same or better clarity.

## 0.3 Out of scope

- Redesigning the parse-error surface beyond any parity work needed to keep it
  aligned with the new compile contract.
- Redesigning the emit-error surface unless a shared helper falls out
  naturally from the compile work.
- Changing public Doctrine prompt syntax.
- Adding runtime shims, fallback parsing, or a second diagnostic formatter.
- Building a custom UI, IDE integration, or interactive diagnostic browser.
- Weakening fail-loud compiler behavior in exchange for "friendlier" output.

## 0.4 Definition of done (acceptance evidence)

- Every manifest-backed authored `compile_fail` case that has one truthful
  authored source site reports exact file, line, column, and source excerpt.
- Multi-site authored compile failures report one primary site plus related
  sites that explain the conflict.
- The shared compile-diagnostic helper pattern is used across compile
  families instead of ad hoc string parsing.
- Shipped codes remain stable, or any intentional exception is documented in
  `docs/COMPILER_ERRORS.md` and the Decision Log.
- New tests prove representative families such as duplicate agent fields,
  missing imported declarations, output inheritance mismatches, unknown
  addressable paths, guard-read violations, and import-root failures.
- `make verify-diagnostics` passes after the new diagnostic shape settles.
- If any compile error still cannot point to one exact authored line, the doc
  records why that case is structurally different and what best-possible
  location it must emit instead.

## 0.5 Key invariants (fix immediately if violated)

- No new parallel compile-diagnostic path.
- No silent fallback from line-level authored diagnostics to path-only output.
- No multi-site conflict without a related-location explanation.
- No behavior drift in shipped error-code identity.
- No compile helper that must regex-parse its own message to know what
  happened.
- No regression in parse-diagnostic clarity while compile-diagnostic work is
  in flight.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-16
Verdict (code): NOT COMPLETE
Manual QA: n/a (non-blocking)

## Code blockers (why code is not done)
- Phase 4 is still open. The approved compile frontier still has raw string `CompileError` branches and unclassified exceptions across the unresolved compiler, resolver, validator, and entrypoint helpers instead of one shared structured path everywhere. Representative anchors: `doctrine/_compiler/compile/agent.py:893`, `doctrine/_compiler/compile/readables.py:413-537`, `doctrine/_compiler/compile/readable_blocks.py:498, 543`, `doctrine/_compiler/compile/records.py:203`, `doctrine/_compiler/compile/workflows.py:38, 64, 109, 351`, `doctrine/_compiler/flow.py:73, 75, 315, 683-911`, `doctrine/_compiler/resolve/output_schemas.py:824, 845, 867, 876, 1112, 1118, 1124, 1129, 1287, 1354`, `doctrine/_compiler/resolve/outputs.py:1289, 1301, 2259, 2385`, `doctrine/_compiler/resolve/reviews.py:164`, `doctrine/_compiler/resolve/schemas.py:196, 260, 294, 328, 363, 387, 389`, `doctrine/_compiler/resolve/skills.py:34, 94, 183, 247`, `doctrine/_compiler/resolve/io_contracts.py:253, 313`, `doctrine/_compiler/resolve/document_blocks.py:195, 235, 246, 285, 428, 477, 522`, `doctrine/_compiler/resolve/analysis.py:33, 108, 186, 241`, `doctrine/_compiler/resolve/agent_slots.py:238, 245, 247, 259, 307`, `doctrine/_compiler/validate/agents.py:143, 199, 220, 257, 269`, `doctrine/_compiler/validate/contracts.py:261, 368`, `doctrine/_compiler/validate/display.py:211, 335, 352`, `doctrine/_compiler/validate/law_paths.py:369, 374`, `doctrine/_compiler/validate/review_agreement.py:47, 52, 56, 60, 102, 248, 261, 280, 287, 296, 314, 327, 339, 349, 386, 419, 445, 460, 470, 500, 505`, `doctrine/_compiler/validate/review_preflight.py:205`, `doctrine/_compiler/validate/review_semantics.py:137, 143, 146`, `doctrine/_compiler/validate/review_branches.py:433`, `doctrine/_compiler/validate/route_semantics_context.py:198`, `doctrine/_compiler/validate/routes.py:66, 906, 1740`, `doctrine/_compiler/validate/outputs.py:240, 299`, `doctrine/_compiler/validate/schema_helpers.py:69, 92, 110`, `doctrine/_compiler/validate/addressable_display.py:354`, `doctrine/_compiler/indexing.py:635, 806, 831`, `doctrine/_compiler/context.py:128-180`, and `doctrine/_compiler/support.py:22, 29`. Both `make verify-diagnostics` and `make verify-examples` pass on the current tree, so the remaining work is the unclosed migration frontier rather than a broken smoke path.
- Phase 5 is still open. The shipped proof still keys `compile_fail` on `message_contains`, the smoke layer still checks codes and snippets instead of exact-line and related-site output, the public docs still describe the older proof surface, and the compile regex bridge in `doctrine/diagnostics.py` is still live. Representative anchors: `doctrine/_verify_corpus/manifest.py:31, 209, 227`, `doctrine/_verify_corpus/runners.py:429`, `doctrine/_diagnostic_smoke/compile_checks.py:29-48`, `docs/COMPILER_ERRORS.md:1`, `examples/README.md:1`, `doctrine/diagnostics.py:347`, and `doctrine/_diagnostics/message_builders.py:80`.

## Reopened phases (false-complete fixes)
- Phase 4 (Authored compile-family migration and policy convergence) — reopened because:
  - helper-backed slices are in place, but the remaining frontier still spans raw string branches across the unresolved compiler, resolver, validator, and entrypoint helpers instead of one shared structured path everywhere.
  - the live frontier still includes the representative surfaces listed above, so the inventory/classification pass cannot honestly say every remaining compile site is already exact-line, related-site, or truthful file-scoped.
- Phase 5 (Proof, docs, corpus contract, and cleanup) — reopened because:
  - `doctrine/_verify_corpus/manifest.py:31` and `:209` still define `message_contains`, `doctrine/_verify_corpus/runners.py:429` still checks snippet containment, and `doctrine/_diagnostic_smoke/compile_checks.py:29-48` still checks codes and snippets instead of the final exact-line and related-site contract.
  - the public docs and corpus notes still describe the older proof surface, and the compile regex bridge in `doctrine/diagnostics.py` is still live even though the legacy corpus run currently passes.

## Missing items (code gaps; evidence-anchored; no tables)
- Remaining compile-family frontier still uses raw `CompileError` branches across the unresolved compiler, resolver, validator, and entrypoint helpers.
  - Evidence anchors:
    - `doctrine/_compiler/compile/agent.py:893`
    - `doctrine/_compiler/compile/readables.py:413-537`
    - `doctrine/_compiler/compile/readable_blocks.py:498, 543`
    - `doctrine/_compiler/compile/records.py:203`
    - `doctrine/_compiler/compile/workflows.py:38, 64, 109, 351`
    - `doctrine/_compiler/flow.py:73, 75, 315, 683-911`
    - `doctrine/_compiler/resolve/output_schemas.py:824, 845, 867, 876, 1112, 1118, 1124, 1129, 1287, 1354`
    - `doctrine/_compiler/resolve/outputs.py:1289, 1301, 2259, 2385`
    - `doctrine/_compiler/resolve/reviews.py:164`
    - `doctrine/_compiler/resolve/schemas.py:196, 260, 294, 328, 363, 387, 389`
    - `doctrine/_compiler/resolve/skills.py:34, 94, 183, 247`
    - `doctrine/_compiler/resolve/io_contracts.py:253, 313`
    - `doctrine/_compiler/resolve/document_blocks.py:195, 235, 246, 285, 428, 477, 522`
    - `doctrine/_compiler/resolve/analysis.py:33, 108, 186, 241`
    - `doctrine/_compiler/resolve/agent_slots.py:238, 245, 247, 259, 307`
    - `doctrine/_compiler/validate/agents.py:143, 199, 220, 257, 269`
    - `doctrine/_compiler/validate/contracts.py:261, 368`
    - `doctrine/_compiler/validate/display.py:211, 335, 352`
    - `doctrine/_compiler/validate/law_paths.py:369, 374`
    - `doctrine/_compiler/validate/review_agreement.py:47, 52, 56, 60, 102, 248, 261, 280, 287, 296, 314, 327, 339, 349, 386, 419, 445, 460, 470, 500, 505`
    - `doctrine/_compiler/validate/review_preflight.py:205`
    - `doctrine/_compiler/validate/review_semantics.py:137, 143, 146`
    - `doctrine/_compiler/validate/review_branches.py:433`
    - `doctrine/_compiler/validate/route_semantics_context.py:198`
    - `doctrine/_compiler/validate/routes.py:66, 906, 1740`
    - `doctrine/_compiler/validate/outputs.py:240, 299`
    - `doctrine/_compiler/validate/schema_helpers.py:69, 92, 110`
    - `doctrine/_compiler/validate/addressable_display.py:354`
    - `doctrine/_compiler/indexing.py:635, 806, 831`
    - `doctrine/_compiler/context.py:128-180`
    - `doctrine/_compiler/support.py:22, 29`
  - Plan expects:
    - every remaining compile site in the approved frontier to be classified and migrated to the shared helper path, or called out as a truthful file-scoped exception.
  - Code reality:
    - raw string `CompileError` branches still survive across the representative compiler, resolver, validator, and entrypoint surfaces, so the inventory/classification sweep is not complete.
  - Fix:
    - finish the shared-helper migration and classify the remaining sites as exact-line primary, multi-site related-site, or truthful file-scoped exception.

- Proof, docs, and bridge cleanup still need to reach the final contract.
  - Evidence anchors:
    - `doctrine/_diagnostic_smoke/compile_checks.py:29-48`
    - `doctrine/_verify_corpus/manifest.py:31, 209, 227`
    - `doctrine/_verify_corpus/runners.py:429`
    - `docs/COMPILER_ERRORS.md:1`
    - `examples/README.md:1`
    - `doctrine/diagnostics.py:347`
    - `doctrine/_diagnostics/message_builders.py:80`
  - Plan expects:
    - smoke checks, corpus cases, and public docs to assert the final exact-line and related-site contract, then remove the compile regex bridge.
  - Code reality:
    - the corpus still keys on `message_contains`, the runner still checks message snippets, the smoke layer still validates codes and snippets instead of exact locations or related sites, the public docs still do not define the richer manifest contract, and `_compile_diagnostic_from_message()` remains the compile regex bridge.
  - Fix:
    - move the corpus proof and smoke checks to the final contract, update the docs/examples, then remove `_compile_diagnostic_from_message()` and its compile-only builders.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- None.
<!-- arch_skill:block:implementation_audit:end -->

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Exact authored line first.
2. Clear explanation of the real problem second.
3. One shared default pattern across the compiler third.
4. Stable public error identity fourth.
5. Exhaustive migration and proof over isolated spot fixes fifth.

## 1.2 Constraints

- The compile-error surface is broad. `rg` shows many raw `raise CompileError`
  sites across `doctrine/_compiler/`.
- The existing formatter already supports location, excerpt, hints, cause, and
  trace, so the main gap is data plumbing and structured construction, not
  final rendering alone.
- The authored parser already tracks line and column on many temporary parts,
  but the authored model drops most of that data before compile validation.
- `docs/COMPILER_ERRORS.md`, manifest-backed examples, and diagnostic smoke
  are part of the shipped truth and must stay aligned.
- Parse failures already behave much better than compile failures, so compile
  work should converge toward that bar rather than fork a new UX style.

## 1.3 Architectural principles (rules we will enforce)

- Source spans must travel with the authored truth that compile validation
  reads.
- Compile diagnostics must be created from structured fields, not recovered
  from prose strings.
- One primary site explains what to edit now. Related sites explain why.
- File-only location is an explicit exception path, not the silent default.
- Session and import trace enrichment may add context, but it must not erase a
  more exact inner location.

## 1.4 Known tradeoffs (explicit)

- Preserving source spans on authored model nodes will widen many dataclasses,
  but that is better than adding a parallel span map.
- Multi-site diagnostics improve clarity, but they require a richer public
  contract than the current single-location shape.
- Project-config semantic failures may need a different source-mapping helper
  than prompt-file failures because `tomllib` does not preserve semantic-node
  locations by itself.
- A temporary bridge from old message builders to structured helpers may make
  migration safer, but it must end as cleanup work, not become the final
  design.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- `doctrine/diagnostics.py` formats a structured diagnostic into summary,
  location, detail, source, trace, hints, and cause.
- Parse errors use that structured path with exact lines and excerpts.
- Compile errors usually raise free-form strings, then
  `doctrine/_diagnostics/message_builders.py` regex-maps those strings back
  into codes, summaries, and hints.
- `CompilationSession` and import-loading wrappers often add a path-level
  location late with `ensure_location(path=...)`, which fills in the file but
  not the actual authored line.

## 2.2 What's broken / missing (concrete)

- In a local review of 160 manifest-backed agent `compile_fail` cases,
  0 reported a line, column, or excerpt.
- 152 of those cases reported only a file path.
- 8 reported no `Location:` block at all.
- Duplicates and overrides tell the user that something conflicts, but they do
  not point at the later line to edit or the earlier line that caused the
  collision.
- Missing imports and missing imported declarations often name the missing
  symbol but not the exact `import` or `use` line that referenced it.
- The current single-location contract cannot express both "change this line"
  and "it conflicts with that earlier line."

## 2.3 Constraints implied by the problem

- This cannot be fixed only in the formatter.
- This cannot be solved honestly with clearer wording alone.
- A real fix needs both source-span preservation and a shared compile
  constructor pattern.
- Because the surface is broad, the migration must be inventory-driven and
  backed by corpus proof, not by a handful of hand-picked examples.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- No external research is needed for the first planning pass. The right bar is
  already clear: one primary span, optional related spans, direct problem
  text, and one short fix hint when the compiler knows the fix.
- Reject any design that adds a second formatter, a browser-only error UI, or
  a runtime-side recovery layer. Repo truth already shows Doctrine can format
  rich diagnostics. The missing piece is structured compile data.

## 3.2 Internal ground truth (code as spec)

- [doctrine/diagnostics.py](/Users/aelaguiz/workspace/doctrine/doctrine/diagnostics.py:48)
  and
  [doctrine/_diagnostics/formatting.py](/Users/aelaguiz/workspace/doctrine/doctrine/_diagnostics/formatting.py:80)
  already own the canonical text shape. They can print `Location:`,
  `Source:`, carets, `Trace:`, `Hint:`, and `Cause:` when the diagnostic
  carries real spans.
- [doctrine/_diagnostics/contracts.py](/Users/aelaguiz/workspace/doctrine/doctrine/_diagnostics/contracts.py:7)
  is the current public data boundary. It only carries one `location` and one
  `excerpt`, so duplicates and conflict pairs cannot honestly show both sites.
- [doctrine/_diagnostics/message_builders.py](/Users/aelaguiz/workspace/doctrine/doctrine/_diagnostics/message_builders.py:51)
  plus the `_diagnostics/_message_builders_*.py` family rebuild many compile
  diagnostics from raw message text. This is the main structural reason
  compile errors lose exact spans and family-specific context.
- [doctrine/_parser/parts.py](/Users/aelaguiz/workspace/doctrine/doctrine/_parser/parts.py:33)
  and parser runtime helpers preserve line and column on parser-owned parts
  before lowering.
- [doctrine/_model/agent.py](/Users/aelaguiz/workspace/doctrine/doctrine/_model/agent.py:12),
  [doctrine/_model/io.py](/Users/aelaguiz/workspace/doctrine/doctrine/_model/io.py:19),
  [doctrine/_model/core.py](/Users/aelaguiz/workspace/doctrine/doctrine/_model/core.py:7),
  and sibling authored-model files drop most source-position data before
  compile validation reads those values.
- [doctrine/_compiler/session.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/session.py:113),
  [doctrine/_compiler/indexing.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/indexing.py:433),
  and `doctrine/_compiler/support.py` currently add file-level
  `ensure_location(path=...)` and trace late. That improves context, but it
  usually stamps the file after the exact authored span is already gone.
- Local corpus review on 2026-04-16 found 160 manifest-backed agent
  `compile_fail` cases: 0 with line or column, 152 path-only, 8 with no
  `Location:` block, and 153 with `Trace:` only.
- Local inventory on 2026-04-16 found 604 raw `raise CompileError(...)` sites
  across `doctrine/**/*.py`. The migration must be inventory-driven, not
  hand-picked by a few obvious error families.
- [tests/test_parse_diagnostics.py](/Users/aelaguiz/workspace/doctrine/tests/test_parse_diagnostics.py:9)
  is the strongest in-repo proof bar for exact-line, excerpt, and hint
  rendering.
- `tests/test_import_loading.py`, `tests/test_output_inheritance.py`,
  `tests/test_decision_attachment.py`, and
  `doctrine/_diagnostic_smoke/compile_checks.py` are the current compile-fail
  proof surfaces. They mostly lock codes and message shape today, not exact
  compile locations.
- `docs/COMPILER_ERRORS.md` is the canonical public catalog. If compile
  wording or rendered sections change, it must move with the code.

Canonical owner path:

- `doctrine/_diagnostics/contracts.py` and `doctrine/diagnostics.py` should
  stay the one diagnostic contract and formatter owner.
- `doctrine/_parser/*` to `doctrine/_model/*` should own span preservation.
- Compile helpers under `doctrine/_compiler/*` should feed the structured
  contract directly instead of routing through regex message recovery.

Adjacent surfaces tied to the same contract family:

- `docs/COMPILER_ERRORS.md`, `doctrine/_diagnostic_smoke/compile_checks.py`,
  manifest-backed `compile_fail` examples, import-loading tests,
  output-inheritance tests, decision-attachment tests, and
  `tests/test_parse_diagnostics.py` all move with this change.

Compatibility posture:

- Preserve shipped error codes and broad section ordering.
- Improve location richness additively.
- Treat file-only compile output as an explicit exception path, not a
  compatible default.

Existing patterns to reuse:

- `DoctrineError.from_parts`, `ParseError.from_lark`,
  `ParseError.from_transform`, `prepend_trace`, and `ensure_location` are the
  current structured-diagnostic building blocks.
- The compile path should converge toward those helpers instead of layering
  more regex message builders.

Duplicate or drifting paths relevant to this change:

- Parser diagnostics already use structured spans. Compile diagnostics often
  recover meaning from strings after the fact. That split is the main drift to
  remove.
- Parser-owned parts keep locations while authored model nodes often do not.
  That is the span-loss boundary this plan needs to close.

Capability-first opportunity before new tooling:

- No new harness, wrapper, or UI is needed. The compiler already has the
  authored nodes in memory. It needs to preserve spans and emit them through
  the existing formatter.

Behavior-preservation signals already available:

- `make verify-diagnostics`, `tests/test_parse_diagnostics.py`,
  `tests/test_import_loading.py`, `tests/test_output_inheritance.py`,
  `tests/test_decision_attachment.py`,
  `doctrine/_diagnostic_smoke/compile_checks.py`, and a corpus sweep over
  manifest-backed `compile_fail` cases.

## 3.3 Decision gaps that must be resolved before implementation

No user blocker remains. Deep-dive resolves the remaining architecture choices
from repo truth:

- Use one model-owned source-span carrier on compile-relevant authored values.
  Do not add a parallel span map.
- Extend the diagnostic contract additively with labeled related locations and
  render them under one `Related:` section.
- Treat prompt-authored compile failures as exact-line by default.
- Treat `pyproject.toml` and filesystem/package-layout failures with the best
  truthful source policy: exact line when Doctrine can prove it, otherwise
  file or key-level context with a plain explanation.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/_parser/parts.py`, `doctrine/_parser/agents.py`,
  `doctrine/_parser/io.py`, `doctrine/_parser/readables.py`,
  `doctrine/_parser/analysis_decisions.py`, and
  `doctrine/_parser/transformer.py` already carry line and column on many
  temporary parser parts.
- `doctrine/_model/core.py`, `doctrine/_model/agent.py`,
  `doctrine/_model/io.py`, `doctrine/_model/review.py`, and sibling model
  files keep the authored declarations that compile code reads, but most of
  those dataclasses and refs do not keep source spans.
- `doctrine/_compiler/session.py`, `doctrine/_compiler/indexing.py`,
  `doctrine/_compiler/resolve/*`, `doctrine/_compiler/compile/*`,
  `doctrine/_compiler/flow.py`, and `doctrine/_compiler/package_layout.py`
  own the compile-stage failure surface.
- `doctrine/_diagnostics/contracts.py`, `doctrine/diagnostics.py`, and
  `doctrine/_diagnostics/formatting.py` own the canonical diagnostic contract
  and rendered text shape.
- `doctrine/_diagnostics/message_builders.py` plus the
  `_diagnostics/_message_builders_*.py` files own compile code and summary
  recovery from free-form message strings.
- `doctrine/_diagnostic_smoke/compile_checks.py`, `tests/test_*`, and the
  manifest-backed `compile_fail` examples are the shipped proof surfaces for
  compile diagnostics.

## 4.2 Control paths (runtime)

The current compile path is:

1. `parse_file()` builds parser parts with line and column.
2. Lowering turns those parts into `model.*` values such as `ImportDecl`,
   `NameRef`, agent fields, output items, and review refs.
3. Most of those lowered model values lose their source position before
   indexing, resolve, and compile logic runs.
4. Compile families raise `CompileError("...")` from many places in
   `_compiler/indexing.py`, `_compiler/resolve/*`, `_compiler/compile/*`,
   `_compiler/flow.py`, and `_compiler/package_layout.py`.
5. `CompileError._diagnostic_from_message()` calls
   `_compile_diagnostic_from_message()`, which regex-maps the message back to
   code, summary, detail, and hints.
6. Session and import wrappers then add `Trace:` frames and often only a file
   path through `ensure_location(path=...)`.
7. `format_diagnostic()` can print `Source:` only when the diagnostic already
   carries an exact line, column, and excerpt.

Two important side paths behave differently:

- Parse failures already go through structured `ParseError.from_lark()` or
  `ParseError.from_transform()` with exact excerpts.
- Compile config TOML decode failures are caught in `CompilationSession`, but
  they currently become path-only `CompileError.from_parts(...)` output even
  though the raw `TOMLDecodeError` contains line information.

## 4.3 Object model + key abstractions

- `DoctrineDiagnostic` carries one `location`, one `excerpt`, one
  `caret_column`, optional `trace`, `hints`, and `cause`. It has no first
  class `related` sites.
- `CompileError.from_parts(...)` exists and can already carry structured
  location and excerpt data, but most compile families do not use it.
- `DoctrineError.ensure_location(...)` can only backfill one location. It
  cannot invent a truthful excerpt after spans are gone.
- Parser parts already hold `line` and `column`, but core model values such as
  `ImportDecl`, `NameRef`, `AddressableRef`, and many authored field wrappers
  do not.
- Several compile families already know the semantic object that failed, but
  not the exact authored line to show.
- `doctrine/_compiler/flow.py` mirrors parts of ordinary output and config
  validation that also exist in `doctrine/_compiler/compile/outputs.py` and
  `doctrine/_compiler/compile/records.py`, so any new diagnostic pattern has
  to land in more than one compile surface.

## 4.4 Observability + failure behavior today

- Compile failures are already fail-loud. The problem is not silence. The
  problem is poor location truth.
- Local corpus review on 2026-04-16 found 160 manifest-backed agent
  `compile_fail` cases: 0 with line or column, 152 path-only, 8 with no
  `Location:` block at all, and 153 with only trace context.
- Local inventory on 2026-04-16 found 604 raw `raise CompileError(...)` sites
  across `doctrine/**/*.py`.
- Duplicate field, override mismatch, unknown ref, and guard-read failures
  usually know the bad authored object, but they only print the owner label or
  file path.
- Import resolution and root indexing failures can occur before the
  `compile_agent()` wrapper adds the root prompt path, so some failures show
  only `Trace:` and no `Location:`.
- Compile config syntax and semantic failures are still weaker than emit-side
  TOML errors, which already have an exact-location helper.
- Filesystem and package-layout failures in `doctrine/_compiler/package_layout.py`
  often have a truthful file path but no authored prompt line. Those are real
  exceptions the plan must model honestly.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This is a text-diagnostic surface, not a product UI change.

<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Add one small model-owned `SourceSpan` value in
  `doctrine/_model/core.py`, not a side map under compiler code.
- Add optional source-span fields to the compile-relevant authored model
  values that survive past parsing, including import refs, named refs,
  addressable refs, agent field wrappers, review refs, output items, and other
  authored values that can become a primary or related error site.
- Keep one diagnostic contract under `doctrine/_diagnostics/contracts.py`, but
  extend it additively with labeled related locations.
- Keep one formatter under `doctrine/diagnostics.py` and
  `doctrine/_diagnostics/formatting.py`.
- Add one compiler-owned helper module, `doctrine/_compiler/diagnostics.py`,
  as the shared path for structured compile diagnostic creation.
- Remove compile-family dependence on `_compile_diagnostic_from_message()` by
  the end of the rollout. Regex builders are not the final compile path.

## 5.2 Control paths (future)

Prompt-authored failure flow:

1. Parser meta is lowered into model-owned source spans.
2. Indexing, resolve, validate, and compile families keep those spans on the
   exact authored objects they inspect.
3. When a failure is detected, the family chooses one primary site:
   the line the author should change now.
4. If the failure involves more than one authored site, the family also passes
   labeled related sites such as `first defined here`, `inherited from here`,
   or `referenced here`.
5. `doctrine/_compiler/diagnostics.py` converts those spans plus the owning
   source file into `CompileError.from_parts(...)` data with exact excerpt
   text.
6. Session and import wrappers may prepend trace, but they do not replace a
   more exact inner span.
7. The formatter prints a stable shape:
   `Location:`, `Source:`, optional `Related:`, `Detail:`, optional `Trace:`,
   optional `Hint:`, and optional `Cause:`.

Non-prompt failure flow:

- Compile config TOML syntax errors use the same exact-line excerpt building
  bar as existing emit TOML decode errors.
- Compile config semantic errors use a bounded config-source locator for the
  Doctrine-owned compile keys when Doctrine can prove the key or array-item
  line. If no honest semantic-node line is available, the error points to the
  config file and key label and says why no exact line exists.
- Filesystem and package-layout failures stay file-scoped. They do not invent
  fake prompt lines.

## 5.3 Object model + abstractions (future)

- Add one shared `SourceSpan` abstraction for authored model values. It should
  carry the minimum truthful data needed to rebuild a precise diagnostic site:
  line and column, plus the owning source file from compile context.
- Add one additive related-site structure to `DoctrineDiagnostic`:
  `DiagnosticRelatedLocation`, with its own label, location, excerpt, and
  caret.
- Add shared compile helper entrypoints such as:
  - build a primary prompt-authored site from `unit + source span`
  - build a related site from `unit + source span + label`
  - build a file-only site for truthful no-line exceptions
  - build a full `CompileError.from_parts(...)` from code, summary, detail,
    primary site, related sites, hints, trace, and cause
- Keep error-code identity at the call site or shared family helper. Do not
  derive it from regex message recovery.
- Choose one default primary-site policy across the compiler:
  the line to change is primary, the prior or inherited source is related.

## 5.4 Invariants and boundaries

- Model-owned spans are the only truth source for authored compile locations.
  No parallel span registry is allowed.
- Structured compile helpers under `doctrine/_compiler/diagnostics.py` are the
  default compile path. New compile families must use them.
- Every prompt-authored compile error must emit an exact primary line unless
  the plan records a structural exception.
- Duplicates, conflicts, overrides, and inheritance mismatches must emit
  labeled related sites.
- `ensure_location(path=...)` remains a last-resort helper for true no-line
  cases. It is not the normal authored compile path.
- Existing compile error codes remain the public compatibility baseline.
- The rendered text shape may grow one additive `Related:` block, but there is
  still only one formatter and one compile-diagnostic contract.
- Any temporary bridge from regex compile builders to structured helpers is
  internal, timeboxed, and deleted by the final cleanup phase.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable.

<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Model span carrier | `doctrine/_model/core.py` | `ImportDecl`, `NameRef`, `ExprRef`, `AddressableRef`, shared authored span value | Core authored refs do not keep source span data. | Add one shared optional source-span value and thread it through compile-relevant refs. | Compile helpers need the same authored object to still know where it came from. | Model-owned `source_span` contract. | New span-preservation tests, parse-diagnostic parity tests |
| Authored field carriers | `doctrine/_model/agent.py`, `doctrine/_model/io.py`, `doctrine/_model/review.py`, sibling model files | agent fields, output items, review refs, record refs | Many authored wrappers know semantic meaning but not authored line. | Add source spans to the compile-relevant wrappers that can become primary or related sites. | Duplicate fields and override conflicts need the real authored line, not just the owner label. | Span-aware authored wrappers. | `tests/test_output_inheritance.py`, `tests/test_decision_attachment.py`, new compile-location tests |
| Parser lowering | `doctrine/parser.py`, `doctrine/_parser/transformer.py`, `doctrine/_parser/agents.py`, `doctrine/_parser/io.py`, `doctrine/_parser/readables.py`, `doctrine/_parser/analysis_decisions.py` | model construction from parser parts | Parser parts have line and column, but lowering often drops them. | Populate model-owned source spans when creating compile-relevant model values. | This is the main span-loss boundary. | One lowering path for authored spans. | Parse tests plus targeted compile-location tests |
| Diagnostic contract | `doctrine/_diagnostics/contracts.py` | `DoctrineDiagnostic` | One `location` and one `excerpt` only. | Add labeled related-location support and any needed caret/excerpt fields per related site. | Multi-site compile failures need honest related context. | Additive `related` contract. | New diagnostic-contract tests |
| Diagnostic formatting | `doctrine/diagnostics.py`, `doctrine/_diagnostics/formatting.py` | `format_diagnostic`, excerpt formatting | Formatter can already render one site. | Render one stable `Related:` section without changing the existing primary-site shape. | The public output must stay readable while becoming richer. | One canonical formatter with related-site rendering. | Formatter tests, smoke checks |
| Shared compile helper boundary | `doctrine/_compiler/diagnostics.py` (new), `doctrine/diagnostics.py` | structured compile construction | Compile families mostly raise raw strings. | Add compiler-owned helpers that turn spans and family data into `CompileError.from_parts(...)`. | Error-family policy belongs with compiler truth, not regex recovery. | Shared compile helper API. | New unit tests per helper family |
| Compile config syntax failures | `doctrine/_compiler/session.py`, `doctrine/project_config.py` | `tomllib.TOMLDecodeError` handling | Compile config TOML errors are path-only today. | Reuse or extract the existing exact TOML excerpt pattern for compile config syntax errors. | `pyproject.toml` syntax should point at the real broken line. | Exact config TOML diagnostic path. | `tests/test_project_config.py`, `make verify-diagnostics` |
| Compile config semantic failures | `doctrine/project_config.py`, `doctrine/_compiler/session.py` | `ProjectConfigError` path | Semantic config errors carry only a message and path. | Add a bounded config-source locator or structured error metadata for Doctrine-owned compile keys and array items. | These are in-scope compile failures and should be exact when Doctrine can prove the key line. | Best-truth config site policy. | `tests/test_project_config.py` |
| Session and import wrappers | `doctrine/_compiler/session.py`, `doctrine/_compiler/indexing.py`, `doctrine/_compiler/support.py` | `prepend_trace`, `ensure_location`, root indexing and import loading | Wrappers often stamp only a file path late, and root indexing can fail before top-level compile wrappers run. | Preserve inner exact spans, add trace only, and move file-only stamping to true no-span cases. | Trace enrichment must not erase primary location truth. | Trace enriches, not replaces, authored sites. | `tests/test_import_loading.py`, compile-location regression tests |
| Indexing and import families | `doctrine/_compiler/indexing.py` | duplicate declarations, import cycles, missing modules, ambiguous modules, enum/render-profile validation | Errors come from raw strings and often show only owner/path. | Migrate these families to shared helpers with exact import or declaration sites and related sites when more than one module participates. | Import failures are one of the worst current location surfaces. | Structured import/index diagnostics. | `tests/test_import_loading.py`, manifest-backed import examples |
| Agent compile families | `doctrine/_compiler/compile/agent.py` | duplicate role field, duplicate typed field, missing role, authored-slot checks | Family knows the bad field key but not the authored line. | Use span-aware helpers and a consistent primary-site policy for duplicate and missing-field errors. | Agent compile errors are common and user-facing. | Structured agent-family helpers. | New agent diagnostic tests, existing compile smoke |
| Output and flow families | `doctrine/_compiler/resolve/outputs.py`, `doctrine/_compiler/compile/outputs.py`, `doctrine/_compiler/compile/final_output.py`, `doctrine/_compiler/flow.py`, `doctrine/_compiler/compile/records.py` | inheritance conflicts, override mismatches, config-key validation, target/shape/schema checks | Many families have strong semantic labels but weak location truth, and some logic is duplicated between compile and flow paths. | Migrate all of these families to shared helpers and keep the same primary/related-site rules across ordinary compile and flow compile paths. | Output inheritance and config mismatches are the clearest multi-site conflict families. | Shared output/flow diagnostic policies. | `tests/test_output_inheritance.py`, final-output tests, flow proof |
| Review and readable families | `doctrine/_compiler/compile/review_contract.py`, `doctrine/_compiler/compile/review_cases.py`, `doctrine/_compiler/compile/reviews.py`, `doctrine/_compiler/compile/readables.py`, `doctrine/_compiler/compile/readable_blocks.py` | review-case exhaustiveness, readable payload shape, guard misuse | Errors are fail-loud but often only carry owner labels. | Migrate these families to shared helpers and classify which ones need related sites versus single primary sites. | Review and readable rules are a large slice of compile diagnostics. | Structured review/readable helpers. | Review tests, readable smoke, new compile-location tests |
| Filesystem and package layout families | `doctrine/_compiler/package_layout.py`, `doctrine/_compiler/compile/skill_package.py` | path normalization and file-read errors | These families often have truthful file paths but no authored prompt line. | Convert them to explicit file-scoped structured diagnostics with a plain explanation that no authored line exists. | Path-only should be an honest exception, not an accidental fallback. | Structured file-scoped compile diagnostics. | Skill-package tests, package-layout coverage |
| Compile message-builder cleanup | `doctrine/_diagnostics/message_builders.py`, `_diagnostics/_message_builders_agents.py`, `_message_builders_authored.py`, `_message_builders_refs.py`, `_message_builders_readables.py`, `_message_builders_reviews.py`, `_message_builders_workflow_law.py` | compile message regex recovery | Compile meaning is reconstructed from strings. | Delete compile-family dependence on these builders after migration, or leave only a narrow unexpected-error fallback during the rollout. | This is the main source of drift and lost structure. | Clean compile cutover. | `make verify-diagnostics`, targeted compile tests |
| Proof and docs | `doctrine/_diagnostic_smoke/compile_checks.py`, `tests/test_parse_diagnostics.py`, `tests/test_import_loading.py`, `tests/test_output_inheritance.py`, `tests/test_decision_attachment.py`, `doctrine/_verify_corpus/manifest.py`, `doctrine/_verify_corpus/runners.py`, `docs/COMPILER_ERRORS.md`, manifest-backed compile-fail examples | Compile proof mostly checks codes and message snippets. | Add exact-location and related-site proof where the surface should now guarantee it. | The public surface is not real until the proof surface can fail when location truth regresses. | Exact-line proof contract. | `make verify-diagnostics`, focused unit tests, `make verify-examples` if manifest proof widens |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - `doctrine/_model/core.py` plus compile-relevant `_model/*` files own the
    source-span truth.
  - `doctrine/_compiler/diagnostics.py` owns structured compile helper
    construction.
  - `doctrine/_diagnostics/contracts.py` and `doctrine/diagnostics.py` remain
    the one public contract and formatter path.
- Deprecated APIs (if any):
  - No public API is being deprecated.
  - Internal use of `CompileError("...")` as the intentional path for known
    compile families becomes legacy and should disappear by the end of the
    rollout.
- Delete list (what must be removed):
  - Compile-family dependence on `_compile_diagnostic_from_message()`.
  - Compile-only regex builders in the `_diagnostics/_message_builders_*.py`
    family once no migrated compile sites depend on them.
  - Any temporary bridge helper that exists only to translate old message
    strings into the new structured helper calls.
- Adjacent surfaces tied to the same contract family:
  - `docs/COMPILER_ERRORS.md`
  - `doctrine/_diagnostic_smoke/compile_checks.py`
  - `tests/test_parse_diagnostics.py`
  - `tests/test_project_config.py`
  - `tests/test_import_loading.py`
  - `tests/test_output_inheritance.py`
  - `tests/test_decision_attachment.py`
  - compile-fail manifest cases plus `doctrine/_verify_corpus/manifest.py` and
    `doctrine/_verify_corpus/runners.py` if richer proof needs manifest support
- Compatibility posture / cutover plan:
  - Preserve shipped error codes.
  - Preserve the broad section order of rendered diagnostics.
  - Add related sites additively under one `Related:` block.
  - Use a clean cutover for migrated compile families.
  - If a temporary bridge is needed during migration, it is internal only and
    deleted in the final cleanup phase.
- Capability-replacing harnesses to delete or justify:
  - None. This plan should not add a wrapper script, UI layer, or runtime
    recovery path.
- Live docs/comments/instructions to update or delete:
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md` only if manifest proof shape changes
  - One short code comment at the model span boundary if the data flow would
    otherwise be hard to follow
  - One short code comment at the session wrapper boundary if the "trace but do
    not overwrite span" rule is not obvious from the code
- Behavior-preservation signals for refactors:
  - `make verify-diagnostics`
  - `tests/test_parse_diagnostics.py`
  - `tests/test_project_config.py`
  - `tests/test_import_loading.py`
  - `tests/test_output_inheritance.py`
  - `tests/test_decision_attachment.py`
  - manifest-backed `compile_fail` corpus runs
  - `make verify-examples` if manifest proof changes

## 6.3 Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Authored refs and wrappers | `doctrine/_model/core.py`, `_model/agent.py`, `_model/io.py`, `_model/review.py` | One shared model-owned source-span field | Prevents one family from getting exact lines while another still drops spans at lowering. | include |
| Parser lowering | `doctrine/parser.py`, `doctrine/_parser/*` | Always populate model-owned spans when lowering compile-relevant authored values | Prevents a second hidden span-loss boundary. | include |
| Compile helper path | `doctrine/_compiler/indexing.py`, `_compiler/resolve/*`, `_compiler/compile/*`, `_compiler/flow.py`, `_compiler/package_layout.py` | One compiler-owned structured diagnostic helper path | Prevents each family from inventing its own location and hint policy. | include |
| Output/config duplication | `doctrine/_compiler/compile/outputs.py`, `_compiler/compile/records.py`, `_compiler/flow.py` | Shared config-key and typed-output diagnostic helpers | Prevents ordinary compile and flow compile from drifting on the same rule family. | include |
| Review families | `doctrine/_compiler/compile/review_contract.py`, `_compiler/compile/review_cases.py`, `_compiler/compile/reviews.py` | Shared review-case and review-contract diagnostic policy | Prevents near-duplicate review code from landing different primary-site rules. | include |
| Message builder cleanup | `doctrine/_diagnostics/message_builders.py`, `_diagnostics/_message_builders_*.py` | Remove compile-family regex recovery | Prevents a permanent parallel compile path. | include |
| Config-source policy | `doctrine/project_config.py`, `doctrine/_compiler/session.py` | One explicit "exact when provable, file/key when not" policy | Prevents fake config line numbers and path-only silent fallback. | include |
| Proof surface | `doctrine/_diagnostic_smoke/compile_checks.py`, `tests/test_*`, `doctrine/_verify_corpus/*`, manifest-backed compile-fail examples | Exact-line and related-site assertions where the new contract guarantees them | Prevents regressions from hiding behind code-only migration. | include |
| Emit diagnostics | `doctrine/_diagnostics/_message_builders_emit.py`, emit error paths | Structured emit diagnostics parity | Valuable later, but not needed to make compile errors truthful now. | defer |
| Editor or UI consumers | `editors/vscode/`, external tooling | IDE rendering of related sites | Not part of the approved scope for this compiler change. | exclude |

<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 - Diagnostic contract, formatter, and compiler helper foundation

Status

- Complete on 2026-04-16.
- Shipped in this pass: related-location contract support, formatter and JSON
  serialization support, compiler diagnostic helpers, and focused formatter
  tests.

Goal

- Establish one public diagnostic shape and one compiler-owned helper path
  before any broad family migration starts.

Work

- Extend the shared diagnostic contract for related sites, keep one formatter,
  and add the compiler-owned helper boundary that later phases will reuse.

Checklist (must all be done)

- Add `DiagnosticRelatedLocation` to
  `doctrine/_diagnostics/contracts.py` with the minimum truthful fields:
  label, location, excerpt, and caret.
- Extend `DoctrineDiagnostic` additively to carry related locations without
  breaking the current primary `location` and `excerpt` path.
- Update `doctrine/diagnostics.py` and
  `doctrine/_diagnostics/formatting.py` to render one stable `Related:`
  section while preserving the current primary-section order.
- Keep parse and emit diagnostics compatible with the shared formatter.
- Add `doctrine/_compiler/diagnostics.py` with shared helpers for:
  primary prompt-authored sites, related sites, file-scoped sites, and
  `CompileError.from_parts(...)` construction.
- Add focused tests for the new contract and formatter behavior, including a
  case with no related sites and a case with labeled related sites.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_parse_diagnostics`
  - `make verify-diagnostics`
- Add focused diagnostic contract and formatter tests for related-site output.

Docs/comments (propagation; only if needed)

- Defer public docs to Phase 5.

Exit criteria (all required)

- The shared diagnostic contract can express one primary site plus labeled
  related sites without ad hoc string encoding.
- The formatter renders the chosen `Related:` shape and parse diagnostics still
  pass unchanged.
- The compiler has one shared helper path ready for later family migrations.

Rollback

- Revert the contract, formatter, and compiler helper scaffold together before
  any family migration lands.

## Phase 2 - Model-owned SourceSpan preservation through parser and model

Status

- Complete.
- Landed in this pass: `SourceSpan` now covers the remaining compile-relevant
  workflow, law, review, route-only, grounding, and readable authored nodes,
  and the parser lowering path now preserves those spans through the nested
  authored structures that route, review, and readable compile failures inspect.
- Added targeted parser proof for representative workflow-law, review, and
  readable nodes so later compile-family migrations can rely on those spans.

Goal

- Make compile-relevant authored values keep their source spans all the way
  from parse lowering into compile-time inspection.

Work

- Add `SourceSpan` to the authored model and thread it through the parser
  lowering path for the refs and wrappers that compile errors need.

Checklist (must all be done)

- Add `SourceSpan` in `doctrine/_model/core.py`.
- Add optional `source_span` fields to compile-relevant core refs and wrappers,
  including import refs, named refs, addressable refs, agent field wrappers,
  review refs, record refs, and other authored values named in the call-site
  audit.
- Update `doctrine/parser.py` and the relevant `_parser/*` lowering modules to
  populate `source_span` from existing parser meta and positioned parts.
- Add any shared model or compiler helper needed to read `SourceSpan` without
  repeating field-unwrapping logic across families.
- Keep imported parse failures and ordinary parse diagnostics unchanged.
- Add one short code comment at the canonical model span boundary that explains
  why `SourceSpan` lives on authored model values instead of in a side map.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_parse_diagnostics`
- Add targeted tests that prove representative authored values now retain
  source-span data through lowering.

Docs/comments (propagation; only if needed)

- Defer public docs to Phase 5.

Exit criteria (all required)

- Compile-relevant authored refs and wrappers can carry `SourceSpan` through
  parsing and lowering.
- Later compile helpers can recover real authored line and column data without
  guessing from owner labels or file paths.
- Parse-location behavior remains unchanged.

Rollback

- Revert the `SourceSpan` model changes and lowering updates together.

## Phase 3 - Config, session, and import-boundary exact-location migration

Status

- Complete on 2026-04-16.
- Landed in this pass: indexing and import-boundary migration for duplicate
  declarations, duplicate enum members, render_profile declaration failures,
  missing imports, ambiguous imports, relative-import root escapes, and import
  cycles, all through shared compiler diagnostics with authored spans.
- Landed in this pass: invalid Doctrine config TOML now points at the exact
  `pyproject.toml` line and excerpt instead of a bare config path.
- Landed in this pass: Doctrine-owned compile-config semantic errors now keep
  bounded key- and array-item truth through `ProjectConfigError`, including
  duplicate configured prompt roots, wrong-kind `additional_prompt_roots`
  values, and invalid configured prompt directories.

Goal

- Make compile-config and import-boundary failures truthful before the rest of
  the compiler families migrate.

Work

- Migrate the config/session/indexing boundary to structured helpers, exact
  config syntax locations, best-truth config semantic locations, and span-safe
  trace handling.

Checklist (must all be done)

- Reuse or extract the exact TOML excerpt builder so compile config syntax
  errors in `CompilationSession` point at the real `pyproject.toml` line.
- Add structured metadata or a bounded source locator for Doctrine-owned
  compile-config semantic errors so `ProjectConfigError` can point at the key
  or array item when Doctrine can prove it.
- Define and implement the explicit fallback policy for config semantic errors:
  exact line when provable, otherwise config file plus key-level context with a
  plain explanation.
- Update `CompilationSession`, import-loading wrappers, and related helpers so
  trace enrichment never overwrites an inner exact span.
- Migrate indexing and import families in `doctrine/_compiler/indexing.py` to
  `doctrine/_compiler/diagnostics.py`, including duplicate declarations,
  duplicate enum/render-profile entries, ambiguous modules, missing modules,
  cyclic imports, and relative-import root escapes.
- Add labeled related sites where import or declaration conflicts involve more
  than one authored location.
- Add one short code comment at the session wrapper boundary that explains the
  "prepend trace but do not overwrite primary span" rule.

Verification (required proof)

- Run:
  - `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading`
  - `make verify-diagnostics`

Docs/comments (propagation; only if needed)

- Defer public docs to Phase 5.

Exit criteria (all required)

- Compile config TOML syntax failures show the exact `pyproject.toml` line.
- Compile config semantic failures follow the chosen best-truth policy and no
  longer silently fall back to a bare path when Doctrine can prove more.
- Import and indexing failures keep exact inner spans where they exist and add
  related sites for real conflict pairs.
- Session and import trace wrappers enrich diagnostics without erasing primary
  location truth.

Rollback

- Revert config/session/indexing migration as one unit if wrapper behavior or
  import diagnostics regress.

## Phase 4 - Authored compile-family migration and policy convergence

Status

- REOPENED (audit found missing code work).
- Missing (code): the remaining compile frontier is still broader than the
  last narrow execution slice. Raw string `CompileError` branches and
  unclassified exceptions still survive across the unresolved compiler,
  resolver, validator, and entrypoint helpers, including `compile/agent.py`,
  `compile/readables.py`, `compile/readable_blocks.py`, `compile/records.py`,
  `compile/workflows.py`, `flow.py`, `resolve/output_schemas.py`,
  `resolve/outputs.py`, `resolve/reviews.py`, `resolve/schemas.py`,
  `resolve/skills.py`, `resolve/io_contracts.py`,
  `resolve/document_blocks.py`, `resolve/analysis.py`, `resolve/agent_slots.py`,
  `validate/agents.py`, `validate/contracts.py`, `validate/display.py`,
  `validate/law_paths.py`, `validate/review_agreement.py`,
  `validate/review_preflight.py`, `validate/review_semantics.py`,
  `validate/review_branches.py`, `validate/outputs.py`,
  `validate/schema_helpers.py`, `validate/addressable_display.py`,
  `indexing.py`, `context.py`, and `support.py`. Both
  `make verify-diagnostics` and `make verify-examples` pass on the current
  tree, so the remaining work is the unclosed migration frontier rather than
  a broken smoke path.
- First family slice landed early: duplicate role fields, duplicate typed
  fields, missing role, and missing abstract authored slots now use
  structured, span-aware compile diagnostics.
- Landed in this pass: workflow-law path resolution and route validation now
  keep exact authored locations on migrated failures, including duplicate
  `route_from` arms with related sites, invalid `route_from` selectors, wrong-
  kind `current artifact` targets, and other law-path failures that already
  had stable message-builder codes.
- Landed in this pass: the next `validate/routes.py` slice now uses
  structured, span-aware diagnostics for abstract route targets, invalid
  `active when` reads, non-routing `handoff_routing` statements, mode values
  outside the declared enum, non-exhaustive `match`, multiple current-subject
  conflicts, `current none` with owned scope, and overlapping branch controls
  such as invalidating the current artifact, ignoring it for truth, or
  overlapping `own only` with `forbid` or `preserve exact`. Two-site route and
  workflow-law conflicts now emit labeled `Related:` locations instead of raw
  owner-label strings.
- Landed in this pass: the shared review-currentness carrier path in
  `resolve/reviews.py` now keeps review-family carrier codes and exact authored
  lines. Review currentness carrier-output failures stay on `E487`,
  trust-surface failures stay on `E488`, and the synthetic review currentness
  paths now preserve source spans instead of dropping back to location-less
  diagnostics.
- Landed in this pass: the next `route_from` slice in `validate/routes.py` and
  `validate/route_semantics_context.py` now uses structured exact-line `E299`
  diagnostics for invalid enum arms, selector values outside the chosen enum,
  unreachable `else`, and non-exhaustive `route_from` blocks. Focused proof
  now locks those line locations directly in `tests/test_compile_diagnostics.py`.
- Landed in this pass: the remaining raw route-helper anchors in
  `validate/routes.py` and `validate/route_semantics_context.py` are now gone.
  Mixed named-section workflow-law bodies always flow through the structured
  helper path, late `match` enum-arm failures and late law-path descendant
  failures now land on exact authored lines, and the final-output route-field
  fallback now raises a structured file-scoped diagnostic at the `route field`
  line instead of a bare `CompileError`.
- Landed in this pass: `DoctrineError.ensure_location()` now upgrades line-aware
  compile failures with source excerpts by default, so migrated families do not
  need one-off excerpt plumbing at every raw `CompileError(...)` site.
- Landed in this pass: the main review compile slice now uses structured,
  span-aware diagnostics in `compile/review_contract.py`,
  `compile/review_cases.py`, and `compile/reviews.py`. Missing review surfaces,
  missing reserved outcome sections, comment-output emission failures, duplicate
  accept gates, overlapping case-selected families, and non-total case families
  now point at the authored review line to fix, with labeled related sites on
  overlap and duplicate-accept conflicts.
- Landed in this pass: the next review resolver slice now uses structured,
  span-aware diagnostics in `resolve/reviews.py` for stable-code inherited
  review conflicts and contract failures. Missing inherited review entries,
  duplicate review item keys, review overrides without inherited parents,
  wrong-kind inherited review overrides, gate-less review contracts, review
  subject wrong-kind failures, and cyclic review inheritance now carry prompt
  lines, with labeled related inherited sites on duplicate and parent-child
  conflicts.
- Landed in this pass: output inheritance conflicts in
  `resolve/outputs.py` now use structured, span-aware diagnostics for
  missing inherited entries, patch-without-parent failures, duplicate child
  keys, and wrong-kind overrides. Those cases now point at the child output
  line to change, show inherited parent sites when the conflict has two real
  authored locations, and preserve `source_span` through output rebinding so
  imported-parent conflicts keep truthful related lines.
- Landed in this pass: workflow inheritance and inherited law patching in
  `resolve/workflows.py` now use structured, span-aware diagnostics for
  cyclic workflow inheritance, duplicate workflow keys, patch-without-parent
  workflow items, missing inherited workflow entries, wrong-kind workflow
  overrides, and the inherited-law named-section rules. Duplicate child keys
  and duplicate inherited law subsections now show `Related:` sites, and
  missing inherited workflow or law sections can point back to the inherited
  parent entry they left out.
- Landed in this pass: readable block structure and document inheritance now
  use structured, span-aware diagnostics in
  `compile/readable_blocks.py`, `resolve/document_blocks.py`, and
  `resolve/documents.py`. Duplicate readable keys now point at the repeated
  authored line with a related first site, block-structure failures such as
  unknown callout kinds, single-line raw or code blocks, empty tables, and
  multiline inline cells now point at the exact authored line when one exists,
  and document patch conflicts now show child and parent locations instead of
  owner-label-only output.
- Landed in this pass: readable guard validation in
  `validate/readables.py` now uses structured diagnostics with the exact
  `when` source line, and the remaining guard-shell compile fallbacks in
  `compile/readable_blocks.py` and `compile/readables.py` now use the same
  readable-block diagnostic contract instead of raw owner-label strings.
- Landed in this pass: the mapped output compile slice in
  `compile/outputs.py` now uses structured, span-aware diagnostics for input
  typed-field completeness, mixed `files` versus `target` / `shape` output
  declarations, incomplete single-artifact outputs, typed-target validation,
  output-target config key failures, and the shipped output `schema:` /
  `structure:` attachment errors. Real conflict pairs now emit labeled
  `Related:` sites for `files` versus `target` / `shape`, duplicate output
  target config keys, and empty attached schemas.
- Landed in this pass: the remaining authored output-file helpers in
  `compile/outputs.py` now use structured, span-aware diagnostics for invalid
  `files:` entry shape, missing output-file `path` or `shape`, non-record
  `must_include` / `current_truth` rows, and invalid `support_files:` entry
  shape or path. Those cases now point at the exact authored line when the
  compiler can prove it instead of falling back to raw-string owner labels.
- Landed in this pass: the stable-code `final_output` slice now uses
  structured, span-aware diagnostics across `resolve/outputs.py`,
  `compile/final_output.py`, `compile/review_contract.py`, and the schema
  validation bridge in `validate/__init__.py`. `E211`, `E212`, `E213`,
  `E215`, `E216`, `E217`, and `E218` now point at the authored `final_output`
  field, the offending output target or file bundle, the retired
  `example_file`, the schema `example:`, or the output-schema declaration line
  as the truthful best-known site, instead of collapsing back to regex-built
  raw strings.
- Landed in this pass: the stable-code output-schema lowering slice now uses
  structured, span-aware diagnostics in `resolve/output_schemas.py` for
  retired `required` / `optional` flags and inline-enum failures. `E227`,
  `E228`, `E229`, `E236`, and `E237` now point at the authored `type:`,
  `values:`, `enum:`, `required`, or `optional` line, with labeled
  `Related:` sites when the failure depends on the conflicting `type:` line.
  The route-final-output resolver in `resolve/outputs.py` was also aligned to
  the new helper signature so route-field final-output proof keeps running on
  the shared lowering path.
- Landed in this pass: the typed-declaration and config-helper slice now uses
  structured, span-aware diagnostics in `compile/records.py` and
  `validate/display.py`. Input config failures now use exact lines for
  non-scalar config rows, duplicate config keys, unknown keys, and missing
  required keys, while input-source and output-target config declaration
  failures now use exact lines for non-string labels, duplicate key
  declarations, and missing local output-shape refs. This pass also restored
  missing nested record spans in `_parser/skills.py` and stopped
  `DoctrineError.ensure_location()` from overwriting an existing imported file
  path with the root prompt path, so imported compile errors can keep the true
  module path once they already know it.
- Landed in this pass: addressable-ref resolution, route-semantic detail
  reads, and skill-package bundle layout now use structured diagnostics in
  `resolve/addressables.py`, `resolve/route_semantics.py`,
  `validate/route_semantics_reads.py`, `package_layout.py`, and
  `compile/skill_package.py`. Stable ref codes `E270`, `E271`, `E272`,
  `E273`, `E274`, `E276`, `E280`, and `E281` now point at the authored ref
  line instead of raw fallback strings, `route.label` and `route.summary`
  still keep `E347` while landing on the real authored read site, and the
  new file-scoped `E304` bundle family now explains invalid skill-package
  companion paths, unreadable bundle files, nested bundled prompts with the
  wrong concrete-agent shape, and path collisions with labeled related source
  files when there is a real second file to show.
- Landed in this pass: generic ref lookup and addressable display titles now
  use structured diagnostics in `resolve/refs.py` and
  `validate/addressable_display.py`. Missing local named-table refs now use
  exact-line `E276`, missing imported refs and import roots now use exact-line
  `E281` and `E280`, generic missing local decl refs now keep a structured
  exact-line fallback when no narrower shipped code exists yet, and the late
  `Input.source` and `Output.target` display checks now use exact-line `E275`
  instead of raw message-only failures.

Goal

- Make structured compile diagnostics the default across the remaining
  prompt-authored and file-scoped compile families.

Work

- Migrate the rest of the compiler onto shared helpers and converge duplicate
  rule families onto one primary-site and related-site policy.

Checklist (must all be done)

- Inventory the remaining `raise CompileError(...)` sites outside the config
  and import boundary and classify each one as exact-line primary,
  multi-site primary plus related, or truthful file-scoped exception.
- Migrate agent compile families in `doctrine/_compiler/compile/agent.py` to
  shared helpers, including duplicate role fields, duplicate typed fields,
  missing role fields, and authored-slot failures.
- Migrate output, final-output, record, and flow families in
  `doctrine/_compiler/resolve/outputs.py`,
  `doctrine/_compiler/compile/outputs.py`,
  `doctrine/_compiler/compile/final_output.py`,
  `doctrine/_compiler/compile/records.py`, and `doctrine/_compiler/flow.py`
  to shared helpers with one consistent policy for duplicate keys, override
  mismatches, inheritance conflicts, config-key failures, and shape/target
  validation.
- Migrate review and readable families in
  `doctrine/_compiler/compile/review_contract.py`,
  `doctrine/_compiler/compile/review_cases.py`,
  `doctrine/_compiler/compile/reviews.py`,
  `doctrine/_compiler/compile/readables.py`, and
  `doctrine/_compiler/compile/readable_blocks.py` to shared helpers with
  explicit classification for which failures need related sites.
- Convert filesystem and package-layout families in
  `doctrine/_compiler/package_layout.py` and
  `doctrine/_compiler/compile/skill_package.py` to structured file-scoped
  diagnostics that plainly explain why no authored line exists.
- Preserve stable error-code identity across all migrated families.
- Keep flow-path and ordinary compile-path diagnostics aligned where the same
  rule family exists in both places.

Verification (required proof)

- Run targeted unit tests for the migrated families, including:
  - `uv run --locked python -m unittest tests.test_output_inheritance tests.test_decision_attachment`
- Run:
  - `make verify-diagnostics`
- Add new focused tests for representative agent, output, review, readable,
  and file-scoped compile failures.

Docs/comments (propagation; only if needed)

- Defer public docs and canonical error examples to Phase 5.

Exit criteria (all required)

- Exact-line compile diagnostics are the default across the migrated
  prompt-authored families.
- Multi-site conflict families emit one primary site plus labeled related
  sites.
- File-scoped exceptions are explicit and truthful rather than accidental
  path-only fallbacks.
- No migrated family still depends on regex message parsing for its final
  user-facing meaning.

Rollback

- Revert a migrated family or tightly related family group as one unit if
  behavior regresses.

## Phase 5 - Proof, docs, corpus contract, and cleanup

Status

- REOPENED (audit found missing code work).
- Missing (code): the shipped `compile_fail` proof still keys on
  `message_contains`, the smoke checks still validate codes and snippets
  instead of exact locations and related sites, the docs still describe the
  older proof surface, and the compile regex bridge is still live even though
  the corpus currently passes under the legacy contract.

Goal

- Lock the new compile-diagnostic behavior as shipped truth and remove the old
  compile recovery path.

Work

- Expand proof to fail on location regressions, update the public docs, and
  delete the temporary compile regex bridge.

Checklist (must all be done)

- Update `doctrine/_diagnostic_smoke/compile_checks.py` so representative
  compile failures assert exact location and related-site output where the new
  contract guarantees it.
- Add or update targeted unit tests for representative compile families,
  including config, import, agent, output, review, readable, and file-scoped
  exceptions.
- Extend `doctrine/_verify_corpus/manifest.py` and
  `doctrine/_verify_corpus/runners.py` so manifest-backed `compile_fail` cases
  can assert exact-line and related-site expectations rather than only message
  snippets.
- Update manifest-backed compile-fail examples to use the richer proof where
  the contract now guarantees exact-line output.
- Update `docs/COMPILER_ERRORS.md` to match the final compile-diagnostic
  contract, including the `Related:` section and the explicit file-scoped
  exception policy.
- Update `examples/README.md` to document the richer `compile_fail` manifest
  proof contract.
- Remove compile-family dependence on `_compile_diagnostic_from_message()` and
  delete compile-only regex builders or temporary bridge helpers that were kept
  only for the migration.
- Remove or rewrite any touched explanatory comments that would otherwise
  describe the old regex-based compile path.

Verification (required proof)

- Run:
  - `make verify-diagnostics`
  - `make verify-examples`
  - `uv run --locked python -m unittest tests.test_project_config tests.test_import_loading tests.test_output_inheritance tests.test_decision_attachment`
- Run any new focused unittest surfaces added during earlier phases.

Docs/comments (propagation; only if needed)

- Sync all touched compile-diagnostic docs and surviving high-leverage comments
  to the final contract in this phase.

Exit criteria (all required)

- The shipped docs, smoke checks, focused tests, and manifest-backed proof all
  agree on the compile diagnostic contract.
- Manifest-backed authored `compile_fail` cases now fail when exact-line or
  related-site guarantees regress.
- No intentional compile family still routes through regex message recovery.
- The repo can point to one shared default pattern for compile diagnostics:
  model-owned `SourceSpan`, compiler-owned structured helpers, additive
  `Related:` rendering, and explicit truthful exceptions for no-line cases.

Rollback

- Restore the prior diagnostic surface only as a full revert, not as a partial
  runtime fallback.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Add focused tests for the shared diagnostic contract, formatting, related
  spans, and representative compile families.
- Add exact-location assertions for cases such as duplicate typed fields,
  missing imported declarations, output override kind mismatch, guard reads
  disallowed source, unknown addressable path, compile-config failures, and
  explicit file-scoped exceptions.

## 8.2 Integration tests (flows)

- Run `make verify-examples` after widening manifest-backed `compile_fail`
  proof so the corpus fails when exact-line or related-site guarantees regress.
- Keep imported parse-failure coverage so compile-side trace enrichment still
  preserves the imported parse location.
- Run `make verify-diagnostics` once wording and rendering settle.
- Keep focused `tests.test_project_config` and `tests.test_import_loading`
  coverage for config and import-boundary location truth.

## 8.3 E2E / device tests (realistic)

- Not applicable beyond CLI-level diagnostic output. Manual smoke checks of a
  few representative failing prompts are enough if a focused automated signal
  is missing.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship as one internal compiler cutover, not as an opt-in flag.
- Keep error-code identity stable so downstream references do not drift even
  when wording and location payload improve.

## 9.2 Telemetry changes

- No product telemetry is planned.
- If useful during implementation, keep only lightweight local audit counts
  such as migrated compile families and remaining no-single-line exceptions.

## 9.3 Operational runbook

- When a new compile family is added later, authors should add it through the
  shared structured helper path and supply the primary location policy up
  front.
- If a future compile error truly has no single authored line, it must say so
  plainly and point to the best-possible file or key-level context.

# 10) Decision Log (append-only)

## 2026-04-16 - Prefer structured compile diagnostics over message parsing

Context

- The compile formatter can already show rich diagnostic data, but compile
  errors rarely supply exact authored spans.
- The current compile path often starts from free-form strings and regexes its
  way back to a code and detail shape.

Options

1. Tighten wording only and keep file-level compile locations.
2. Keep regex message builders but add more `ensure_location(path=...)`.
3. Move compile diagnostics onto a structured span-carrying contract and
   migrate families to it.

Decision

- Choose option 3 as the draft direction for this plan.

Consequences

- The work is broader than a formatter-only tweak.
- The plan must audit compile families exhaustively instead of fixing a few
  examples.
- The diagnostic contract may need a richer public shape for related
  locations.

Follow-ups

- Confirm the North Star before deeper planning.
- Use `research` to harden the full inventory and any true exceptions.

## 2026-04-16 - Use model-owned SourceSpan and compiler-owned compile helpers

Context

- Deep-dive confirmed that parser parts already know line and column, but the
  authored model drops that data before compile validation runs.
- The compiler already owns the family-specific meaning of duplicate fields,
  missing imports, output conflicts, and review failures.
- The current single-location diagnostic contract cannot express both the line
  to change and the related line that caused the conflict.

Options

1. Add a side span map in compiler code and keep model dataclasses unchanged.
2. Keep compile builders under `_diagnostics/` and let them reconstruct family
   meaning from strings plus ad hoc compiler metadata.
3. Put `SourceSpan` on compile-relevant authored model values, extend the
   diagnostic contract with `DiagnosticRelatedLocation`, and move compile
   family construction onto compiler-owned structured helpers.

Decision

- Choose option 3.

Consequences

- Compile location truth now has one owner: the authored model plus compile
  context.
- The compiler gets one shared helper path for primary-site, related-site, and
  file-scoped compile diagnostics.
- Regex compile message builders become migration scaffolding only and must be
  removed from intentional compile-family paths before cleanup is done.
- `pyproject.toml` and filesystem/package-layout failures keep an explicit
  best-truth exception policy instead of pretending every compile error comes
  from a prompt line.

Follow-ups

- Use `phase-plan` to turn the chosen `SourceSpan`,
  `DiagnosticRelatedLocation`, and compiler-helper design into phase checklists.

## 2026-04-16 - Keep file-scoped package truth explicit and preserve route-detail wording

Context

- Skill-package bundle failures still had raw path-only `CompileError(...)`
  branches even after the main prompt-authored compile families moved onto
  structured helpers.
- Addressable refs and route-detail reads already had stable user-facing
  meaning, but the late helpers still rebuilt that meaning from raw strings or
  dropped the old wording when moved too quickly.

Options

1. Keep package errors on generic fallback code and accept path-only conflicts
   with no structured related source file.
2. Reuse the prompt-authored helpers for file-scoped package failures even
   when no authored line exists.
3. Add a dedicated file-scoped package helper, give the bundle family one
   stable code, keep real source-file related sites on collisions, and keep
   the shipped `E347` route-detail wording while moving that family onto exact
   authored read sites.

Decision

- Choose option 3.

Consequences

- File-scoped skill-package failures stay explicit instead of pretending every
  compile error comes from a prompt line.
- Package collisions can now show the first bundled source file when there is
  a real second file to compare.
- The route-detail slice can move to structured exact-line diagnostics without
  forcing corpus or doc churn on the shipped `E347` wording.

Follow-ups

- Finish the remaining late compile, flow, and review-agreement families.
- Let the fresh audit decide whether `E304` needs wider package-surface proof
  before Phase 4 can close.
