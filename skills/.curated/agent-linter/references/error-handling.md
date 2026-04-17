# Incomplete Audit Handling

Say the audit is incomplete only when the requested call would be fake without
more surface.

Do not call an audit incomplete just because you found weak text.
Do not call an audit incomplete just because one supporting surface is missing.

## Real Coverage Gaps

These are real incomplete-audit cases:

- the user asked for authored-versus-emitted comparison, but one side is
  missing
- the user asked for a cross-target duplication pass, but one target is
  missing the needed text
- the user asked for repo-wide or package-wide coverage, but too much of the
  honest surface family is missing to make a fair call
- the user asked for declared-constraint checks, but the exact constraint
  surface is missing

## Not Incomplete Cases

These are not incomplete-audit cases:

- one supporting surface is missing, but other findings still have enough
  evidence
- one duplication suspicion is weak and should stay as a gap, not a finding
- a broad audit has some missing emitted companions, but enough real surface
  still exists for supported findings
- a prompt file has `#` comments; those are authoring comments, not shipped
  agent text and not a coverage gap by themselves

In those cases:

- keep the real findings
- narrow the claims to what you can prove
- print the coverage gap clearly

## Gap-First Behavior

When the audit is incomplete:

- name the missing field or surface
- say what that gap blocks
- give the shortest next step that would unblock the pass
- do not invent findings to fill the hole
- say plainly when the honest answer is `I cannot make that call yet`

## Human Default

Use plain language.

Good:

- `Verdict: incomplete audit. The emitted skill is missing, so I cannot make a fair authored-versus-emitted drift call yet.`

Bad:

- `Verdict: fail.` with guessed drift findings and no evidence
