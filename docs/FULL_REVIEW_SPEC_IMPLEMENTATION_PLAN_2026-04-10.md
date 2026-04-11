---
title: "Doctrine - Full Review Spec Implementation - Architecture Plan"
date: 2026-04-10
status: active
fallback_policy: forbidden
owners: ["aelaguiz"]
reviewers: []
doc_type: architectural_change
related:
  - docs/REVIEW_SPEC.md
---

# TL;DR

## Outcome

Doctrine ships full first-class `review` support exactly as specified in
`docs/REVIEW_SPEC.md` across the shipped language core, diagnostics, renderer,
manifest-backed examples `43` through `49`, live docs, and the repo-local VS
Code extension, so `review` becomes real shipped language truth instead of a
detached design document and the new review corpus teaches the feature with
the same fully commented style used by examples `30` through `42`, while VS
Code fully colorizes the shipped review surface and supports Ctrl/Cmd-follow
navigation across the review links that belong to the shipped clickable
surface.

## Problem

The repo currently stops at the workflow-law route-only ladder. `review` is
only a non-shipped spec in `docs/REVIEW_SPEC.md`; there is no top-level
`review` declaration in the grammar, no review AST or compiler semantics, no
review-specific diagnostic band, no review example ladder, and no VS Code
adaptation for review declarations or review-owned surfaces. If we land only
part of that surface, Doctrine will have two truths: the frozen review spec
and a smaller accidental implementation.

## Approach

Treat `docs/REVIEW_SPEC.md` as the binding semantic contract and implement it
end to end in the same pattern used for workflow law: widen the grammar,
parser, and model; add compiler-owned review resolution, evaluation, output
agreement, and rendering plus stable diagnostics; add the full commented
example ladder `43` through `49` with targeted invalid cases; align live docs
so the review spec becomes shipped reference instead of proposal drift; and
extend the VS Code adapter and tests to the same shipped surface. No scope
trimming, aliasing to `workflow`, or deferral of the advanced rungs is
allowed.

## Plan

1. Add the review declaration family, AST, reserved agent slot handling, and
   expression and statement surfaces the spec requires.
2. Implement compiler-owned review semantics in one canonical path: contract
   gate export, subject resolution, branch evaluation, carried state,
   currentness carriers, output agreement, rendering, and stable diagnostics.
3. Land the full manifest-backed review ladder `43` through `49`, with prompt
   comments and negative cases that mirror the teaching quality of examples
   `30` through `42`.
4. Update live docs and error references so shipped truth, examples, and docs
   all describe the same review language.
5. Extend the VS Code grammar, resolver, indentation rules, validator,
   snapshots, integration tests, and README to the shipped review surface.
6. Verify with `make verify-examples`, `make verify-diagnostics` when
   diagnostics change, and `cd editors/vscode && make`.

## Non-negotiables

- No scope cuts from `docs/REVIEW_SPEC.md`.
- No top-level `review` implementation that silently drops `block`, carried
  mode and trigger state, multi-subject disambiguation, inheritance, or
  output-agreement semantics.
- `output` remains the one produced-contract primitive; `review` does not
  introduce a packet side channel, shadow carrier, or route-payload model.
- Workflow-law semantics and the existing `30` through `42` ladder must keep
  working unchanged except for truthful docs and index updates.
- Examples `43` through `49` must be fully commented teaching artifacts, not
  terse parser fixtures.
- No compatibility shims, parallel compiler path, or VS Code-only
  interpretation of review syntax.
- VS Code must fully colorize the shipped review surface and support
  Ctrl/Cmd-follow navigation for the shipped clickable review refs.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-10
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. Fresh repo inspection still shows the planned review surface landed in
  the shipped compiler, review corpus, live docs, repo instructions, and VS
  Code mirror through `examples/49_review_capstone`.

## Reopened phases (false-complete fixes)
- None. This fresh audit found no missing or incorrect code work in Section 7
  that requires reopening a completed phase.

## Missing items (code gaps; evidence-anchored; no tables)
- None. Fresh code-verifiable evidence in this environment is clean:
  `./.venv/bin/python -m doctrine.verify_corpus`,
  `./.venv/bin/python -m doctrine.diagnostic_smoke`, `npm run test:unit`,
  `npm run test:snap`,
  `./.venv/bin/python editors/vscode/scripts/validate_lark_alignment.py`, and
  `./.venv/bin/python editors/vscode/scripts/package_vsix.py` all passed.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- `uv sync`, `make verify-examples`, and `make verify-diagnostics` could not be
  rerun in this sandbox because `uv` cannot access `~/.cache/uv`; the direct
  checked-in `.venv` equivalents above passed.
- `cd editors/vscode && make` reached unit and snapshot coverage, then the
  Electron integration runner aborted with `SIGABRT` after locating the local
  VS Code install. Re-run that command outside this sandbox for the full editor
  integration signal.
- Human editor smoke is still worth doing after reinstalling the newest VSIX:
  one `review:` slot, one inherited review section key, one `contract.<gate>`
  ref, one `fields.<semantic_field>` ref, and one review carrier path.
- Manual prose readthrough for the advanced review ladder remains worthwhile as
  polish, but it is no longer a code-completeness gate.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-10
external_research_grounding: done 2026-04-10
deep_dive_pass_2: done 2026-04-10
recommended_flow: phase plan -> implement -> audit implementation
note: This is a warn-first checklist only. It should not hard-block execution.
-->
<!-- arch_skill:block:planning_passes:end -->

<!-- arch_skill:block:reference_pack:start -->
# Reference Pack (folded materials; phase-aligned)
Updated: 2026-04-10

## Inventory
- R1 — Review Spec — docs/REVIEW_SPEC.md

## Binding obligations (distilled; must satisfy)
- `review` ships as a first-class top-level declaration and reserved agent slot,
  not as a workflow alias or standard-library convention. (From: R1)
- `workflow` remains the producer/coordinator law home, `review` becomes the
  critic/reviewer law home, and `output` remains the one produced-contract
  primitive. (From: R1)
- Review outputs remain ordinary `output`s with `trust_surface`, keyed
  conditional output sections, and guarded sections that may read resolved
  review semantic fields only after review resolution. (From: R1)
- Review must ship the full semantic family the spec names: subject and
  subject families, exact contract gate identity, block and reject gates, one
  accept gate, preserved truth assertions, total accept and reject routing,
  carried mode and trigger state, portable currentness, exact output coupling,
  and explicit inheritance and patching. (From: R1)
- Review-contract workflows are restricted `workflow` declarations whose
  exported contract gates are their first-level keyed sections after
  flattening. (From: R1)
- `fields:` is a distinct inherited binding surface with required and
  conditional channels; it is not prose and not a carrier alias. (From: R1)
- Currentness and carried state must reuse shipped output and trust-surface
  rules: `current artifact ... via Output.field`, `current none`, and carried
  state on `comment_output`. (From: R1)
- The reserved review error band `E470` through `E499` is part of the shipped
  surface, not optional follow-up. (From: R1)
- The review ladder `43` through `49` is part of the implementation contract,
  and each rung must stay generic, narrow, and fully commented. (From: R1)
- The remaining holes are implementation-facing only; the plan may not reopen
  language design or cut scope under the pretext of unresolved semantics.
  (From: R1)

## Instruction-bearing structure (only when present; preserve exact or equivalent operational form)
### R1 — Review Spec
1. Freeze the layer split:
   - `workflow` remains the general semantic home for producer and coordinator law.
   - `review` becomes the semantic home for critic and reviewer law.
   - `output` remains the produced-contract primitive.
   - `trust_surface` remains the typed downstream-trust surface.
2. Ship the full review surface model:
   - top-level `review` and `abstract review`
   - reserved agent `review:` slot
   - restricted review-contract workflows
   - reserved `fields`, `on_accept`, and `on_reject` surfaces
   - keyed guarded output sections owned by `output`
3. Preserve the grammar and namespace decisions:
   - review statements include `block`, `reject`, `accept`, `current artifact`,
     `current none`, `carry`, `route`, `when`, and `match`
   - review expressions add only `not in`, `present(...)`, and `missing(...)`
   - allowed names stay limited to declared inputs, enum members, subject
     members, compiler-known review facts, subject-rooted paths, and carried
     fields when live
4. Preserve the semantic model exactly:
   - blocked turns live inside `review`
   - gate evaluation order is fixed
   - outcome routing must be total and deterministic
   - currentness reuses shipped output carriers
   - carried `active_mode` and `trigger_reason` live on `comment_output`
   - semantic-to-output agreement is explicit and staged
5. Preserve explicit reuse:
   - `abstract review` is the inheritance-only form
   - `fields` is inherited explicitly
   - review sections use explicit `inherit` / `override`
   - no hidden merge and no silent section dropping
6. Ship the proof ladder `43` through `49` in order:
   - basic verdict and route coupling
   - handoff-first block gates
   - contract gate export and exact failures
   - current truth and trust surface
   - multi-subject mode and trigger carry
   - inheritance and explicit patching
   - full capstone
- Hard negatives:
  - Do not trim the feature back to a pattern or deferred sketch.
  - Do not introduce a packet side channel, route payload, or shadow trust carrier.
  - Do not move carried mode or trigger state into route syntax.
  - Do not replace explicit review inheritance with a fuzzy merge model.
- Escalation or branch conditions:
  - If implementation reveals mismatch between shipped code and the spec,
    align code to the spec or record an explicit decision-log amendment before
    shipping; do not silently drift.
  - If a proof requirement cannot fit the current manifest lanes, extend the
    verifier minimally and honestly instead of deleting the proof requirement.

## Phase alignment guidance (advisory; core planning commands adopt into Section 7 if needed)
### Global (applies across phases)
- Keep `output` as the one produced-contract primitive. (From: R1)
- Keep the review ladder generic and fully commented. (From: R1)
- Do not reopen resolved design questions under implementation pressure. (From: R1)

### Phase 1 — Review grammar and AST foundation
- Status: complete 2026-04-10
- Current implementation notes:
  - `review` and `abstract review` now parse as top-level declarations, `review:` is a reserved typed agent field, and the grammar admits the full authored review statement family plus `not in`.
  - The AST now carries concrete review config, section, outcome, carry, and match nodes instead of leaving review syntax as draft-only prose.
  - Parser and compiler entry smokes passed under `uv run --locked python`, and the shipped corpus still passes under `make verify-examples`.
- Potentially relevant obligations (advisory):
  - Add the full review declaration and statement surface, not only the easy subset. (From: R1)
  - Add only the narrow expression additions the spec allows. (From: R1)
- References:
  - R1

### Phase 2 — Compiler review semantics, contract export, and inheritance
- Status: in progress 2026-04-10
- Current implementation notes:
  - Concrete agents now compile attached `review:` declarations instead of hard-failing at the attachment point.
  - Review bodies resolve through explicit inheritance accounting for `fields`, ordinary named sections, and reserved `on_accept` / `on_reject` sections.
  - Review-contract workflows now export flattened first-level gate identities, and the compiler rejects contract-law or skills surfaces inside the contract profile.
- Potentially relevant obligations (advisory):
  - Review-contract workflows export first-level keyed gates after flattening. (From: R1)
  - `fields`, `on_accept`, and `on_reject` are reserved inherited surfaces. (From: R1)
  - Concrete agents may not define both `workflow:` and `review:`. (From: R1)
- References:
  - R1

### Phase 3 — Review evaluation, output agreement, and render shape
- Status: in progress 2026-04-10
- Current implementation notes:
  - Review outcomes now validate total currentness and routing, next-owner structural binding, carried-field trust-surface membership, guarded review-output refs, non-exhaustive enum-like matches, and multi-subject disambiguation failures.
  - Resolved review agreement branches now validate verdict, route, currentness,
    carries, reviewed-artifact proof, and guarded output liveness against the
    review-bound `comment_output`, with E495-E499 mappings and representative
    smoke coverage.
  - Exact failing-gate and blocked-gate identity now flow through the resolved
    review gate model.
  - Review semantic addressability for explicit lowercase `contract.*` and
    `fields.*` refs now flows through the compiler-owned addressable path and
    diagnostic smoke coverage.
  - Remaining parse-stage review codes, the manifest-backed review ladder, live
    docs, and editor parity remain to be finished in later phases.
- Potentially relevant obligations (advisory):
  - Gate evaluation order is fixed. (From: R1)
  - Blocked turns live inside `review`. (From: R1)
  - Currentness and carried state stay on declared outputs. (From: R1)
  - Output agreement is staged and exact. (From: R1)
- References:
  - R1

### Phase 4 — Review ladder foundation examples `43` through `46`
- Status: in progress 2026-04-10
- Current implementation notes:
  - `examples/43_review_basic_verdict_and_route_coupling` is now shipped with one positive render contract and three adjacent compile negatives for missing `fields`, missing `on_accept`, and missing `on_reject`.
  - The examples index, docs index, and repo instructions now acknowledge the first shipped review rung and the corpus range through `43`.
- Potentially relevant obligations (advisory):
  - Ship the first four rungs exactly as the spec sequences them. (From: R1)
  - Keep each rung narrow and comment-rich. (From: R1)
- References:
  - R1

### Phase 5 — Advanced review ladder examples `47` through `49`
- Potentially relevant obligations (advisory):
  - Ship multi-subject carry, inheritance, and the full capstone; do not stop
    at the easy rungs. (From: R1)
- References:
  - R1

### Phase 6 — Live docs, error references, and corpus indexes
- Potentially relevant obligations (advisory):
  - Promote the review spec into live shipped truth instead of leaving it as a
    detached draft. (From: R1)
- References:
  - R1

### Phase 7 — VS Code grammar, resolver, tests, and README
- Potentially relevant obligations (advisory):
  - Mirror the shipped review surface in the editor; do not create editor-only
    review semantics. (From: R1)
- References:
  - R1

## Folded sources (verbatim; inlined so they cannot be missed)
### R1 — Review Spec — docs/REVIEW_SPEC.md
~~~~markdown
This revision answers the open review questions as **hard spec decisions**.
It does not trim the feature back to a pattern or a deferred sketch. It treats
the recurring critic bundle as a real Layer 1 surface: blocked review turns,
shared review-contract evaluation, exact failing-gate identity, portable
currentness when the review output is trusted downstream, carried mode /
trigger state, deterministic outcome routing, and explicit
semantic-to-output coupling. [Resolved decisions note](sandbox:/mnt/data/Pasted%20text%283%29.txt)

The design still stays Doctrine-native:

* `workflow` remains the general semantic home for producer / coordinator law
* `review` becomes the semantic home for critic / reviewer law
* `output` remains the produced-contract primitive
* review outputs remain declared `output`s
* currentness reuses the existing `current artifact ... via Output.field` rule
* reuse still follows explicit ordered patching
* no packet side channel, route payload, or shadow trust carrier is introduced

## Full `review` support spec

### 1. Status and layer

`review` is a **new top-level Doctrine declaration** and a **new reserved agent
authored slot**.

It is not a workflow alias. It is not a standard-library convention. It is a
first-class language surface for reviewer / critic turns.

This is the layer decision:

* `workflow` remains the semantic home for producer / coordinator law
* `review` is the semantic home for reviewer / critic law
* `output` remains the only produced-contract primitive
* `trust_surface` remains the typed downstream-trust surface for current truth and carried review state
* no packet, obligation token, or route payload primitive is introduced just to make review work

### 2. Governing split

The review feature family is governed by this split:

* `review` decides **what was reviewed, what failed, what passed, what remains current, and who owns next**
* `output` decides **what the next owner must be able to read and trust from that review**

That keeps the same Doctrine-native split already earned by workflow law:
typed local semantics in the authored surface, typed downstream readability on
`output`.

### 3. What review support must solve

A complete review surface must be able to express:

* one reviewed subject or one reviewed subject family
* one referenced shared review contract
* handoff-first block gates
* ordinary reject gates
* one accept gate
* preserved truth that the reviewer must confirm stayed intact
* assertion-style review checks such as `preserve`, `support_only`, and `ignore`
* exact outcome routing on accept and reject
* typed downstream carried mode / trigger state when multiple branches go to the same next owner
* portable currentness when the review output is supposed to tell the next owner what artifact is current now
* exact coupling between semantic verdict / route / currentness and declared output fields
* exact exported contract gate identity, not just contract pass / fail
* inheritance and patching with the same explicit Doctrine model already used elsewhere

---

## 4. Surface model

### 4.1 New declaration

```prompt
abstract review BaseReview: "Title"
```

```prompt
review Name: "Title"
```

Inherited forms:

