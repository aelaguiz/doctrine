# Worklog

Plan doc: docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md

## Initial entry
- Run started.
- Current phase: Phase 1 - Normalize the authored readable grammar and AST.

## Phase 1 (Normalize the authored readable grammar and AST) Progress Update
- Work completed:
  - Fast-forwarded this implementation worktree from `d70a274` to `d3aea41` so the run starts from the parent branch's newer grammar/model/parser and canonical plan state.
  - Re-synced Python and Node dependencies with `uv sync` and `npm ci`.
  - Armed `.codex/implement-loop-state.json` for this `implement-loop` run.
- Tests run + results:
  - `uv sync` — passed.
  - `npm ci` — passed.
- Issues / deviations:
  - None yet. Implementation now proceeds from the newer parent-branch base instead of the original worktree cut point.
- Next steps:
  - Widen the readable grammar and AST for typed block headers and typed payloads.

## Final implementation update
- Work completed:
  - Landed the full typed readable-markdown model and grammar across `document`, record/output bodies, workflow section bodies, and skill-entry bodies.
  - Reworked the compiler and renderer for native `definitions`, `table`, `callout`, `code`, `rule`, readable guards, document inheritance, override-kind validation, and keyed readable descendants.
  - Added manifest-backed examples `58` through `61` and updated example `27` proof to match the now-stable readable spacing contract.
  - Synced evergreen docs, diagnostics coverage, VS Code resolver support, tmLanguage keyword coverage, integration assertions, and packaged VSIX output.
  - Recorded the non-obvious renderer and resolver regressions in `gbrain` after confirming the repo env and brain health.
- Tests run + results:
  - `uv sync` — passed.
  - `npm ci` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/58_readable_document_blocks/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/59_document_inheritance_and_descendants/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/60_shared_readable_bodies/cases.toml` — passed.
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/61_multiline_code_and_readable_failures/cases.toml` — passed.
  - `make verify-diagnostics` — passed.
  - `make verify-examples` — passed.
  - `cd editors/vscode && make` — passed.
- Issues / deviations:
  - Renderer spacing initially double-counted blank lines because older compiled bodies already carry explicit empty-string separators. The final renderer contract now collapses those transitions to one blank line, and the proof was updated where older manifests assumed the inconsistent spacing.
  - VS Code packaging surfaced two real drift points that were fixed in this run: readable header regexes needed qualifier-aware matching for resolver navigation, and tmLanguage keyword coverage needed the new readable keywords so `validate_lark_alignment.py` could pass.
- Next steps:
  - None inside this implement loop. The readable-markdown cutover is implemented, verified, and reflected in the canonical plan/worklog state.

## Reopened Phase 5 follow-through
- Work completed:
  - Hardened `editors/vscode/tests/integration/run.js` so VS Code integration runs use short temp `--user-data-dir` and `--extensions-dir` paths instead of the repo-local `.vscode-test` profile path that had been producing the macOS IPC-length warning during the failed audit run.
  - Reframed `docs/archive/second_wave/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md` as a historical umbrella artifact and updated its baseline/problem-grounding sections so they no longer present pre-ship readable-markdown and `structure:` gaps as current repo reality.
  - Reframed `docs/archive/second_wave/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md` the same way, keeping it as implementation history instead of live shipped-truth commentary for readable markdown.
- Tests run + results:
  - `cd editors/vscode && make` — passed, including `npm run test:integration`, alignment validation, and VSIX packaging.
  - `.venv/bin/python -m doctrine.verify_corpus` — passed.
  - `.venv/bin/python -m doctrine.diagnostic_smoke` — passed.
- Issues / deviations:
  - None remaining from the reopened Phase 5 audit items. The loop remains armed so the next fresh audit can decide whether to close Phase 5 again.
- Next steps:
  - Stop here for the next implement-loop audit pass to update the authoritative audit block and phase state.

## Reopened Phase 5 follow-through (second fresh-audit fix)
- Work completed:
  - Added a bounded retry in `editors/vscode/tests/integration/run.js` for transient VS Code startup aborts that surface as `SIGABRT` from `@vscode/test-electron`, while still using short temp profile paths on every attempt.
  - Replaced the stale `Implementation Audit (authoritative)` block in `docs/archive/second_wave/DOCTRINE_INTEGRATION_SURFACES_FULL_IMPLEMENTATION_2026-04-11.md` with a superseded historical snapshot note that explicitly points current audit authority back to `docs/archive/second_wave/DOCTRINE_READABLE_MARKDOWN_FULL_IMPLEMENTATION_2026-04-11.md`.
  - Softened the umbrella mechanics doc wording in `docs/archive/second_wave/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md` so editor-package success is described as a historical plan-closure signal, not as current repo truth.
