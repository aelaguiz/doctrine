# Report Contract

This skill returns a layered markdown report for humans.
It is for human review.

## Default Markdown Shape

Use this order:

1. verdict and scope summary
2. what was checked
3. top fixes first
4. scorecard
5. grouped findings
6. coverage gaps
7. next moves

Helpful defaults:

- highest-value findings first
- severity grouping
- exact evidence on every finding
- rewrite help for wording and readability issues
- one normalized duplicate excerpt plus affected targets
- say what good looks like when the fix would otherwise feel vague
- coverage gaps printed clearly when exact evidence is missing
- enough context that a tired human can fix the issue without re-reading the
  whole package

## Human Finding Shape

Every finding should carry:

- `AL###` code and title
- severity and confidence
- scope and affected targets
- principle or rule
- short summary
- exact evidence
- why it matters
- the smallest credible fix
- concrete fix steps
- suggested rewrite when useful
- good example and bad example when they help
- shared owner suggestion

If there is no exact evidence, there is no finding.

## Shared Owner Suggestion

Every finding should say whether a shared owner is needed.
This is one of the most valuable parts of the report.

For reuse-law findings, almost always name a concrete owner.
This is especially true for:

- `AL200`
- `AL210`
- `AL220`
- `AL230`
- `AL910`

When a shared owner is needed, name:

- `kind`: `skill`, `module`, `contract`, or `other`
- `name`
- `rationale`

When no shared owner is right, say `Shared owner: none.` plainly.

## Verdict

Lead with one honest verdict:

- `pass` when no material findings remain
- `fail` when one or more material findings matter
- `incomplete audit` when missing surface makes the requested call fake

Do not invent findings just to avoid an incomplete audit.

## Coverage Gaps

Call out missing evidence plainly.
Do not guess over gaps.

Typical gap cases:

- emitted Markdown is missing for a requested authored-versus-emitted audit
- declared constraints are missing for a constraints audit
- broad repo coverage was requested, but only one local slice was inspected
- one target in a duplication comparison is missing the needed surface

## Scorecard

Keep the scorecard short and human-readable.
Useful sections include:

- resolver fit
- thin-harness fit
- reusable-method fit
- deterministic split
- evidence quality
- actionability

Use scorecards for triage, not fake precision.
Do not let the scorecard distract from the top fixes.

## Quality Bar

Great output feels like a strong linter, not a vague reviewer.
It should feel like a sharp teammate stepping in with a clear read and a fix
path.

Great output:

- names the strongest issue first
- proves it with exact evidence
- uses the right code
- gives a fix the developer can act on now
- pushes for the smallest credible fix first
- names the shared owner when reuse is the real problem
- gives a rewrite only when it is clearly useful
- feels like a sharp review from a strong teammate, not a compliance dump
- clears the fog fast and tells the reader where to start

Weak output:

- sounds plausible but cannot prove the claim
- reports local policy as if it were Doctrine law
- emits five overlapping findings where one would do
- skips the shared owner on a reuse finding
- repeats the bad text without a fix
- gives a rewrite that changes meaning
- reads like a drained checklist instead of a useful review
- leaves the reader with more fog than they started with
