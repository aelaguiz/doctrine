# Examples And Output

## Canonical User Asks

These are the core asks this skill should handle well:

- `Audit this SKILL.prompt and tell me what is weak.`
- `Audit this flow or package for drift, duplication, and thin-harness fit.`
- `Audit our repo's agent surfaces and tell me what to fix first.`
- `Audit this full skill package end to end.`
- `Audit this authored prompt against the emitted skill.`

Nearby anti-case:

- `Rewrite this prompt for me` with no audit ask

## Strong Output Shape

Good:

- one reusable skill reads caller-supplied inputs
- exact constraints live in typed or deterministic surfaces
- read-many work ends in one compact synthesis artifact
- the report names the strongest fixes first
- the report says when the surface is too thin instead of guessing
- prompt-source `#` comments are treated as authoring comments, not emitted
  agent text
- reuse findings name a real shared owner
- the first screen tells the reader what to fix now and what can wait
- the report sounds like a sharp reviewer, not a timid rubric
- the report clears the fog and gives the reader a clean starting point

Bad:

- one skill hardcodes one founder, one dataset, or one case
- prose does exact counting or routing work with no typed owner
- the output is a folder of raw notes instead of one compact handoff
- the audit floods the user with weak findings and no clear order
- the audit treats prompt comments as always-on bloat
- the audit skips shared-owner guidance on a reuse problem
- the report sounds bloodless and generic
- the report leaves the reader unsure what to do first

## Human Report Examples

Use these to learn the quality bar.
Do not copy them by pattern match.

### Example 1: Good Internal Contradiction Finding

Why it is good:

- it shows both conflicting spans
- it uses the narrowest correct code
- it gives a small fix and a safe rewrite

Good:

```md
Verdict: fail
Scope: one target, authored source only

[HIGH] AL800 Internal contradiction

Target: `InterviewSummaryWriter`

Summary: The role gives incompatible answer-length instructions.

Evidence:
- "Always keep the answer under five lines."
- "Provide a full, exhaustive analysis of every interview theme."

Why it matters: The agent cannot satisfy both instructions reliably.
If you leave this alone, outputs will swing between too short and too long.

Smallest credible fix: Keep one default rule and state the exception clearly.

Fix steps:
- Keep the short-answer rule as the default
- Add an exception for user-requested depth
- Remove the word "always" if depth is not absolute

Shared owner: none.

Suggested rewrite:
Be concise by default. Go longer only when the user asks for depth.
```

Bad:

```md
Some instructions feel inconsistent.
This could be confusing.
Make it better.
```

### Example 2: Good Shared-Owner Duplication Finding

Why it is good:

- it shows one normalized duplicate
- it names the affected targets
- it names a real shared owner

Good:

```md
Verdict: fail
Scope: cross-target duplication across two roles

[MEDIUM] AL200 Duplicate rule across agents

Targets: `InterviewSummaryWriter`, `InterviewSummaryReviewer`

Summary: The same evidence-check rule appears in both targets.

Evidence:
- "Check each claim against a source quote. Mark weak quotes. Remove unsupported claims."

Why it matters: This rule now has two owners and can drift.
If one copy changes and the other does not, the team will start getting two
different review standards for the same job.

Smallest credible fix: Move the repeated rule into one shared skill.

Shared owner:
- Kind: skill
- Name: `ClaimEvidenceCheck`
- Why: This method is reused in the same form and should have one owner.

Fix steps:
- Create one shared evidence-check skill
- Point both targets to that skill
- Delete the local copies

Why this fix first: This is shared law. Fixing it once will clean up both
roles at the same time.
```

Bad:

```md
There is some duplication in the batch.
Refactor it.
```

### Example 3: Good Cross-Surface Finding

Why it is good:

- it cites both surfaces
- it makes the edit target clear
- it keeps the fix local and honest

Good:

```md
[MEDIUM] AL810 Cross-surface contradiction

Scope: authored source vs emitted skill

Target: `InterviewSummaryWriter`

Summary: The authored prompt tells the role to use browser tools, but the
emitted skill limits the role to `ReadFile` and `SearchDocs`.

Evidence:
- Authored source: "Use any browser or shell tool that seems useful."
- Emitted markdown: "Use `ReadFile` and `SearchDocs` when you need source material."

Why it matters: The author and the shipped surface now teach different tool
behavior.
That is the kind of mismatch that wastes time fast because the reader does not
know which surface to trust.

Smallest credible fix: Edit the authored prompt so it matches the shipped tool
surface.

Edit target: authored source.

Shared owner: none.
```

Bad:

```md
The prompt and emitted skill feel a little out of sync.
```

### Example 4: Good Incomplete Audit Handling