```prompt
abstract review ChildBase[ParentBase]: "Title"
```

```prompt
review ChildReview[BaseReview]: "Title"
```

### 4.2 New agent slot

A concrete agent may define:

```prompt
review: SomeReview
```

An agent may **not** define both `workflow:` and `review:` in the same
concrete declaration. Other authored slots are still allowed: `role`,
`read_first`, `inputs`, `outputs`, `skills`, and other already-earned authored
slots. The review body renders where the main semantic body would otherwise
render.

An `abstract review` may not be attached directly to a concrete agent.

### 4.3 Review-contract workflows

`contract:` may reference only a top-level named `workflow` that compiles as a
**review-contract workflow**.

A review-contract workflow is a restricted workflow profile:

* it may contain ordinary preamble prose
* it may contain first-level keyed titled sections
* it may inherit and compose other workflows through ordinary Doctrine rules
* it may **not** contain operational `route`, `current`, `invalidate`, or `carry` semantics

Its exported contract gates are the **first-level keyed workflow section
identities after inheritance/composition flattening**.

So:

```prompt
workflow MetadataReviewContract: "Shared Metadata Review Contract"
    review_basis: "Review Basis"
        ...
    handoff_truth: "Handoff Truth"
        ...
    metadata_specific_checks: "Metadata-Specific Checks"
        ...
```

exposes:

* `contract.review_basis`
* `contract.handoff_truth`
* `contract.metadata_specific_checks`

Those are gate identities, not booleans and not freeform strings.

### 4.4 Supporting output surface

`review` does not replace rich output contracts. Review outputs remain ordinary
`output` declarations. The output-side rules this spec relies on are:

* `trust_surface`
* keyed conditional output sections with stable identities
* guarded sections that may read resolved review semantic fields after review semantics have already been computed

So the keyed conditional section form becomes:

```prompt
failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
    ...
```

not a title-only anonymous `section "..." when ...:` form. That keeps it
Doctrine-native, patchable, and addressable.

### 4.5 Reserved review surfaces

`review` reserves exactly these keyed surfaces:

* `fields`
* `on_accept`
* `on_reject`

Everything else is an ordinary named pre-outcome review section.

---

## 5. Grammar

### 5.1 Review declaration

```ebnf
abstract_review_decl     ::= "abstract" "review" CNAME ["[" review_ref "]"] ":" string NEWLINE
                             INDENT review_item+ DEDENT

review_decl              ::= "review" CNAME ["[" review_ref "]"] ":" string NEWLINE
                             INDENT review_item+ DEDENT

review_item              ::= review_config
                           | pre_outcome_review_section
                           | outcome_review_section
                           | review_inherit
                           | review_override_section

review_ref               ::= name_ref

review_config            ::= subject_stmt
                           | subject_map_stmt
                           | contract_stmt
                           | comment_output_stmt
                           | fields_stmt

subject_stmt             ::= "subject" ":" artifact_subject_expr

subject_map_stmt         ::= "subject_map" ":" NEWLINE
                             INDENT subject_map_entry+ DEDENT

subject_map_entry        ::= enum_member_ref ":" artifact_ref NEWLINE

contract_stmt            ::= "contract" ":" workflow_ref
comment_output_stmt      ::= "comment_output" ":" output_ref

fields_stmt              ::= "fields" ":" NEWLINE
                             INDENT semantic_field_binding+ DEDENT

semantic_field_binding   ::= semantic_field_name ":" field_path NEWLINE

semantic_field_name      ::= "verdict"
                           | "reviewed_artifact"
                           | "analysis"
                           | "readback"
                           | "failing_gates"
                           | "blocked_gate"
                           | "next_owner"
                           | "active_mode"
                           | "trigger_reason"

artifact_subject_expr    ::= artifact_ref
                           | "{" artifact_ref ("," artifact_ref)* "}"

artifact_ref             ::= name_ref
enum_member_ref          ::= name_ref
workflow_ref             ::= name_ref
output_ref               ::= name_ref
```

### 5.2 Review sections and patching

```ebnf
pre_outcome_review_section ::= CNAME ":" string NEWLINE
                               INDENT pre_outcome_review_stmt+ DEDENT

outcome_review_section     ::= "on_accept" ":" [string] NEWLINE
                               INDENT outcome_review_stmt+ DEDENT
                             | "on_reject" ":" [string] NEWLINE
                               INDENT outcome_review_stmt+ DEDENT

review_inherit             ::= "inherit" review_item_key NEWLINE
review_override_section    ::= "override" review_item_key ":" [string] NEWLINE
                               INDENT (semantic_field_binding+
                                     | pre_outcome_review_stmt+
                                     | outcome_review_stmt+) DEDENT

review_item_key            ::= CNAME
                             | "fields"
                             | "on_accept"
                             | "on_reject"
```

Ordinary pre-outcome section keys are stable compiler identities exactly like
workflow section keys. `fields`, `on_accept`, and `on_reject` are reserved
surfaces with fixed semantics.

### 5.3 Review statements

```ebnf
pre_outcome_review_stmt  ::= block_stmt
                           | reject_stmt
                           | accept_stmt
                           | preserve_stmt
                           | support_only_stmt
                           | ignore_stmt
                           | pre_outcome_when_stmt
                           | pre_outcome_match_stmt
                           | prose_line

outcome_review_stmt      ::= current_artifact_stmt
                           | current_none_stmt
                           | carry_stmt
                           | outcome_route_stmt
                           | outcome_when_stmt
                           | outcome_match_stmt
                           | prose_line

block_stmt               ::= "block" gate_label "when" expr
reject_stmt              ::= "reject" gate_label "when" expr
accept_stmt              ::= "accept" gate_label "when" expr

gate_label               ::= string
                           | contract_gate_ref
                           | section_gate_ref

contract_gate_ref        ::= "contract" "." CNAME
section_gate_ref         ::= CNAME

current_artifact_stmt    ::= "current" "artifact" artifact_ref "via" output_field_ref
current_none_stmt        ::= "current none"

carry_stmt               ::= "carry" carried_field "=" expr
carried_field            ::= "active_mode" | "trigger_reason"

output_field_ref         ::= output_ref "." field_path

pre_outcome_when_stmt    ::= "when" expr ":" NEWLINE
                             INDENT pre_outcome_review_stmt+ DEDENT

outcome_when_stmt        ::= "when" expr ":" NEWLINE
                             INDENT outcome_review_stmt+ DEDENT

pre_outcome_match_stmt   ::= "match" expr ":" NEWLINE
                             INDENT pre_outcome_match_case+ DEDENT

outcome_match_stmt       ::= "match" expr ":" NEWLINE
                             INDENT outcome_match_case+ DEDENT

pre_outcome_match_case   ::= review_match_head ":" NEWLINE
                             INDENT pre_outcome_review_stmt+ DEDENT

outcome_match_case       ::= review_match_head ":" NEWLINE
                             INDENT outcome_review_stmt+ DEDENT

review_match_head        ::= union_expr ["when" expr]
                           | "else"

union_expr               ::= expr ("|" expr)*

outcome_route_stmt       ::= "route" string "->" agent_ref ["when" expr]
```

### 5.4 Reused law statements and expression additions

`preserve`, `support_only`, and `ignore` inside `review` reuse the same
path/basis semantics as the workflow-law family:

```ebnf
preserve_stmt            ::= "preserve" preserve_kind preserve_target ["except" path_set_expr] ["when" expr]
support_only_stmt        ::= "support_only" support_target "for" "comparison" ["when" expr]
ignore_stmt              ::= "ignore" ignore_target ["for" ignore_basis_list] ["when" expr]
```

What changes is their role in verdict computation: inside `review`, they are
**check assertions**. A failed assertion causes the containing pre-outcome
review section to fail as a gate once, under that section's identity.

Review expressions add two narrow forms beyond the currently shipped baseline:

* membership negation: `expr not in expr`
* presence predicates: `present(channel_name)` and `missing(channel_name)`

These are limited to review semantics and review-output guard evaluation.

---

## 6. Exact expression namespace

This is now frozen.

### 6.1 Allowed names in review expressions

Review expressions may read only:

1. declared `input` roots attached to the current agent
2. enum members
3. declared subject members by artifact identity
4. compiler-known derived review facts
5. paths rooted in the reviewed subject(s)
6. carried field names inside the active outcome branch, after they have been set

### 6.2 Compiler-known derived review facts

The compiler owns these review-derived facts:

* `contract.passes`
* `contract.failed_gates`
* `contract.first_failed_gate`
* `failed(contract.some_check_key)`
* `passed(contract.some_check_key)`
* `current_truth.from_unnamed_support`
* `current_truth.from_unaccepted_output`
* `present(channel_name)`
* `missing(channel_name)`
* `writes(path_expr)`
* `unclear(...)`

Nothing else is implicit.

If you want values such as `copy_outcome`, `upstream_problem`,
`section_metadata_owed`, or `trigger_reason`, they must come from declared
inputs like `ReviewState`. No implicit `_present` booleans exist.

### 6.3 Output guards

Guards on conditional output sections may read:

* declared input roots
* enum members
* compiler-known derived review facts
* semantic field names resolved by the current review result

They may **not** read arbitrary sibling output fields, workflow-local names, or
review-local ad hoc variables that are not otherwise declared.

Guard timing is fixed:

1. resolve review semantics
2. bind semantic fields and carried option values
3. evaluate guarded output sections
4. validate required output content
5. render

---

## 7. Semantic model

### 7.1 Subject

`subject:` declares the artifact identity or artifact identity set that this
review may review.

A subject member may be only a declared `input` or `output` root. Review does
not compare raw path strings. It compares **normalized artifact identities**:

* declaration kind: `input` or `output`
* fully qualified declaration reference

The host/runtime must normalize any incoming "current artifact" or "reviewed
artifact" reference into one of those declared artifact identities before
review semantics use it.

If `subject` is a set, the review is multi-subject and every reachable terminal
branch must prove **exactly one live subject member**. The compiler accepts
three proof forms:

1. direct currentness proof
   the branch binds exactly one subject member with `current artifact X via Output.field`
2. mode-map proof
   the review declares a total `subject_map` from one enum mode to one subject member,
   and the branch carries exactly one `active_mode` value
3. explicit reviewed-artifact proof
   the branch binds a semantic `reviewed_artifact` value that normalizes to exactly one subject member

If the compiler cannot prove exactly one subject member per terminal branch, it
must raise `E489 REVIEW_SUBJECT_SET_REQUIRES_DISAMBIGUATION`.

### 7.2 Contract

`contract:` may reference only a review-contract workflow as defined above.

The compiler exposes these derived contract facts:

* `contract.passes`
* `contract.failed_gates`
* `contract.first_failed_gate`
* `failed(contract.some_check_key)`
* `passed(contract.some_check_key)`

`contract.passes` is defined **only from the referenced contract workflow**.
It does not include local review law. This avoids circularity with
`accept "..." when contract.passes`.

`contract.failed_gates` is an ordered list of exported contract gate
identities in contract order.

### 7.3 Comment output

`comment_output:` names the one declared `output` this review emits as its
durable verdict / handoff artifact.

Every concrete agent that uses a `review:` must emit that output.

### 7.4 Semantic fields

`fields:` is a **distinct inherited binding surface**. It is not ordinary prose
and it is not a loose config bag.

Its job is to bind compiler-known review channels to relative paths inside
`comment_output`.

These field bindings are relative to `comment_output`.

Required field bindings for concrete reviews:

* `verdict`
* `reviewed_artifact`
* `analysis`
* `readback`
* `next_owner`
* `failing_gates`

Conditionally required field bindings:

* `blocked_gate`: required if any `block` gate exists
* `active_mode`: required if any route branch carries downstream mode
* `trigger_reason`: required if any route branch carries downstream trigger reason

`fields:` does **not** carry currentness by alias. Review currentness still uses
the direct carrier rule `current artifact ... via Output.field`.

### 7.5 Hard language verdicts

`review` has exactly two language verdicts:

* `ReviewVerdict.accept`
* `ReviewVerdict.changes_requested`

These are compiler-owned verdict atoms, not freeform string labels.

A bound `verdict` output field must agree with one of those exact semantic
values and no others.

### 7.6 Gate evaluation order

Gate evaluation is fixed.

1. Evaluate local `block` gates in source order.
2. If one or more `block` gates fire:

   * verdict = `ReviewVerdict.changes_requested`
   * `failing_gates` = all true block gate identities in source order
   * `blocked_gate` = first true block gate identity
   * skip content-review evaluation for this branch

3. If no block gates fired, evaluate explicit local `reject` gates in source order.
4. If no block gates fired, evaluate assertion-style check sections. A
   pre-outcome section containing one or more `preserve`, `support_only`, or
   `ignore` statements fails once under that section's identity if any of those
   assertions fail.
5. If no block gates fired, evaluate the referenced contract workflow and compute:

   * `contract.failed_gates`
   * `contract.first_failed_gate`
   * `contract.passes`

6. If no block gates fired and there are still no local reject failures, no
   assertion-section failures, and no contract failures, evaluate the single
   `accept` gate.
7. Verdict is `ReviewVerdict.accept` iff no failing gates remain. Otherwise it
   is `ReviewVerdict.changes_requested`.

`failing_gates` ordering is fixed:

* true block gates in source order
* true local reject gates in source order
* failed assertion-section identities in authored section order
* `contract.failed_gates` in contract order
* the accept gate identity only if every earlier layer passed but the accept gate still failed

This gives exact gate identity without collapsing the contract layer to one
opaque boolean.

### 7.7 Blocked review turns

Blocked / unclear review turns live **inside** `review`.

They are expressed with `block` gates, not with a separate pre-review workflow.
That keeps the handoff-first stop line inside the same reviewer semantic unit
that ultimately produces verdict, currentness, and next-owner routing.

### 7.8 Outcome routing and placement

A review must define both:

* `on_accept`
* `on_reject`

Those are reserved outcome sections. Only the section matching the resolved
verdict is evaluated for routing, carried state, and currentness.

Statement placement is fixed.

Allowed only outside outcome sections:

* `block`
* `reject`
* `accept`
* `preserve`
* `support_only`
* `ignore`
* prose
* `when`
* `match` used to select pre-outcome check variants

Allowed only inside `on_accept` / `on_reject`:

* `current artifact ... via Output.field`
* `current none`
* `carry ...`
* `route ...`
* prose
* `when`
* `match`

Each terminal outcome branch must produce:

* exactly one route outcome
* exactly one currentness outcome (`current artifact ... via Output.field` or `current none`)
* zero or more carried semantic fields

### 7.9 Route determinism

Route resolution is fixed.

* plain `route` statements with guards are evaluated in source order
* `match` blocks use first-match-wins
* union heads such as `new_lesson | redesigned_lesson` are legal and mean logical disjunction
* guarded match heads such as `bounded_tweak when ReviewState.section_metadata_owed` are legal
* `else` is required unless the compiler can prove the match is exhaustive over the referenced enum or literal set
* after all nested `when` and `match` selection resolves, exactly one route must remain live

### 7.10 Current truth in reviews

`review` reuses the exact shipped portable-currentness rule:

* `current artifact X via Output.field`
* `current none`

No `via current` alias exists.

Every terminal outcome branch must resolve exactly one currentness outcome.

`current artifact X via Output.field` means:

* `X` is authoritative after this review outcome
* `Output.field` is the carrier that tells the next owner this is true

The carrier rules are the same as workflow law:

* the carrier root must be a declared emitted `output`
* the carrier field must exist
* the carrier field must appear in that output's `trust_surface`

`current none` means no durable artifact is carried forward as current after
that outcome and requires no carrier.

### 7.11 Carried downstream mode / trigger reason

Typed downstream mode does **not** travel in route syntax.

It travels on the declared `comment_output` through carried semantic fields:

* `carry active_mode = Enum.member`
* `carry trigger_reason = Enum.member`

Each optional carried channel follows an explicit option model:

* `Some(value)` when the branch carries it
* `None` when the branch does not

No implicit `_present` booleans exist.

Guards and trust-surface clauses use built-ins:

* `present(active_mode)`
* `missing(trigger_reason)`

Those fields must be bound in `fields:` and must appear in the output's
`trust_surface` under the same presence conditions that make them live.

### 7.12 Output agreement rules

Semantic-to-output agreement happens in three layers.

Compile-time agreement checks:

* the bound field exists and is addressable
* required semantic channels are bound
* currentness carriers point at declared output fields in `trust_surface`
* the concrete agent emits `comment_output`
* outcome branches are total

Emit/runtime agreement checks:

