# Language Gaps Surfaced by Layered Curriculum Authoring

**Date:** 2026-04-19
**Source of evidence:** audit of `psflows/flows/{curriculum_scope,track_shape,section_shape,lesson_plan,lesson_materialize}/` and the shared `psflows/prompts/curriculum_common/` tree, read against `doctrine/docs/LANGUAGE_REFERENCE.md`, `REVIEW_SPEC.md`, `SKILL_PACKAGE_AUTHORING.md`, and `AGENT_LINTER.md`.
**Context for a cold reader.** The psflows repo is building a layered authoring pipeline (L0 track scope → L4 lesson materialize) on top of doctrine + rally. Each layer is a `warden → producer → critic` chain. The shared surfaces for that pipeline live under `psflows/prompts/curriculum_common/`. The pipeline is mostly built in doctrine; the places where it *isn't* built in doctrine — where authors fell back to prose workarounds, separate near-duplicate files, or Bash invocations — are what this document catalogs.

## How to read this document

Each entry is a **feature request**, not a design proposal. I describe:

- **Why it bites** — the cost of not having the feature, observed in real pipeline code.
- **What we need to express** — the shape of the expressiveness authors need, at the language-user level.
- **Use case** — a concrete piece of the curriculum pipeline that demonstrates the gap.

I deliberately do not prescribe implementation — syntax, compiler internals, and feature layering are doctrine-team territory. The goal here is to make the *problems* legible so doctrine can decide how (and whether) to close them.

Requests are roughly ordered by how much prose weight each one would buy back in the curriculum pipeline.

---

## 1. Typed `gate` as a first-class, referenceable entity

### Why this bites

Review contracts in a layered authoring pipeline carry many sub-gates per contract — a typical L3 contract names fifteen-plus gates spanning output correctness, receipt dereferencing, process grounding, upstream leakage, and warden setup. Today, each gate lives as a prose token embedded inside a single `workflow`/`bullets` block: the ID (`output_gates_pass.step_concepts_subset_of_lesson_concepts`), the dimension (output / receipt / process / leakage / setup), and the check body are all spelled out in natural language inside one string.

The critic emits those IDs at runtime in a `failing_gates[]` array of bare strings. Nothing at compile time verifies that the ID the contract declares matches the ID the critic is allowed to emit, or that every ID the critic emits was declared by some contract. A typo, a rename, or a drifted copy during a round of editing silently desyncs them.

The weight shows up in file size: the curriculum pipeline's shared `review.prompt` carries roughly 4,000 words of prose primarily because every gate has to be spelled out in full inside one workflow body, with its ID inlined. Authors can't factor gates out, because there's no gate symbol to factor *to*.

### What we need to express

Gates should be declarable and referenceable as typed entities. Authors should be able to:

- Declare a gate once, give it a symbol name, and tag it with the dimension it belongs to.
- Reference the gate by symbol from multiple places — the review contract that names its check, the critic's `failing_gates` enum, prose elsewhere that quotes its ID — and have the compiler enforce that those references all resolve to the same declared gate.
- Get a compile error when a gate is declared but never referenced, or referenced but never declared, the same way unknown slots and unknown skills are caught today.

### Use case

Every curriculum critic emits `failing_gates: list[string]` on rework. Today those strings are free-form — the L0 contract names one, the L0 critic emits one, and the only thing that couples them is that both happen to spell it the same way. During the L3 build we renamed one sub-gate and had to grep across six files to keep the contract and the critic in sync. With a typed `gate` entity, the contract would declare the gate, the critic's failing-gates enum would reference it by symbol, and the rename would be a one-edit operation the compiler verified.

---

## 2. Per-case gate scoping inside `review_family`

### Why this bites

`review_family` supports case-selection today: different `subject`, `contract`, and `checks` per case, all sharing a verdict carrier and routing. What it does not support is *different gate lists per case*. All cases of one family share one flat gate set.

If four concrete critics want four *different* gate bundles while still sharing verdict shape, `next_owner`, `blocked_gate` routing, and the review-body layout, the author cannot use one review family cleanly. They fall back to declaring one abstract review base plus N concrete reviews plus N concrete contract workflows. The one thing authors actually cared about sharing per case — the gate bundle — is the one thing the family doesn't let them share.

