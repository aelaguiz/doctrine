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