* `verdict` must equal the resolved semantic verdict
* `next_owner` must equal the resolved route target
* `current` must equal the resolved artifact identity or explicit none on the declared carrier
* `active_mode` and `trigger_reason` must equal any carried enum values
* `failing_gates` must equal the ordered failing gate list
* `blocked_gate` must equal the first blocking gate identity when one exists
* `reviewed_artifact` must normalize to the reviewed artifact identity

Presence-only authored fields:

* `analysis`
* `readback`

Those two are required for presence and placement, not semantic string
equality. This avoids pretending compile-time rules can prove human review
analysis prose while still keeping the coordination fields compiler-owned.

---

## 8. Inheritance and patching

`review` uses the same explicit ordered patching model as Doctrine workflows.

### 8.1 Abstract reviews and config inheritance

`abstract review` is the inheritance-only form:

```prompt
abstract review BaseReview: "Base Review"
```

Rules:

* `abstract review` may omit `subject`, `subject_map`, `contract`, `comment_output`, `accept`, `on_accept`, and `on_reject`
* `abstract review` may not be attached directly to a concrete agent
* a concrete `review` must satisfy all required surfaces before compilation succeeds

Config inheritance rules:

* `subject`, `subject_map`, `contract`, and `comment_output` inherit by value unless explicitly overridden

### 8.2 Binding surface and section inheritance

`fields` is a reserved inherited binding surface.

Children must account for it explicitly via:

* `inherit fields`
* `override fields:`

Within `override fields:`, bindings are keyed by semantic channel name and
follow the same explicit inherit/override rules as other Doctrine patchable
surfaces.

If a base review declares ordinary named pre-outcome sections or outcome
sections, the child review must account for every inherited section exactly
once via:

* `inherit section_key`
* `override section_key: "Title"`

New sections may be inserted explicitly by key.

No implicit merge exists. No silent section dropping exists.

### 8.3 Why this is required

This is not stylistic. The whole Doctrine direction has been explicit ordered
patching for reusable authored surfaces, and review support should not
introduce a second, fuzzier composition model.

---

## 9. Render semantics

The rendered review section should read naturally, not like a debug dump.

Render order is:

1. title
2. subject summary
3. referenced contract summary
4. named pre-outcome review sections in authored order
5. accept gate
6. routes and carried state on accept
7. routes and carried state on reject
8. outputs section, where the `comment_output` contract renders in ordinary output form

Render significance is fixed:

* ordinary named review section keys are patch identities
* ordinary named review section titles are authored render data
* `fields` does not render
* `on_accept` and `on_reject` may use authored titles or default to "If Accepted" / "If Rejected" when omitted

The renderer may normalize semantic order for readability, but it may not
silently discard authored titles for ordinary named review sections.

If a conditional output section exists, compiled static docs may show the
section shell plus "Rendered only when ...", while runtime required-content
semantics treat the section as present only when its guard is true.

---

## 10. Diagnostics

Review reuses the existing generic route parse diagnostics:

* `E131` missing route label
* `E132` missing route target

Review then reserves `E470`–`E499` for review-specific failures.

Parse-stage:

* `E470` invalid `review` declaration shape
* `E471` illegal statement placement in review body
* `E472` invalid guarded match head
* `E473` invalid or incomplete `fields:` binding surface

Compile-stage:

* `E474` missing `subject`
* `E475` invalid `subject` kind
* `E476` missing `contract`
* `E477` invalid `contract` target or unknown contract gate ref
* `E478` missing `comment_output`
* `E479` concrete agent does not emit `comment_output`
* `E480` concrete agent defines both `workflow:` and `review:`
* `E481` missing `accept`
* `E482` multiple `accept` gates
* `E483` missing reserved outcome section
* `E484` outcome not total
* `E485` multiple routes in one terminal branch
* `E486` multiple currentness outcomes in one terminal branch
* `E487` currentness declared without a valid carrier
* `E488` bound current carrier missing from `trust_surface`
* `E489` subject-set disambiguation failure
* `E490` missing inherited review section
* `E491` duplicate inherited review section accounting
* `E492` unknown overridden review section
* `E493` carried semantic channel is missing a required binding
* `E494` illegal concrete use of `abstract review`

Emit/runtime-agreement stage:

* `E495` semantic verdict does not match bound output field
* `E496` semantic next owner does not match bound output field
* `E497` semantic currentness does not match declared carrier field
* `E498` required carried field omitted when a semantic value exists
* `E499` required conditional output section missing after its guard resolved true

---

## 11. Canonical declarations used by the examples

### 11.1 Verdict, mode, and outcome enums

```prompt
enum ReviewVerdict: "Review Verdict"
    accept: "accept"
    changes_requested: "changes_requested"

enum MetadataPassMode: "Metadata Pass Mode"
    lesson_title: "lesson_title"
    section: "section"

enum MetadataTriggerReason: "Metadata Trigger Reason"
    new_lesson: "new_lesson"
    redesigned_lesson: "redesigned_lesson"

enum CopyOutcome: "Copy Outcome"
    new_lesson: "new_lesson"
    redesigned_lesson: "redesigned_lesson"
    bounded_tweak: "bounded_tweak"
```

### 11.2 Shared inputs and contract workflows

```prompt
input ProducerHandoff: "Producer Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the current producer handoff facts, including whether the handoff is invalid and what artifact identity it names as current."

input ReviewState: "Review State"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use current review-state facts such as copy outcome, whether the problem is upstream, whether section metadata is still owed, whether scope leaked, and whether a metadata trigger reason is present."

input ApprovedBoundary: "Approved Boundary"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the approved boundary facts whose exact scope must remain stable during review."

workflow CopyReviewContract: "Copy Review Contract"
    handoff_truth: "Handoff Truth"
        "Confirm the producer handoff is complete enough to identify the reviewed artifact honestly."

    copy_specific_checks: "Copy-Specific Checks"
        "Confirm the copy pass stayed inside the allowed title and boundary rules."

workflow MetadataReviewContract: "Metadata Review Contract"
    handoff_truth: "Handoff Truth"
        "Confirm the producer handoff names the exact metadata artifact now under review."

    metadata_specific_checks: "Metadata-Specific Checks"
        "Confirm the metadata pass stayed inside the intended scope and wording rules."

output CopyManifest: "Copy Manifest"
    target: File
        path: "unit_root/_authoring/COPY_MANIFEST.md"
    shape: MarkdownDocument
    requirement: Required

output LessonTitleMetadata: "Lesson Title Metadata"
    target: File
        path: "unit_root/_authoring/LESSON_TITLE_METADATA.json"
    shape: JsonObject
    requirement: Required

output SectionMetadata: "Section Metadata"
    target: File
        path: "unit_root/_authoring/SECTION_METADATA.json"
    shape: JsonObject
    requirement: Required
```

### 11.3 Shared review output and concrete owners

```prompt
output CriticVerdictAndHandoffOutput: "Critic Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    verdict: "Verdict"
        "Say `accept` or `changes_requested`. No other verdict values."

    reviewed_artifact: "What You Reviewed"
        "Name the exact artifact identity you reviewed."
        "If review stopped before content review, name the producer handoff comment and say content review did not start."

    analysis_performed: "Analysis Performed"
        "Put the actual review analysis here."

    output_contents_that_matter: "Output Contents That Matter"
        "Put the actual reviewed contents, preserved constraints, or concrete failing details that still matter now."

    current_artifact: "Current Artifact"
        "Name the current artifact when one remains current after this review outcome."

    next_owner: "Next Owner"
        "Name the next owner for the same issue."

    active_mode: "Active Mode"
        "Name the active downstream mode when the next owner needs one."

    trigger_reason: "Trigger Reason"
        "Name the trigger reason when the next owner needs it."

    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
        failing_gates: "Failing Gates"
            "Name the exact failing gates in order."

        failing_gate_if_blocked: "Failing Gate If Blocked"
            "If the review was blocked before content review, name that first blocking gate. Otherwise say plainly that no blocking gate applies."

    trust_surface:
        current_artifact when present(current_artifact)
        active_mode when present(active_mode)
        trigger_reason when present(trigger_reason)

    standalone_read: "Readable On Its Own"
        "A downstream owner should be able to read this comment alone and know the verdict, see the real review analysis and output readback, know what artifact is current now when one is current, know any carried mode or trigger reason, know what failed if it did not pass, and know who owns next."

agent ReviewLead:
    role: "Own explicit reroutes when specialist review work cannot continue cleanly."
    workflow: "Instructions"
        "Take back the same issue when review cannot hand off to a more specific owner honestly."

agent CopyAuthor:
    role: "Own copy revisions when review sends copy work back."
    workflow: "Instructions"
        "Revise the current copy artifact when review requests copy-local changes."

agent MetadataAuthor:
    role: "Own metadata revisions when review sends metadata work back."
    workflow: "Instructions"
        "Revise the current metadata artifact when review requests metadata changes."
```

---

## 12. Canonical positive example: `CopyReview`

```prompt
review CopyReview: "Copy Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.failing_gate_if_blocked
        next_owner: next_owner
        active_mode: active_mode
        trigger_reason: trigger_reason

    start_review: "Start Review"
        block contract.handoff_truth when ProducerHandoff.invalid
        reject "Current artifact does not match the copy manifest." when ProducerHandoff.current_artifact != CopyManifest
        reject "Unnamed support was treated as current truth." when current_truth.from_unnamed_support
        reject "Unaccepted output was treated as current truth." when current_truth.from_unaccepted_output

    contract_checks: "Contract Checks"
        preserve exact ApprovedBoundary.exact_scope_boundary
        reject contract.copy_specific_checks when writes(LessonTitleMetadata.title)
        accept "Shared copy review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact

        match ReviewState.copy_outcome:
            CopyOutcome.new_lesson:
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = MetadataTriggerReason.new_lesson
                route "Accepted copy needs a lesson-title metadata pass." -> MetadataAuthor

            CopyOutcome.redesigned_lesson:
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = MetadataTriggerReason.redesigned_lesson
                route "Accepted copy needs a lesson-title metadata pass." -> MetadataAuthor

            CopyOutcome.bounded_tweak when ReviewState.section_metadata_owed:
                carry active_mode = MetadataPassMode.section
                route "Accepted copy needs a section metadata pass." -> MetadataAuthor

            CopyOutcome.bounded_tweak:
                route "Accepted bounded tweak returns to ReviewLead." -> ReviewLead

            else:
                route "Accepted copy still leaves the boundary unclear, so keep the issue on ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact

        route "Return copy-local defects to CopyAuthor." -> CopyAuthor when ReviewState.upstream_problem == false
        route "Return upstream defects to ReviewLead." -> ReviewLead when ReviewState.upstream_problem
```

### Intended render

```md
## Copy Review

Review the current copy manifest and the producer handoff.

Block first if the producer handoff is too vague to tell what was really reviewed.

Reject if the current artifact does not match the copy manifest.
Reject if unnamed support was treated as current truth.
Reject if unaccepted output was treated as current truth.

Preserve the exact approved scope boundary.

Reject if the copy pass rewrote the lesson-title metadata outside the allowed contract.
Accept only if the shared copy review contract passes.

If accepted:
- the current artifact remains the copy manifest
- new lesson -> Metadata Author, carry `lesson_title` and `new_lesson`
- redesigned lesson -> Metadata Author, carry `lesson_title` and `redesigned_lesson`
- bounded tweak with section metadata still owed -> Metadata Author, carry `section`
- bounded tweak with no metadata owed -> Review Lead
- unclear accepted boundary -> Review Lead

If rejected:
- the current artifact remains the copy manifest
- copy-local defects go to Copy Author
- upstream defects go to Review Lead
```

This is the recurring semantic family the corpus keeps spelling out in prose
today: handoff-first stop line, exact current artifact, preserved upstream
truth, exact failing gates, current artifact readback, and next-owner routing.

---

## 13. Canonical positive example: `MetadataReview`

This example proves the fully-defined support for a multi-subject review family
and typed downstream mode.

```prompt
review MetadataReview: "Metadata Review"
    subject: {
        LessonTitleMetadata,
        SectionMetadata
    }
    subject_map:
        MetadataPassMode.lesson_title: LessonTitleMetadata
        MetadataPassMode.section: SectionMetadata
    contract: MetadataReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.failing_gate_if_blocked
        next_owner: next_owner
        active_mode: active_mode
        trigger_reason: trigger_reason

    start_review: "Start Review"
        block "Current mode is implicit." when unclear(ReviewState.active_mode)
        block "Current artifact is implicit." when unclear(ProducerHandoff.current_artifact)
        block "Lesson-title trigger reason is implicit." when ReviewState.active_mode == MetadataPassMode.lesson_title and unclear(ReviewState.trigger_reason)
        reject "Producer handoff named an artifact outside the metadata review family." when ProducerHandoff.current_artifact not in subject

    metadata_checks: "Metadata Checks"
        reject contract.metadata_specific_checks when ReviewState.scope_leak
        accept "Shared metadata review contract passes." when contract.passes

    on_accept: "If Accepted"
        match ReviewState.active_mode:
            MetadataPassMode.lesson_title:
                current artifact LessonTitleMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = ReviewState.trigger_reason
                route "Accepted lesson-title metadata returns to ReviewLead." -> ReviewLead

            MetadataPassMode.section:
                current artifact SectionMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.section
                route "Accepted section metadata returns to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        match ReviewState.active_mode:
            MetadataPassMode.lesson_title:
                current artifact LessonTitleMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.lesson_title
                carry trigger_reason = ReviewState.trigger_reason
                route "Return lesson-title metadata defects to MetadataAuthor." -> MetadataAuthor

            MetadataPassMode.section:
                current artifact SectionMetadata via CriticVerdictAndHandoffOutput.current_artifact
                carry active_mode = MetadataPassMode.section
                route "Return section metadata defects to MetadataAuthor." -> MetadataAuthor
```

This closes the multi-subject and typed-downstream-mode gap cleanly:

* `subject` is a real artifact set
* `subject_map` proves how mode selects the live subject
* route syntax stays narrow
* mode travels on the output, not on the route
* the next owner does not have to guess which metadata branch is live

---

## 14. Inheritance example

```prompt
abstract review BaseArtifactReview: "Artifact Review"
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        blocked_gate: failure_detail.failing_gate_if_blocked
        next_owner: next_owner

    common_gates: "Common Gates"
        block "Producer handoff is incomplete." when ProducerHandoff.invalid
        reject "Unnamed support was treated as current truth." when current_truth.from_unnamed_support
        reject "Unaccepted output was treated as current truth." when current_truth.from_unaccepted_output


review CopyReview[BaseArtifactReview]: "Copy Review"
    subject: CopyManifest
    contract: CopyReviewContract

    inherit fields
    inherit common_gates

    copy_specific: "Copy-Specific Checks"
        preserve exact ApprovedBoundary.exact_scope_boundary
        reject contract.copy_specific_checks when writes(LessonTitleMetadata.title)
        accept "Shared copy review contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact
        route "Accepted copy returns to ReviewLead." -> ReviewLead

    on_reject: "If Rejected"
        current artifact CopyManifest via CriticVerdictAndHandoffOutput.current_artifact
        route "Return copy defects to CopyAuthor." -> CopyAuthor
```

This is the Doctrine-native reuse story: explicit inheritance, explicit ordered
patching, no hidden merge.

---

## 15. Invalid examples

### 15.1 Incomplete `fields:` binding surface

```prompt
review InvalidReview: "Invalid Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        reviewed_artifact: reviewed_artifact
        next_owner: next_owner

    start_review: "Start Review"
        accept "Shared copy review contract passes." when contract.passes

    on_accept: "If Accepted"
        route "Route accepted copy." -> ReviewLead

    on_reject: "If Rejected"
        route "Route rejected copy." -> CopyAuthor
```

**Error:** `E473 invalid or incomplete fields binding surface`

### 15.2 Agent defines both workflow and review

```prompt
agent InvalidCritic:
    role: "Invalid."
    workflow: SomeWorkflow
    review: CopyReview
```

**Error:** `E480 concrete agent defines both workflow and review`

### 15.3 Current truth without a valid carrier

```prompt
review InvalidReview: "Invalid Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    start_review: "Start Review"
        accept "Contract passes." when contract.passes

    on_accept: "If Accepted"
        current artifact CopyManifest via current
        route "Route accepted copy." -> ReviewLead

    on_reject: "If Rejected"
        route "Route rejected copy." -> CopyAuthor
```

**Error:** `E487 currentness declared without a valid carrier`

### 15.4 Non-total accept routing