### What we need to express

A review family should let each case declare its own gate list (or gate bundle, if gates become first-class per request §1) while still inheriting the verdict carrier, routing fields, and review-body shape from the family. From the author's seat: "producer review for L0 has these five gate groups; triage review has these three different ones; continuity review has these two others" — all plugging into the same shared review envelope.

### Use case

The curriculum proposal specs `LayerAcceptanceReview` as a four-case family:

- `producer_review` — per-layer output / receipt / process / upstream-leakage / setup gates
- `triage_review` — descendants-actually-read, rationale-dated, classification-matches-evidence
- `continuity_review` — concept-only-edit, every-edit-traces-to-prereq-violation
- `manifest_validation` — blend of deterministic C9 validation plus C8 composition audit

Each case has a genuinely different gate bundle but shares the `verdict` / `reviewed_artifact` / `failing_gates` / `next_owner` / `blocked_gate` shape so downstream state handling stays uniform. Today the pipeline ships one abstract review base plus one contract workflow per layer, which gets most of the shape sharing but re-authors the gate list from scratch every time.

---

## 3. Typed identity on note-appended outputs so they round-trip as typed inputs

### Why this bites

Rally's issue-note output target appends to `home:issue.md` without per-output declaration identity. Rally then refuses to reopen those note-backed outputs as typed previous-turn inputs on downstream agents — there is no handle to reopen on.

The practical consequence: the moment a handoff carries real structure (tables, typed sections, IO blocks), the downstream agent cannot read that structure *as a typed input*. It has two choices, neither clean:

1. Read the previous turn's final JSON (typed, but usually narrow — it carries turn-control fields, not handoff payload) plus the raw issue ledger (prose). The critic then has to reconstruct structure from prose, inside its own turn.
2. Duplicate the handoff payload onto the turn-result JSON, conflating the handoff content with the routing discriminator.

Neither preserves the typing the handoff was authored with. The typed `*HandoffNote` document declaration on the producer becomes prose-as-far-as-the-critic-is-concerned, which forces the critic to pattern-match on section headings and table shapes rather than binding fields.

### What we need to express

A handoff note with typed internal structure — documents, tables, IO blocks — should be bindable as a typed input on the next agent in the chain. Rally and doctrine together need to let authors say "this typed note output is also this typed handoff input on the downstream agent" without routing the structure through a prose ledger and reconstructing it by hand.

### Use case

Every curriculum producer writes a concrete `*HandoffNote` (`TrackScoperHandoffNote`, `TrackShaperHandoffNote`, `SectionShaperHandoffNote`, `LessonPlannerHandoffNote`) that carries multiple tables (`LessonPartitionTable`, `SiblingContinuityTable`, `PerSectionKbGroundedAnchorClaimsTable`), receipt lists, closure readbacks, and analysis sections. The critic's core job is to audit those tables row-by-row. If the handoff note had typed identity, each critic would bind the concrete handoff as a typed input, and review-body checks could reference table cells by field name. Today the review body has to talk about tables in prose (`every row in PerLessonKbGroundedAnchorClaimsTable ...`) and trust that the critic's runtime behavior is aligned with the prose description.

---

## 4. Typed receipt envelope emitted from a skill's `host_contract:`

### Why this bites

Authors often want a skill to emit, alongside its substantive result, a machine-inspectable record of what it actually did: what it queried, what query shape it used (discovery vs. confirmation vs. leading), what came back, what it cited from what came back, what it *didn't* check that the skill's procedure would normally require. This is the structural defense against LLM process fakery — a producer claiming "I consulted the knowledge base" when it paraphrased general knowledge and never issued a query.

`host_contract:` today can carry typed input slots and typed output shapes. It does not model "every invocation of this skill emits *also* a typed receipt envelope with these fields." Authors work around this by declaring the receipt shape externally — on the underlying CLI the skill wraps, or as a prose field in a handoff table — which loses doctrine-enforced typing exactly where it matters most, on the evidence surface a downstream critic audits.

