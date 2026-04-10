# Rocky Linux Website

## Why This Source Matters

This repo combines a root CLAUDE guide with nested documentation playbooks that explain i18n, testing, upgrade, lint, and issue-handling policy for a large multilingual site.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the root guide points into a docs tree that acts like a second layer of repo instructions.
- `commands_and_quality_gates`: build, lint, format, unit, and E2E commands are spelled out in the root guide and reinforced by the upgrade playbook.
- `negative_guardrails`: the lint decision and known-issues documents define what not to change and when to revisit a technical choice.
- `domain_specific_constraints`: i18n caching, Playwright selectors, Next.js proxy rename, and 34-language support are strong repo-specific constraints.
- `context_and_memory`: the docs index and “Last updated” discipline create a stable breadcrumb trail for decisions and workarounds.

## What To Pull Into Doctrine

- repo docs that behave like instruction surfaces
- locale-sensitive routing and caching rules
- Playwright testing patterns that encode accessibility and portal handling
- upgrade playbooks and decision records as first-class repo memory