- Tests run + results:
  - `npm run test:integration` — passed repeatedly after the retry-wrapper hardening.
  - `cd editors/vscode && make` — passed non-interactively, including integration, alignment validation, and VSIX packaging.
  - `.venv/bin/python -m doctrine.verify_corpus` — passed.
  - `.venv/bin/python -m doctrine.diagnostic_smoke` — passed.
- Issues / deviations:
  - The direct integration runs were already passing locally when this reopen pass started, so the retry wrapper is a stability hardening for the audit-reported transient abort rather than a fix for a deterministic local repro.
  - Phase 5 remains intentionally reopened in the plan doc until the next fresh audit rewrites the authoritative audit block.
- Next steps:
  - Stop again for the next implement-loop audit pass.

## Reopened Phase 5 follow-through (third fresh-audit fix)
- Work completed:
  - Increased the VS Code integration startup retry budget in `editors/vscode/tests/integration/run.js` from one retry to a four-attempt bounded retry loop with a short backoff, so the editor test runner can survive the audit-observed double-`SIGABRT` startup failure mode instead of failing after two aborted launches.
  - Reframed the remaining stale mechanics umbrella pass note in `docs/archive/second_wave/DOCTRINE_LANGUAGE_MECHANICS_FULL_IMPLEMENTATION_2026-04-11.md` so it no longer asserts that `cd editors/vscode && make` is currently green; it now points readers back to the dedicated readable-markdown plan for current editor-package truth.
- Tests run + results:
  - `npm test` in `editors/vscode` — passed.
  - `cd editors/vscode && make` — passed, including integration, alignment validation, and VSIX packaging.
  - `.venv/bin/python editors/vscode/scripts/validate_lark_alignment.py` — passed.
  - `.venv/bin/python editors/vscode/scripts/package_vsix.py` — passed.
  - `.venv/bin/python -m doctrine.verify_corpus` — passed.
  - `.venv/bin/python -m doctrine.diagnostic_smoke` — passed.
- Issues / deviations:
  - The larger retry budget is defensive hardening for the audit-reported transient abort pattern. The local reruns in this pass all completed without needing to surface a final retry failure.
  - Phase 5 remains reopened in the plan doc until the next fresh audit rewrites the authoritative audit block from current repo state.
- Next steps:
  - Stop again for the next implement-loop audit pass.

## Reopened Phase 5 follow-through (fourth fresh-audit fix)
- Work completed:
  - Moved the `@vscode/test-electron` cache root in `editors/vscode/tests/integration/run.js` off the repo-local `.vscode-test` tree and onto a short temp path under `os.tmpdir()`, then resolved the VS Code executable from that short cache before entering the startup retry loop.
  - Kept the short temp `--user-data-dir` and `--extensions-dir` launch args, so both the cached executable install and the per-run profile state now avoid long cloned-worktree paths during extension-host startup.
- Tests run + results:
  - `cd editors/vscode && make` — passed, including `npm test`, alignment validation, and VSIX packaging.
  - `npm run test:integration` in `editors/vscode` — passed again and reused the short temp cache install at `/var/folders/.../T/doctrine-vscode-test/...`.
  - `.venv/bin/python -m doctrine.verify_corpus` — passed.
  - `.venv/bin/python -m doctrine.diagnostic_smoke` — passed.
- Issues / deviations:
  - The first run against the new cache path had to download the pinned VS Code build into the short temp cache because the previous install lived under the repo-local `.vscode-test` directory. The immediate rerun then reused the short cache install cleanly.
  - Phase 5 remains reopened in the plan doc until the next fresh audit rewrites the authoritative audit block from current repo state.
- Next steps:
  - Stop again for the next implement-loop audit pass.

## Reopened Phase 5 follow-through (fifth fresh-audit fix)
- Work completed:
  - Changed `editors/vscode/tests/integration/run.js` to stage the extension under a short temp directory before launching VS Code, so the extension host no longer loads from the full cloned-worktree path during integration startup.
  - Stopped reusing the same VS Code test cache across separate `npm test` invocations by switching to a fresh short temp cache per run, while still reusing that cache within the current retry loop.
  - Passed the real repo root into the integration suite through `DOCTRINE_REPO_ROOT` and updated `editors/vscode/tests/integration/suite/index.js` to honor that env var, so the staged extension can still open and validate repo-owned example files.
  - Added the extra launch hardening flags `--disable-gpu` and `--use-mock-keychain` alongside the existing short temp profile dirs.
- Tests run + results:
  - `node ./tests/integration/run.js` in `editors/vscode` — passed with the extension loaded from `/var/folders/.../T/doctrine-vscode-extension-.../extension`.
  - `cd editors/vscode && make` — passed, including `npm test`, alignment validation, and VSIX packaging (`doctrine-language-0.0.1775935869985.vsix`).
  - `.venv/bin/python -m doctrine.verify_corpus` — passed.
  - `.venv/bin/python -m doctrine.diagnostic_smoke` — passed.
