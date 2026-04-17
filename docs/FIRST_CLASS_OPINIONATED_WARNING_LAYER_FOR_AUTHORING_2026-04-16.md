---
title: "Doctrine - First-Class Opinionated Warning Layer For Authoring - Audit"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: audit
related:
  - PRINCIPLES.md
  - docs/AUTHORING_PATTERNS.md
  - docs/COMPILER_ERRORS.md
  - docs/FAIL_LOUD_GAPS.md
  - docs/FAIL_LOUD_GAP_AUDIT_AND_ENFORCEMENT_2026-04-16.md
  - docs/DOCTRINE_LANGUAGE_AUDIT_2026-04-16.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/AUTHORING_PATTERNS.md
  - docs/EMIT_GUIDE.md
  - examples/README.md
  - doctrine/diagnostics.py
  - doctrine/_diagnostics/contracts.py
  - doctrine/_compiler/diagnostics.py
  - doctrine/_compiler/context.py
  - doctrine/_compiler/session.py
  - doctrine/_compiler/package_layout.py
---

# TL;DR

- Outcome: Doctrine gets a clear plan for a first-class warning layer that
  makes valid-but-bad authoring hard to miss without turning Doctrine into a
  second harness or a generic style linter.
- Problem: Doctrine has a strong error story for invalid source, but it has no
  first-class way to say "this compiles, but it is bloated, duplicated,
  shadowing typed truth, or pushing against the project principles."
- Approach: add warning diagnostics on the same authoring graph, source spans,
  and compile pipeline that already power parse, compile, and emit errors.
- Plan:
  1. add real warning severity and report surfaces
  2. ship one small first wave of high-confidence warning families
  3. prove them on Doctrine and keep any outside-repo examples read-only
  4. add strict mode and suppression only after the warning codes are stable
- Non-negotiables:
  - no second semantic model
  - no LLM judge or vibe-based lint
  - no Rally-only or psflows-only rules in core Doctrine
  - if the compiler can prove semantic wrongness, the long-term home is an
    error, not a warning
  - warnings must point at one Doctrine-native fix, not vague taste

# 0) Holistic North Star

## 0.1 The claim

If Doctrine ships a first-class warning layer for valid-but-bad authoring,
authors will get early and clear guidance on bloat, duplication, weak
load-boundary design, and narrow typed-truth shadowing before those problems
turn into drift, confusing runtime Markdown, or repo-local rule piles.

## 0.2 In scope

- Add a real non-fatal diagnostic path to Doctrine.
- Reuse the current source spans, excerpts, related sites, codes, and
  formatting shape from the error system.
- Keep warning ownership inside Doctrine's existing authoring pipeline:
  parser, index, resolve, validate, compile, render, and emit.
- Ship a first wave of deterministic warning families that line up with
  Doctrine's own principles:
  - context budget
  - reuse pressure
  - narrow semantic shadowing
  - short bridge warnings for proven fail-loud gaps only when an immediate
    breaking error is not yet ready
- Add docs, tests, and manifest-backed proof for shipped warnings.
- Make warning output visible in compile, emit, and corpus verification
  surfaces.
- Use any sibling repo examples only as read-only reference material, not as
  edit targets for this work.

## 0.3 Out of scope

- Rally runtime facts such as `allowed_skills`, MCP allowlists, run-home
  layout, session control, or final JSON rules.
- Editing sibling repos such as `../rally` or `../psflows`.
- Product-specific smells such as one repo's banned sidecar file names.
- Prose grading for tone, elegance, or "good writing" in the abstract.
- A general lint framework with many knobs and host-specific policy planes.
- Turning known semantic bugs into permanent warnings instead of fixing them as
  errors.
- Warning on comments, generated files, or repo-local build output.

## 0.4 Acceptance evidence

- Doctrine can return warnings without raising an exception.
- Warning output uses the same location quality and message shape as current
  errors.
- `emit_docs` and corpus verification can surface warnings in a machine-usable
  report.
- Doctrine ships one stable warning reference doc with codes, meaning, and
  fix guidance.
- The first warning wave finds real issues in Doctrine's own corpus without
  mostly lighting up intentional authoring.

## 0.5 Key invariants

