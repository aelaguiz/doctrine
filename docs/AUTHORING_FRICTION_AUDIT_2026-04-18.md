# Authoring Friction Audit — 2026-04-17/18

This is a point-in-time audit of Doctrine-language stumbling blocks that real
agents and a human author hit while writing flows in the neighboring
`psflows` project on the evening of 2026-04-17 and the morning of 2026-04-18.

It exists to:

- List confusions we can address in `doctrine-learn` so future authors do not
  hit them.
- List suspected rough edges in the shipped language, compiler, or docs we
  should consider addressing.
- Keep an honest ledger of what we already closed on this branch vs. what is
  still open.

## How This Was Built

Source material was the raw Claude Code and Cursor session transcripts on
this machine, scoped to psflows work from 2026-04-17 18:00 through
2026-04-18 15:00:

- `~/.claude/projects/-Users-aelaguiz-workspace-psflows/*.jsonl` (9 files)
- `~/.cursor/projects/Users-aelaguiz-workspace-psflows/agent-transcripts/**/*.jsonl` (5 files plus sub-agent transcripts)

Three parallel Explore agents grepped each bucket for compiler error codes
(`E0xx`–`E5xx`), confusion markers (`confused`, `not sure`, `why does`,
`can't find`, `doesn't work`, etc.), retries on the same construct, and
user corrections to the assistant. Findings below include direct quotes
trimmed to the key sentence plus a session pointer.

A single author ran every session, so one person's vocabulary shapes the
sample. Treat this as qualitative signal, not a balanced survey.

## Severity Key

- **[SHIPPED]** — already addressed on this branch (`feat/carrier-review-fields-and-shared-rules-split` through `main`), 2026-04-18.
- **[OPEN — DOCS]** — docs or `doctrine-learn` gap. No code change needed.
- **[OPEN — CODE]** — shipped behavior we should consider changing.
- **[LIKELY-NOT-DOCTRINE]** — the confusion is real but the fix lives in a
  neighbor project (Rally, psflows, or psmobile lint), not in `doctrine/`.

## Findings, Grouped By Theme

### Theme 1 — Flow Namespaces And The `export` / `import` Cut

