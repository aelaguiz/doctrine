# Example Mistakes — Layered Curriculum Authoring Flows

Source repo: `psflows/` (layered curriculum flows — L0 `curriculum_scope`, L1
`track_shape`, L2 `section_shape`, L3 `lesson_plan`; shared tree at
`prompts/curriculum_common/`). Each entry below is a concrete anti-pattern we
shipped, what doctrine language already covers it, and a detection heuristic the
linter can target.

Every entry uses this structure:

- **What we wrote** — a real snippet (trimmed for readability)
- **Why it's wrong** — the doctrine rule the code sidesteps
- **What we should have written** — the idiomatic shape
- **Detection heuristic** — how a linter could find it

---

## Mistake 1 — Bare `skill` declaration for a skill with load-bearing host slots

### What we wrote

`prompts/curriculum_common/skills.prompt`:

```
export skill CatalogOpsSkill: "catalog-ops"
    purpose: "Lens-bound primitive over the psmobile catalog and doorstop spine. ..."

    use_when: "Use When"
        "Use this for any catalog or spine inspection verb ... On greenfield track
        creation, the sequence is `add` → `set name/description/order` → `spine
        write --full-body` (carry Brief + Concepts in one document) → `spine
        review`. ..."
```

Every host (producer or critic) that takes this skill does so as:

```
skill catalog_ops: CatalogOpsSkill
    requirement: Required
```

No `bind:` block, no typed coupling between the skill's outputs and the host's
handoff-note document slots. All the per-layer discipline about "receipts go into
the producer's `## Scope And Receipts` section" is carried in prose `use_when:`
text, not typed.

### Why it's wrong

Doctrine has `skill package` with `host_contract:` for exactly this case —
declare the host-side document/final_output slots the skill's output is expected
to land in, and host-side agents must `bind:` concrete slots to satisfy the
contract. Reference: `examples/124_skill_package_host_binding/prompts/skills/host_bound/SKILL.prompt`.

A bare `skill` declaration with prose describing where output goes makes the
skill/host coupling invisible to the compiler. A host that forgets to create
the `## Scope And Receipts` section still emits a buildable agent; the prose
discipline is checked at run time only (or, realistically, never).

### What we should have written

```
skill package CatalogOpsSkill: "catalog-ops"
    metadata:
        name: "catalog-ops"
        description: "Lens-bound primitive over the psmobile catalog and spine."
    host_contract:
        document handoff_section: "Scope And Receipts"
        # more slots as the skill's output discipline dictates
    "Cite every receipt into {{host:handoff_section.title}}."
    "Use When ..."
```

Host:

```
skill catalog_ops: CatalogOpsSkill
    requirement: Required
    bind:
        handoff_section: ScopeAndReceiptsSection
```

### Detection heuristic

Flag a `skill` declaration without `host_contract:` when any of:
- `use_when:` prose references host-owned section/document titles (e.g. quotes
  like `` `## Scope And Receipts` ``, `"HandoffNote"`, `"FinalResponse"`)
- `use_when:` prose imperative directives ("cite into", "write to", "emit
  into") combined with a named target
- The skill is imported into ≥2 agent files — broad reuse with prose-only
  coupling is exactly what `host_contract:` exists to type

---

## Mistake 2 — Raw Bash exception baked into shared discipline prose

### What we wrote

`prompts/curriculum_common/lens_discipline.prompt:10`:

```
"**Critic exception** (Auditor role, Appendix A): the layer's critic agent ...
is permitted to invoke the admin CLI's read-only auditor verbs via Bash:
`authoring_lens/cli.py session inspect`, `rules list`, `receipts list`,
`receipts read <id>`. These are how the critic dereferences the producer's
claimed receipts and confirms the warden's rules are still installed. The
critic MAY NOT call any mutating verb ..."
```

The carveout appears once in a shared discipline module and is textually
reinforced in every critic's `role:` body (e.g.
`flows/curriculum_scope/prompts/track_scope_critic.prompt:73-82` re-lists the
allowed and forbidden verbs as prose).

### Why it's wrong

The entire point of the lens-discipline module is **"no direct file access, no
tool-level shortcuts"** — every curriculum-surface touch goes through a
primitive skill. Carving out "except these four verbs via Bash, because it's
convenient" reintroduces the exact untyped tool surface the discipline was
written to forbid. Worse, the allowlist is prose — the compiler can't verify a
critic didn't call a mutating verb.

A typed skill package (`AdminLensSkill` with `purpose:` naming the four
read-only verbs) gives the critic the same capability through the same typed
`$primitive` channel every other skill uses.

### What we should have written

A shared `AdminLensSkill` skill package wrapping the four read-only verbs, and:

- `lens_discipline.prompt` line 10 becomes "the critic calls the four read-only
  admin verbs exclusively through `$admin-lens`."
- Every critic's skills block adds `skill admin_lens: AdminLensSkill` and its
  role body drops the prose allowlist.

### Detection heuristic

Flag any `workflow` or role-body text where the pattern is:

- "permitted to invoke … via Bash" / "exception for … run directly" / "call
  `<tool-name>` directly via Bash"
