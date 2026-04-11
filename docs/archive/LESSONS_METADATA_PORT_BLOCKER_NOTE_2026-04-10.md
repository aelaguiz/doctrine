---
title: "Lessons Metadata Port Blocker Note"
date: 2026-04-10
status: archived
doc_type: blocker_note
related:
  - ../../../paperclip_agents/docs/LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md
  - ../REVIEW_SPEC.md
  - ../WORKFLOW_LAW.md
---

# TL;DR

The Paperclip Lessons symbolic port blocked on the metadata seam, not because
Doctrine was missing first-class `review` or route-only workflow law, but
because the compiler state that shipped at the time only accepted
`current artifact` and `own only` roots when they resolved directly to
declared input or output artifacts visible to the concrete agent turn.

The Lessons metadata family in `paperclip_agents` currently routes that seam
through shared imported contracts plus inherited role-home output buckets. In
that shape, the metadata port could not land honest one-current-file law
without either duplicating local I/O owners or redesigning the metadata-writer
surface.

Doctrine now ships concrete-turn bound roots through keyed `inputs:` and
`outputs:` bindings. This note is historical context for the failed port, not a
statement about the current compiler ceiling.

# External Ref

The failed implementation attempt is recorded in Paperclip's implementation
plan:

- [LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md](../../../paperclip_agents/docs/LESSONS_SYMBOLIC_DOCTRINE_PORT_IMPLEMENTATION_PLAN_2026-04-10.md)

The relevant section is `Phase 2 - Prove the model on metadata`, which marks
the phase `BLOCKED` and explains why the prompt family was restored to the last
green state.

# What Blocked

Paperclip tried to port
`paperclip_agents/doctrine/prompts/lessons/contracts/metadata_wording.prompt`
onto shipped workflow-law carriers for:

- mode handling
- one-current-file law
- narrow scope
- rewrite exclusions

That port hit a real shipped Doctrine constraint:

- `current artifact` must resolve to one declared input or output artifact, not
  an indirect or partially addressed target.
- The `via Output.field` carrier must point at an emitted output on the
  concrete turn, and that carrier field must be present in `trust_surface`.
- `own only` must stay rooted in that same `current artifact`.

Paperclip's metadata lane currently spreads the seam across:

- shared contract outputs in
  [metadata_wording.prompt](../../../paperclip_agents/doctrine/prompts/lessons/contracts/metadata_wording.prompt)
- inherited role-home outputs in
  [role_home.prompt](../../../paperclip_agents/doctrine/prompts/lessons/common/role_home.prompt)
- the concrete metadata-writer agent's inherited output buckets in
  [lessons_metadata_copywriter/AGENTS.prompt](../../../paperclip_agents/doctrine/prompts/lessons/agents/lessons_metadata_copywriter/AGENTS.prompt)
- shared handoff carriers in
  [outputs.prompt](../../../paperclip_agents/doctrine/prompts/lessons/outputs/outputs.prompt)

The plan's blocker claim is that these honest symbolic targets were not direct
enough for the current compiler checks. That matches the shipped Doctrine code.

# Doctrine Evidence

The shipped compiler enforces the relevant constraints directly:

- `current artifact` roots must resolve to declared `input` or `output`
  declarations in [compiler.py](../../doctrine/compiler.py).
- `current artifact` outputs must be emitted by the concrete turn in
  [compiler.py](../../doctrine/compiler.py).
- `current artifact` carriers must point at emitted outputs and
  `trust_surface` fields in [compiler.py](../../doctrine/compiler.py).
- `own only` roots must stay inside the current artifact in
  [compiler.py](../../doctrine/compiler.py).

The shipped review docs also show that `review` already reuses the same
portable-currentness rule:

- [REVIEW_SPEC.md](../REVIEW_SPEC.md)

That matters because it narrows the blocker. The missing piece was not
"review exists" or "currentness exists." The missing piece was support for
binding those semantics through the Lessons shared and inherited I/O model.

This last sentence is an inference from the compiler rules plus the Paperclip
prompt shape, not a standalone compiler comment.

# What Was Not Missing

This blocker should not be summarized as "Doctrine did not have review yet" or
"workflow law was not fully built."

What already shipped:

- first-class `review`
- `current none` for route-only or blocked outcomes
- portable currentness via `current artifact X via Output.field`
- `trust_surface`-backed carrier validation
- `own only` scope validation rooted in the current artifact

The blocked seam was narrower: metadata current-file and owned-scope law across
shared or inherited I/O surfaces.

# Next Honest Move

The honest next move is no longer "wait for Doctrine support." That support now
exists for concrete-turn bound roots.

The open question is narrower and belongs on the Paperclip side:

- port the metadata seam onto Doctrine's shipped bound-root model, or
- deliberately redesign the metadata-writer I/O surface if the shared contract
  layering still creates pressure beyond what concrete-turn bindings should own

That keeps the historical blocker note accurate while leaving the remaining
port decision on the repo that owns the metadata seam.
