---
title: "Remove stale legacy draft port references"
date: 2026-04-07
status: complete
owners: [aelaguiz]
reviewers: [aelaguiz]
fallback_policy: forbidden
related:
  - AGENTS.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md
  - docs/PYPROMPT_VSCODE_LANGUAGE_HIGHLIGHTING_PLAN_2026-04-06.md
  - docs/PORT_EXAMPLE_SYNTAX_THROUGH_PHASE_FOURTEEN_2026-04-06.md
  - docs/aelaguiz/remove_legacy_draft_port_references_2026-04-07_WORKLOG.md
---

# TL;DR

Delete the docs that only existed for the removed legacy draft port effort, then scrub the remaining live docs so the repo no longer points at deleted draft or port paths.

## North Star

Claim:
- The repo should no longer contain live guidance or doc links that point at the deleted legacy draft corpus or its deleted port workspace.

In scope:
- deleting docs that are only about the removed legacy draft port effort
- rewriting live docs that still point at deleted draft or port paths
- keeping any still-useful language-design guidance, but rewriting it in generic terms instead of naming deleted paths
- verifying the active corpus still passes after doc cleanup

Out of scope:
- changing shipped parser/compiler behavior
- rewriting unrelated doc wording just for style
- removing unrelated numeric strings such as lockfile hashes or external standards

Definition of done:
- `rg` finds no remaining live references to the deleted draft corpus, its deleted port workspace, or repo guidance that still depends on that removed effort
- the repo keeps any still-useful guidance in generic language where needed
- `make verify-examples` still passes

## Requirements
<!-- lilarch:block:requirements:start -->

- Remove stale references to deleted legacy draft/port paths from live repo docs and instructions.
- Default to hard deletion for docs whose whole purpose was the removed legacy draft port effort.
- For mixed-purpose docs, preserve useful design guidance but rewrite it so it no longer depends on deleted draft or port names or paths.
- Do not touch runtime code unless verification proves the docs were masking a real implementation dependency.

Defaults:
- Treat `AGENTS.md` and active docs under `docs/` as live guidance that must be current.
- Prefer generic phrases like "legacy draft role docs" only when a design point still matters after the named corpus is gone.

Non-requirements:
- Preserve historical references for their own sake.
- Keep dead links as context.
<!-- lilarch:block:requirements:end -->

## Research Grounding
<!-- arch_skill:block:research_grounding:start -->

- `rg` found stale references in `AGENTS.md`, `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md`, `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`, `docs/LANGUAGE_DESIGN_NOTES.md`, `docs/PYPROMPT_VSCODE_LANGUAGE_HIGHLIGHTING_PLAN_2026-04-06.md`, and `docs/PORT_EXAMPLE_SYNTAX_THROUGH_PHASE_FOURTEEN_2026-04-06.md`.
- Two docs were fully dedicated to the removed legacy draft effort and were clear delete candidates.
- `examples/` now contains only `01` through `26`; the old legacy draft directory is gone.
- `git status --short` shows existing user edits in several docs, so cleanup must be minimal and cooperative in already-dirty files.
<!-- arch_skill:block:research_grounding:end -->

## Current Architecture
<!-- arch_skill:block:current_architecture:start -->

- Repo instructions in `AGENTS.md` still describe the deleted legacy draft surface as if it exists.
- Two docs are pure leftovers from the removed port effort.
- Several live docs still use deleted draft shorthand, which now creates dead links or stale repo shorthand.
<!-- arch_skill:block:current_architecture:end -->

## Target Architecture
<!-- arch_skill:block:target_architecture:start -->

- The repo contains no live references to deleted legacy draft or port paths.
- Active docs describe any still-useful historical pressure in generic language instead of naming deleted artifacts.
- Repo instructions stay aligned with the current manifest-backed `01` through `26` surface and existing docs only.
<!-- arch_skill:block:target_architecture:end -->

## Call-Site Audit
<!-- arch_skill:block:call_site_audit:start -->

- Delete:
  - the two docs dedicated only to the removed legacy draft port effort
- Edit:
  - `AGENTS.md`
  - `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md`
  - `docs/LANGUAGE_AND_PARSER_FIT_ANALYSIS.md`
  - `docs/LANGUAGE_DESIGN_NOTES.md`
  - `docs/PYPROMPT_VSCODE_LANGUAGE_HIGHLIGHTING_PLAN_2026-04-06.md`
  - `docs/PORT_EXAMPLE_SYNTAX_THROUGH_PHASE_FOURTEEN_2026-04-06.md`
<!-- arch_skill:block:call_site_audit:end -->

## Phase Plan
<!-- arch_skill:block:phase_plan:start -->

Phase 1:
- create the compact doc/worklog
- delete the pure legacy-draft leftovers
- rewrite live docs to remove dead references

Phase 2:
- rerun targeted searches
- run `make verify-examples`
- mark the doc complete only if both cleanup and verification hold
<!-- arch_skill:block:phase_plan:end -->

## Plan Audit
<!-- lilarch:block:plan_audit:start -->

- The work fits lilarch: one cleanup pass plus verification.
- The delete list is explicit and limited.
- The edit list is grounded by search evidence.
- Risk is low because the change is doc-only, but already-dirty files require narrow patches.
<!-- lilarch:block:plan_audit:end -->

## Implementation Audit
<!-- arch_skill:block:implementation_audit:start -->

Status:
- Complete.

Verification target:
- `rg` for stale references
- `make verify-examples`

Verification result:
- Targeted `rg` searches for deleted draft and port paths returned no matches in live repo docs or instructions.
- `make verify-examples` passed on 2026-04-07 after the cleanup.
<!-- arch_skill:block:implementation_audit:end -->