- Issues / deviations:
  - The fresh per-run cache means integration and `make` now download the pinned VS Code build into a short temp directory on each new invocation instead of reusing a shared repo-local or cross-run cache. That is an intentional stability tradeoff for the audit environment.
  - VS Code logs a warning that `use-mock-keychain` is not in its known option list before forwarding it to Electron/Chromium. The run still completed cleanly, and the keychain-related startup noise was otherwise gone in this pass.
  - Phase 5 remains reopened in the plan doc until the next fresh audit rewrites the authoritative audit block from current repo state.
- Next steps:
  - Stop again for the next implement-loop audit pass.

## Reopened Phase 5 follow-through (sixth fresh-audit fix)
- Work completed:
  - Reworked `editors/vscode/tests/integration/run.js` so the integration harness no longer requires a fresh network download on every invocation. It now accepts `DOCTRINE_VSCODE_EXECUTABLE_PATH`, accepts `DOCTRINE_VSCODE_TEST_CACHE`, and otherwise uses a stable short cache under `os.tmpdir()`.
  - Added local-cache seeding from `editors/vscode/.vscode-test` into the configured short cache before calling `downloadAndUnzipVSCode(...)`, so restricted audit environments can reuse the checked-in local install instead of failing on `update.code.visualstudio.com`.
  - Kept the staged temp extension path, the short temp profile dirs, and the retry loop from the previous passes.
- Tests run + results:
  - `DOCTRINE_VSCODE_TEST_CACHE=$(mktemp -d) npm run test:integration` in `editors/vscode` — passed and found an existing install in the brand-new cache directory after seeding from the local repo cache, without downloading.
  - `cd editors/vscode && make` — passed, including `npm test`, alignment validation, and VSIX packaging (`doctrine-language-0.0.1775936303232.vsix`).
  - `.venv/bin/python -m doctrine.verify_corpus` — passed.
  - `.venv/bin/python -m doctrine.diagnostic_smoke` — passed.
- Issues / deviations:
  - `--use-mock-keychain` still emits a benign “not in the list of known options” warning before VS Code forwards the flag to Electron/Chromium. The integration run still completed cleanly.
  - Phase 5 remains reopened in the plan doc until the next fresh audit rewrites the authoritative audit block from current repo state.
- Next steps:
  - Stop again for the next implement-loop audit pass.

## Reopened Phase 5 follow-through (seventh fresh-audit fix)
- Work completed:
  - Restored the pinned repo-root D2 runtime in this worktree with `npm ci`, which put `@terrastruct/d2@0.1.33` back under `node_modules/` so the flow-emission proof path can run again.
  - Tightened `editors/vscode/tests/integration/run.js` again so the integration harness no longer opens the full repo as the VS Code workspace during startup. It now launches against a short temp workspace and relies on the already-wired `DOCTRINE_REPO_ROOT` env var for repo-backed fixture access.
  - Verified the current fixes directly in the local shell before stopping, instead of relying on the next child audit to discover whether the surfaces were green.
- Tests run + results:
  - `npm ci` at repo root — passed.
  - `make verify-examples` — passed.
  - `make verify-diagnostics` — passed.
  - `cd editors/vscode && make` — passed, including `npm test`, alignment validation, and VSIX packaging (`doctrine-language-0.0.1775936796784.vsix`).
- Issues / deviations:
  - `--use-mock-keychain` still emits the same benign VS Code option warning before Electron/Chromium accepts the flag. The end-to-end editor run still completed cleanly.
  - Phase 5 remains reopened in the plan doc until the next fresh audit rewrites the authoritative audit block from current repo state.
- Next steps:
  - Stop again for the next implement-loop audit pass.

## Reopened Phase 5 follow-through (eighth fresh-audit fix)
- Work completed:
  - Changed `editors/vscode/tests/integration/run.js` so each startup retry now gets its own freshly staged extension tree and its own freshly seeded short temp VS Code cache, instead of reusing the same staged extension path and cached executable across all four retry attempts.
  - Kept the offline-safe local-cache seeding from `editors/vscode/.vscode-test`, so the fresh per-attempt caches still avoid network downloads in restricted audit environments.
  - Re-tested the current state directly in the local shell after this runner change instead of waiting for the next audit to validate it.
- Tests run + results:
  - `npm run test:integration` in `editors/vscode` — passed directly from the current runner state.
  - `make verify-examples` — passed.
  - `make verify-diagnostics` — passed.
  - `cd editors/vscode && make` — passed, including `npm test`, alignment validation, and VSIX packaging (`doctrine-language-0.0.1775937177001.vsix`).
- Issues / deviations:
  - `--use-mock-keychain` still emits the same benign VS Code option warning before Electron/Chromium accepts the flag. The direct integration run and the packaged editor run both still completed cleanly.
  - Phase 5 remains reopened in the plan doc until the next fresh audit rewrites the authoritative audit block from current repo state.
- Next steps:
  - Stop again for the next implement-loop audit pass.