The single biggest cost was authors ramping up on the flow-namespace hard
cut (`PROPOSAL_FLOW_NAMESPACE.md`, merged as PR #54 on 2026-04-16). Every
pre-existing psflows file still used v3-era plain imports; the first
cross-flow import in v4 fired `E314` loudly, then the fix triggered `E315`,
then the next fix triggered `E289`. Authors had no migration guide, so each
code surfaced the next layer of the rule the hard way.

Representative quotes:

- `E314 compile error: Imported declaration is not exported... Imported output declaration LessonsSectionNote is not exported from flow shared.` — `05818545-…jsonl`
- `E315 (same-flow import retired): from curriculum_shared.lens_discipline import when AGENTS.prompt imports same flow's sibling. Fixed by renaming.` — `05818545-…jsonl`
- `zero export keywords exist anywhere in psflows (so cross-flow imports will all fail E314 in v4)` — `05818545-…jsonl`
- `E289 Cyclic import: Root AGENTS.prompt imports agents.project_lead → project_lead imports shared.outputs → shared/outputs was a MEMBER of root flow via v4 rglob → cycle. Fixed by adding AGENTS.prompt markers to shared/ and contracts/ directories.` — `05818545-…jsonl`
- `Flat-namespace siblings at flow root can bare-ref each other; shared/ is separate namespace; cross-boundary imports can cycle.` — `2ad5e3a6-…jsonl`

Issues to address:

1. **[OPEN — DOCS]** No migration guide for the v3 → v4 flow-namespace cut.
   `docs/WORKFLOW_LAW.md` is the only doc touching the new namespace rule,
   and it covers runtime law, not import semantics. `doctrine-learn`'s
   `imports_and_refs.md` mentions exports in one sentence but never
   explains the `export` keyword, never names `E314`/`E315`/`E316`, and
   never contrasts flat-namespace sibling refs against cross-flow imports.
2. **[OPEN — DOCS]** The rule that `AGENTS.prompt` is the flow root marker,
   and the consequence that recursive rglob sweeps any loose `.prompt`
   subdirectory into the parent flow, is not stated in any `doctrine-learn`
   reference. Authors discover it only after `E289` fires.
3. **[OPEN — CODE]** `E315` ("same-flow import retired") fires on an exact
   v3 pattern the compiler could recognize and map to a crisper message.
   Today the text says "retired"; a migration-friendly message would name
   the fix ("drop the `from <flow>. ... import`; siblings bare-ref inside
   one flow") and link to the migration guide once it exists.
4. **[OPEN — CODE]** `E289`'s message names the cycle but does not name
   which subdirectory became a flow-member via rglob. For authors new to
   v4, "subdir X was swept into flow Y because it has no AGENTS.prompt
   root" would turn a 15-minute diagnosis into a 30-second one.
5. **[SHIPPED]** The rule itself (`export`, flat namespace, AGENTS.prompt
   roots, `E314`–`E316`) is real, shipped, and listed in
   `docs/COMPILER_ERRORS.md`. Only the author-facing onboarding is thin.

### Theme 2 — Review Family vs. Review Inheritance

The author reached for `review_family` with `selector:` + `cases:` to share
review structure across N critics, then ran into `E470`'s bijection rule
and the family ownership model, and eventually re-primitive'd to `abstract
review` + inheritance. The quote from the session is diagnostic:

- `User asked "Is this like an ugly doctrine rough edge or gap, or is this more just like, oh, we just gotta change how we're doing and it makes sense how doctrine expects it?" I explained we picked wrong primitive; review_family is for one agent runtime-selecting shape; abstract review + inheritance is for N critics sharing structure.` — `2ad5e3a6-…jsonl`

Other adjacent confusions:

- `E470 requires bijection... My plan had Level pre-declaring all 5 values (track_scope through lesson_materialize); that would fail compile until L1-L4 exist. Fix: declare enum Level with just track_scope today.` — `2ad5e3a6-…jsonl`
- `Doctrine 4.1 E500 single-carrier review ✓ review.on_reject.route (E317) delayed route binding in shared carrier ✓` — `2ad5e3a6-…jsonl`
- `E299 Missing local agent declaration: TrackScoper at shared/review.prompt:355 when family case referenced -> TrackScoper. Shared module can't resolve flow-root agent.` — `2ad5e3a6-…jsonl`

Issues to address:

6. **[OPEN — DOCS]** `doctrine-learn/reviews.md` already explains
   `review_family` as "one compiler path with scaffold or mode-selected
   cases" but never contrasts it against `abstract review` + inheritance
   as the N-critics pattern. Authors reliably pick the wrong primitive
   first. We should add a one-paragraph "Which review primitive?" decision
   rule with two example paths.
7. **[OPEN — DOCS]** `E470` bijection is documented as a single line in
   `COMPILER_ERRORS.md`. The practical upshot — that you must grow the
   enum in lockstep with the cases, one member per PR — is not stated
   anywhere. Worth pulling into `doctrine-learn/reviews.md` and linking
   from the `E470` row.
8. **[OPEN — DOCS]** `E500`'s carrier-mode relaxation (the commit on this
   branch: "relax E500 for carrier review_fields") is real but the docs
   still describe `E500` as "used on a non-review agent." The relaxation
   rule — carrier-mode review-driven agents may opt into `review_fields:`
   as explicit structural validation — is in the `COMPILER_ERRORS.md`
   entry, but not in `doctrine-learn/reviews.md`.
9. **[LIKELY-NOT-DOCTRINE]** `E299` firing on a `shared/` module referring
   to a flow-root agent bare-word is the expected scoping rule. The
   author's confusion is really about flow namespaces (Theme 1), not
   reviews. The fix is in the migration guide.

### Theme 3 — Skills, Emit Targets, And The `skills/*` Migration

Transcripts show that `psflows` still has eight skills on the old
`SKILL.md` + `agents/` shape with no Doctrine emit target in
`pyproject.toml`, living alongside the v4 shape (`prompts/SKILL.prompt` +
`build/SKILL.contract.json`). Authors tripped on the mixed fleet:

- `Check pyproject.toml: they have no [[tool.doctrine.emit.targets]] entry.` — `d8ae41ba-…jsonl` (Cursor subagent)
- `Two Doctrine skills still carry a surfaced build/ subtree with only SKILL.md (no SKILL.contract.json).` — `d8ae41ba-…jsonl`
- `eight skills are still in the old 'agent-authoring' top-level form with SKILL.md + agents/ at skill root (no build/, no prompts/SKILL.prompt, no Doctrine emit target in pyproject.toml).` — `d8ae41ba-…jsonl`
- `Let me verify the emit still works by running the build command.` — `d8ae41ba-…jsonl` (after a silent no-op build)

Issues to address:

10. **[LIKELY-NOT-DOCTRINE]** The mixed-fleet problem is a psflows
    migration state, not a Doctrine bug. But it surfaces a Doctrine-side
    observation: the compiler silently ignores `skills/*` directories
    with no matching emit target, instead of warning "you have a skill
    here but no target lists it."
11. **[OPEN — CODE, LOW]** Consider a lint/warn pass ("skill-directory
    without emit target") that fires in `make verify-examples` or in the
    `emit_skill` path when a `skills/*/prompts/SKILL.prompt` exists but
    no `[[tool.doctrine.emit.targets]]` entry points at it. This is on
    the "fail loud gaps" side of the line.
12. **[OPEN — DOCS]** `doctrine-learn/skills-and-packages.md` does not
    walk the minimum working shape of a skill package end-to-end
    (`prompts/SKILL.prompt`, the emit target entry in `pyproject.toml`,
    and the resulting `build/SKILL.contract.json`). The author had to
    reconstruct it from shipped examples.

### Theme 4 — Build Cache And The Rally Wrapper

Two build-side gotchas cost real time:

- `E280 (rally.base_agent not found): Direct python -m doctrine.emit_docs bypasses rally's stdlib wiring. Fixed by switching to ensure_flow_assets_built via rally's flow_build service.` — `05818545-…jsonl`
- `Build cache not invalidating: First rebuild showed no output but exit 0 and no diff. Fix: rm -rf flows/curriculum_scope/build/ before each ensure_flow_assets_built call.` — `2ad5e3a6-…jsonl`

Issues to address:

13. **[LIKELY-NOT-DOCTRINE]** The Rally `rally.base_agent` module and its
    stdlib-wiring wrapper are a neighbor-project concern. But the `E280`
    message fires from the Doctrine compiler, so an author's first
    instinct is to blame Doctrine. Worth adding one sentence to the
    `E280` row in `COMPILER_ERRORS.md`: "If you are invoking Doctrine
    through a wrapper (e.g. Rally), the wrapper owns the import-root
    registry; use the wrapper's build entry point, not `python -m
    doctrine.emit_docs` directly."
14. **[OPEN — CODE]** Stale-cache silent-success is a real Doctrine
    footgun if `emit_flow`/`emit_skill` ever short-circuits on an unchanged
    manifest but the source `.prompt` files did change. Worth a probe
    against the shipped emit path to confirm whether this is a Rally
    wrapper issue or a Doctrine-side invalidation bug. Filed here so we
    do not lose it; I have not checked the root cause yet.

### Theme 5 — Inheritance, Authored Slots, And The Linter's Blast Radius

Cursor sessions repeatedly tripped over the interaction between Doctrine
inheritance and downstream lints in psmobile:

- `Each of the 8 agents must explicitly inherit the new slots. Let me update them all.` — `d8ae41ba-…jsonl`
- `Since each file has two mentions of legacy_and_old_authoring_files (one in a comment and one in the actual agent body), I need to target only the indented line in the agent body itself...` — `d8ae41ba-…jsonl`
- `The linter flagged some problems—it looks like each agent has entries in the AGENTS.md file where a bypass tool and curriculum path are appearing on the same line.` — `d8ae41ba-…jsonl`

Issues to address:

15. **[OPEN — DOCS]** `doctrine-learn/agents-and-workflows.md` and
    `authoring-patterns.md` do not give a concrete "base agent mixin"
    pattern for a shared set of authored slots across N concrete children.
    Real authoring hit it; the fix took eight near-identical edits. A
    one-example treatment ("base agent carries these authored slots; each
    child `inherit {a, b, c}`s") would have flattened this.
16. **[LIKELY-NOT-DOCTRINE]** The psmobile linter running on the emitted
    AGENTS.md and flagging inherited prose as violations is not a
    Doctrine concern. But it is worth writing down in psflows' own docs
    that `inherit` causes the parent's prose to appear in every child's
    emitted file, which multiplies the lint surface.

### Theme 6 — Conceptual Gaps The Transcripts Surfaced But Doctrine Is Not Guilty Of

These are "doctrine issues" in the loose sense — the author did not know
where Doctrine's boundary sits — but the right fix is a note in the
neighbor project, not in our code or our skill:

- The "critics as poisoning defense" vs. "lens as input-boundary defense"
  architecture insight (`e54a7d46-…jsonl`) is a curriculum-scope
  architecture call. Doctrine gives the author `review_family`, case
  selection, and `final_output.route`; it does not prescribe when to use
  them.
- "Transliteration vs. translation of domain skills" (`14fad2f8-…jsonl`)
  is an authoring-technique observation, not a Doctrine gap.
- "Receipts as first-class typed output" is a psflows convention. Doctrine
  gives them `output schema` and `final_output`; it does not define
  what a receipt's fields must be.

No action here except to keep resisting the pull to absorb these into
Doctrine. They belong on the authoring side of the thin-harness line.

### Theme 7 — Smaller One-Off Frictions

- **[OPEN — CODE, LOW]** `E101` on a comment-only `AGENTS.prompt`:
  authors sometimes drop a marker file with just a comment. The grammar
  rejects it. Either document this plainly in `doctrine-learn` or accept
  comment-only files as a valid "marker" shape.
  Seen in `05818545-…jsonl` ("Comment-only AGENTS.prompt fails grammar.
  Fixed by adding an import statement to satisfy grammar.").
- **[OPEN — DOCS]** Naming overlap between `output schema`, `output shape`,
  and `output target`. First-time authors routinely tried the wrong one.
  `doctrine-learn/outputs-and-schemas.md` covers each; it does not contrast
  them in a single decision rule. One paragraph would likely close this.

## What Already Shipped On This Branch

Cross-referenced against `git log feat/carrier-review-fields-and-shared-rules-split` (Apr 16 → Apr 18):

- `E317` — `via review` clause binding, on this branch.
- `E318`/`E319` — output shape selector + case dispatch and agent selector
  binding, on this branch.
- `E500` relaxation for carrier `review_fields`, on this branch (commit
  `b1915a1`).
- Shared rules pattern split that the carrier-review-fields change
  enabled, on this branch.
- Flow-namespace hard cut (`PROPOSAL_FLOW_NAMESPACE.md`, PR #54, merged
  Apr 16) — the single biggest upstream cause of Theme 1.

The shipped codes and language rules are all catalogued in
`docs/COMPILER_ERRORS.md`. The missing piece is the author-facing
migration and teaching layer.

## Recommended Next Moves, Ranked By Payoff

1. Write `docs/FLOW_NAMESPACE_MIGRATION.md` (v3 → v4 import cut): covers
   `export`, flat-namespace sibling refs, `AGENTS.prompt` as flow root,
   recursive rglob behavior, the `E314`/`E315`/`E316`/`E289` sequence, and
   the one-commit fix shape. Closes Theme 1 for future authors.
2. Update `doctrine-learn/imports-and-refs.md` to reference the migration
   doc above, add the `export` keyword to its vocabulary list, and add
   the flat-namespace vs. cross-flow decision rule.
3. Add a "Which review primitive?" one-pager to
   `doctrine-learn/reviews.md` contrasting `review_family` (runtime case
   selection on one agent) against `abstract review` + inheritance (N
   critics sharing structure). Include the `E470` bijection gotcha.
4. Extend `E280`'s row in `COMPILER_ERRORS.md` with the wrapper-harness
   note so authors invoking Doctrine through Rally/other harnesses stop
   blaming Doctrine first.
5. Walk the minimum working shape of a skill package in
   `doctrine-learn/skills-and-packages.md` end-to-end (emit target entry
   through emitted `SKILL.contract.json`).
6. Probe whether `emit_flow`/`emit_skill` has a stale-cache silent-success
   case on its own (not just via the Rally wrapper). If yes, file as a
   fail-loud gap in `docs/FAIL_LOUD_GAPS.md`.
7. Consider a soft warning on `skills/*/prompts/SKILL.prompt` without an
   emit target. Low cost, catches silent drift.

## Out Of Scope

- Poker-domain architecture decisions. These belong to psflows.
- Rally wrapper internals (`ensure_flow_assets_built`, stdlib injection).
- psmobile lint rules. Doctrine owns the emit shape; psmobile owns the
  rules that run on it.

## Revisit

Re-run this audit when the flow-namespace migration doc lands and when
`doctrine-learn` ships the review-primitive decision rule. Compare
transcript friction on future psflows work against Theme 1 and Theme 2
quote frequencies to see whether the docs moved the needle.