Why it is good:

- it says the audit is incomplete only because the requested call would be fake
- it names the missing surface and the next step

Good:

```md
Verdict: incomplete audit

Scope requested: authored-versus-emitted drift for the full skill package

What I checked:
- `SKILL.prompt`
- bundled references

What I could not check:
- emitted `SKILL.md`
- emitted companion references

Coverage gap:
- The emitted skill is missing, so I cannot make a fair authored-versus-emitted
  drift call yet.

Next move:
- Emit the skill bundle, then rerun the drift pass.
```

Bad:

```md
Verdict: fail

The emitted skill probably drifts from the prompt.
```

### Example 5: Prompt Comment Handling

Why it is good:

- it knows prompt-source comments do not go into the agent
- it does not flag authoring notes as always-on bloat

Good:

- `These # lines are prompt-source comments. They do not ship to the agent. Keep them if they help authors understand the package.`

Bad:

- `This prompt has too much always-on context because it includes three # comments.`

### Example 6: Strong Repo-Wide Opening

Why it is good:

- it tells the reader what got inspected
- it names the top fixes first
- it sounds like a useful human review

Good:

```md
Verdict: fail
Scope: repo instruction surfaces

What I checked:
- root `AGENTS.md`
- `skills/agent-linter/`
- emitted skill bundle

Fix first:
1. The skill still copied one shared law into two places.
2. The package still mixed one hard gate with taste advice.
3. One emitted companion drifted from its prompt source.

The biggest real problem is duplicated shared law. Fix that first because it
will remove two findings at once.
```

Bad:

```md
I found several things.
Some are medium.
Some may be worth looking at.
```

### Example 7: Good No-Leverage Bulk Finding

Why it is good:

- it shows the local prompt growth directly
- it explains why the added text did not buy reusable leverage
- it keeps the fix small and load-aware

Good:

```md
[MEDIUM] AL100 Oversized Always-On Context

Target: `ReleaseReviewer`

Summary: The home added a long always-on release checklist, but it does not create a shared owner, a load trigger, or a typed truth surface.

Evidence:
- "Keep the full release glossary, rollback playbook, three sample announcements, and the full comms checklist in mind on every turn."

Why it matters: The prompt got bigger, but the added text did not buy reusable leverage. Load cost went up with no durable gain.

Smallest credible fix: Move the deep release material into one shared reference and keep one short pointer in the home.

Shared owner:
- Kind: module
- Name: `ReleaseReviewReference`
- Why: The detailed release reference should live in one place and load only when needed.
```

Bad:

```md
This role feels a little long.
Maybe shorten it.
```

### Example 8.5: Good Inlined-Vocabulary Finding

Why it is good:

- it names the pipe list as the shape that matters
- it points at the canonical form instead of asking for vague rewording
- it names the critic-gate copy that drifts once the vocabulary moves

Good:

```md
[MEDIUM] AL950 Inlined vocabulary should be an enum-typed field

Target: `LessonStepPlanner` (producer role) and `LessonStepCritic` gate `step_role_in_vocabulary`

Summary: The `step_role` vocabulary is written as prose on the producer role and repeated as a separate critic gate check. No `enum` declaration owns the four values.

Evidence:
- Role body: "`step_role` values are `introduce | practice | test | capstone`."
- Critic gate body: "Fail if `step_role` is not one of `introduce`, `practice`, `test`, `capstone`."

Why it matters: Two prose copies of the same vocabulary drift by hand. The rendered schema should own the four values so the critic gate can disappear.

Smallest credible fix: Declare `enum StepRole: "Step Role"` with members `introduce`, `practice`, `test`, `capstone`. Set `type: StepRole` on the `step_role` field. Delete the producer prose and the critic gate.

Shared owner:
- Kind: enum declaration
- Name: `StepRole`
- Why: The vocabulary is shared by the schema, the producer, and the critic, so it should have one declared home.

Suggested rewrite:
Declare `enum StepRole: "Step Role"` once. Type `step_role` as `StepRole` on the field. See `examples/139_enum_typed_field_bodies/` for the canonical form on a `row_schema` entry.

See also: `AL200`.
```

Bad:

```md
The `step_role` list should probably be an enum or something.
```

### Example 8: Good Harness-Boundary Safety Finding

Why it is good:

- it keeps the issue inside the existing runtime-boundary family
- it shows that safety control belongs to the harness
- it tells the reader what to delete and what to leave alone

Good:

