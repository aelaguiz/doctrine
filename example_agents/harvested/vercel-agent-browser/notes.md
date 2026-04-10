# Notes

## Source Summary

This source combines a repo-level AGENTS file with a browser automation skill
and several focused reference docs. The strongest patterns are command
sequencing, snapshot-driven interaction, auth reuse, session persistence, and
proxy handling.

## High-Signal Patterns

- The browser skill is explicit about the navigate -> snapshot -> interact ->
  re-snapshot loop.
- Authentication is treated as a first-class problem with multiple reusable
  state strategies.
- Session state and browser profiles are distinct from one-off auth imports.
- Proxy settings, bypass rules, and troubleshooting are written as contracts
  rather than as incidental setup notes.
- The root AGENTS file adds repo-wide quality gates and style constraints that
  shape how the browser skill should be extended.

## What This Teaches Doctrine

This source is useful for Doctrine examples that need:

- ordered browser workflows with refresh-after-change discipline
- stateful auth and session carriers that are separate from ordinary inputs
- explicit environment and network controls
- fail-loud command gating and kebab-case CLI conventions
- markdown-native behavioral contracts for browser/computer-use agents