### What we need to express

A skill should be able to declare, once, that its emitted tuple includes a typed receipt envelope with fields the skill itself populates. Downstream agents — especially critics — should be able to bind that receipt shape as typed input, dereference its fields by name, and let the compiler check that the receipt shape the critic expects matches the receipt shape the skill declares it emits.

### Use case

The proposal names this `ProcessReceipt`. The receipt's fields include a `queries[]` list (each entry tagged `discovery` / `confirmation` / `leading`), a `citations[]` list binding each claim back to a returned query result, and an `omissions[]` list for steps the skill's procedure would normally take but this call skipped. Every judgment-carrying skill (C2 concept curation, C3 poker-KB grounding, C4 sibling continuity, C7 scrappy-state classification, C8 manifest composition) was designed to emit one.

Today, each psmobile primitive emits a `lens.receipt_id` string buried inside an opaque envelope. Critics dereference it via Bash calls to `authoring_lens/cli.py receipts read <id>`. The typed surface — queries, query shape, citations — lives in a psmobile CLI and is read back into doctrine through prose discipline. If `host_contract:` could declare a typed receipt emission, the receipt would become a doctrine-level compile-enforced artifact, and every critic would bind it without redeclaring it per skill or per caller.

---

## 5. Declarative inheritance-enforcement lint rules

### Why this bites

Some rules are cross-agent rather than intra-agent: "every agent whose output can reach a producer must inherit `UpstreamPoisoningInvariant`"; "every curriculum-scoped critic must inherit `AuditSkills` and must not bind any write skill"; "no agent in role class X may bind both a read-only skill and its mutating sibling." These are safety-critical invariants in a layered pipeline — they prevent identifier leakage, audit-mode drift, and write-surface privilege creep — but they can only be enforced as prose discipline today.

The agent-linter is judgment-first. It flags fat context, weak handoff shape, rules-that-should-be-shared — all valuable, all heuristic. It has no way for the project author to declare a *named rule* that fires across the agent graph: "flag any agent with tag X missing module Y."

The gap is felt every time a new agent lands. The discipline lives in comment blocks on the base agent ("when a composer-style agent lands on this flow, it must inherit `UpstreamPoisoningInvariant` explicitly"), which is load-bearing *until* someone doesn't read the comment. Then an agent ships with the invariant silently missing, and the whole defense depends on code review catching what the compiler couldn't.

### What we need to express

Project authors should be able to declare named rules in their own workspace that the agent-linter applies. The rules should be:

- **Declarative** — a rule spec, not a custom Python script.
- **Scoped** — by agent tag, by flow, by file-tree location, by role class.
- **Compile-time** — failing rules break the build, not the next manual review pass.

The shape authors want: "agents matching `<scope>` must inherit `<module>`"; "agents matching `<scope>` must not bind `<skill>`"; "agents matching `<scope>` must declare `<slot>`."

### Use case

The proposal's §20 poisoning defense rests on four enforcement points. One of them, verbatim: *"Lint rule fails any agent whose output can reach a producer and does not inherit `UpstreamPoisoningInvariant`."* The curriculum pipeline ships the module, the base-agent commentary explaining when to inherit it, and the handoff filter that catches what slips through — but the lint rule itself cannot exist today, so the invariant rests on human vigilance. Every new composer-style agent is a chance for the invariant to silently go un-inherited.

---

## 6. Parameterized abstract agents

### Why this bites

When N concrete agents differ only in a single well-defined policy — a quarantine rule set, a verb allowlist, a scope-resolution rule — doctrine's slot-by-slot inherit/override model forces each concrete agent to restate the surrounding workflow with the variable spliced in by hand. Authors end up with N nearly-identical agent files where the variable lives as prose inside a `bullets` block (the only reliable place it can go) and the shared workflow shape is restated around it every time.

The weight shows up in maintenance cost: a change to the shared workflow shape means touching N files; a drift between files is a bug that only surfaces when the variant runs; a new layer has to copy-and-modify rather than inherit-and-bind.

### What we need to express