```md
[HIGH] AL300 Runtime Boundary Leak

Target: `SafetyGateReviewer`

Summary: The prompt tells the role to track safety strikes across turns and auto-block future work after three strikes.

Evidence:
- "Keep a safety strike count for this user across sessions."
- "After three strikes, refuse future requests automatically."

Why it matters: Safety control and cross-turn runtime state belong to the harness. Leaving them in prose creates a second runtime owner.

Smallest credible fix: Delete the strike policy from the prompt and let the harness own that control.

Shared owner: none.

Suggested rewrite:
If the current request cannot be handled, say so in this turn and leave runtime control to the harness.
```

Bad:

```md
This safety language feels a bit strong.
```

### Example 9: Thin-Agent Boundary, Five Findings On One Role

Why it is good:

- it fires five distinct findings on one compacted role excerpt
- each finding names the single edit that removes it
- it keeps the offending excerpt short and cites the one sentence that triggered each finding
- it shows the reader how AL140, AL250, AL260, AL440, and AL740 stack on the same role body

Good:

```md
Verdict: fail
Scope: one role body (`LensWarden`), authored source only

Offending excerpt (one sentence from the role body):
- "Per rule L3-A1 in docs/CURRICULUM_L3_IMPLEMENTATION_2026-04-18.md, LensWarden (when invoked, typically after the section planner (which itself runs after the track planner)) must install each rule (a) by calling `python authoring_lens/cli.py rules add --strict`, (b) verifying the sha256, then (c) handing the artifact to \"LessonPlanner\" via home:issue.md."

[HIGH] AL140 Planning-Doc Scaffolding In Agent Body
Evidence: "Per rule L3-A1 in docs/CURRICULUM_L3_IMPLEMENTATION_2026-04-18.md,..."
Fix: Strip the planning-doc citation and the `L3-A1` rule ID. Keep the behavior; drop the provenance.

[HIGH] AL250 Skill Capabilities Pulled Into Agent Role
Evidence: "install each rule ... by calling `python authoring_lens/cli.py rules add --strict`, ... verifying the sha256"
Shared owner:
- Kind: skill
- Name: `LensInstall`
- Why: The install procedure and the sha256 check are reusable capability and should live on one skill.
Fix: Move the install procedure into the `LensInstall` skill. Have the agent reference the skill.

[MEDIUM] AL260 Naked Script Or CLI Invocation In Role Prose
Evidence: "`python authoring_lens/cli.py rules add --strict`"
Fix: Promote the invocation into the `LensInstall` skill body; delete the command from the role prose.

[MEDIUM] AL440 Declaration Name Quoted As String Instead Of Typed Ref
Evidence: "handing the artifact to \"LessonPlanner\" via home:issue.md"
Fix: Replace the string `"LessonPlanner"` with the typed route ref on the workflow law or `final_output.route:` binding.

[HIGH] AL740 Machine-Language Prose
Evidence: The one sentence runs past 60 words, nests three parentheticals, and carries inline `(a)`/`(b)`/`(c)` enumerations.
Fix: Split into short sentences. Move the three steps into a bullet list. Read the result out loud; one breath per sentence.

Smallest credible fix first: AL250 and AL260 unblock AL740, because once the install steps move to the skill the remaining role prose is short enough to read at a 7th grade level.

Suggested rewrite (role body after all five fixes):
LensWarden installs each rule through the `LensInstall` skill. The skill owns the CLI call and the sha256 check. Hand the artifact to the declared route owner once install finishes.
```

Bad:

```md
The role is too long and reads like code.
It also mentions a CLI and a planning doc.
Consider cleaning it up.
```

### Example 10: Good Parallel-Workflows-As-Contracts Finding

Why it is good:

- it names every parallel workflow as evidence, not just the first one
- it shows the shared slot keys as the signal
- it points at the one `review_family` shape that collapses them

Good:

```md
Verdict: fail
Scope: cross-target, four parallel review contracts

[MEDIUM] AL270 Parallel Workflows As Review Contracts

Targets: `TrackScopeReviewContract`, `TrackShapeReviewContract`, `SectionShapeReviewContract`, `LessonPlanReviewContract`

Summary: Four `workflow` declarations carry the same five gate slot keys and are each bound as a review `contract:` on a separate critic.

Evidence:
- Shared slot keys (all four workflows): `output_gates_pass`, `receipt_gates_pass`, `process_gates_pass`, `upstream_leakage_clean`, `setup_gates_pass`
- `TrackScopeReviewContract` bound as `contract:` on `TrackScopeCritic`
- `TrackShapeReviewContract` bound as `contract:` on `TrackShapeCritic`
- `SectionShapeReviewContract` bound as `contract:` on `SectionShapeCritic`
- `LessonPlanReviewContract` bound as `contract:` on `LessonPlanCritic`

Why it matters: The gate taxonomy lives in four places. One change has to land in all of them, and the four contracts already drift in prose (`setup.lens_rules_match_scope` vs `setup_gates_pass`). A critic binding can silently pick up the wrong contract.

Smallest credible fix: Collapse the four workflows into one `review_family` with a `selector` and exhaustive `cases:`.

Shared owner:
- Kind: contract
- Name: `LayerAcceptanceReview`
- Why: The five gate groups are one taxonomy. One `review_family` owns the shared shape; cases override only per-layer prose.

Fix steps:
- Define `review_family LayerAcceptanceReview` with `fields:` for the five gate identities.
- Add `selector: mode layer = ReviewFacts.layer as ReviewLayer`.
- Add four cases (`track_scope`, `track_shape`, `section_shape`, `lesson_plan`), each carrying its `subject`, `contract`, and `checks`.
- Point every critic at the family; drop the parallel workflows.
- See `examples/69_case_selected_review_family` for the shape.
```

