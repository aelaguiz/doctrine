# Cloudflare Docs

## Why This Source Matters

This repo is not a code SDK, but it is a strong markdown instruction corpus. The repo-level AGENTS file and the style-guide pages together define how contributors should write, validate, review, and AI-optimize documentation.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the repo AGENTS file governs the whole tree, while the style guide splits into overview, AI tooling, writing rules, formatting rules, and review workflow.
- `commands_and_quality_gates`: the root instructions define `npm ci`, `npm run check`, local-only full builds, and validation steps for MDX and code changes.
- `negative_guardrails`: the docs repo bans unescaped MDX syntax, contractions, skipped heading levels, invalid code block languages, and other content gotchas.
- `skills_tools_and_capabilities`: the AI tooling page explicitly covers Markdown for Agents, MCP servers, agent skills, and rulesync-based AI config generation.
- `context_and_memory`: the review workflow page describes preview builds, codeowner assignment, no-response handling, and stale-workflow avoidance.
- `domain_specific_constraints`: the style guide defines Cloudflare-specific voice, formatting, and content structure constraints that behave like repo-local law.

## What To Pull Into Doctrine

- markdown-based instruction layers above code
- explicit docs authoring law with local overrides
- AI-tooling guidance embedded in a docs repo
- review automation and preview-build requirements
- syntax-level guardrails for markdown and MDX content