An abstract agent should be able to declare a typed policy slot that concrete descendants bind with a named policy value. The descendant becomes thin — an inheritance link plus a policy binding — and the shared workflow reads the policy through the slot rather than spelling it out inline.

### Use case

Each curriculum layer ships its own `lens_warden.prompt` — curriculum_scope, track_shape, section_shape, lesson_plan, and eventually lesson_materialize. Each file is 78–130 lines. Turn shape is identical. Rule-installation sequence is identical. Readiness-signal discipline is identical. Handoff is identical. The only variable per layer is the quarantine rule spec: "quarantine every later-ordered sibling's brief" vs. "quarantine prior per-lesson Template rows but preserve Template-stub design-intent prose" vs. "quarantine later-ordered lesson manifests but leave doorstops visible." A parameterized abstract warden taking a typed quarantine policy would reduce each concrete warden to the policy declaration and an inheritance line.

---

## 7. Skill `mode` binding — producer vs audit

### Why this bites

A thin-skill architecture often wants the same skill package to be invokable in two modes. In producer mode, the skill does the substantive work (walk the ontology, query the KB, classify the slots) and emits results. In audit mode, the skill replays against an existing receipt from a prior producer call and emits a reproducibility verdict (did the queries return the same thing? are the producer's citations consistent with what actually came back? were leading queries used where discovery was prescribed?).

Today `host_contract:` doesn't carry a mode parameter, so authors have three imperfect options. (a) Duplicate the skill into producer and audit packages — doubles the surface area, drifts over time. (b) Let the skill infer its mode from calling context — loses compile-time distinction, lets producers accidentally call audit-mode code paths and vice versa. (c) Skip audit mode entirely and have critics re-call the producer-mode skill, comparing prose output by hand — loses the replay-against-receipt discipline, which is the whole point of audit mode.

### What we need to express

A skill binding should be able to declare which mode it runs in at the point of use. The skill package's contract should express what each mode takes and emits — producer mode takes producer inputs and emits the result plus a receipt; audit mode takes audit inputs (the receipt being replayed, the environment state) and emits a reproducibility verdict. Agents binding in audit mode should be unable to accidentally trigger producer-mode side effects; audit-mode skill bindings should be the canonical thing a critic declares.

### Use case

The proposal's §14 describes every judgment-carrying skill (C2 ConceptCuration, C3 PokerKBGrounding, C4 CrossSiblingContinuity, C7 ScrappyStateClassification, C8 LessonManifestComposition) as having an audit-mode sibling that replays against an existing `ProcessReceipt` and returns `{reproducible, divergences, suspicious_patterns}`. Producer agents bind producer mode; critic agents bind audit mode via a shared `AuditSkills` block. Today neither the shared block nor the mode binding exists at the doctrine level, so critic agents re-invoke the primitive CLI with Bash and compare results in prose, losing the structural separation the proposal calls for.

---

## Priority ordering (from the audit's perspective)

The layered curriculum pipeline would benefit from these gaps closing roughly in this order, weighted by prose reduction and by what unblocks the proposal's load-bearing defenses:

1. **§4 (typed receipt envelope)** — unblocks ProcessReceipt as a doctrine-level artifact, which is the proposal's primary defense against process fakery.
2. **§1 (typed `gate` entity)** — buys back the largest chunk of prose in the pipeline (the per-layer review contracts) and earns compile-time gate-ID checking.
3. **§3 (note-output typed identity)** — closes the two-channel read pattern every critic uses today; turns handoff notes into the typed inputs the proposal designed them as.
4. **§5 (declarative inheritance lints)** — makes the upstream-poisoning invariant compile-enforced instead of convention-enforced.
5. **§2 (per-case gate scoping)**, **§6 (parameterized abstract agents)**, **§7 (skill mode binding)** — smaller individually, but complementary; closing them finishes the "one declaration, inherited everywhere" property the proposal leans on throughout.

The audit that surfaced these gaps lives at `psflows/docs/CURRICULUM_LAYERED_AUTHORING_PROPOSAL_2026-04-17.md` (the proposal that specified the shape) and in the delta between that proposal and the implementation under `psflows/flows/` + `psflows/prompts/curriculum_common/`.