```prompt
review InvalidReview: "Invalid Review"
    subject: CopyManifest
    contract: CopyReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    start_review: "Start Review"
        accept "Contract passes." when contract.passes

    on_accept: "If Accepted"
        match ReviewState.copy_outcome:
            CopyOutcome.new_lesson:
                route "Route accepted copy." -> MetadataAuthor

    on_reject: "If Rejected"
        route "Route rejected copy." -> CopyAuthor
```

**Error:** `E484 outcome not total`

### 15.5 Multi-subject review without disambiguation

```prompt
review InvalidMetadataReview: "Invalid Metadata Review"
    subject: {
        LessonTitleMetadata,
        SectionMetadata
    }
    contract: MetadataReviewContract
    comment_output: CriticVerdictAndHandoffOutput

    fields:
        verdict: verdict
        reviewed_artifact: reviewed_artifact
        analysis: analysis_performed
        readback: output_contents_that_matter
        failing_gates: failure_detail.failing_gates
        next_owner: next_owner

    start_review: "Start Review"
        accept "Contract passes." when contract.passes

    on_accept: "If Accepted"
        route "Route accepted metadata." -> ReviewLead

    on_reject: "If Rejected"
        route "Route rejected metadata." -> MetadataAuthor
```

**Error:** `E489 subject-set disambiguation failure`

---

## 16. Corpus build plan

This is the ladder to actually check in.

It is deliberately shaped like the existing `30` through `42` workflow-law and
guarded-output corpus: each example proves **one new review idea at a time**,
keeps public examples generic rather than product-specific, keeps `output` as
the produced-contract primitive, and makes the new `review` surface carry real
compiler-owned semantics instead of merely renaming prose.

One planning correction matters here: the repo already ships `39` through `42`,
so the review ladder should use the next free range. This plan therefore maps
the new review corpus to `43` through `49`.

### 16.1 Fixed conventions for the whole ladder

These examples assume the following decisions are frozen:

* `review` is a top-level declaration and a reserved agent slot.
* `contract:` points to a review-contract workflow: a top-level `workflow` whose first-level keyed sections export gate identities.
* `fields:` binds compiler-owned review channels to concrete paths on `comment_output`.
* `ReviewVerdict.accept` and `ReviewVerdict.changes_requested` are hard language verdicts.
* `current artifact ... via Output.field` is reused exactly as the portable-currentness carrier form.
* guarded output sections may read bound semantic fields such as `verdict` or `active_mode`, but only after review resolution.
* `on_accept` and `on_reject` are mandatory outcome sections.
* outcome routing is first-match-wins and must be total.
* `output` still owns the readable downstream contract: exact fields, trust surface, standalone-read promise, and conditional failure sections.
* each rung should ship with targeted `INVALID_*` negatives that prove the new validation surface added by that rung.

### 16.2 Example `43_review_basic_verdict_and_route_coupling`

What this proves:

* the smallest first-class `review`
* one reviewed subject
* one shared review contract
* one accept gate
* one reject gate
* one `comment_output`
* verdict, failing-gates, and next-owner coupling

Minimum prompt shape:

* one generic contract workflow with two exported gates such as `completeness` and `clarity`
* one file input such as `DraftSpec`
* one comment output that binds `verdict`, `reviewed_artifact`, `analysis_performed`, `output_contents_that_matter`, `next_owner`, and guarded `failure_detail.failing_gates`
* one producer owner and one accepted-work owner
* one `review` that rejects an obviously bad local condition and accepts on `contract.passes`

Minimum render commitments:

* the rendered review must read like a real reviewer instruction surface, not a compiler dump
* the rendered output contract must show `Failure Detail` only conditionally on `ReviewVerdict.changes_requested`
* the rendered prose must make the accept and reject next-owner consequences visible

Required negatives:

* missing required `fields:` binding
* missing `on_accept`
* missing `on_reject`

### 16.3 Example `44_review_handoff_first_block_gates`

What this proves:

* `block`
* blocked review turns live inside `review`
* `blocked_gate`
* handoff-first stop line before content review

Minimum prompt shape:

* add `ProducerHandoff`
* add a guarded `failing_gate_if_blocked` field under `failure_detail`
* block on incomplete producer handoff
* reject if the handoff names the wrong current artifact
* still use one durable review comment output

Minimum render commitments:

* the review prose must say clearly that handoff quality is checked first
* the output contract must explain that blocked review still produces `changes_requested`
* the output contract must explain that `reviewed_artifact` names the handoff comment when content review never started

Required negatives:

* missing `blocked_gate` binding when a `block` gate exists
* illegal `block` placement inside `on_accept` / `on_reject`

### 16.4 Example `45_review_contract_gate_export_and_exact_failures`

What this proves:

* `contract.some_check_key`
* exported contract gate identities
* exact failing-gate naming from the shared contract family

Minimum prompt shape:

* one contract workflow with at least three exported keyed sections
* one review that explicitly rejects on `contract.<gate>`
* one output whose `failing_gates` field promises exact exported contract-gate identities

Minimum render commitments:

* the review prose should surface the named contract gates as actual checks, not opaque contract plumbing
* the output prose must make it clear that shared-contract failures use exported gate identities

Required negatives:

* unknown `contract.some_check_key`
* contract target that is not a review-contract workflow

### 16.5 Example `46_review_current_truth_and_trust_surface`

What this proves:

* `current artifact ... via Output.field`
* `trust_surface`
* semantically coupled current artifact readback on the review output

Minimum prompt shape:

* one review comment output with a dedicated carrier field such as `use_now` or `current_artifact`
* that carrier field listed in `trust_surface`
* both `on_accept` and `on_reject` bind the current artifact through the review output

Minimum render commitments:

* the review prose must say what remains current after accept and reject
* the output render must show the trusted carrier field under `trust_surface`
* the standalone-read promise must name current truth explicitly

Required negatives:

* currentness with an invalid carrier path
* carrier field not listed in `trust_surface`
* current artifact rooted outside declared review subjects / emitted outputs

### 16.6 Example `47_review_multi_subject_mode_and_trigger_carry`

What this proves:

* subject sets
* branch disambiguation through `subject_map` and `match`
* carried `active_mode`
* carried `trigger_reason`
* same next owner, different live mode

Minimum prompt shape:

* one mode enum
* one trigger-reason enum
* two reviewed subject artifacts
* `subject_map` tying the mode enum to the subject set
* one review output with optional `active_mode` and `trigger_reason` fields in `trust_surface` using `present(...)`
* accept and reject branches that carry different combinations of mode and trigger

Minimum render commitments:

* the prose must show how each mode selects a different current artifact
* the output render must show that `active_mode` and `trigger_reason` are trusted only when present

Required negatives:

* subject set without disambiguation proof
* carried `active_mode` without a bound `fields:` entry
* carried `trigger_reason` without a bound `fields:` entry

### 16.7 Example `48_review_inheritance_and_explicit_patching`

What this proves:

* `abstract review`
* explicit `inherit`
* explicit child sections
* no hidden merge model

Minimum prompt shape:

* one `abstract review` base with `comment_output`, `fields`, and shared gates
* one concrete child review with `subject`, `contract`, `inherit fields`, and inherited common gates
* one local child-only section plus concrete `on_accept` / `on_reject`

Minimum render commitments:

* the final render must read like one coherent review surface
* inherited shared review gates must appear exactly once in the final render
* local child law must appear in authored order, not hidden-parent order

Required negatives:

* missing inherited review section
* duplicate inherited review section accounting
* illegal concrete use of `abstract review`

### 16.8 Example `49_review_capstone`

What this proves:

* blocked review turns live inside `review`
* exact contract gates
* `support_only`
* `ignore ... for rewrite_evidence`
* `preserve`
* multi-subject review
* carried `active_mode`
* carried `trigger_reason`
* `current artifact ... via Output.field`
* `current none` for blocked handoff-first outcomes
* one durable review comment output that stays readable and trusted downstream

Minimum prompt shape:

* a multi-subject metadata-like family with one review-contract workflow
* `ProducerHandoff`, `ReviewState`, current subject artifacts, one preserved upstream structure input, and one comparison-only advisory input
* one review output with verdict, reviewed artifact, analysis, readback, current artifact, next owner, active mode, trigger reason, and guarded failure detail
* block on invalid handoff or unclear mode
* reject on contract gates and local scope violations
* `support_only` comparison help and `ignore ... for rewrite_evidence` branches
* `on_accept` branches that carry current artifact plus typed downstream state
* `on_reject` branches that either route blocked work with `current none` or route concrete defects with current artifact still explicit

Minimum render commitments:

* the render must read like one coherent reviewer surface, not like pasted sections from unrelated features
* blocked branches must clearly state that no durable artifact is current
* accepted and rejected branches must clearly state what remains current, what mode is active, and who owns next
* the output contract must remain readable on its own and faithful to the trust surface

Required negatives:

* illegal mixture of `current none` and `current artifact` in one terminal branch
* illegal use of pre-outcome statements inside outcome sections
* guarded review-output section that reads a disallowed name

### 16.9 Why this ladder is the right progression

This is the right order to implement and prove:

* `43` proves that `review` is real and not just workflow prose with a new name.
* `44` proves blocked turns live inside `review`.
* `45` proves contract gate exposure and exact `failing_gates`.
* `46` proves review reuses the shipped portable-currentness carrier rule.
* `47` proves mode-carry and multi-subject disambiguation.
* `48` proves reuse and explicit patching.
* `49` proves the full bundle together.

That mirrors the example-first design discipline already explicit in Doctrine:
prove one idea at a time, keep the runtime Markdown natural, and only widen the
language where the compiler actually owns the meaning.

## 17. The one-sentence version

**`review` is a first-class critic surface whose job is to bind reviewed subject, review contract, exact gates, portable current truth, next-owner routing, and typed verdict/handoff readback into one compiler-owned semantic unit, with `output` still serving as the canonical downstream contract.**

## 18. Resolved audit decisions

The current audit pressure is now answered directly in the spec:

* `review` is treated as a full Layer 1 primitive, not a narrow alias
* blocked / unclear review turns live inside `review`
* portable currentness is part of `review`, but it reuses the exact existing `via Output.field` carrier rule
* contract workflows export first-level keyed gate identities after flattening
* contract evaluation exposes `contract.passes`, `contract.failed_gates`, `contract.first_failed_gate`, `failed(...)`, and `passed(...)`
* `fields:` is a distinct inherited binding surface, not a prose section and not a hidden carrier alias
* guarded review-output sections may read resolved semantic fields such as `verdict`
* multi-subject reviews must prove exactly one live subject member per terminal branch through direct currentness, `subject_map`, or explicit reviewed-artifact proof
* `abstract review` is the inheritance-only form for reusable review bases
* optional carried state uses `present(...)` / `missing(...)` instead of implicit `_present` booleans
* semantic-to-output agreement is explicit and staged

## 19. Remaining holes

There are no longer any **big semantic holes** in this draft. The remaining
work is implementation-facing and documentation-facing rather than feature-shape
ambiguity.

Implementation-facing follow-through:

* the compiler and renderer need one executable flattening algorithm for exported review-contract gates after workflow inheritance/composition
* the host/runtime needs a small contract for normalizing incoming artifact references into Doctrine artifact identities before review evaluation starts
* the verifier and error catalog need the final concrete mapping from this spec's review semantics onto checked examples, parser/compiler ownership, and emitted mismatch checks

Documentation-facing follow-through:

* keep public examples generic and avoid drifting back to product-specific names once this spec is published as live reference

Those are real implementation tasks, but they are no longer large unresolved
language-design questions.
~~~~
<!-- arch_skill:block:reference_pack:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

After this change, the repo can parse, compile, render, document, verify, and
editor-highlight the full `review` surface described in `docs/REVIEW_SPEC.md`
without hidden exceptions: manifest-backed examples `43` through `49` pass,
their invalid siblings prove the reserved `E470` through `E499` review
diagnostic band where applicable, no live doc still describes `review` as
non-shipped, and the VS Code extension recognizes `review` declarations and
review-owned authoring surfaces as part of the shipped language with full
colorization plus Ctrl/Cmd-follow navigation for the shipped clickable review
refs.

If any major semantic family from the spec remains unimplemented, is silently
narrowed, or survives only as prose convention, this claim is false and the
plan is incomplete.

## 0.2 In scope

- Add shipped grammar support for `review`, `abstract review`, review
  sections, review statements, review expression additions, and the reserved
  agent `review:` slot semantics.
- Add AST and compiler support for review declarations, review inheritance,
  review-contract workflow validation and gate export, review semantic-field
  bindings, review branch evaluation, currentness, carried state, total
  routing, and output-agreement checks.
- Add stable diagnostics and docs coverage for the review-specific error band
  `E470` through `E499`.
- Add the full manifest-backed example ladder `43_review_basic_verdict_and_route_coupling`
  through `49_review_capstone`, including prompt comments and targeted invalid
  prompts.
- Update live docs so `docs/REVIEW_SPEC.md` becomes live shipped reference,
  then align the docs index, examples index, README surfaces, and I/O/error
  references to that reality.
- Extend the repo-local VS Code extension so highlighting, indentation, and
  Ctrl/Cmd-followable Go to Definition follow the shipped review surface
  rather than stopping at workflow law, and full review syntax colorization
  lands with the same ship.

## 0.3 Out of scope

- Inventing new product capability beyond the frozen review spec, including
  packets, route payloads, new output primitives, review-only transport
  shims, or speculative runtime orchestration.
- Narrowing the shipped review surface to a smaller MVP that omits the later
  ladder rungs, advanced diagnostics, or the fully commented example-teaching
  surface.
- Recasting review as mere workflow prose, a standard-library convention, or a
  verifier-only pattern instead of a first-class language primitive.
- Adding a full language server, new editor architecture, or a second parser
  outside the existing repo-local VS Code adapter.
- Introducing non-repo rollout systems, telemetry infrastructure, or product
  ops surfaces unrelated to the local language/tooling ship.

## 0.4 Definition of done (acceptance evidence)

- `uv sync` completes so the repo environment is current.
- `make verify-examples` passes with the shipped corpus extended through
  examples `43` through `49`.
- `make verify-diagnostics` passes if diagnostics or the diagnostic smoke
  surface changed.
- `cd editors/vscode && make` passes if the editor adapter changed.
- Examples `43` through `49` each have manifest-backed proof and checked-in
  refs, and their prompts are fully commented in the same teaching style as
  examples `30` through `42`.
- `docs/REVIEW_SPEC.md`, `docs/README.md`, `examples/README.md`, root
  `README.md`, `docs/COMPILER_ERRORS.md`, and any other touched live docs tell
  the same story about shipped review support.
- The VS Code extension fully colorizes the shipped review surface and the
  supported review refs are Ctrl/Cmd-followable in the same way the current
  shipped clickable workflow-law refs are.

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks.
- No dual sources of truth between `docs/REVIEW_SPEC.md` and `doctrine/`.
- No shadow review semantics in the verifier, renderer, or editor adapter that
  do not also exist in the compiler truth path.
- `output` remains the one produced-contract primitive.
- `review` and `workflow` are distinct top-level semantic homes, and a
  concrete agent may not define both.
- Examples stay generic, comment-rich, and one-new-idea-per-rung.
- Review authoring in VS Code is not allowed to ship half-finished: the
  shipped review syntax must be colorized and the shipped clickable review refs
  must remain Ctrl/Cmd-followable.
- Existing workflow-law behavior remains stable unless a deliberate live-doc
  correction is needed to describe what already ships.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Ship the full frozen review spec without scope cuts or silent semantic
   downgrades.
2. Keep `doctrine/` as the single semantic owner, with examples, docs, and the
   editor following that truth.
3. Preserve the example-first teaching model by making `43` through `49`
   fully commented, narrow, and manifest-backed.
4. Ship full VS Code parity for the review surface: colorization plus
   Ctrl/Cmd-followable links on the shipped clickable refs.
5. Keep diagnostics and rendered `AGENTS.md` natural and fail-loud so users do
   not need the spec open to understand review behavior.
6. Extend the VS Code adapter only as far as the shipped compiler surface
   requires; no separate editor architecture.

## 1.2 Constraints

- The shipped language is centered on one grammar, one AST, one compiler, and
  one verifier path. The implementation must stay inside that shape.
- The current repo already has a stable workflow-law family through examples
  `30` to `42`; review must reuse or extend that machinery rather than fork
  around it.
- Public docs and examples must stay generic and must not import product names
  or internal workflow jargon from other repos.
- Error-code stability matters. The plan must add the reserved review band
  cleanly rather than rewriting existing code meanings.