- Errors stay fail-loud.
- Warnings stay deterministic.
- One rule has one owner.
- No second harness.
- No repo-specific workflow law in core Doctrine.
- Warnings must be explainable from authored source or compiled graph facts.
- Warnings are non-fatal by default in the first wave.
- Suppression, if added later, must stay explicit and reviewable.
- Warning reports stay sideband authoring output, not runtime package truth.

# 1) The Missing Layer

Doctrine already has three strong layers:

1. parse errors for bad syntax
2. compile and emit errors for invalid or unsafe authored meaning
3. docs, examples, and principles that teach good shape

What it does not have is a first-class layer for this fourth case:

> The source is valid, but it is using Doctrine in a way that is bloated,
> duplicated, weakly named, or quietly fighting the principles.

That gap is already visible in the repo.

- `PRINCIPLES.md` says Doctrine should "move toward warnings, docs, and
  patterns that expose oversized agent homes, copied prose, weak
  descriptions, and bad boundaries."
- `docs/FAIL_LOUD_GAP_AUDIT_AND_ENFORCEMENT_2026-04-16.md` explicitly keeps
  style and best-practice lint out of the error path.
- `docs/LANGUAGE_REFERENCE.md`, `docs/AUTHORING_PATTERNS.md`,
  `docs/DOCTRINE_LANGUAGE_AUDIT_2026-04-16.md`, and
  the live render guidance in `docs/EMIT_GUIDE.md` plus `examples/README.md`
  all document real
  repetition, awkward surface shape, or misleading valid authoring that is not
  yet owned by the compiler.
- Reference-only use cases in sibling repos point at the same general problem:
  keep roles thin, move repeated judgment into skills, keep exact truth on
  deterministic surfaces, and do not create shadow control planes. Doctrine
  still does not make those failures visible on its own.

Today the author only learns about many of these problems through:

- a manual repo review
- a dated audit doc
- a porting guide
- a shared root `AGENTS.md`
- local tests in a host repo

That is too late and too indirect for a framework that wants to make the good
path obvious.

# 2) Current State Audit

## 2.1 What exists today

- `DoctrineDiagnostic` carries `code`, `stage`, `summary`, `detail`, location,
  excerpt, related sites, hints, trace, and cause.
- `format_diagnostic()` always prints `error`.
- `ParseError`, `CompileError`, and `EmitError` are exception-first.
- `CompilationSession` and `CompilationContext` have no report object or
  warning collector.
- `doctrine/_compiler/diagnostics.py` and
  `doctrine/_compiler/output_diagnostics.py` already provide structured helper
  seams for error locations.
- A large amount of compile behavior still raises raw `CompileError("...")`
  strings, and there is active work underway to tighten exact error spans and
  shared diagnostic construction.
- That helper cleanup matters for warnings too. If Doctrine adds warnings
  before it reuses the same exact-site seams, it will duplicate the same
  diagnostic debt on a second path.

## 2.2 What is missing

- No severity field.
- No non-fatal diagnostic collector.
- No warning reference docs.
- No corpus proof for warning expectations.
- No policy line that says what belongs in a warning and what belongs in an
  error.
- No way for `emit_docs` or verification to say "this built, but the source is
  probably misapplied."

## 2.3 Why this matters now

The repo is already doing the thinking that a warning layer would need.
Doctrine has:

- fail-loud audits for semantic wrongness
- elegance plans for repeated but valid authoring
- render audits for output bloat
- principles that explicitly call for visible bloat and bad boundaries

The missing part is not insight.
The missing part is a first-class mechanism.

# 3) What Doctrine Should Own

Doctrine should own a warning only when all of these are true:

- The signal is visible from Doctrine's own source graph or compiled output.
- The fix is a Doctrine authoring change.
- The rule is generic across many repos.
- The message can point to a concrete place and a concrete fix.
- The false-positive risk is low enough to ship by default.

Doctrine should not own the warning when the problem depends on:

- runtime config outside the prompt graph
- adapter behavior
- repo-specific policy names
- product semantics
- tool allowlists that Doctrine does not model
- subjective writing taste

## 3.1 Ownership table

