# `claude-code-system-prompts`

This source is a strong model for split instruction artifacts: a planning agent, an exploration agent, a verification specialist, and a two-part security monitor.
It teaches how to divide duties cleanly, how to make a read-only mode honest, and how to separate policy tables from execution behavior.

Use this source to pressure Doctrine around:

- role-specific prompts with sharply different authority
- split prompts where part one carries context and part two carries rules
- a verification role that must actually run checks before issuing a verdict
- security policy with explicit block and allow rules instead of vague caution

What to ignore:

- release/version chatter
- product-specific names that do not affect behavior
- any phrasing that is only there to match Claude Code branding