- The VS Code extension is intentionally adapter-only. Its grammar, resolver,
  and tests must mirror shipped compiler truth rather than interpret review
  independently.

## 1.3 Architectural principles (rules we will enforce)

- Fail-loud boundaries over silent fallback or best-effort interpretation.
- Reuse the canonical path before adding new machinery. Review should reuse
  existing workflow-law and output-owner concepts where the spec says it does.
- Keep one produced-contract primitive: `output`.
- Keep one proof lane: manifest-backed examples.
- Preserve explicit ordered patching and do not introduce hidden review merges.
- Update or delete stale live docs, comments, and instructions in the same run.
- Prefer a few high-leverage comments in tricky compiler and example boundaries
  over sprawling comment noise elsewhere.

## 1.4 Known tradeoffs (explicit)

- Full-scope shipping is a large cross-cutting change, but partial shipping is
  worse because it hardens drift between the spec and the code.
- Exported contract-gate flattening adds real compiler complexity, but that is
  the cost of preserving exact gate identity without turning contract failures
  into an opaque boolean.
- The review ladder increases corpus size materially, but the language is
  example-first and the spec already defines a ladder; shrinking the proof
  surface would undercut the language-design contract.
- Editor parity work is not optional polish. Without it, the repo would again
  ship two practical languages: the compiler one and the editor one.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- The shipped grammar recognizes `workflow`, typed I/O, `skills`, enums,
  agents, workflow law, guarded output sections, and trust-surface carriers,
  but not top-level `review` declarations or review-specific statements.
- The AST models workflow law and output-owned guarded readback, but it has no
  review declaration family, no review binding surface, and no review branch
  semantics.
- The compiler resolves authored slots generically and only special-cases
  `workflow` for law semantics. It has no notion of review contracts, review
  verdicts, review branch evaluation, or review output agreement.
- The verifier ships the manifest-backed corpus through example `42`, which is
  still entirely about the workflow-law family.
- `docs/REVIEW_SPEC.md` already freezes the intended review design, but that
  file is not yet part of the repo's live shipped language path.
- The VS Code extension mirrors the shipped workflow-law and guarded-output
  surfaces, not review.

## 2.2 What’s broken / missing (concrete)

- There is no shipped implementation for the spec the repo already wrote and
  resolved.
- The review error band `E470` through `E499` exists only in prose.
- The corpus has no review ladder and therefore no active proof of review
  semantics.
- The docs index and README surfaces do not present review as a shipped live
  reference.
- The editor adapter cannot highlight or navigate review declarations and
  review-owned surfaces because those surfaces do not exist in shipped code.

## 2.3 Constraints implied by the problem

- This must be a hard cutover, not a staged half-ship. The repo cannot leave a
  frozen review spec on one side and a smaller shipped surface on the other.
- The compiler must own the semantics; the verifier, docs, and editor cannot
  substitute for a missing review engine.
- Existing workflow-law and output semantics are adjacent to review and must
  remain correct after the change.
- The example ladder, docs, and editor mirror must ship in the same change
  series, or the repo will immediately drift.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No external semantic anchor is adopted for this change. Reject importing
  outside prior art here because `docs/REVIEW_SPEC.md` is already the frozen
  Doctrine contract, and outside systems would only reopen resolved language
  choices.
- No external editor-model anchor is adopted either. The repo already ships
  one VS Code mirror path in `editors/vscode/`; the honest job is parity with
  shipped compiler truth, not a second editor-specific design.

## 3.2 Internal ground truth (code as spec)

### Authoritative behavior anchors (do not reinvent)

- `docs/REVIEW_SPEC.md`:
  binding review contract for the declaration family, reserved surfaces,
  carried state, output agreement, diagnostics band, and example ladder `43`
  through `49`.
- `doctrine/grammars/doctrine.lark`:
  current top-level grammar and agent-field fence; proves `review` is not
  shipped yet and that non-reserved agent keys still fall through to generic
  authored slots.
- `doctrine/parser.py`:
  single transformer and AST-lowering path for declarations, workflow bodies,
  outputs, guarded sections, and `trust_surface`; the review parser must mirror
  this path rather than bypass it.
- `doctrine/model.py`:
  AST truth; currently no `ReviewDecl`, `ReviewBody`, reserved review
  sections, review statement union, or typed agent `review` field exists.
- `doctrine/compiler.py`:
  one canonical resolve and compile path for agent slots, workflow
  inheritance, workflow law, output guards, trust-surface validation,
  addressable refs, and rendered section structure. Review must land here as a
  sibling surface, not as a sidecar evaluator.
- `doctrine/renderer.py`:
  intentionally generic nested-section renderer; strong signal that review
  should compile into ordinary `CompiledSection` trees instead of inventing a
  review-only renderer.
- `doctrine/diagnostics.py` and `doctrine/diagnostic_smoke.py`:
  stable-code mapping and smoke-coverage owner; review codes must be deliberate
  because diagnostics are still message-derived.
- `doctrine/verify_corpus.py`:
  manifest-backed proof owner with active lanes `render_contract`,
  `build_contract`, `parse_fail`, and `compile_fail`.
- `docs/WORKFLOW_LAW.md`:
  current shipped law, currentness, invalidation, and carrier vocabulary, and
  still truthfully says a separate `review` primitive is not shipped today.
- `docs/AGENT_IO_DESIGN_NOTES.md`:
  current produced-contract truth that keeps `output` as the one produced
  primitive, `trust_surface` as the portable carrier, guarded sections as
  output-owned, and `standalone_read` out of the carrier business.
- `examples/README.md` plus `examples/37_law_reuse_and_patching` through
  `examples/42_route_only_handoff_capstone`:
  current advanced teaching ladder, proof rhythm, and comment density bar the
  review ladder must match.
- `docs/README.md`, `docs/COMPILER_ERRORS.md`, `README.md`, and
  `editors/vscode/README.md`:
  live docs that currently describe shipped truth through the workflow-law
  cutover and will drift immediately once review ships.