| Pressure | Best owner | Why |
| --- | --- | --- |
| Oversized role homes and large local prose blocks | Doctrine warning | Doctrine can see emitted size and local authoring shape. |
| Repeated prose or repeated step lists across agents | Doctrine warning | The compile graph can detect normalized duplication. |
| Weak names or weak descriptions on reusable load boundaries | Doctrine warning later | Doctrine owns resolver-facing names, but this needs a tight scope. |
| Typed truth mirrored by a second authored control surface | Doctrine warning in narrow cases | Doctrine can see the typed surface and the duplicate carrier in the same graph. |
| Per-agent `allowed_skills` drift | Rally or host repo | That truth lives in `flow.yaml`, not in Doctrine. |
| Sidecar product files like `COPY_GROUNDING.md` | Host repo docs or tests | The names are repo-specific. |
| Subject-matter copy quality | Skills, review, or product repo | Doctrine cannot judge domain meaning in a general way. |
| Proven semantic wrongness | Doctrine error | This is the fail-loud boundary, not a warning boundary. |

# 4) Ranked Findings

## 4.1 Highest finding: Doctrine has the principle but not the mechanism

The principles already ask for visible bloat, copied prose, weak descriptions,
and bad boundaries. The shipped diagnostic model still only knows how to raise
errors.

That means the framework is relying on prose and human review for exactly the
class of misuse it says should be made visible.

## 4.2 The strongest real pressure is shadow authority

Read-only use cases outside this repo fight the same problem:

- second state surfaces
- prose summaries of deterministic truth
- repeated instructions that should have one owner
- duplicated route or currentness truth
- growing role homes that carry too much always-on ballast

Doctrine cannot see most repo-local runtime drift.
But it can see the authoring shapes that often create it:

- repeated shared procedure
- manual restatement of typed truth
- large always-on prose bodies
- load-boundary names that do not help a resolver

## 4.3 The best first-wave warning families are already visible

The most grounded candidates from Doctrine's own docs and the read-only
reference audit
are:

- context budget
- reuse pressure
- narrow semantic shadowing

Those are high-value because they are:

- principle-backed
- generic
- visible from the compile graph
- actionable without a second harness

## 4.4 Some tempting warnings should stay out for now

Do not ship first-wave warnings for:

- tone
- voice
- "good writing"
- generic naming taste across all declarations
- product-specific sidecar files
- any rule that depends on Rally `flow.yaml` or run state

Those would either leak framework boundaries or turn Doctrine into a style
linter.

## 4.5 Some fail-loud gaps may deserve a warning bridge, but only as a bridge

Examples:

- near-miss reserved field typos
- duplicate review singleton blocks
- literal guards
- semantic misbindings that look compiler-owned

If the repo already believes these are wrong, the long-term answer is an
error. A warning is only useful when release timing or compatibility posture
means the hard error cannot land yet.

# 5) Candidate Warning Catalog

## 5.1 First-wave warning families

These are the strongest candidates for the first shipped wave.

| Family | Example signal | Owner phase | Why it matters | First-wave posture |
| --- | --- | --- | --- | --- |
| `Context budget` | a concrete agent renders an unusually large always-on home, or a local section carries a very large prose block | compile or emit | Doctrine exists to keep always-on context small | ship |
| `Reuse pressure` | normalized prose, step lists, or typed scaffolds repeat across agents or modules in one compile graph | index, resolve, or compile | repeated doctrine should get one owner | ship |
| `Narrow semantic shadowing` | one agent carries review or route control meaning twice through separate authored surfaces | resolve or compile | typed truth should not be mirrored by a second local control plane | ship, but keep scope tight |
| `Transition fail-loud bridge` | a proven fail-loud gap still compiles in a way that looks valid | parse, resolve, or validate | do not let known-danger shapes look normal while waiting for a hard error | ship only where the repo already agrees |

## 5.2 Second-wave candidates

These look useful, but they need more proof before they should be default-on.

| Family | Example signal | Why defer |
| --- | --- | --- |
| `Resolver quality` | vague names or weak descriptions on `skill`, package, or reusable declaration boundaries | useful, but easy to make noisy if it becomes generic prose scoring |
| `Long qualified-ref sprawl` | one block repeats long imported paths many times | high value, but current syntax still lacks some of the planned alias and grouped-inherit relief |
| `Mixed-scope skill handbook` | one skill owns several distinct jobs and proof surfaces | useful, but some broader skills are intentional |
| `Bulky read-list prose` | long file-path lists embedded in prose instead of a typed bundle | useful, but may depend on repo-local habits |

## 5.3 Warning families to keep out

- flow-aware runtime checks
- host repo policy names
- code-style opinions
- prose taste scoring
- content correctness that needs domain judgment
- warnings on comments or generated outputs

