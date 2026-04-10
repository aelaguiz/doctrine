# LangChain

## Why This Source Matters

This repo is a useful baseline for a large Python monorepo that keeps top-level behavioral guidance, API stability rules, and contribution gates in markdown. It is less about a single agent runtime and more about a strong repo-wide contract.

## High-Signal Doctrine Pressure

- `scope_hierarchy`: the same development guide is published as both `AGENTS.md` and `CLAUDE.md`, which makes the repo a clean example of duplicate-format parity.
- `commands_and_quality_gates`: the docs lead with `uv`, `make`, `ruff`, `mypy`, and `pytest` commands before they get into architecture.
- `negative_guardrails`: the guide is full of explicit "do not break public interfaces" and doc-format restrictions that can become Doctrine negative cases.

## What To Pull Into Doctrine

- stable public-interface rules with warning language for exported APIs
- repo-wide command gates and test structure expectations
- duplicated instruction files in different agent formats