- `editors/vscode/extension.js`, `editors/vscode/resolver.js`,
  `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
  `editors/vscode/language-configuration.json`,
  `editors/vscode/scripts/validate_lark_alignment.py`, and
  `editors/vscode/tests/`:
  current editor mirror and proof harness for syntax-colorization and
  Ctrl/Cmd-follow parity. Today they know workflow law and guarded outputs, not
  review.

### Canonical path and owner to reuse

- `doctrine/compiler.py`:
  own review semantics here beside workflow law; do not create a sidecar
  evaluator, renderer-driven interpretation, or example-only semantics path.
- `doctrine/grammars/doctrine.lark`, `doctrine/parser.py`, and
  `doctrine/model.py`:
  own the first-class `review` declaration family here, including reserved
  sections and the typed agent `review:` slot.
- `editors/vscode/resolver.js`:
  own Ctrl/Cmd-follow parity here; do not rely on incidental TextMate coloring
  or generic fallback slot behavior.
- `examples/*/cases.toml` plus `doctrine/verify_corpus.py`:
  own proof here; do not create advisory review-only fixtures outside the
  manifest-backed corpus.

### Existing patterns to reuse

- `doctrine/compiler.py` `_resolve_workflow_body()` and `_resolve_law_body()`:
  explicit inherited-body accounting, required parent coverage, and `inherit`
  and `override` discipline to reuse for review inheritance and reserved
  section patching.
- `doctrine/compiler.py` workflow-law branch collection and validation:
  reuse the branch-analysis pattern, but with dedicated review state instead of
  overloading workflow-law leaves.
- `doctrine/compiler.py` trust-surface and carrier validation helpers:
  reuse for review current-artifact carriers and `comment_output` checks
  instead of inventing a second currentness mechanism.
- `doctrine/compiler.py` output guard compilation:
  reuse the phase ordering, then widen allowed resolved names only after review
  semantics are bound.
- `doctrine/parser.py` plus `TransformParseFailure`:
  reuse for review-only shape errors that belong in parse and transform space.
- `doctrine/verify_corpus.py` active case kinds:
  reuse `render_contract`, `parse_fail`, and `compile_fail` for review proof
  before inventing new manifest lanes.
- `examples/37_law_reuse_and_patching`:
  inheritance-teaching template for explicit patching and negative proof.
- `examples/38_metadata_polish_capstone`:
  full walkthrough capstone template.
- `examples/39_guarded_output_sections`:
  “one new surface first” template.
- `examples/40_route_only_local_ownership`,
  `examples/41_route_only_reroute_handoff`, and
  `examples/42_route_only_handoff_capstone`:
  split-branch then recombine ladder shape to reuse for accept and reject
  outcomes and the review capstone.
- `doctrine/renderer.py` `CompiledSection` rendering:
  generic render tree to reuse instead of adding a review-only renderer.

### Prompt surfaces and agent contract to reuse

- `docs/WORKFLOW_LAW.md`:
  current shipped law, currentness, and trust-surface vocabulary that review
  must extend without contradiction.
- `docs/AGENT_IO_DESIGN_NOTES.md`:
  produced-contract model that keeps `output` as the one produced primitive,
  `trust_surface` as the portable carrier, guarded sections output-owned, and
  routed `next_owner` structurally bound.
- `examples/39` through `42` prompts:
  current fully commented teaching surface and proof style to match,
  especially for annotated declarations and adjacent invalid prompts.

### Existing grounding, tool, and file exposure

- `make verify-examples`:
  current full-corpus preservation signal across shipped semantics.
- `make verify-diagnostics` plus `doctrine/diagnostic_smoke.py`:
  current signal for stable-code and formatter preservation.
- `cd editors/vscode && make`:
  current editor mirror verification path.
- `editors/vscode/scripts/validate_lark_alignment.py`:
  current lexical drift check between Lark and the VS Code grammar.
- `editors/vscode/tests/unit`, `editors/vscode/tests/snap`, and
  `editors/vscode/tests/integration`:
  current editor proof surfaces for colorization and navigation.

### Duplicate or drifting paths relevant to this change

- `README.md`:
  already stale on the verified corpus range and will drift further once review
  ships.
- `docs/README.md`:
  currently says the shipped numbered corpus ends at `42`.
- `examples/README.md`:
  currently treats `30` through `42` as the advanced ladder and stops there.
- `docs/WORKFLOW_LAW.md`:
  truthfully says a separate `review` primitive is not shipped today and must
  be updated or cross-linked once that changes.
- `docs/AGENT_IO_DESIGN_NOTES.md`:
  currently has no live review surface for `fields`, explicit outcome coupling,
  or carried review state.
- `docs/COMPILER_ERRORS.md`:
  currently has no live `E470` through `E499` review band.
- `editors/vscode/README.md`:
  currently promises shipped clickable and colorized surfaces through workflow
  law and the `39` through `42` ladder only.
- `doctrine/grammars/doctrine.lark`,
  `editors/vscode/syntaxes/doctrine.tmLanguage.json`,
  `editors/vscode/language-configuration.json`, and
  `editors/vscode/resolver.js`:
  four mirrored grammar and navigation surfaces that can drift independently if
  review lands unevenly.
- `editors/vscode/resolver.js`:
  today non-reserved agent slots fall back to workflow-like handling, so
  `review:` would click wrong until it becomes reserved there too.

### Capability-first opportunities before new tooling

- `doctrine/compiler.py` already owns branch semantics, trust carriers, output
  guards, inheritance accounting, and compiled section structure:
  strongest signal to extend the canonical compiler instead of building a
  review harness beside it.
- `doctrine/verify_corpus.py` already provides enough active proof lanes for
  the first honest review ship:
  no mandatory new manifest kind is justified yet.
- `editors/vscode` already ships both TextMate colorization and custom
  definition and navigation:
  parity should come from widening that mirror, not adding a second editor
  adapter or language server.
- `doctrine/renderer.py` is already generic:
  compile richer section trees first, and only touch rendering if a concrete
  review shape cannot be expressed there.
- `TransformParseFailure` already gives stable parse-stage diagnostics for
  structured authoring errors:
  use it before inventing a new parse error mechanism.

### Behavior-preservation signals already available

- `make verify-examples`:
  protects the shipped corpus `01` through `42` while review lands.
- `make verify-diagnostics`:
  protects user-facing diagnostic stability once review codes are added.
- `doctrine/diagnostic_smoke.py`:
  protects representative parse, compile, and emit invariants and should gain
  review smoke cases early.
- `cd editors/vscode && make`:
  protects the editor mirror end to end.
- `examples/39` through `42` manifests:
  protect the latest workflow-law, guarded-output, and route-only invariants
  most likely to regress when review touches currentness, carriers, and guarded
  reads.

## 3.3 Open questions (evidence-based)

- How should review-local semantic fields become addressable for guarded output
  sections and Ctrl/Cmd-follow navigation without turning arbitrary local names
  into pseudo-declarations?
  Evidence needed: a compiler-owned addressability design that handles
  `contract.<gate>` and `fields:` descendants while preserving current readable
  and addressable boundaries.
- Does review need any verifier extension beyond the existing manifest kinds?
  Current evidence says no, but this stays open until the first
  output-agreement and post-review guarded-read proofs are sketched against
  real example cases.
- Can every required review render shape be expressed as ordinary
  `CompiledSection` trees?
  Current evidence says probably yes; settle it by sketching one accept and
  reject capstone render before any renderer-specific abstraction is blessed.
- Which review shape errors belong in transformer space versus compile space?
  Evidence needed: a short matrix mapping failures like illegal reserved
  sections, mixed inheritance forms, and agent `workflow:` plus `review:`
  conflicts to existing parse and compile conventions so diagnostics stay
  stable.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark`:
  one grammar owner for shipped syntax. It defines top-level declarations,
  agent-field grammar, workflow-law statements, and output-guard expressions.
  Today it has no top-level `review` declaration, no reserved `review:` agent
  field, and no review-only operator such as `not in`; generic call syntax
  already exists, but nothing in the shipped surface blesses `present(...)` or
  `missing(...)` as review semantics.
- `doctrine/parser.py`:
  one `ToAst` transformer for the entire language. `WorkflowBodyParts`,
  `SkillsBodyParts`, `IoBodyParts`, and `OutputBodyParts` normalize mixed
  grammar bodies, and `_workflow_slot_value()` still treats non-reserved agent
  slots as workflow-shaped content.
- `doctrine/model.py`:
  typed AST truth. `Declaration` and `Field` stop at the shipped workflow,
  law, outputs, records, skills, typed I/O, and agents; no review family
  exists.
- `doctrine/compiler.py`:
  one semantic owner. `IndexedUnit`, `_compile_agent_decl()`,
  `_resolve_agent_slots()`, `_resolve_workflow_body()`, `_resolve_law_body()`,
  `_compile_workflow_law()`, output/trust-surface validation, and addressable
  refs all live here.
- `doctrine/renderer.py`:
  generic `CompiledSection` renderer only; it does not own language semantics.
- `doctrine/diagnostics.py` and `doctrine/diagnostic_smoke.py`:
  stable-code and smoke-check surfaces. Parse failures can carry explicit
  transformer codes; compile failures are still message-pattern-driven.
- `doctrine/verify_corpus.py`:
  one manifest-backed proof harness with `render_contract`, `build_contract`,
  `parse_fail`, and `compile_fail`.
- `examples/37_*` through `examples/42_*`:
  the current advanced ladder and the strongest nearby regression anchors for
  explicit inheritance, guarded outputs, route-only coupling, and guarded
  readback.
- `docs/README.md`, `docs/WORKFLOW_LAW.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
  `docs/COMPILER_ERRORS.md`, `README.md`, and `docs/REVIEW_SPEC.md`:
  current live-doc and draft-spec layer. Review is still documented outside the
  shipped live-doc path.
- `editors/vscode/extension.js`, `resolver.js`, `language-configuration.json`,
  `syntaxes/doctrine.tmLanguage.json`, `scripts/validate_lark_alignment.py`,
  and `tests/`:
  one local editor mirror for tokenization, indentation, and Ctrl/Cmd-follow
  navigation. It mirrors compiler truth locally and does not call into Python.

## 4.2 Control paths (runtime)

- Compile path:
  `parse_file()` -> Lark parse -> `ToAst` -> `model.PromptFile` ->
  `compile_prompt()` -> `CompilationContext.compile_agent()` -> `_index_unit()`
  -> `_compile_agent_decl()` -> `render_markdown()`.
- Existing semantic path:
  concrete agents compile roles, typed I/O, generic authored slots, workflow
  bodies, workflow law, output guards, and trust-surface carriers through one
  path in `doctrine/compiler.py`. Review has no first-class semantic path.
- Verification path:
  `verify_corpus()` dispatches `render_contract`, `build_contract`,
  `parse_fail`, and `compile_fail` against the same parse -> compile -> render
  / emit stack and checked refs.
- Emit path:
  `emit_target()` reuses the compile and render path for configured entrypoints.
- Reader and proof path:
  repo entrypoint -> docs index -> workflow-law or I/O reference -> numbered
  examples -> manifest-backed proof.
- Editor path:
  `extension.js` registers document-link and definition providers only.
  `resolver.js` indexes declarations, infers container context, classifies
  cursor sites, and resolves direct, readable, addressable, or structural refs.
  TextMate colorization and `language-configuration.json` indentation run
  separately.
- Current sharp edge:
  if an author writes `review:` today, the parser and compiler do not stop at a
  clean review boundary. That key is accepted as a generic authored slot and
  then treated like workflow-shaped content, while the VS Code resolver would
  also click it like a workflow slot.

## 4.3 Object model + key abstractions

- Generic authored-slot model:
  unknown agent slot keys are still workflow-shaped. `workflow` is the only
  semantic carve-out.
- Workflow-law model:
  `LawBody`, `LawSection`, branch collection, currentness carriers,
  preservation rules, invalidation, and route validation are all workflow-owned
  and compiler-owned.
- Output model:
  outputs already own nested record sections, guarded output sections,
  `trust_surface`, and the existing `standalone_read` guarded-readback fence.
  Output guards currently admit declared inputs and enum members only.
- Addressability model:
  readable and addressable refs are compiler-owned and declaration-rooted.
  There is already an addressable workflow mirror for traversing inherited
  workflow structure, but there is no semantic namespace for `contract.*`,
  review `fields.*`, or other review-local channels.
- Docs and corpus model:
  manifests are the proof surface, docs are thin explanations, and the late
  example ladder is the teaching template. There is no second proof or teaching
  track for review today.

## 4.4 Observability + failure behavior today

- Parser structure failures already surface through `TransformParseFailure`
  with explicit codes and hints.
- Compile failures are only stable when message shapes match
  `_COMPILE_PATTERN_BUILDERS`; there is no live review band yet.
- `doctrine/diagnostic_smoke.py` is intentionally narrow and has no review
  coverage.
- The strongest preservation signals are `make verify-examples`, targeted
  manifest runs, `make verify-diagnostics` when diagnostics change, and
  `cd editors/vscode && make`.
- The highest-value nearby regression sentries are examples `37`, `39`, `41`,
  and `42`.
- Editor proof is split across unit fixtures, example snapshots, and extension-
  host integration tests, but it stops at the current shipped pre-review
  surface.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No product UI is in scope, but three human-facing surfaces must stay aligned:

```text
Author .prompt
  -> parse / compile / render
  -> AGENTS.md runtime Markdown

Example rung
  -> prompts + cases.toml
  -> checked ref / expected failure

Editor .prompt
  -> tmLanguage scopes + indentation
  -> Ctrl/Cmd-follow on shipped refs
```
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- `doctrine/grammars/doctrine.lark`:
  widens in place to include the full review declaration family, reserved
  review surfaces, review-only statements, review match heads, and the narrow
  operator addition `not in`. `present(...)` and `missing(...)` stay on the
  existing call syntax and become blessed review semantics in compiler space.
- `doctrine/parser.py`:
  gains dedicated review lowering and review-specific transform failures instead
  of routing review through workflow-body helpers; generic call lowering stays
  reused for `present(...)` / `missing(...)`.
- `doctrine/model.py`:
  gains typed review AST nodes and typed agent-field support for `review:`,
  making review a sibling declaration family to `workflow`.
- `doctrine/compiler.py`:
  gains one review-aware canonical path for indexing, inheritance,
  review-contract export, semantic evaluation, semantic addressability,
  output agreement, and compiled-section assembly. No new package or sidecar
  interpreter is introduced.
- `doctrine/diagnostics.py` and `doctrine/diagnostic_smoke.py`:
  gain the live `E470` through `E499` band and the smallest extra smoke
  coverage needed to keep it stable.
- `doctrine/verify_corpus.py`:
  remains the one proof harness unless a concrete review requirement proves one
  of its current case kinds insufficient.
- `examples/43_*` through `examples/49_*`:
  become the review ladder in the same manifest-backed, fully commented style
  as the late workflow-law ladder.
- `docs/REVIEW_SPEC.md`:
  becomes the live review reference, while `docs/WORKFLOW_LAW.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, and
  `docs/COMPILER_ERRORS.md` remain boundary-focused live docs.
- `editors/vscode/`:
  stays one mirror-only adapter, widened in place across tmLanguage,
  indentation, resolver, validator, tests, and README. No language server or
  Python bridge is added.

## 5.2 Control paths (future)

- Canonical runtime path:
  `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
  `doctrine/model.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`
  remains the sole shipped runtime truth path.
- Public compile entrypoint:
  callers keep entering through `compile_prompt(prompt_file, agent_name)` and
  `CompilationContext.compile_agent()`. Review work widens the internal owner
  seams beneath that public surface instead of inventing a second compile API.
- Parse path:
  `.prompt` source produces `ReviewDecl` and related review AST nodes directly
  from the grammar and transformer, with structural review failures surfacing as
  ordinary parse or transform diagnostics.
- Index and compile path:
  `_index_unit()` indexes reviews beside workflows, and `_compile_agent_decl()`
  plus `_resolve_agent_slots()` enforce exactly one primary semantic owner for
  a concrete agent, either `workflow` or `review`.
- Review semantic path:
  1. Resolve inherited review bodies and reserved sections explicitly.
  2. Validate `subject`, `subject_map`, `contract`, `comment_output`, and
     `fields`.
  3. Flatten review-contract workflow gates after workflow reuse.
  4. Evaluate pre-outcome checks in fixed spec order and capture exact
     failing-gate identity.
  5. Resolve one total outcome path: blocked, accepted, or rejected.
  6. Bind currentness carriers and carried state onto declared outputs.
  7. Validate output agreement and only then admit review semantic names to
     guarded output checks and rendered readback.
  8. Emit ordinary `CompiledSection` trees for the generic renderer.
- Verification path:
  manifests remain the proof owner; review positives and negatives stay in the
  existing `render_contract`, `build_contract`, `parse_fail`, and
  `compile_fail` lanes unless a concrete proof gap appears.
- Editor path:
  the VS Code mirror only learns surfaces the compiler blesses. Ctrl/Cmd-follow
  on review refs is derived from compiler-owned declaration and semantic
  boundaries, not editor-only heuristics or a second ref system.

## 5.3 Object model + abstractions (future)

- First-class review declarations:
  add typed review declarations, bodies, sections, reserved outcome sections,
  field-binding surfaces, and typed agent `review` fields instead of routing
  review through `WorkflowBody` or generic authored slots.
- Dedicated review semantic state:
  add review-specific resolution and evaluation layers for review-contract
  exported gates, field-binding resolution, subject identity and disambiguation,
  branch and outcome state, carried-state binding, and semantic-to-output
  agreement.
- Compiler-owned semantic addressability:
  `contract.*`, review `fields.*`, and other shipped review semantic refs
  become compiler-owned readable and addressable surfaces with explicit
  boundaries after review resolution. They do not degrade into arbitrary locals
  or editor-only pseudo-declarations, and the blessed surface is explicit:
  authored-prose interpolation, shipped readable refs, guarded-output
  expressions, and editor follow-links may use only the review semantic nodes
  the compiler exposes.
- Reuse where semantics already match:
  explicit inherited patch accounting, enum resolution, output-node and carrier
  resolution, trust-surface validation, interpolation walking, manifest-backed
  proof, and compiled-section rendering.
- Editor mirror model:
  one TextMate grammar plus one resolver continue to own colorization and
  Ctrl/Cmd-follow parity. Review support widens those same surfaces instead of
  adding a second parser, including dedicated review ref collectors,
  inheritance-aware parent-body lookup, and review-specific addressable body
  items for lowercase `contract.*` and `fields.*` paths.

## 5.4 Invariants and boundaries

- `review` is a first-class top-level declaration family and a reserved typed
  agent field, not a workflow alias.
- `workflow` remains the producer/coordinator law home; `review` becomes the
  critic/reviewer law home.
- `output` remains the one produced-contract primitive, including review turns.
- Review-contract workflows remain `workflow` declarations under a restricted
  profile; exported gate identities are compiler-owned after flattening.
- `fields` is a non-rendered inherited binding surface. `on_accept` and
  `on_reject` are reserved mandatory outcome sections.
- Carried mode and trigger state live on `comment_output`, not on routes and
  not on a shadow carrier.
- Portable currentness remains `current artifact ... via Output.field` or
  `current none`; there is no review-only alias.
- Review semantic names become legal in guarded output checks only after review
  resolution. No earlier phase may treat them as ordinary locals.
- No generic-authored-slot fallback, no sidecar evaluator, no review-only
  renderer, no second verifier lane, and no second addressability engine are
  allowed.
- Compiler, corpus, docs, and editor support must converge in the same change
  series. No live layer may keep framing review as draft after ship.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Runtime Markdown stays ordinary Doctrine output:

```text
Reviewer role prose

## Review
subject / contract framing
review checks
accepted path
rejected path
output contract
```

Editor authoring stays ordinary Doctrine authoring with review as first-class
syntax:

```text
review SharedReview: ...
agent Critic:
    review: SharedReview

Ctrl/Cmd-follow:
  review decls
  review inheritance keys
  contract refs
  comment_output refs
  shipped review-local paths
```
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## Change map (table)
| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar surface | `doctrine/grammars/doctrine.lark` | `declaration`, `agent_field`, review body and statement rules, `comparison_expr` | Ships `workflow`/law/output syntax only; no top-level `review`, no reserved `review:` field, no review statements, and no review-only `not in` operator. Generic call syntax already exists, but no review predicate is blessed there yet | Add the full review declaration family, reserved agent field, review body surfaces, review match syntax, and the narrow `not in` addition while keeping `present(...)` / `missing(...)` on the existing call grammar | Review cannot be first-class if it enters as generic workflow text or if compiler-owned review predicates look like random calls | Shipped grammar parses `review` as a sibling declaration family with explicit reserved surfaces and keeps review predicates on the canonical call surface | New review `parse_fail` manifests; full `make verify-examples` |
| Parser scaffolds | `doctrine/parser.py` | `WorkflowBodyParts`, `ToAst.workflow_decl()`, `workflow_body()`, agent-field lowering, expression lowering | Lowers only shipped workflow/law/output surfaces; generic call lowering already exists, but transformer failures are workflow/output-specific and there is no review decl/body/statement lowering | Add review body-part scaffolds, review decl lowering, review-field lowering, review statement lowering, `not in` lowering, and transformer-space review shape failures while reusing generic call lowering for `present(...)` / `missing(...)` | Prevents review from becoming a late compiler heuristic over raw tuples | Parser emits first-class review AST nodes and review shape errors surface as `ParseError` with stable codes | Review `parse_fail` manifests; `make verify-diagnostics` if new parse codes land |
| AST truth | `doctrine/model.py` | `Field`, `Declaration`, new review dataclasses and unions | No review declaration, review field, review statement, or review outcome types exist | Add `ReviewDecl`, review body/items, review field bindings, reserved outcome sections, review statements, and minimal compiler helper state types | The compiler needs typed review truth, not overloaded workflow types | Review AST becomes part of the shipped declaration union and field union | All review examples; compiler import / inheritance paths |
| Compile entrypoint and registry | `doctrine/compiler.py` | `compile_prompt()`, `CompilationContext.compile_agent()`, `IndexedUnit`, compiler `__init__` caches, `_index_unit()`, `_resolve_decl_ref()` family | Public callers enter through `compile_prompt()` and `compile_agent()`, but the indexed declaration set and caches stop at workflows, skills, typed I/O, outputs, enums, and agents; no review registry exists | Keep the public compile API stable while adding `reviews_by_name`, review caches, `_resolve_review_ref()`, and parent-review resolution beneath it | Imported refs, inheritance, trace shaping, and compile caches cannot work without registry-level support on the canonical compile path | Reviews resolve like other top-level decls through the existing compiler registry path without a second compile API | Review compile positives/negatives; imported review cases if added later |
| Agent semantic entrypoint | `doctrine/compiler.py` | `_RESERVED_AGENT_FIELD_KEYS`, `_typed_field_key()`, `_compile_agent_decl()`, `_resolve_agent_slots()`, `_resolve_slot_value()` | Authored slots are generic workflow-shaped slots; only `workflow` is special-cased semantically | Reserve `review`, add a typed review field path, enforce `workflow` xor `review`, and reject abstract-review attachment on concrete agents | `review` must not ride the generic authored-slot path | Concrete agents own exactly one primary semantic body and `review:` is no longer a generic slot key | Review compile-fail cases for exclusivity and invalid attachment; full corpus |
| Review inheritance | `doctrine/compiler.py` | `_resolve_workflow_body()`, `_resolve_workflow_addressable_body()`, `_resolve_law_body()` pattern; new review resolvers | Explicit inheritance exists only for workflow, skills, I/O, and law | Add `_resolve_review_decl()`, `_resolve_review_body()`, and an addressable review-body mirror using the same explicit accounting discipline | Review inherits reserved surfaces and named sections; hidden merge is forbidden | Review inheritance uses explicit `inherit` / `override` accounting for `fields`, named sections, `on_accept`, and `on_reject` | Review inheritance positives/negatives, especially example `48` |
| Review-contract export | `doctrine/compiler.py` | `_resolve_workflow_body()`, `_resolve_law_body()`, `_compile_workflow_decl()`, `_compile_resolved_workflow()`, `_compile_workflow_law()`, `_collect_law_leaf_branches()` plus new review-contract helpers | Workflow inheritance and law flattening exist, but there is no notion of review-contract workflows or exported gate identities | Add restricted workflow-profile validation plus first-level gate export from resolved workflow law before review outcome evaluation | Exact gate identity is part of the review contract | `contract.<gate>` becomes compiler-owned data derived from resolved workflow law with stable gate names | Example `45`; compile-fail cases for invalid contract targets and unknown gates |
| Review branch evaluation | `doctrine/compiler.py` | `_compile_workflow_decl()`, `_compile_resolved_workflow()`, `_compile_workflow_law()`, `_validate_workflow_law()`, `_collect_law_leaf_branches()`, `_branch_with_stmt()` | Workflow law has one branch-analysis engine; no review verdict or outcome engine exists | Add a sibling review compile/evaluate path with dedicated review branch state, verdict state, and total outcome enforcement; reuse shared validators where semantics match | Review semantics are the core shipped behavior | Compiler owns review verdict, failing gates, block handling, carried state, currentness, and total accept/reject routing | Positive review manifests `43`-`49`; review compile-fail manifests; full corpus |
| Review semantic addressability | `doctrine/compiler.py` | `AddressableRootDecl`, `AddressableTarget`, `_resolve_addressable_root_decl()`, `_resolve_addressable_path_node()`, `_get_addressable_children()`, `_interpolate_authored_prose_string()`, `_resolve_authored_prose_interpolation_expr()`, `_resolve_readable_decl()`, `_resolve_addressable_ref_value()` | Addressable roots are readable decls plus workflow/skills; authored-prose interpolation and readable refs already flow through one compiler-owned path, but there is no review semantic scope | Extend the addressable/readable contract so review-local semantic channels such as `contract.*` and resolved `fields.*` become compiler-owned nodes after review resolution across authored-prose interpolation, shipped readable refs, guarded-output expressions, and the mirrored editor follow surface | Review needs clickable/readable semantic names without inventing a second resolver or pseudo-local namespace | Review semantic names are visible only through explicit compiler-owned nodes, not arbitrary local variables | Review guarded-output proofs; future editor integration parity; full corpus |
| Output agreement and carrier reuse | `doctrine/compiler.py` | `_validate_output_guard_sections()`, `_validate_output_guard_expr()`, `_output_guard_ref_allowed()`, `_compile_trust_surface_section()`, `_validate_current_artifact_stmt()`, `_validate_invalidation_stmt()`, `_resolve_output_field_node()`, `_validate_standalone_read_guard_contract()`, `_iter_record_item_interpolation_refs()`, `_interpolation_ref_enters_guarded_output_section()` | Output guards allow only input decls and enum members; currentness and trust-surface checks are workflow-law-only, and `standalone_read` already has a guarded-readback fence that review must not weaken | Widen output validation so review semantic refs are legal only after review resolution, enforce exact agreement between review semantics and `comment_output` structure / carriers, and preserve the existing `standalone_read` guarded-readback fence | Review must reuse output as the one produced-contract primitive without leaking guarded detail into readback | Review-resolved fields, carried state, and currentness bind onto declared output fields before guard validation passes and before guarded-readback validation is rechecked | Examples `46`, `47`, `49`; `make verify-diagnostics` if messages change |
| Generic render boundary | `doctrine/compiler.py`, `doctrine/renderer.py` | `CompiledSection`, `CompiledAgent`, `render_markdown()`, `_render_section()` | Renderer is generic and semantics-free | Keep `renderer.py` generic and compile review into ordinary `CompiledSection` trees; only add a renderer helper if the compiler proves a concrete section-shape gap | Avoids a review-only serializer and keeps one render path | Review rendering remains a compiler responsibility; renderer stays structurally generic | Positive review render manifests; full corpus |
| Diagnostic classification | `doctrine/diagnostics.py` | `TransformParseFailure`, `_COMPILE_PATTERN_BUILDERS`, `CompileError._diagnostic_from_message()` | Parse codes can be explicit; compile codes stop before the review band | Add stable review parse/compile mappings in the reserved `E470`-`E499` band and shape new compile messages deliberately to fit those patterns | Diagnostics are message-derived today; drift is easy if the shapes are sloppy | Review diagnostics become part of the shipped code map instead of prose only | Review `parse_fail` / `compile_fail`; `make verify-diagnostics` |
| Diagnostic smoke | `doctrine/diagnostic_smoke.py` | `main()`, new review smoke helpers | Smoke checks only generic parse, compile, emit, and JSON-safety behavior | Add the smallest high-value review smoke cases where the corpus does not already defend the diagnostic surface | Keeps stable-code claims honest without duplicating the whole review ladder | Smoke covers representative review parse and compile failures only | `make verify-diagnostics` |
| Verifier harness | `doctrine/verify_corpus.py` | `CaseSpec`, `_load_case()`, `_run_render_contract()`, `_run_build_contract()`, `_run_parse_fail()`, `_run_compile_fail()` | Existing manifest kinds already cover render, build, parse-fail, and compile-fail | Default to no harness expansion; only widen the verifier if a concrete review proof need cannot fit the existing lanes | Prevents a parallel proof surface from appearing next to the shipped harness | Review proof stays inside the existing manifest-backed lanes unless a real gap is proven | `make verify-examples`; targeted new manifests |
| Review ladder foundation | `examples/43_*` through `examples/46_*` | new example directories, `cases.toml`, prompts, refs, invalid siblings | No review ladder exists today | Add four fully commented foundation rungs for verdict coupling, handoff-first block gates, contract gate export, and current/trust coupling, each with adjacent narrow negatives | The spec requires the ladder to teach one idea at a time and stay example-first | Review becomes part of the shipped numbered corpus, not a detached spec appendix | Targeted manifest runs; full `make verify-examples` |
| Review ladder advanced | `examples/47_*` through `examples/49_*` | new example directories, `cases.toml`, prompts, refs, invalid siblings | No advanced review ladder exists today | Add the multi-subject carry rung, inheritance-and-patching rung, and full capstone with fully commented prompts and negative proofs | The no-scope-cut requirement explicitly includes the hard rungs, not only the easy foundation cases | The shipped ladder reaches the full review capstone and preserves the comment-rich teaching style of examples `30+` | Targeted manifest runs; full `make verify-examples` |
| Existing late-ladder sentries | `examples/37_*` through `examples/42_*` | current workflow-law and guarded-output manifests | These are the strongest nearby regression anchors and already prove adjacent invariants | Keep them intact and use them as regression sentries while review lands | Review touches the same inheritance, guard, route-only, and currentness boundaries | Existing advanced examples stay active proof, not migration debris | Full `make verify-examples` |
| Root and docs index | `README.md`, `docs/README.md`, `examples/README.md` | shipped surface summary, docs index, corpus range and ladder text | Live docs stop at `38` or `42` and still route readers mainly through workflow law | Update shipped-surface summaries, corpus range, ladder narrative, and the start-here review entrypoint | Prevent immediate repo-doc drift and avoid hiding shipped review behind old navigation | Live docs acknowledge first-class review and examples `43` through `49` from the repo entrypoints onward | Doc review; full corpus |
| Review live reference | `docs/REVIEW_SPEC.md` | review reference status and shipped-language wording | Review still reads as draft or proposal material | Promote the spec into shipped reference status without trimming semantics | Preserve one binding review reference instead of a detached design memo | Review docs become shipped truth without opening a second semantics story | Doc review; full corpus |
| Boundary docs and design notes | `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md` | workflow boundary, I/O model, language decisions, error catalog | Workflow law and I/O/design notes still stop at `42`, can overclaim workflow-law exclusivity, and still carry pre-ship review-pressure language | Align the boundary docs and notes to first-class review without erasing workflow-law semantics or compiler error truth | Prevent stale semantics and stale shipped-surface ceilings from surviving beside the new feature | Boundary docs describe review as shipped language truth and the error catalog covers the live review band | Doc review; `make verify-diagnostics` when codes land |
| VS Code grammar | `editors/vscode/syntaxes/doctrine.tmLanguage.json` | declaration patterns, keyword buckets, keyed-line rules, outcome headers, review-match patterns | No review declaration or review-only lexical coverage exists, and the generic keyed rules would swallow review syntax if ordering is naive | Add review declaration, outcome-header, and review-match colorization in place before the generic keyed rules | Full review colorization is a non-negotiable ship surface and tmLanguage rule order is part of correctness | tmLanguage scopes the shipped review surface with the right precedence | `cd editors/vscode && make` |
| VS Code indentation | `editors/vscode/language-configuration.json` | all three overlapping `onEnterRules` buckets | No review declaration or outcome-body indentation coverage exists; all current regex buckets are pre-review only | Add explicit review coverage to each relevant indentation bucket instead of one broad catch-all | Editor authoring must remain usable for the new syntax | Enter indentation mirrors shipped review block structure across declaration, outcome, and nested review sections | `cd editors/vscode && make` |
| VS Code resolver | `editors/vscode/resolver.js` | declaration kinds, reserved slot keys, parent-body resolution, structural-key lookup, review-slot inheritance path, definition-site collectors, review-local ref collectors | `review:` falls through as workflow-like; no review declaration kind, inheritance-aware review-body lookup, or lowercase review-local navigation exists | Add review indexing, reserved-key handling, review body discovery, parent-body resolution for `inherit` / `override`, dedicated review ref collectors, and review-specific addressable body items for `contract.*` / `fields.*` | Prevent editor/compiler drift on Ctrl/Cmd-follow | Resolver mirrors only shipped clickable review refs, including review inheritance and lowercase review-local semantic paths | VS Code integration tests |
| VS Code validator | `editors/vscode/scripts/validate_lark_alignment.py` | keyword sample lists, named-pattern assertions, review lexical samples | Proves keyword presence only for shipped pre-review surfaces | Add review lexical coverage and sample assertions for declaration lines, `review:` slots, outcome headers, and review-match syntax | Prevent lexical drift between Lark and tmLanguage | Review keywords and named patterns stay aligned | `cd editors/vscode && make` |
| VS Code unit tests | `editors/vscode/tests/unit/declarations.test.prompt`, `editors/vscode/tests/unit/agent-slot-references.test.prompt`, `editors/vscode/tests/unit/keyword-identifiers.test.prompt`, new review fixtures | No review lexical or slot coverage exists | Add review declaration, slot, outcome-header, `subject_map`, keyword, and keyword-identifier cases | Lock review colorization basics and preserve plain authored identifiers where review words are not reserved | Review lexical surfaces stay stable | `cd editors/vscode && make` |
| VS Code snapshots | `editors/vscode/tests/snap/examples/**` | example snapshot tree | Snapshot ladder stops at `42` | Add review example snapshots for `43` through `49` | Mirror the new corpus in editor proof | Snapshot tree includes the review ladder | `cd editors/vscode && make` |
| VS Code integration tests | `editors/vscode/tests/integration/suite/index.js` | Go to Definition coverage | No review definition tests exist | Add definition coverage for `review:` slots, inherited review bodies, `contract`, `comment_output`, review route targets, and lowercase shipped review-local refs such as `contract.*` and `fields.*` | Full Ctrl/Cmd-follow parity must be proven, not implied | Extension-host tests cover the shipped clickable review surface | `cd editors/vscode && make` |
| VS Code docs | `editors/vscode/README.md` | supported surface list and smoke checklist | README smoke path stops at workflow law and `39` through `42` | Extend docs and manual smoke steps to review | Prevent extension-doc drift | README documents review colorization and Ctrl/Cmd-follow surfaces | `cd editors/vscode && make` |

## Migration notes
* Canonical owner path / shared code path:
  `doctrine/grammars/doctrine.lark` -> `doctrine/parser.py` ->
  `doctrine/model.py` -> `doctrine/compiler.py` -> `doctrine/renderer.py`
  remains the one runtime truth path. `editors/vscode/` mirrors it locally and
  the numbered examples prove it through manifests.
* Deprecated APIs (if any):
  There is no shipped review API to deprecate. The thing to prevent is a new
  pseudo-API where `review` behaves like a generic authored workflow slot or an
  editor-only concept.
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  Any implementation attempt that treats `review:` as a generic authored slot,
  any review-only serializer beside `renderer.py`, any review-only verifier
  mode, any editor-only review parser, stale proposal framing for
  `docs/REVIEW_SPEC.md`, stale "`review` is not shipped" wording in
  `docs/WORKFLOW_LAW.md`, stale corpus-end claims at `38` or `42` in
  `README.md`, `docs/README.md`, `examples/README.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`, and `docs/LANGUAGE_DESIGN_NOTES.md`, plus
  any ad hoc review ref resolver outside the compiler's existing
  readable/addressable contract.
* Capability-replacing harnesses to delete or justify:
  Review sidecar evaluators, regex-only review analyzers, post-render review
  patchers, a second proof track, or a Python-backed editor bridge are
  forbidden unless the plan is amended explicitly.
* Live docs/comments/instructions to update or delete:
  Rewrite the `_RESERVED_AGENT_FIELD_KEYS` comment and any nearby compiler
  boundary comments that currently imply only `workflow` is special; update
  `README.md`, `docs/README.md`, `examples/README.md`,
  `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/COMPILER_ERRORS.md`,
  `docs/REVIEW_SPEC.md`, and
  `editors/vscode/README.md` once review ships.
* Behavior-preservation signals for refactors:
  `make verify-examples`, targeted review `parse_fail` and `compile_fail`
  manifests, targeted per-rung manifest runs for `43` through `49`, the
  existing late-ladder sentries in `examples/37_*`, `examples/39_*`,
  `examples/41_*`, and `examples/42_*`, `make verify-diagnostics` when codes
  or wording change, `cd editors/vscode && make`, and one manual corpus-style
  review comparing an early review rung, a truth/carrier rung, and the capstone
  against the comment density and teaching rhythm of the shipped late ladder.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)
| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Explicit inheritance | `doctrine/compiler.py::_resolve_workflow_body`, `doctrine/compiler.py::_resolve_law_body` | Reuse explicit parent-accounting and `inherit` / `override` discipline for review surfaces | Prevents a second merge dialect for review inheritance | include |
| Addressability | `doctrine/compiler.py::_resolve_workflow_addressable_body`, `doctrine/compiler.py::_interpolate_authored_prose_string`, `doctrine/compiler.py::_resolve_authored_prose_interpolation_expr`, `doctrine/compiler.py::_resolve_readable_decl`, `doctrine/compiler.py::_get_addressable_children`, `editors/vscode/resolver.js` body-spec stack | Extend the existing readable/addressable model instead of inventing review-only resolvers | Prevents compiler truth from splitting across two ref systems | include |
| Example authoring shape | `examples/README.md`, `examples/37_*` through `examples/42_*`, new `examples/43_*` through `examples/49_*` prompts/manifests | Preserve the one-new-idea-per-rung, adjacent-negative, fully commented ladder pattern for review | Prevents the review ladder from degrading into terse fixtures that prove semantics but stop teaching the language | include |
| Carrier validation | `doctrine/compiler.py::_validate_current_artifact_stmt`, `doctrine/compiler.py::_validate_invalidation_stmt`, `doctrine/compiler.py::_compile_trust_surface_section` | Reuse shipped output-carrier and currentness checks for review | Prevents a shadow currentness model | include |
| Generic rendering | `doctrine/compiler.py::CompiledSection`, `doctrine/renderer.py::render_markdown` | Preserve one compiled-section render path | Prevents a review-only serializer path | include |
| Proof harness | `doctrine/verify_corpus.py::_run_render_contract`, `doctrine/verify_corpus.py::_run_build_contract`, `doctrine/verify_corpus.py::_run_parse_fail`, `doctrine/verify_corpus.py::_run_compile_fail` | Keep review proof inside existing manifest lanes unless a real gap appears | Prevents a second proof surface | include |
| Diagnostic shaping | `doctrine/diagnostics.py::_COMPILE_PATTERN_BUILDERS` | Add review messages using the existing pattern-driven mapping style | Prevents undocumented or unstable review codes | include |
| Live docs index | `README.md`, `docs/README.md`, `examples/README.md` | Extend the shipped surface narrative and corpus range through `49` | Prevents repo entrypoints from lying about shipped truth | include |
| Workflow boundary docs | `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_DESIGN_NOTES.md` | Add review boundary and output-agreement narrative without replacing workflow law | Prevents readers from inferring the wrong semantic boundary or a stale shipped-surface ceiling | include |
| VS Code proof | `editors/vscode/tests/unit/*`, `editors/vscode/tests/snap/examples/**`, `editors/vscode/tests/integration/suite/index.js` | Mirror new review syntax and clickable refs across all three proof layers | Prevents editor/compiler parity drift | include |
| Editor runtime | `editors/vscode/extension.js`, `editors/vscode/package.json`, `editors/vscode/Makefile` | Keep current activation and packaging model | Avoids architecture theater around review support | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria and
> explicit verification with the smallest credible signal. Refactors,
> consolidations, and shared-path extractions must preserve existing behavior.
> No fallbacks, runtime shims, sidecar evaluators, review-only renderers,
> review-only verifier lanes, or editor-only review semantics are allowed.
> Keep `output` as the one produced-contract primitive, keep review proof inside
> the existing manifest lanes unless a real gap is proven, and document only
> the high-leverage boundary comments needed to prevent future drift.

## Phase 1 — Review grammar and AST foundation

Goal:
- Make the full review surface parseable and representable in the shipped AST
  without changing semantics by convention or ad hoc dictionaries.

Work:
- Add top-level `review` and `abstract review` declarations to
  `doctrine/grammars/doctrine.lark`.
- Add reserved `review:` agent-field syntax, review config surfaces, review
  sections, outcome sections, review statements, review-match heads, and
  `expr not in expr`.
- Add matching review dataclasses, body items, outcome nodes, and field-binding
  types to `doctrine/model.py`.
- Add parser lowering in `doctrine/parser.py`, including narrow parse-time
  failures for invalid review shape and placement, while reusing the existing
  call-expression path for `present(...)` / `missing(...)`.
- Add only the boundary comments needed to explain the reserved review
  declaration and agent-slot split.

Verification (smallest signal):
- Run targeted `parse_fail` proof for the first invalid review shapes as soon as
  those manifests exist.
- Run the first positive review manifest directly once example `43` exists.
- Run `make verify-examples` before leaving the phase because grammar changes
  touch shared surfaces.

Docs/comments (propagation; only if needed):
- Keep live docs unchanged in this phase except for touched inline comments that
  would otherwise become false immediately.

Exit criteria:
- The AST can represent every syntactic surface required by
  `docs/REVIEW_SPEC.md`.
- Existing non-review corpus still parses and compiles unchanged.

Rollback:
- If review grammar destabilizes shared surfaces before compiler support is
  ready, revert the grammar/model/parser widening rather than leaving a
  parse-only half-surface behind.

## Phase 2 — Compiler structural ownership, inheritance, contract export, and diagnostics

Goal:
- Land one canonical review compiler path that understands review declarations
  as real semantic owners rather than generic authored slots.

Work:
- Add review indexing, caches, and reference resolution in
  `doctrine/compiler.py` beneath the existing `compile_prompt()` /
  `CompilationContext.compile_agent()` entrypoint.
- Reserve `review` in `_RESERVED_AGENT_FIELD_KEYS`, add the typed review field
  path, enforce `workflow` xor `review`, and reject abstract-review attachment
  on concrete agents.
- Implement review declaration resolution, explicit inheritance, reserved
  section patch accounting, and the addressable review-body mirror for
  `inherit` / `override`.
- Implement review-contract workflow validation and first-level gate export
  from resolved workflow law before review outcome evaluation begins.
- Add the structural half of the reserved `E470` through `E499` diagnostic band
  in `doctrine/diagnostics.py`, plus the smallest `diagnostic_smoke.py` cases
  that the corpus will not already cover.
- Add one or two high-leverage compiler comments where review-contract
  flattening and inheritance accounting would otherwise be hard to recover.

Verification (smallest signal):
- Run targeted review `compile_fail` manifests for slot exclusivity, invalid
  contract targets, bad inheritance shapes, and invalid reserved review
  sections as they land.
- Re-run nearby non-review sentries that touch shared inheritance and routing
  surfaces, especially `examples/37_*`, `examples/41_*`, and `examples/42_*`.
- Run `make verify-diagnostics` when review codes or message patterns land.
- Run `make verify-examples` before leaving the phase.

Docs/comments (propagation; only if needed):
- Update only the touched compiler comments that would otherwise keep implying
  `workflow` is the lone special semantic owner.

Exit criteria:
- The compiler can resolve review declarations, validate structural review
  requirements, export contract gates, and reject invalid attachment and
  inheritance shapes with stable review codes.

Rollback:
- If inheritance accounting or contract export cannot be made coherent on the
  canonical compiler path, revert the entire review compiler entrypoint rather
  than leaving slot exclusivity or partial structural checks behind.

## Phase 3 — Review evaluation, semantic addressability, output agreement, and render shape

Goal:
- Make review turns semantically real end to end: verdict, failing gates,
  routing, currentness, carried state, readable refs, and truthful output
  coupling.

Work:
- Implement gate evaluation order exactly as the spec defines, including
  blocked review handling and total accepted/rejected routing.
- Implement subject-set disambiguation via currentness, `subject_map`, or
  explicit reviewed-artifact proof.
- Bind currentness reuse via `current artifact ... via Output.field` and
  `current none`, plus carried `active_mode` and `trigger_reason` on
  `comment_output`.
- Extend compiler-owned readable and addressable surfaces so `contract.*` and
  resolved `fields.*` become legal only after review resolution across
  authored-prose interpolation, readable refs, guarded-output expressions, and
  the mirrored editor follow surface.
- Widen output validation so review semantic refs participate in guarded-output
  timing correctly, and preserve the existing `standalone_read` guarded-readback
  fence.
- Keep `renderer.py` generic by compiling review into ordinary
  `CompiledSection` trees instead of adding a second serializer.
- Land the remaining evaluation/output-agreement review diagnostics and smoke
  coverage needed to keep the `E470` through `E499` band honest.

Verification (smallest signal):
- Run targeted manifests for examples `43`, `46`, `47`, and `49` as the
  semantics they depend on come online.
- Re-run nearby non-review sentries that guard output/currentness/readback
  boundaries, especially `examples/39_*` and `examples/42_*`.
- Run `make verify-diagnostics` when review code mappings or wording change.
- Run `make verify-examples` before leaving the phase.

Docs/comments (propagation; only if needed):
- Update touched compiler comments so review timing, output agreement, and the
  no-shadow-carrier rule are stated truthfully at the canonical boundary.

Exit criteria:
- Positive review examples can render truthfully through the generic renderer.
- Review semantic refs are only legal on the blessed post-resolution surfaces.
- Invalid review outcomes, currentness, and output agreement fail loudly with
  stable review-specific codes.

Rollback:
- If output agreement or timing cannot be made truthful on the canonical path,
  revert the review-evaluation path rather than leaving review renders coupled
  only by prose convention.

## Phase 4 — Review ladder foundation examples `43` through `46`

Goal:
- Ship the first four review rungs as both proof and teaching material.

Work:
- Add fully commented prompts, manifests, refs, and adjacent narrow invalid
  siblings for:
  - `43_review_basic_verdict_and_route_coupling`
  - `44_review_handoff_first_block_gates`
  - `45_review_contract_gate_export_and_exact_failures`
  - `46_review_current_truth_and_trust_surface`
- Keep each rung to one new idea, keep names generic, and keep the explanatory
  burden in prompt comments and checked refs rather than sidecar prose.
- Keep proof inside the existing manifest lanes; do not widen the verifier
  unless a concrete review requirement truly cannot fit `render_contract`,
  `build_contract`, `parse_fail`, or `compile_fail`.

Verification (smallest signal):
- Run each new manifest directly once created.
- Run targeted invalid manifests for the adjacent narrow negatives.
- Run `make verify-examples` after all four rungs land.

Docs/comments (propagation; only if needed):
- Only the example comments and refs should carry the teaching load in this
  phase; avoid new explanatory planning sidecars.

Exit criteria:
- Rungs `43` through `46` pass, teach one new idea per rung, and their invalid
  siblings prove the intended validation surfaces.

Rollback:
- If a rung is too broad or conflates ideas, split or rewrite it before
  landing; do not keep a muddy rung and promise to clarify it later.

## Phase 5 — Advanced review ladder examples `47` through `49`

Goal:
- Finish the review corpus at full semantic depth, not just the easy subset.

Work:
- Add fully commented prompts, manifests, refs, and adjacent narrow invalid
  siblings for:
  - `47_review_multi_subject_mode_and_trigger_carry`
  - `48_review_inheritance_and_explicit_patching`
  - `49_review_capstone`
- Ensure `49` proves the full bundle: block, contract gates, preserved truth
  assertions, `support_only`, `ignore ... for rewrite_evidence`,
  multi-subject review, carried mode and trigger reason, and both currentness
  forms.
- Compare the comment density and teaching rhythm of an early review rung, a
  truth/carrier rung, and the capstone against the shipped late ladder instead
  of letting the advanced review examples collapse into terse fixtures.

Verification (smallest signal):
- Run each new manifest directly once created.
- Run targeted invalid manifests for advanced review negatives.
- Re-run `make verify-examples` after all advanced rungs land.

Docs/comments (propagation; only if needed):
- Keep the same authoring clarity as examples `39` through `42`; do not move
  teaching burden into docs that should simply describe shipped truth.

Exit criteria:
- The review corpus truly runs through `49` and covers the full spec, not a
  trimmed subset.

Rollback:
- If the capstone is too tangled to teach, refactor the example structure
  without cutting semantics.

## Phase 6 — Live docs, error references, and corpus indexes

Status: complete 2026-04-11

Current implementation notes:
- `AGENTS.md`, `README.md`, `docs/README.md`, `examples/README.md`,
  `docs/WORKFLOW_LAW.md`, `docs/LANGUAGE_DESIGN_NOTES.md`,
  `docs/COMPILER_ERRORS.md`, and `docs/REVIEW_SPEC.md` now agree that review
  ships through `examples/49_review_capstone`.
- The canonical review reference now uses shipped-reference framing instead of
  stale implementation-follow-through wording.
- `docs/AGENT_IO_DESIGN_NOTES.md` now also runs through examples `08` to `49`
  and explicitly documents review `comment_output` carriers, `active_mode` /
  `trigger_reason` carried state, review-bound guarded semantic refs, and
  output-agreement checks, so the live I/O notes no longer stop at the
  pre-review surface.

Goal:
- Make the live docs tell the same truth as the shipped compiler and examples.

Work:
- Promote `docs/REVIEW_SPEC.md` from detached design artifact to live shipped
  reference without rewriting away its instruction-bearing structure.
- Update `README.md`, `docs/README.md`, and `examples/README.md` to describe
  the shipped review surface, corpus range through `49`, and the start-here
  path for review.
- Update `docs/WORKFLOW_LAW.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, and
  `docs/LANGUAGE_DESIGN_NOTES.md` so they no longer stop at `42`, imply review
  is unshipped, or omit review-output agreement semantics.
- Update `docs/COMPILER_ERRORS.md` for the live review diagnostic band.
- Delete or rewrite stale proposal framing in any touched live doc instead of
  leaving legacy wording behind after ship.

Verification (smallest signal):
- Re-run `make verify-diagnostics` if error wording, code tables, or smoke
  descriptions changed.
- Re-run `make verify-examples` if doc-linked refs or manifests changed.
- Manually confirm no touched live doc still frames review as non-shipped or
  the corpus as ending at `42`.

Docs/comments (propagation; only if needed):
- Preserve instruction-bearing detail when moving text from proposal framing to
  live reference framing; do not silently summarize away operational rules.

Exit criteria:
- Live docs, examples, and compiler behavior agree on what review is and what
  ships.

Rollback:
- If a docs update gets ahead of the implementation, revert the docs change
  until the code and examples are ready instead of publishing aspirational
  truth.

## Phase 7 — VS Code grammar, resolver, tests, and README

Goal:
- Keep the editor authoring experience aligned with the shipped review
  language, including full colorization and Ctrl/Cmd-followable review refs.

Work:
- Update `syntaxes/doctrine.tmLanguage.json` so review declarations, outcome
  headers, review-match patterns, and review slot lines scope correctly before
  the generic keyed rules.
- Update `language-configuration.json` so all relevant `onEnterRules` buckets
  understand review declaration bodies and outcome sections.
- Update `resolver.js` so it indexes review declarations, handles reserved
  review keys, resolves inherited review bodies, mirrors the review-slot
  inheritance path, and exposes the shipped clickable review-local refs for
  lowercase `contract.*` and `fields.*` paths without inventing editor-only
  semantics.
- Update `scripts/validate_lark_alignment.py` with review lexical samples for
  declaration lines, `review:` slots, outcome headers, review-match syntax,
  `subject_map` entries, and keyword-identifier cases that must remain plain
  authored identifiers.
- Update unit fixtures, snapshots for `43` through `49`, integration tests for
  review Ctrl/Cmd-follow coverage, and `editors/vscode/README.md`.

Verification (smallest signal):
- Run `cd editors/vscode && make`.
- If the resolver changed substantially, smoke-check one review declaration,
  one `review:` slot, one inherited review body, one `contract.<gate>` ref,
  and one lowercase review-local path in a live editor.

Docs/comments (propagation; only if needed):
- Add a brief resolver boundary comment if needed to explain that the editor is
  mirroring only the shipped clickable review surface.

Exit criteria:
- The editor mirror accepts the shipped review syntax, scopes it correctly, and
  proves full review colorization plus shipped clickable review refs through
  Ctrl/Cmd-follow navigation.

Rollback:
- If an editor-side rule requires a second parser, Python bridge, or broad
  heuristic rewrite, back it out and redesign within the current adapter
  architecture.

## Phase 8 — Full verification, cleanup, and artifact convergence

Status: complete 2026-04-10

Current implementation notes:
- The prior truth-cleanup sweep removed the stale `AGENTS.md` and
  `docs/REVIEW_SPEC.md` contradictions that the earlier audit found.
- Fresh code-verifiable checks in this environment still pass via the checked-in
  `.venv`: `./.venv/bin/python -m doctrine.verify_corpus`,
  `./.venv/bin/python -m doctrine.diagnostic_smoke`, `npm run test:unit`,
  `npm run test:snap`,
  `./.venv/bin/python editors/vscode/scripts/validate_lark_alignment.py`, and
  `./.venv/bin/python editors/vscode/scripts/package_vsix.py`.
- `uv sync`, `make verify-examples`, and `make verify-diagnostics` are
  sandbox-blocked here because `uv` cannot access `~/.cache/uv`, while
  `cd editors/vscode && make` reaches the JS checks but the Electron
  integration runner aborts with `SIGABRT` after locating the local VS Code
  install.

Goal:
- Finish with one coherent shipped truth across code, examples, docs, and
  editor support.

Work:
- Run `uv sync` if needed.
- Run `make verify-examples`.
- Run `make verify-diagnostics` if diagnostics changed.
- Run `cd editors/vscode && make` if the editor adapter changed.
- Re-check touched live docs, comments, and indexes for stale pre-review or
  pre-`49` wording and delete dead truth surfaces instead of preserving them.
- Confirm there is no surviving sidecar review code path, review-only proof
  lane, or editor-only review interpretation.
- Record meaningful plan drift or approved exceptions in the Decision Log; do
  not silently leave contradictions behind.

Verification (smallest signal):
- The commands above are the authoritative final signals.

Docs/comments (propagation; only if needed):
- Final pass only for truth alignment and dead-truth cleanup, not new feature
  scope.

Exit criteria:
- The full review surface ships end to end and the repo no longer contains a
  live contradiction between the spec, implementation, corpus, docs, and
  editor.

Rollback:
- If final verification exposes a contradiction, reopen the owning phase and
  fix it there instead of papering it over in docs or refs.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Canonical checks

- `uv sync`
- `make verify-examples`
- `make verify-diagnostics` when diagnostics or smoke checks changed
- `cd editors/vscode && make` when editor surfaces changed

## 8.2 Development-time checks

- Run single-manifest proof while developing each rung:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/43_review_basic_verdict_and_route_coupling/cases.toml`
  - repeat for `44` through `49` once those examples exist
- Use compile-fail and parse-fail cases as the main review diagnostic proof.
- When shared compiler behavior changes, re-run the strongest nearby non-review
  sentries from `examples/37_*`, `examples/39_*`, `examples/41_*`, and
  `examples/42_*` alongside the in-flight review manifest.
- Use the full corpus run before leaving each major phase that touches shared
  compiler behavior.

## 8.3 Manual checks (non-blocking but useful)

- Read the compiled `AGENTS.md` refs for one basic review example, one
  currentness example, and the capstone to ensure the prose reads naturally.
- In a live editor, smoke-check one `review` declaration, one `review:` agent
  slot, one `contract.<gate>` reference, one review field-binding path, and
  one carried-state field if VS Code support changed.

## 8.4 Signals we will not add

- No bespoke runtime harness for review/output agreement.
- No separate golden-doc framework outside the existing ref and manifest
  surfaces.
- No VS Code-only proof machinery outside the current unit, snapshot,
  integration, and alignment-validator setup.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout

- This is a hard-cut repo ship. There is no runtime flag, migration shim, or
  compatibility mode because no shipped `review` primitive exists today.
- The rollout unit is one merged repo truth: compiler, corpus, docs, and
  editor support all aligned.

## 9.2 Ops

- Ops burden is local repository maintenance only:
  - keep the corpus green
  - keep error docs aligned
  - publish a fresh VSIX if the extension changes
- No external service, deploy pipeline, or telemetry dashboard is in scope.

## 9.3 Telemetry / health signals

- The health signals are the shipped verification commands and the checked
  example refs.
- The doc health signal is that no live doc still frames review as non-shipped
  after the feature lands.
- The editor health signal is `cd editors/vscode && make` plus a brief manual
  smoke if desired.

# 10) Decision Log (append-only)

- 2026-04-10: Created the canonical full-arch artifact for full review-spec
  implementation at the user's explicit request for no scope cuts.
- 2026-04-10: Kept `fallback_policy: forbidden`. The plan does not permit a
  smaller interim review surface, runtime shims, or editor-only compatibility.
- 2026-04-10: Chose `docs/REVIEW_SPEC.md` as the one binding reference to fold
  into this plan verbatim instead of paraphrasing it into a side checklist.
- 2026-04-10: Chose to ship examples `43` through `49` fully commented like
  examples `30` through `42`, because the review spec itself defines an
  example ladder and the repo is example-first.
- 2026-04-10: Rejected external-research-first planning for this change. The
  remaining work is local implementation of a frozen repo spec, not an open
  design problem.
- 2026-04-10: Locked the runtime architecture for `review` to the existing
  grammar -> parser -> model -> compiler -> renderer path as a sibling of
  `workflow`; rejected a sidecar evaluator, review-only renderer, review-only
  verifier lane, or generic-authored-slot fallback as the implementation
  shape.
- 2026-04-10: Deep-dive locked review-local semantic refs such as
  `contract.*` and review `fields` to compiler-owned readable/addressable
  surfaces mirrored by VS Code; rejected editor-only synthetic review
  semantics and a second ref system.
- 2026-04-10: Left the artifact in `draft` because this run began as
  `arch-step new`, but the scope and phase plan are already fully drafted so a
  later confirmation should only change `status`, not the technical scope.
- 2026-04-10: Phase-plan locked the authoritative execution order to grammar
  and AST foundation -> structural compiler ownership -> review evaluation and
  output agreement -> review ladder -> live docs -> VS Code parity -> final
  convergence; rejected a separate verifier expansion phase and any editor-only
  shortcut path.
