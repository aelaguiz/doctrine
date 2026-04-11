---
title: "Doctrine VS Code Auditor Codex Exec SIGABRT"
date: 2026-04-11
status: fix-ready
owners: ["aelaguiz"]
reviewers: []
related:
  - /Users/aelaguiz/.agents/skills/arch-step/scripts/arch_controller_stop_hook.py
  - editors/vscode/tests/integration/run.js
  - editors/vscode/package.json
  - /Users/aelaguiz/Library/Logs/DiagnosticReports/Code-2026-04-11-144827.ips
  - /Users/aelaguiz/Library/Logs/DiagnosticReports/Code-2026-04-11-144829.ips
---

# TL;DR

<!-- bugs:block:tldr:start -->
## Symptom

Fresh `implement-loop` auditor runs fail `cd editors/vscode && make` even when the
same command passes from the main worktree session.

## Impact

`audit-implementation` reopens clean work and blocks loop completion on a
non-repo-local failure mode.

## Most likely cause

The Stop-hook auditor launches Codex with `codex exec --full-auto`, which means
a sandboxed child run. In that sandboxed child context, VS Code/Electron aborts
at macOS app startup and registration time before the integration suite can run.
This is not a Doctrine test failure and not a model/reasoning issue.

## Next action

Change the auditor verification strategy so the VS Code integration path is not
run inside the sandboxed `codex exec --full-auto` child. The lowest-risk fix is
to special-case that verification to an unsandboxed child or to treat the
main-worktree unsandboxed editor verification as the authoritative signal.

## Status

`fix-ready`
<!-- bugs:block:tldr:end -->

# 0) Bug North Star

Prove whether the failing `audit-implementation` result is caused by Doctrine
code/tests or by the Codex fresh-audit runtime. The issue is only fix-ready if
the failure boundary is concrete enough that we can repair the controller or
verification policy without touching unrelated language/editor behavior.

# 1) Bug Summary

The failing surface is the fresh auditor launched by the Stop hook, not the
main session and not a spawned subagent. The exact hook path is:

- [arch_controller_stop_hook.py](/Users/aelaguiz/.agents/skills/arch-step/scripts/arch_controller_stop_hook.py:325)
- the hook invokes `codex exec --ephemeral --disable codex_hooks --cd <repo> --full-auto ...`
  at [arch_controller_stop_hook.py](/Users/aelaguiz/.agents/skills/arch-step/scripts/arch_controller_stop_hook.py:338)

The VS Code verification path itself lives in
[run.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/run.js:127)
and retries `SIGABRT` startup failures four times before surfacing the final
`TestRunFailedError`.

# 2) Evidence

<!-- bugs:block:analysis:start -->
## 2.1 Reproduced failing path

The real failing path was reproduced with the same child-process shape the
auditor uses, but pinned to `gpt-5.4` with `model_reasoning_effort="medium"`:

- `codex exec --ephemeral --disable codex_hooks --cd /Users/aelaguiz/workspace/doctrine --full-auto -m gpt-5.4 -c 'model_reasoning_effort="medium"' ...`
- child command run: `cd editors/vscode && make`
- result:
  - `npm install`, `test:unit`, and `test:snap` passed
  - `npm run test:integration` aborted with `SIGABRT` on all four retries
  - top-level `make` exited non-zero

This ruled out the earlier mistaken theory that the failure was specific to
`spawn_agent` or to `xhigh` reasoning.

## 2.2 Same child shape passes when unsandboxed

The same `codex exec` child path, same model, and same prompt passed when the
sandbox was removed:

- `codex exec --ephemeral --disable codex_hooks --cd /Users/aelaguiz/workspace/doctrine --dangerously-bypass-approvals-and-sandbox -m gpt-5.4 -c 'model_reasoning_effort="medium"' ...`
- child command run: `cd editors/vscode && make`
- result:
  - full `make` passed, including `npm run test:integration`, alignment
    validation, and VSIX packaging

This isolates the bug to the sandboxed auditor runtime rather than to the repo
state, test corpus, or model selection.

## 2.3 Crash evidence points to macOS app startup, not Doctrine tests

The relevant macOS crash reports show Code aborting during application
registration and AppKit initialization:

- [Code-2026-04-11-144827.ips](/Users/aelaguiz/Library/Logs/DiagnosticReports/Code-2026-04-11-144827.ips:46)
  records `SIGABRT`
- [Code-2026-04-11-144827.ips](/Users/aelaguiz/Library/Logs/DiagnosticReports/Code-2026-04-11-144827.ips:51)
  shows the main thread aborting via:
  - `___RegisterApplication_block_invoke`
  - `_RegisterApplication`
  - `GetCurrentProcess`
  - `_NSInitializeAppContext`
  - `+[NSApplication sharedApplication]`
- the same report also shows LaunchServices work on background threads via
  `LaunchServices::Database::Context::_get`
- [Code-2026-04-11-144829.ips](/Users/aelaguiz/Library/Logs/DiagnosticReports/Code-2026-04-11-144829.ips:46)
  and [Code-2026-04-11-144829.ips](/Users/aelaguiz/Library/Logs/DiagnosticReports/Code-2026-04-11-144829.ips:51)
  show the same abort shape

That evidence means the app dies before Doctrine's extension-host assertions can
even become relevant.

## 2.4 Rejected theories

- DNS failure to `update.code.visualstudio.com` is not the root cause.
  - In the sandboxed child, `downloadAndUnzipVSCode` reports `ENOTFOUND`, but
    it falls back to the cached `1.115.0` install and still aborts.
  - In the unsandboxed child, the cached install also works without needing a
    network fetch.
- Model/reasoning settings are not the root cause.
  - The failure reproduces on `gpt-5.4` with `medium`.
- Repo worktree drift is not the root cause.
  - The same worktree passes `cd editors/vscode && make` from the main session
    and from an unsandboxed `codex exec` child.
<!-- bugs:block:analysis:end -->

# 3) Investigation

## 3.1 Ranked hypotheses

1. The sandboxed fresh-audit child cannot safely launch the macOS VS Code/Electron
   app bundle, so Electron aborts during app registration before the test suite
   starts.
2. The retry logic in [run.js](/Users/aelaguiz/workspace/doctrine/editors/vscode/tests/integration/run.js:102)
   is treating a deterministic sandbox startup failure as transient.
3. The network lookup failure is noisy but secondary; cached binary launch still
   reaches the same abort.

## 3.2 Verdict

The likely root cause is now concrete:

- the Stop-hook auditor uses `--full-auto`, which is a sandboxed child runtime
- the sandboxed child can reach the cached VS Code install but cannot complete
  macOS app startup
- Electron aborts in AppKit/LaunchServices registration, so the VS Code
  integration suite never gets a real chance to run

This is fix-ready because the blast radius is now narrow and the fix target is
the controller/verification policy, not the language implementation.

# 4) Suspected Blast Radius

- `implement-loop` and any other hook-driven auditor path that tries to run a
  GUI Electron/VS Code verification inside `codex exec --full-auto`
- potentially any future macOS GUI app verification launched from the same
  sandboxed child runtime

# 5) Verification Plan

- If we change the controller:
  - reproduce the old failing path once with the sandboxed child to confirm the
    baseline
  - run the new auditor path
  - confirm `cd editors/vscode && make` is no longer evaluated in the sandboxed
    child or is rerun unsandboxed where it passes
- Keep repo verification unchanged:
  - `cd editors/vscode && make`

# 6) Fix Plan

<!-- bugs:block:fix_plan:start -->
## Minimal credible fix

- Do not run the VS Code integration verification inside the Stop-hook
  `--full-auto` sandboxed child.
- Either:
  - special-case the editor verification signal to an unsandboxed child run, or
  - treat the main-session unsandboxed `cd editors/vscode && make` result as
    the authoritative proof signal for editor parity and keep the auditor
    read-only on that surface.

## Explicit non-goals

- Do not change Doctrine language/editor behavior to "work around" the sandbox.
- Do not weaken the VS Code test suite itself unless a separate repo-local test
  bug is found.
- Do not keep retrying `SIGABRT` as though it were random if the launch context
  is known-bad.
<!-- bugs:block:fix_plan:end -->

# 7) Implementation

<!-- bugs:block:implementation:start -->
No code changes yet. Investigation only.
<!-- bugs:block:implementation:end -->