Bad:

```md
There is duplication across the four review contracts.
Consider merging them.
```

### Example 11: Good Agent Skeleton Duplication Finding

Why it is good:

- it shows the exact declaration blocks that overlap
- it keeps the real per-child difference in view
- it names the abstract base that absorbs the scaffold

Good:

```md
Verdict: fail
Scope: cross-target, four concrete agents inheriting one abstract base

[MEDIUM] AL280 Agent Skeleton Duplication

Targets: `TrackScopeLensWarden`, `TrackShapeLensWarden`, `SectionShapeLensWarden`, `LessonPlanLensWarden`

Summary: Four concrete wardens restate the same `inputs`, `skills`, `outputs`, `output schema`, and `output shape` declarations. The abstract base they inherit only carries the lens slot bindings.

Evidence:
- Identical import block in each file: `CurriculumHandoffNote`, `LensWardenHandoffNote`, `CurriculumAgentResultSchema`, `CurriculumAgentResultJson`, `CurriculumAgentResult`, `CatalogOpsSkill`.
- Identical `inputs LensWardenInputs[base.RallyManagedInputs]` declaration.
- Identical `skills LensWardenSkills[base.RallyManagedSkills]` declaration.
- Identical `output schema`, `output shape`, and `outputs` struct.
- Only genuine per-layer difference: the one `route field next_route: <target>` line, the `workflow LensWardenWorkflow` step sequence, and the `role:` prose.

Why it matters: One scaffold change has to land in all four files. The real per-layer logic (route target, workflow steps, role) is buried under ~70% boilerplate. Every new warden brings another copy.

Smallest credible fix: Hoist the shared scaffold into the existing abstract base.

Shared owner:
- Kind: other
- Name: `LensWardenBase`
- Why: The abstract base already exists; it just stops at the lens-slot bindings. Moving inputs, skills, outputs, schema, and shape into the base lets concrete wardens carry only the parts that differ.

Fix steps:
- Move `inputs`, `skills`, `output schema`, `output shape`, and the `outputs` struct onto `LensWardenBase`.
- Keep `workflow`, `role`, and the per-layer `route field next_route` on the concrete wardens.
- Use `override` (`examples/25_abstract_agent_io_override`) for the route-field difference.
- See `examples/21_first_class_skills_blocks` for hoisted reusable blocks.
```

Bad:

```md
The four wardens look similar.
Consider sharing more code.
```

## What Good Looks Like

A strong run should leave the reader with:

- one clear verdict
- a short scope line
- the top fixes in priority order
- exact evidence on every finding
- rewrite help when wording is the problem
- honest coverage gaps when evidence is missing
- shared-owner guidance when reuse is the real issue
- clear boundary calls when prompt bulk should shrink back to a pointer or shared owner

## Anti-Patterns

Never do these:

- do not use keyword lists as a shortcut for choosing codes
- do not use one weak sentence as evidence for a big claim
- do not issue several overlapping findings when one is enough
- do not report host-specific policy as Doctrine law
- do not reward prompt growth that buys no shared owner, load trigger, or typed truth
- do not invent hidden files, tools, or constraints
- do not let authored doctrine own harness safety control
- do not treat prompt-source `#` comments as emitted agent text
- do not hallucinate findings when the honest answer is a gap
- do not skip the shared owner on a reuse-law finding

## Checklist

Before you return:

- Did you read the full surface family the ask implies?
- Did you decide honestly between no issue, one finding, or several findings?
- Does every finding have exact evidence?
- Is each code the narrowest correct code?
- Did you push for the smallest credible fix first?
- Did you name the shared owner when reuse is the real problem?
- Did you ask whether the added prompt bulk actually earned its keep?
- Did you treat safety control like other harness-owned behavior?
- Did you treat prompt comments as authoring notes, not shipped text?
