# 99 Language Gap Audit

## Current Read

Right now, `99` is not showing a clear hard language blocker.

The remaining useful pressure mostly looks like example work and authoring
cleanup, not proof that the language needs new primitives.

## Purpose

This audit looks at the useful pressure from `examples/99_not_clean_but_useful`
without treating the current shipped bootstrap as the decision surface.

It also records later review commentary that changes how some older notes
should be read.

## Working Assumptions

- This audit is about language direction, example shape, and design pressure.
  It is not about the current shipped compiler being incomplete.
- `12_role_home_composition` already earns the basic role-home shell.
- `14_handoff_truth` now shows the clean way to name what the next owner should
  use now with inputs, outputs, authored routing / stop slots, and plain prose.
- The open question is now what belongs inside that shell, not whether role
  homes need a new primitive.
- Packets are not a language primitive direction.
- The same authoring pressure should be handled through inputs, outputs,
  authored routing / stop slots, ownership, and readable file contracts.
- The language remains skill-first.
- A separate `runtime_tools` surface is drift, not direction.
- `99` remains requirement fodder, not a target design.

## What 99 Still Teaches

### 1. Shared role-home structure is real

The repeated sections across `99` are useful because they show that many roles
share the same human reading order and the same broad support structure.

That part is already earned enough by example 12.

The remaining issue is cleanup and scope:

- what should live in shared sections
- what should stay role-local
- what should stay plain prose instead of becoming structured

### 2. Ownership flow is real

`99` repeatedly encodes:

- normal owner order
- critic checkpoints
- reroutes
- stop and escalate behavior
- what the next owner should trust now

Examples 7, 10, and 13 already point in the right direction.

The remaining issue is simplification and cleanup, not whether routing needs to
exist at all.

### 3. File ownership and review truth are real

`99` cares a lot about:

- which files are in scope now
- which files changed semantically
- which files are still valid without semantic change
- what a downstream role may trust
- what review files must be named explicitly

That pressure is real.

It should not become a packet primitive.

It should be expressed through inputs, outputs, authored routing / stop slots, readable file
contracts, and explicit review truth.

`14_handoff_truth` now covers the narrow "tell the next owner what to use now"
pattern, so this is no longer a reason to invent a new trust primitive.

### 4. Proof and authority boundaries are real

This is one of the strongest useful pressures in `99`.

`99` clearly distinguishes:

- wording and concept grounding
- deterministic validation
- exact action authority
- live runtime parity

That distinction still needs cleaner modeling and cleaner examples.

### 5. Attached checkout truth is real

`99` repeatedly separates workflow truth from product truth in an attached
checkout or external surface.

That distinction should survive.

The useful pressure is:

- where truth comes from
- how it is verified
- what should fail loud when setup is not honest

## What Should Not Become Language Features

These show up in `99`, but they should not drive the language:

- packet primitives
- redundant `owns` prose when the output contract already makes ownership
  obvious
- raw helper-command catalogs as first-class syntax
- env var dumps as first-class syntax
- giant copied quality-bar doctrine blocks
- HTML anchors
- hardcoded hostnames and machine paths as language structure
- giant repeated role homes

Those are refactoring targets or prose concerns, not language goals.

## What Now Looks Stale

### Role-home composition as a major unresolved primitive

That reading is stale.

Example 12 already earned enough of the shell.

The remaining work is about content discipline inside the shell.

### Packet modeling as the next big primitive

That direction is rejected.

The same pressure should be handled through I/O, authored routing and stop
guidance, ownership, and file contracts.

### `runtime_tools` as a separate surface

That drifted into examples 12 and 13.

It is not the intended direction.

That cleanup has now been done.

## Real Issues In Simple Terms

These are the things that still look real after removing the stale framing:

1. The examples still need a cleaner way to talk about proof routes and exact
   authority boundaries.
2. The examples still need a cleaner way to talk about attached checkouts and
   external product truth.
3. `99` still carries too much duplicated doctrine and too many inline helper
   details to be used as a direct design source.

## What Should Be Treated As Example Cleanup Instead Of New Primitives

- role-home shell cleanup
- review wording cleanup
- proof-route explanation cleanup
- file-ownership explanation cleanup
- attached-checkout explanation cleanup

Those may need new examples, but they do not automatically imply new language
features.

## Suggested Example Follow-Up

If the repo wants to keep earning the useful parts of `99`, the next examples
should be small and narrow:

1. one example for proof-route and authority boundaries
2. one example for attached-checkout truth and fail-loud verification

Those would be better than promoting the messy `99` packet pattern into the
language.

## Short Conclusion

The main useful pressure from `99` is not "more Markdown."

It is cleaner modeling of:

- ownership flow
- I/O and readable file contracts
- evidence and review truth
- proof boundaries
- attached checkout truth

The main things to reject from `99` are:

- packet primitives
- `runtime_tools` as a separate surface
- giant copied doctrine blobs

This audit supersedes earlier readings that treated role-home composition or
packet primitives as the main next language problems.
