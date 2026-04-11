# Why Doctrine

Doctrine exists because serious agent systems are not really Markdown authoring
problems.

The first real pressure test was a section-dossier-style agent in a multi-stage
workflow. One role needed shared turn rules, typed inputs and outputs, routed
handoffs, skill contracts, and a few precise lane-specific overrides. The
runtime still had to be a single `AGENTS.md` file, but the authoring surface
had already become a program.

## The Failure Mode

When the source of truth is hand-maintained Markdown:

- shared sections get copied into multiple agents and drift
- a small policy change turns into a multi-file search-and-hope edit
- humans lose track of which wording is canonical
- large agent families keep paying the same load and index cost whenever you
  need to regenerate runtime artifacts
- coding agents make the problem worse by expanding or duplicating large files
  instead of making small structural edits

### Before: copied Markdown drifts

Names and paths below are anonymized, but this shape is real.

```md
## Handoff Comment

Say what changed.
Name the current output files.
Name the next owner.
```

```md
## Handoff Comment

Say what changed.
Name the current output files.
If blocked, name the failing gate.
Name the next owner.
```

Both versions are plausible. Neither is obviously canonical. The divergence is
the problem.

### After: shared doctrine plus local overrides

```prompt
workflow SharedHandoff: "Handoff Comment"
    what_changed: "What Changed"
        "Say what changed."

    current_files: "Current Output Files"
        "Name the current output files."

    next_owner: "Next Owner"
        "Name the honest next owner."


workflow BlockedHandoff[SharedHandoff]: "Handoff Comment"
    inherit what_changed
    inherit current_files

    failing_gate: "Failing Gate If Blocked"
        "If the work is blocked, name the exact failing gate."

    inherit next_owner


abstract agent RoleHome:
    handoff_comment: SharedHandoff


agent SectionAnalyst[RoleHome]:
    role: "Core job: build the current section brief."
    inherit handoff_comment


agent AcceptanceReviewer[RoleHome]:
    role: "Core job: review the current section brief."
    override handoff_comment: BlockedHandoff
```

One shared change now lands once. The compiler keeps the children honest.

## Why This Is Programming, Not Prompting

Doctrine is useful because it gives agent doctrine the properties we expect from
code:

- named declarations give shared doctrine stable identities
- inheritance and composition let one fix land once instead of in copied prose
- typed `inputs`, `outputs`, and `skills` make turn contracts explicit
- compile-time errors fail loud when a child forgets an inherited section or
  points at the wrong thing
- shared compile sessions and safe parallel batch work keep large prompt
  families practical instead of redoing the same serial compile setup for every
  concrete agent
- runtime Markdown stays clean because the structure lives in the source, not in
  emitted boilerplate

The important point is not "Markdown is bad." The important point is that
runtime Markdown is the wrong authoring surface once agents become nuanced,
shared, and long-lived.

## Why Keep `AGENTS.md` At Runtime

Today, coding-agent tools already know how to consume `AGENTS.md`. Doctrine does
not try to replace that runtime surface. It replaces the maintenance surface.

That split is deliberate:

- author in a structured DSL
- compile to the Markdown runtime artifacts existing tools can read
- keep humans and coding agents editing the structured source of truth instead
  of giant emitted files

## Design Goals

- author clarity first
- maximize sharing and reusability
- keep the runtime artifact compatible with current coding-agent tools
- make small, safe edits possible for coding agents that are bad at maintaining
  giant Markdown files
- keep large prompt families practical by making compilation deterministic,
  reusable, and fast enough for real repos
- fail loud when the source is inconsistent instead of silently papering over
  drift