- A list of specific verb names adjacent to the exception

— especially when another skill in the same file uses a `$primitive` syntax
for equivalent operations. The asymmetry is the tell.

---

## Mistake 3 — N parallel `workflow` declarations as review contracts

### What we wrote

`prompts/curriculum_common/review.prompt` declares four separate workflows:

```
export workflow TrackScopeReviewContract: "Track Scope Review Contract"
    output_gates_pass: "Output Gates" "..."
    receipt_gates_pass: "Receipt Gates" "..."
    process_gates_pass: "Process Gates" "..."
    upstream_leakage_clean: "Upstream Leakage Clean" "..."
    setup_gates_pass: "Setup Gates" "..."

export workflow TrackShapeReviewContract: "Track Shape Review Contract"
    output_gates_pass: "Output Gates" "..."     # different prose
    receipt_gates_pass: "Receipt Gates" "..."   # different prose
    process_gates_pass: "Process Gates" "..."   # different prose
    upstream_leakage_clean: "Upstream Leakage Clean" "..."
    setup_gates_pass: "Setup Gates" "..."

# ... SectionShapeReviewContract and LessonPlanReviewContract follow
# the exact same five-slot shape
```

Each is bound to a concrete critic via `review <Name>[CurriculumLayerReviewBase]:
contract: <Name>ReviewContract`.

### Why it's wrong

Doctrine has `review_family` with a `selector` and `cases:` block — one
declaration, N per-case contracts, shared `fields:` and `handoff_first:`.
Reference:
`examples/69_case_selected_review_family/prompts/AGENTS.prompt:83-127`.

Four parallel workflows with identical slot names (the slot keys ARE the gate
taxonomy) fragment the review surface: a change to the taxonomy has to be
made four times, and a critic binding can silently pick up the wrong contract
without any cross-contract consistency check.

### What we should have written

One `review_family LayerAcceptanceReview` with a `selector: mode layer =
ReviewFacts.layer as ReviewLayer` and four `cases:` (`track_scope`, `track_shape`,
`section_shape`, `lesson_plan`), each case carrying its own `subject`,
`contract`, and `checks`. The per-case `contract` workflows still differ in
prose — but they're authored as siblings inside one declaration, and the
taxonomy (five gate groups) is defined once.

### Detection heuristic

Flag when ≥2 `workflow` declarations share ≥70% of their slot keys AND each is
bound as a `contract:` inside a `review` declaration. Recommend collapsing
under `review_family` with `selector` + `cases`.

A stricter variant: if the same abstract `review` base is instantiated in
multiple concrete agents, each binding a different concrete `workflow`, that
is always a `review_family` candidate.

---

## Mistake 4 — `contract_checks:` collapsing N typed gates to `contract.passes`

### What we wrote

`flows/curriculum_scope/prompts/track_scope_critic.prompt:18-19`:

```
contract_checks: "Contract Checks"
    accept "All five gate groups pass — output is well-formed, receipts
    dereference, process signals are present, no quarantined identifier
    leaked through, and the warden's lens rules match the target slot's
    prior content." when contract.passes
```

The bound contract (`TrackScopeReviewContract`) defines five typed gate slots
(`output_gates_pass`, `receipt_gates_pass`, `process_gates_pass`,
`upstream_leakage_clean`, `setup_gates_pass`), but the check collapses them to
one boolean.

Same pattern repeats in `track_shape_critic`, `section_shape_critic`, and
`lesson_plan_critic`.

### Why it's wrong

The typed gates are the whole point of the contract. Collapsing to
`when contract.passes` means:

- A failing gate is only visible in the producer-facing prose (inside the
  critic's analysis text), not in the structured check outcome.
- The compiler loses the per-gate acceptance criterion — "output gates" and
  "setup gates" have different upstream routing consequences (setup failure
  blocks the whole run; output failure routes back to the producer), but a
  single `contract.passes` roll-up can't express that shape.

Per-gate `accept` lines make each gate's acceptance a first-class check.

### What we should have written

```
checks:
    accept "Output gates pass." when contract.output_gates_pass
    accept "Receipt gates pass." when contract.receipt_gates_pass
    accept "Process gates pass." when contract.process_gates_pass
    accept "Upstream leakage clean." when contract.upstream_leakage_clean
    accept "Setup gates pass." when contract.setup_gates_pass
```

(Inside `review_family`'s per-case `checks:` block once Mistake 3 is also
fixed.)

### Detection heuristic

Flag a `contract_checks:` (or `checks:` inside a `review_family` case) block
whose `accept` / `reject` lines all reference `contract.passes` (or any single
roll-up predicate) when the bound contract declares ≥2 named gate slots.

Include the gate-slot count in the lint message so the author sees the missed
granularity: "contract defines 5 gates; checks collapse to 1 predicate."

---

## Mistake 5 — Shared agent skeleton duplicated across N flow files

### What we wrote

Four warden files (`flows/curriculum_scope/prompts/lens_warden.prompt`,
`flows/track_shape/.../lens_warden.prompt`,
`flows/section_shape/.../lens_warden.prompt`,
`flows/lesson_plan/.../lens_warden.prompt`) each carry ~65 lines of shared
scaffold:

- Identical import block (`CurriculumHandoffNote`, `LensWardenHandoffNote`,
  `CurriculumAgentResultSchema`, `CurriculumAgentResultJson`,
  `CurriculumAgentResult`, `CatalogOpsSkill`)
- Identical `inputs LensWardenInputs[base.RallyManagedInputs]` block
- Identical `skills LensWardenSkills[base.RallyManagedSkills]` block
- Identical `output schema`, `output shape`, `output` wrapping declarations
  (only the `route field next_route:` line genuinely differs per layer — the
  rest is boilerplate)
- Identical `outputs` struct
- Identical concrete-agent `inherit { ... }` block at the bottom

Legitimately per-layer: the `workflow LensWardenWorkflow` step sequence, the
`role:` prose, and the single `route field next_route: <target>` line.

### Why it's wrong

Doctrine has `abstract agent` and `[Base]` inheritance. The layered curriculum
codebase already uses an abstract `LensWardenBase` — but the base stops at the
lens-slot bindings and leaves every warden to re-declare the inputs / skills /
outputs / schema / shape scaffold. The result is four files where ~70% of the
lines are character-identical.

Every doctrine language feature that makes code DRY (abstract inheritance,
`inherit { ... }`, slot binding on abstract bases) is designed to collapse
exactly this pattern.

### What we should have written

`LensWardenBase` carries the full scaffold:

- `inputs: LensWardenInputsBase` (binding `issue_ledger`)
- `skills: LensWardenSkillsBase` (binding `rally_kernel` + `CatalogOpsSkill`)
- An abstract output schema/shape/response shell that concrete wardens
  override only for the `route field next_route` declaration
- `outputs: LensWardenOutputsBase` (binding `issue_note:
  LensWardenHandoffNote` and the `turn_result:` line)

Concrete wardens carry only `workflow LensWardenWorkflow`, `role:`, and the
per-layer `next_route` override. Target shrink: ~90–130 lines → ~40–50 lines
per file, no prose duplicated across layers.

### Detection heuristic

Flag when ≥2 concrete agent files share above-threshold (suggest 60%) exact-
token overlap in their DECLARATION blocks (`inputs`, `skills`, `outputs`,
`output schema / shape`) — ignoring `role:` prose, `workflow:` bodies, and
comments.

A simpler proxy: ≥2 concrete agents in the same codebase that extend the same
abstract base AND each file's line count exceeds the base file's line count by
a configurable multiple (e.g. 2×). Strong signal that the base is not
absorbing what it should.

Agent files sharing imports of the same N shared modules (≥4 imports in
common) is another weak signal that the skeleton is common enough to hoist.

---

## Secondary patterns worth catching

These overlap with the five above but may merit independent linter rules:

### 5a — Role-body prose re-declaring a discipline that a typed binding could encode

Every critic role-body enumerates the four allowed admin verbs and six
forbidden admin verbs as prose (example:
`track_scope_critic.prompt:73-82`). The allowlist/blocklist is not enforced
— the prose is advice the model either follows or doesn't. Once Mistake 2 is
fixed via a typed `AdminLensSkill`, the role-body prose is dead weight.

**Detection:** role-body text enumerating specific verb names with
permission qualifiers ("may call", "may not call") where a skill-package
scope already types the verb set. Flag as prose duplicating typed
discipline.

### 5b — Cross-layer prose drift on shared concepts

The four review-contract workflows drift in small ways despite nominally
covering the same five gate groups: one layer's `setup_gates_pass` prose
references `setup.lens_rules_match_scope`; another references
`setup_gates_pass` verbatim. Single-source contract authoring (via
`review_family`) would make this drift impossible.

**Detection:** same slot-key across ≥2 workflows where prose bodies
reference gate ids that differ by punctuation or namespacing
(`setup_gates_pass` vs `setup.lens_rules_match_scope`). Flag as
taxonomy-drift smell.

---

## Summary table for linter rule design

| # | Rule name | Primary signal | Secondary signal |
|---|---|---|---|
| 1 | `skill-needs-host-contract` | bare `skill` declaration with `use_when:` naming host slots | skill imported across ≥2 agents |
| 2 | `typed-discipline-escape-hatch` | workflow/role prose authorizing Bash + named verbs | asymmetry with `$primitive` skills in same file |
| 3 | `parallel-workflows-for-review-contracts` | ≥2 workflows with ≥70% shared slot keys, each bound as `contract:` | same abstract review base instantiated N times |
| 4 | `coarse-contract-checks` | `accept ... when contract.passes` against N-gate contract | all checks reference one roll-up predicate |
| 5 | `agent-skeleton-duplication` | ≥2 agent files share ≥60% declaration-block tokens | children >> base in line count |
| 5a | `prose-duplicates-typed-discipline` | role prose verb allow/blocklist paralleling a typed skill | |
| 5b | `cross-layer-gate-id-drift` | same slot key, divergent gate id prose | |