# 6) Concrete High-Value Warning Shapes

## 6.1 Split review and final-output restatement

Doctrine's own render audit already calls this a major bloat front.
The authored source in the split review examples can bind the same review
semantics once on the review carrier and again on `final_output.review_fields`.

Good warning:

> `W310` compile warning: Final output repeats review semantics already owned
> by the review carrier. Keep the control surface small or remove duplicate
> review-field mappings.

Why this belongs:

- Doctrine can see both surfaces.
- The fix is local and clear.
- It aligns with typed-truth and render-bloat principles.

Why this must stay narrow:

- some split review outputs are intentionally asymmetric
- only warn when the overlapping semantic set is large and clearly redundant

## 6.2 Sole-child wrapper title echo

Doctrine already has active docs about omitted wrapper titles and duplicate
heading drift.

Good warning:

> `W211` compile warning: Wrapper title matches its only child title. Omit the
> wrapper title or add wrapper-only meaning.

Why this belongs:

- it is visible from structure alone
- it points to a real source of render bloat
- it does not need subject-matter judgment

## 6.3 Oversized agent home

This is the cleanest match for Doctrine's principles.

Good warning:

> `W110` emit warning: Concrete agent `SectionDossierEngineer` renders an
> oversized always-on home. Move deep reference material into shared doctrine,
> a skill, or a narrower reusable declaration.

Good rule shape:

- use rendered size plus local authoring facts
- warn on the agent, not on every line
- include a short summary of what made it large

## 6.4 Repeated prose or repeated typed scaffold

The same "one owner per rule" pressure shows up in read-only reference repos
too.
Doctrine can help by showing when the same rule appears again.

Good warning:

> `W210` compile warning: This step list repeats the same normalized text used
> by `SharedReadFirst`. Move the shared rule into one named workflow or shared
> declaration.

And:

> `W212` compile warning: Adjacent branches repeat the same preservation and
> invalidation scaffold with only the target changed. Factor the shared family.

Important restraint:

- do not warn per line
- warn on the repeated block family
- ignore comments and generated output

## 6.5 Bridge warnings for strict-looking but lossy surfaces

If a surface already looks compiler-owned but still accepts a likely mistake,
the author should not be left unaware.

Good warning:

> `W320` compile warning: This surface looks compiler-owned, but the current
> shape can still accept a plausible typo or overwrite. Prefer exact field,
> helper, and binding names.

This is useful only as a bridge.
If the repo has already settled that the shape is wrong, it should graduate to
an error.

# 7) Proposed Warning Model

## 7.1 Diagnostic contract

Extend `DoctrineDiagnostic` so it can represent warnings directly.

Recommended additions:

- `severity: "error" | "warning"`
- `category: str | None`
- reserve a stable `W` code band for warnings

Keep the rest of the current shape:

- stable code
- stage
- summary
- detail
- location
- excerpt
- related
- hints
- trace
- cause

This keeps errors and warnings on one shared formatting and JSON path.

## 7.2 Do not change the core exception model

Errors should keep raising `ParseError`, `CompileError`, and `EmitError`.

Warnings should be collected, not raised.

Recommended public additions:

- `CompilationReport`
- `EmitReport`
- `CompilationSession.compile_agent_report(...)`
- `CompilationSession.compile_skill_package_report(...)`
- `emit_target_report(...)` or an additive report mode for `emit_target(...)`

Keep `compile_prompt()` unchanged for backward compatibility.
It can stay the thin "compiled agent or exception" path.

## 7.3 Warning collector

Add one report collector that lives on the compile task, not on a second
global plane.

Recommended shape:

- new warning package under `doctrine/_compiler/warnings/`
- `WarningCollector`
- `WarningMixin` added to `CompilationContext`

Hard rule:

- warning passes may read existing indexed, resolved, compiled, or emitted
  facts
- warning passes may not create a second semantic model
- warning passes may not parse rendered Markdown back into meaning

## 7.4 Suggested internal module shape

```text
doctrine/_compiler/
  warnings/
    __init__.py
    collector.py
    budget.py
    reuse.py
    shadowing.py
    bridge.py
```

And then wire it through:

- `doctrine/_compiler/context.py`
- `doctrine/_compiler/session.py`
- `doctrine/_compiler/diagnostics.py`
- `doctrine/diagnostics.py`

