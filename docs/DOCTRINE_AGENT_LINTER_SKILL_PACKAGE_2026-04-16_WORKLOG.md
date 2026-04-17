# Worklog

Plan doc: docs/DOCTRINE_AGENT_LINTER_SKILL_PACKAGE_2026-04-16.md

## Initial entry
- Run started.
- Original plan path was the full-arch package-spine flow.

## 2026-04-16 correction
- The prior implement loop for session `019d9832-0a84-7371-960f-f04c7a1bbd64`
  was disarmed at the user's request.
- Updated the plan north star and phase guidance so the skill is clearly the
  auditor and any code surface stays evidence-only or contract-validation only.
- Removed the bundled script files under
  `skills/agent-linter/prompts/scripts/`.
- Replaced the oversized full-arch plan with a compact mini-plan and changed
  the next move to `miniarch-step implement`.

## 2026-04-16 implementation pass
- Rewrote `skills/agent-linter/prompts/SKILL.prompt` so the package now owns:
  - the three core user asks
  - the anti-case
  - naive versus specific use
  - the human-first output bar
  - the no-heuristic, no-script-audit-brain rule
- Added `skills/agent-linter/prompts/references/audit-method.md` and upgraded
  the existing references so the old linter doctrine now lives inside the
  package instead of behind old cross-references.
- Reframed the bundle around direct file-read audits first, with review packets
  kept as an optional proof path.
- Removed the "one tiny thing" bias so package, flow, and repo audits stay
  first-class when that is the real job.
- Updated `agents/openai.yaml` to a stronger runtime metadata shape that better
  matches the real skill contract.
- Added the real emit target, a focused emit test, and live docs for emit,
  install, and use.
- Verification results:
  - `uv sync` passed.
  - `npm ci` passed.
  - `uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_skill`
    passed and emitted `skills/agent-linter/build/`.
  - `uv run --locked python -m unittest tests.test_emit_skill` passed.
  - `make verify-package` passed.
  - `make verify-examples` passed.
- Installed the emitted bundle into
  `~/.codex/skills/agent-linter/` with `rsync -a --delete` so the installed
  skill exactly matches the new script-free build.

## 2026-04-16 doctrine fold-in pass
- Restored the missing packet-gap and `error` verdict doctrine inside the
  package by adding `references/error-handling.md` and reinforcing the same
  rule in the report contract.
- Expanded the skill's audit method so package, flow, and repo audits must map
  and read the full honest surface family before findings are decided.
- Added stronger calibration material to `references/examples.md`, including
  good and bad finding examples, anti-patterns, and a final checklist.
- Made surface-tag and rewrite-target discipline explicit again.
- Clarified that `#` comments in Doctrine `.prompt` files are authoring
  comments, do not go into the agent, and are often the right way to explain
  intent without spending runtime budget.