## 7.5 Message shape

Warnings should look like errors, except for severity.

Example:

```text
W210 compile warning: Repeated workflow guidance block

Location:
- prompts/agents/reviewer.prompt:18:5

Related:
- matching block: prompts/shared/workflows.prompt:4:5

Detail:
- This step list repeats the same normalized text already used by `SharedReadFirst`.

Hint:
- Move the shared rule into one named workflow or shared declaration and `inherit` it.
```

This keeps the warning path clear, local, and actionable.

# 8) Current Architecture

## 8.1 Current compile path

```text
parse_file
  -> PromptFile
  -> CompilationSession
      -> index root and imports
      -> CompilationContext
          -> resolve
          -> validate
          -> compile
      -> render_markdown / emit_docs
```

## 8.2 Current diagnostic path

```text
error condition
  -> ParseError / CompileError / EmitError
  -> DoctrineDiagnostic
  -> format_diagnostic()
```

## 8.3 Current gap

There is no peer path for:

```text
valid source
  -> warning-worthy graph fact
  -> structured warning
  -> surfaced in compile / emit / verify
```

# 9) Target Architecture

## 9.1 Target compile path

```text
parse_file
  -> PromptFile
  -> CompilationSession
      -> index root and imports
      -> CompilationContext
          -> resolve
          -> validate
          -> warning passes on existing facts
          -> compile
          -> optional render-budget warning pass
      -> CompilationReport
      -> render_markdown / emit_docs / verify_corpus
```

## 9.2 Target diagnostic path

```text
structured finding
  -> DoctrineDiagnostic(severity=error|warning)
  -> report collector
  -> formatter / JSON / corpus expectations
```

## 9.3 Target contracts and boundaries

- errors stay exception-first
- warnings stay report-first
- one shared diagnostic data model
- one shared span and excerpt path
- warning passes read existing compiler truth only
- warning reports stay outside emitted `AGENTS.md`, `SOUL.md`, schema files,
  and `final_output.contract.json`
- no host-runtime dependency in core Doctrine

# 10) Call-Site Audit

| Area | File | Current behavior | Required change | Why |
| ---- | ---- | ---------------- | --------------- | --- |
| Diagnostic model | `doctrine/_diagnostics/contracts.py` | diagnostics have no severity | add warning severity and optional category | warning layer must be first-class, not a side note |
| Diagnostic formatting | `doctrine/diagnostics.py`, `doctrine/_diagnostics/formatting.py` | formatter always says `error` | render `warning` cleanly in text and JSON | users must see warnings clearly |
| Compiler helper boundary | `doctrine/_compiler/diagnostics.py`, `doctrine/_compiler/output_diagnostics.py` | helpers build structured compile errors only | add warning constructors on the same location path | avoid a second stringly warning path |
| Compile session API | `doctrine/_compiler/session.py` | compile surfaces return compiled object or raise | add report-returning surfaces | warnings need a public transport |
| Compile task orchestration | `doctrine/_compiler/context.py` | no warning collector or pass order | wire in warning passes over existing facts | keep warnings inside the authoring pipeline |
| Emit surfaces | `doctrine/emit_docs.py`, later `emit_skill.py` and `emit_flow.py` if needed | emit prints success or errors only | surface warnings in CLI output and optional JSON report | make misapplication visible during normal author workflow |
| Corpus proof | `doctrine/verify_corpus.py`, manifest handling, example corpus | no warning expectations | add expected warning codes and report checks | make warnings a shipped surface |
| Docs | new `docs/AUTHORING_WARNINGS.md`, `docs/README.md`, `docs/VERSIONING.md`, and `docs/COMPILER_ERRORS.md` cross-links | no warning reference path | teach stable codes, warning policy, and compatibility posture | warnings need a canonical home |

# 11) Recommended Phase Plan

## Phase 1 - Build the shared warning infrastructure

### Work

- Add warning severity to the diagnostic model.
- Add report-returning compile and emit surfaces.
- Add shared warning constructors beside current compile error helpers.
- Add formatter and JSON support.
- Add one new warning reference doc and docs index link.
- Keep warning output out of emitted runtime files.

### Exit criteria

- One warning can be created with exact location, excerpt, related sites, and
  hint.
- Compile and emit callers can receive warnings without changing error
  behavior.
- Warning output is visible in text and JSON.
- Warning output does not leak into emitted runtime Markdown or emitted schema
  or contract files.

## Phase 2 - Ship one small first wave

### Work

- Implement `Context budget`.
- Implement `Reuse pressure`.
- Implement one narrow `Semantic shadowing` rule.
- Add one or two bridge warnings only where the repo already agrees the shape
  is wrong but cannot tighten to an error yet.

### Exit criteria

- Each warning family has stable codes.
- Each family has focused tests.
- Each family has at least one manifest-backed example or equivalent proof.
- First-wave warnings find real issues in Doctrine examples without mostly
  firing on intentional authoring.

## Phase 3 - Add corpus proof and normal author workflow support

### Work

- Teach `verify_corpus` how to assert warning codes.
- Surface warnings in `emit_docs`.
- Add machine-readable report output.
- Run the warning families on Doctrine. If outside examples are still useful,
  use them only as read-only reference checks.

### Exit criteria

- Normal author workflow surfaces show warnings by default.
- Corpus proof can lock expected warning behavior.
- Warning output is stable enough to document publicly.

## Phase 4 - Add strict mode and suppression only after stability

### Work

- Add opt-in warnings-as-errors.
- Add the smallest possible suppression story.
- Require a reason for any future ignore list.

### Exit criteria

- Strict mode is opt-in.
- Suppression does not create a second policy plane.
- The warning families are stable enough that a repo can choose to gate on
  them.

# 12) Guardrails For Any New Warning Family

Before a warning ships by default, answer all of these:

1. Can Doctrine prove the signal from its own graph?
2. Is the fix a Doctrine authoring change?
3. Is the rule generic across repos?
4. Can the warning point to one owner path and one likely fix?
5. Is the false-positive risk low?
6. Would a better model tomorrow still need this structural guidance?
7. If the shape is actually wrong, why is this not an error yet?

If the answer to any of these is weak, do not ship the warning by default.

# 13) Risks And Failure Modes

## 13.1 Cargo-cult factoring

If warnings are too eager, authors will split good readable doctrine into tiny
pieces just to make the warning go away.

Guardrail:

- warn on real pressure, not on every long section
- prefer one warning on one owner block, not many line-level warnings

## 13.2 Framework leakage

Read-only use cases outside this repo are useful pressure tests, but Doctrine
must stay general.

Guardrail:

- core Doctrine warnings may learn from those repos
- core Doctrine warnings may not absorb their repo-local law

## 13.3 Diagnostic debt duplication

Compile diagnostics are still moving away from raw string recovery and toward
shared exact-site helpers.

Guardrail:

- land warnings on the same helper seams
- do not build a parallel string-based warning system

## 13.4 Style-linter drift

Tone and prose taste are not a stable compile boundary.

Guardrail:

- keep wording quality out of scope except where names and descriptions affect
  loading boundaries

## 13.5 Warning creep into error territory

Some surfaces already look compiler-owned and are dangerous because they still
accept likely mistakes.

Guardrail:

- use warnings only as a short bridge
- once the repo agrees the shape is semantically wrong, move it to an error

## 13.6 Second policy plane

A warning system with many ignore lists and thresholds can recreate the same
shadow-config problem it was meant to reduce.

Guardrail:

- keep first-wave config small
- delay suppression until the codes are stable
- require reasons for future ignore paths

## 13.7 Public surface creep

Warning codes, report APIs, and corpus proof are additive public surface even
if emitted Markdown does not change.

Guardrail:

- document the compatibility rule in `docs/VERSIONING.md`
- keep the first public warning API small

# 14) Recommendation

Doctrine should build a warning layer.

It should do it in a very specific way:

- same diagnostic shape as errors
- same source spans as errors
- same compiler truth as errors
- non-fatal by default
- very small first wave
- no host-runtime leakage

The right first release is not "warn on everything ugly."
The right first release is:

1. add real warning severity and report surfaces
2. ship `Context budget`
3. ship `Reuse pressure`
4. ship one narrow `Semantic shadowing` family
5. use bridge warnings only where the repo already knows a fail-loud fix is
   coming

That would finally give Doctrine the missing middle layer between:

- hard semantic errors
- and soft human advice in docs

It would also line up with Doctrine's own promise:

make bloat visible, make misuse visible, and make the clean path obvious before
the author ships drift.
