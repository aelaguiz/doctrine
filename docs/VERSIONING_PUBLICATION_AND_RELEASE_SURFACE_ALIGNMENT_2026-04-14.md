---
title: "Doctrine - Versioning, Publication, and Release Surface Alignment - Architecture Plan"
date: 2026-04-14
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: phased_refactor
related:
  - README.md
  - CONTRIBUTING.md
  - pyproject.toml
  - Makefile
  - CHANGELOG.md
  - docs/README.md
  - docs/VERSIONING.md
  - doctrine/release_flow.py
  - doctrine/_package_release.py
  - .github/workflows/publish.yml
  - .github/release.yml
---

# TL;DR

Outcome

Routine Doctrine releases should have one clear source of truth for version, package metadata, GitHub release data, PyPI publish data, maintainer commands, and public install docs. A maintainer should be able to cut a routine patch release without hunting for hidden steps or fixing drift by hand.

Problem

Doctrine already has a solid release spine, but truth still lives across `pyproject.toml`, `docs/VERSIONING.md`, `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md`, `Makefile`, `doctrine.release_flow`, `doctrine._package_release`, and `.github/workflows/publish.yml`. Some of that split is healthy. Some of it is duplicate wording, repeated inputs, or disconnected wiring that can drift.

Approach

Keep the release system lean. Find the canonical owners for release policy, release metadata, publish wiring, and maintainer commands. Move easy-to-connect surfaces onto those owners, delete stale duplicate truth, and add only small fail-loud checks that protect the shipped release path.

Plan

Ground the current owner paths and drift points, then implement in three steps: tighten executable owners first, converge signposts and deliberate reflections second, and run final proof plus cleanup last. Keep proof focused on existing release tests, package smoke checks, and a short maintainer-path review.

Non-negotiables

- No new document-testing framework, repo-policing gate, or release bureaucracy.
- No new parallel source of truth for release or publish metadata.
- Prefer fail-loud drift checks over manual memory or silent fallback.
- Keep the repo-root maintainer commands simple and intact unless there is a strong reason to change them.
- Keep routine public work on the patch line unless the shipped release policy says a larger move is required.

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-14
Verdict (code): COMPLETE
Manual QA: complete (non-blocking)

## Code blockers (why code is not done)
- None.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Final manual read completed during audit for `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `.github/PULL_REQUEST_TEMPLATE.md`, and `.github/release.yml`.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-14
external_research_grounding: skipped 2026-04-14 (repo evidence sufficient)
deep_dive_pass_2: done 2026-04-14
recommended_flow: deep dive -> external research grounding when needed -> deep dive again -> phase plan -> consistency-pass -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

After this change, a maintainer can prepare, tag, draft, and publish a routine Doctrine release by updating the approved release inputs once, running the repo-owned release commands, and relying on repo-owned checks to catch drift across package metadata, changelog payload, GitHub release flow, PyPI/TestPyPI publish wiring, and public install docs. This work must not add a generic docs-audit framework or a pile of document unit tests.

## 0.2 In scope

- Release-policy truth across `docs/VERSIONING.md`, `CHANGELOG.md`, and the maintainer guidance that points to them.
- Release and package metadata ownership across `pyproject.toml`, `doctrine.release_flow`, `doctrine._package_release`, `Makefile`, and `.github/workflows/publish.yml`.
- GitHub release and publish wiring that should move in lockstep with the canonical release inputs.
- Public install, maintainer, and contributor signpost docs in `README.md`, `CONTRIBUTING.md`, `docs/README.md`, and `.github/PULL_REQUEST_TEMPLATE.md` when those surfaces restate release, package-install, or release-label truth.
- Small, high-value fail-loud guards that protect the real release path and package publish path.
- Deletion or tightening of stale duplicated wording, constants, or steps when a stronger owner path already exists.

Allowed architectural convergence scope:

- Move duplicated release metadata or repeated release commands behind one repo-owned path when that keeps behavior the same and reduces drift.
- Update closely related tests, workflow outputs, and maintainer docs in the same change when they depend on the same release truth.
- Tighten ownership boundaries between policy docs, executable release helpers, and workflow YAML so each surface has a clear job.

## 0.3 Out of scope

- New release platforms, new packaging systems, or a new publish framework.
- Generic document linting, grep gates, repo-shape policing, or "unit testing docs."
- Changes to Doctrine language semantics, release classes, or the public package name unless repo evidence shows current shipped truth is wrong.
- Publishing the private flow-renderer package or the private VS Code extension, or forcing those private package versions onto the Doctrine public package line without clear repo evidence that they belong there.
- Rewriting healthy duplication that is only explanatory and already points back to a clear canonical owner.

## 0.4 Definition of done (acceptance evidence)

- The plan names one clear owner path for release policy, package release metadata, publish workflow inputs, and maintainer commands.
- Touched docs, templates, and scripts no longer disagree about the package install name, release steps, publish flow, or release-note label taxonomy.
- Routine release and package publish drift is caught by lean fail-loud checks in existing or closely related proof surfaces.
- Existing release behavior is preserved or intentionally tightened with explicit evidence from the repo-owned proof path.
- Credible proof includes the relevant subset of:
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `uv run --locked python -m unittest tests.test_package_release`
  - `make verify-package`
  - a short manual read of the touched release, maintainer, install, and release-label signpost surfaces against the shipped commands, workflow wiring, and generated-note taxonomy

## 0.5 Key invariants (fix immediately if violated)

- No fallbacks or runtime shims for mismatched release truth.
- No new parallel source of truth for release version, package metadata, or publish targets.
- No silent behavior drift in the existing release commands.
- No generic docs enforcement framework added as a side effect of this work.
- Public docs must describe the release path that the code and workflows actually implement.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make one small set of canonical owners for release truth.
2. Keep the maintainer release path easy to run from the repo root.
3. Catch real drift with fail-loud checks instead of human memory.
4. Reuse the existing release spine instead of inventing a new framework.
5. Update public docs only where they carry live release or install truth.

## 1.2 Constraints

- `docs/VERSIONING.md` is already the policy doc, while `CHANGELOG.md` is already the public release record.
- `doctrine.release_flow` and `doctrine._package_release` already own real release behavior and package metadata wiring.
- `.github/workflows/publish.yml` already consumes package metadata outputs and runs `make verify-package`.
- The repo wants plain, lean proof and explicitly rejects doc-policing theater.
- Routine public work should stay on patch bumps unless the shipped release policy says otherwise.

## 1.3 Architectural principles (rules we will enforce)

- One owner per release fact. Other surfaces may explain it, but they should not redefine it.
- Keep executable release truth in code or workflow wiring, not in repeated prose.
- Keep policy truth in the canonical policy doc, not split across several near-duplicate guides.
- Reuse the current `make` commands and release helpers unless there is a clear user-facing gain from changing them.
- Prefer deleting stale duplicate truth over keeping two live paths in sync by hand.

## 1.4 Known tradeoffs (explicit)

- Some explanatory repetition is fine when one source is clearly canonical and the repeated text points back to it.
- Not every disconnected surface should be auto-generated. Some should simply stop restating facts they do not own.
- Tighter fail-loud checks help maintainers, but only when they protect real release behavior and stay cheap to run.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine already ships a real public release flow. `docs/VERSIONING.md` defines policy, `CHANGELOG.md` carries public release entries, `doctrine.release_flow` drives prepare/tag/draft/publish commands, `doctrine._package_release` centralizes package release metadata and smoke proof, `Makefile` exposes the repo-root commands, and `.github/workflows/publish.yml` builds and publishes package artifacts.

## 2.2 What's broken / missing (concrete)

- Release truth still spans many human-edited surfaces, so maintainers can still fix one layer and miss another.
- Public install and maintainer docs repeat parts of the release story, which creates drift risk even when the release helpers are correct.
- It is not yet obvious which surfaces should own release facts and which should only point to those owners.
- Some release-adjacent surfaces may still be disconnected even though the repo already has enough structure to connect them cleanly.

## 2.3 Constraints implied by the problem

- The fix should converge existing surfaces, not replace them with a new release subsystem.
- The work has to preserve current public release commands and current package publish behavior unless there is a strong reason to tighten them.
- The proof story should stay lean and use real release/package checks, not doc-audit machinery.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal “ground truth”)

## 3.1 External anchors (papers, systems, prior art)

- No external release framework adopted for this plan — reject broader automation or docs-enforcement patterns for now — the repo already has a working release spine and the user explicitly wants lean convergence, not a new framework.

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `docs/VERSIONING.md` — canonical release policy, version-line rules, changelog entry shape, release process, and signed-tag/GitHub publish rules.
  - `CHANGELOG.md` — canonical public release record and upgrade payload; stable release sections already carry the exact header fields that the helper validates and reuses.
  - `pyproject.toml` — canonical package distribution name, package metadata version, and `[tool.doctrine.package]` publish environment inputs.
  - `doctrine/_package_release.py` — canonical projection from `pyproject.toml` into package-release metadata, GitHub workflow outputs, PyPI/TestPyPI project URLs, and the fresh-venv package smoke path.
  - `doctrine/_release_flow/parsing.py` — canonical parser and validator for current language version, expected package-version mapping from release tags, changelog entry truth, and placeholder rejection.
  - `doctrine/_release_flow/tags.py` — canonical release tag grammar, bump-class rules, clean-worktree and signed-tag gates, and pushed-tag verification.
  - `doctrine/_release_flow/ops.py` — canonical release worksheet, derived update/check list, tag message, draft notes body, and repo-owned `gh release` command construction.
  - `doctrine/release_flow.py` — public CLI entrypoint for `prepare`, `tag`, `draft`, and `publish`.
  - `Makefile` — thin repo-root command surface that delegates to the Python release helpers. This is a wrapper, not the business-logic owner.
  - `.github/workflows/publish.yml` — canonical post-release build/upload/publish workflow. It consumes `_package_release.py` outputs and runs `make verify-package`.
  - `.github/workflows/ci.yml` and `.github/workflows/pr.yml` — existing proof surfaces that already reuse `make verify-package`.
  - `.github/release.yml` — generated-notes category shaping for GitHub release notes. This is supplementary to the curated header/body coming from `CHANGELOG.md` and `doctrine/_release_flow/ops.py`.
  - `.github/PULL_REQUEST_TEMPLATE.md` — contributor-facing signpost for the release-note label taxonomy used by generated GitHub notes.
  - `README.md`, `CONTRIBUTING.md`, and `docs/README.md` — live signpost docs that point users and maintainers at install, verification, and release surfaces.
  - `tests/test_release_flow.py` and `tests/test_package_release.py` — existing preservation signals for release rules, notes/header shape, package metadata wiring, and workflow outputs.
- Canonical path / owner to reuse:
  - Release policy: `docs/VERSIONING.md`.
  - Public release record and upgrade guidance: `CHANGELOG.md`.
  - Release tag semantics and bump validation: `doctrine/_release_flow/tags.py` plus `doctrine/_release_flow/parsing.py`.
  - Repo-root release behavior: `doctrine/_release_flow/ops.py`, surfaced through `doctrine/release_flow.py` and `Makefile`.
  - Package release metadata and workflow export: `pyproject.toml`, read through `doctrine/_package_release.py`.
  - GitHub publish execution: `.github/workflows/publish.yml`.
- Existing patterns to reuse:
  - Thin wrapper pattern: `Makefile` exposes simple repo-root commands while Python modules own the logic.
  - Projection pattern: `doctrine/_package_release.py` turns one metadata source into both workflow outputs and smoke-test inputs.
  - Shared proof pattern: `make verify-package` is reused locally, in PR, in CI, and in the publish workflow.
  - Curated + generated release-note pattern: `doctrine/_release_flow/ops.py` passes curated notes from `CHANGELOG.md` and still lets GitHub add categorized notes via `--generate-notes` and `.github/release.yml`.
- Prompt surfaces / agent contract to reuse:
  - Not applicable. This plan is not agent-backed.
- Native model or agent capabilities to lean on:
  - Not applicable. This plan is repo-code and docs alignment work.
- Existing grounding / tool / file exposure:
  - Repo-local code, tests, docs, workflows, and `gh`/git-based release helpers already expose the full release path. No new discovery surface is needed to plan this work.
- Duplicate or drifting paths relevant to this change:
  - `README.md` carries live package-install truth that must stay aligned with `pyproject.toml`, `CHANGELOG.md`, and `doctrine/_package_release.py`.
  - `CONTRIBUTING.md` repeats some verification and release-adjacent guidance that can drift from `Makefile` and `docs/VERSIONING.md`.
  - `docs/README.md` is mostly a healthy signpost, but it still participates in release truth when it describes which docs are canonical.
  - `.github/release.yml` influences generated GitHub notes, while `CHANGELOG.md` and `doctrine/_release_flow/ops.py` define the curated release header/body. That split needs an explicit ownership boundary.
  - `.github/PULL_REQUEST_TEMPLATE.md` lists the release-note labels contributors are expected to use, so it can drift from `.github/release.yml` even when the generated-note system still works.
  - `tests/test_release_flow.py` hard-codes required update surfaces in the worksheet. That is good protection, but it becomes a drift point if owner boundaries change and the worksheet is not updated in sync.
- Capability-first opportunities before new tooling:
  - Reuse `doctrine/_package_release.py` as the one metadata projection path instead of adding a second metadata manifest for workflows or docs.
  - Reuse `doctrine._release_flow` validation and worksheet output instead of adding doc-lint or changelog-policing scripts.
  - Where docs only repeat owned facts, prefer shortening them into signposts back to the canonical owner instead of generating or testing more prose.
  - Reuse `make verify-package`, `tests.test_release_flow`, and `tests.test_package_release` before adding any new proof surface.
- Behavior-preservation signals already available:
  - `uv run --locked python -m unittest tests.test_release_flow` — guards tag parsing, version-move rules, changelog truth, note construction, and release worksheet output.
  - `uv run --locked python -m unittest tests.test_package_release` — guards package metadata loading and GitHub output projection.
  - `make verify-package` — guards build, fresh-venv install, and smoke compile outside the repo root.
  - `.github/workflows/ci.yml` and `.github/workflows/pr.yml` packaging lanes — exercise the same package smoke path in automation.

## 3.3 Decision gaps that must be resolved before implementation

- None that require user input after repo grounding.
- The remaining work is implementation planning, not architecture choice.
- The owner-boundary decisions are now settled:
  - `README.md` keeps package install and source-bootstrap facts only.
  - `CONTRIBUTING.md` keeps contributor proof guidance only.
  - `docs/README.md` stays a pure docs index.
  - `.github/release.yml` stays a supplementary generated-notes surface.
  - `.github/PULL_REQUEST_TEMPLATE.md` stays a contributor signpost for the release-note label taxonomy and must stay aligned with `.github/release.yml`.
  - `HEADER_FIELD_ORDER` and the worksheet text stay as executable contracts inside the release engine and tests, while `docs/VERSIONING.md` stays the human policy owner.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

The current release path is already split by job, not by accident:

- `docs/VERSIONING.md` owns release policy, release classes, release process, and the changelog header shape.
- `CHANGELOG.md` owns the public release record and the curated release-note body.
- `pyproject.toml` owns the published package name, the package version, and the publish environment names under `[tool.doctrine.package]`.
- `doctrine/_package_release.py` reads `pyproject.toml`, exports GitHub workflow outputs, builds project URLs, and runs the fresh-venv package smoke path.
- `doctrine/_release_flow/models.py` defines the release data contracts such as `ReleaseTag`, `LanguageVersion`, `ReleasePlan`, and `HEADER_FIELD_ORDER`.
- `doctrine/_release_flow/parsing.py` reads `docs/VERSIONING.md`, `CHANGELOG.md`, and `pyproject.toml` and validates the release entry truth.
- `doctrine/_release_flow/tags.py` owns tag parsing, version-move rules, signed-tag checks, and pushed-tag checks.
- `doctrine/_release_flow/ops.py` composes the release worksheet, required update list, verify command list, tag message, draft notes body, and `gh release` calls.
- `doctrine/release_flow.py` is the CLI entrypoint. `Makefile` is the thin repo-root wrapper.
- `.github/workflows/publish.yml` is the post-release build and publish workflow. `.github/workflows/ci.yml` and `.github/workflows/pr.yml` reuse the same package smoke path.
- `.github/release.yml` shapes GitHub generated-note categories but does not own the curated release header or body.
- `.github/PULL_REQUEST_TEMPLATE.md` tells contributors which release-note labels to use. It is a human signpost for the generated-note taxonomy, not a release-policy owner.
- `README.md`, `CONTRIBUTING.md`, and `docs/README.md` still carry some live release or install truth as human-facing signposts.
- `tests/test_release_flow.py` and `tests/test_package_release.py` protect the release engine and metadata projection behavior.

## 4.2 Control paths (runtime)

There are four main control paths today:

1. Prepare path:
   `make release-prepare` calls `python -m doctrine.release_flow prepare`.
   That path reads git tags, `docs/VERSIONING.md`, `CHANGELOG.md`, and `pyproject.toml`, then prints one worksheet with derived status, exact headers, verify commands, and next commands.
2. Tag and draft path:
   `make release-tag` and `make release-draft` call the same Python release engine.
   Tagging fails on a dirty worktree, missing signing key, invalid release move, bad changelog entry, or mismatched package version.
   Draft creation fails if the pushed signed tag is missing or if the curated release entry is invalid.
3. Publish path:
   `make release-publish` publishes the GitHub draft release.
   The GitHub `release.published` event then triggers `.github/workflows/publish.yml`, which reads package metadata through `_package_release.py`, runs `make verify-package`, uploads dist artifacts, and publishes to PyPI through environment-gated Trusted Publishing.
   Manual `workflow_dispatch` can publish to TestPyPI or PyPI from an explicit ref.
4. Human docs path:
   `README.md` tells users how to install `doctrine-agents` and how to bootstrap a source checkout.
   `CONTRIBUTING.md` tells contributors which proof commands to run.
   `docs/README.md` points readers at the canonical docs.
   `.github/PULL_REQUEST_TEMPLATE.md` tells contributors which release-note labels to use.
   These surfaces do not drive code, but they can drift from the executable release path and release-note taxonomy.

## 4.3 Object model + key abstractions

The release engine already has a clear split:

- `ReleaseTag` and `LanguageVersion` model the two version lines.
- `ReleasePlan` models the derived release worksheet state.
- `ReleaseEntry` models one validated changelog section.
- `HEADER_FIELD_ORDER` is the canonical release-entry header order shared by parsing and release-note building.
- `PackageReleaseMetadata` models the package distribution name, import name, version, environment names, and project URLs for workflow consumers.
- `run_checked()` and `release_error()` in `doctrine/_release_flow/common.py` provide one fail-loud error path with stable Doctrine error codes.

This split is already good. The main weakness is not missing structure. The weakness is that human-facing docs still repeat enough facts that maintainers can drift outside these code-owned paths.

## 4.4 Observability + failure behavior today

The current system is already fail-loud at the executable boundary:

- Release helpers raise stable errors such as `E522` through `E530` for bad tags, invalid version moves, missing language version lines, bad changelog entries, tag verification failures, signing misconfig, GitHub command failures, and package-version mismatch.
- `prepare_release()` reports drift in plain English through the worksheet, including package metadata status and changelog entry status.
- `make verify-package` proves that built artifacts install outside the repo root and can compile a small temp project.
- CI, PR, and publish workflows already reuse that package smoke path.

The current blind spots are narrower:

- The signpost docs are not executable owners, so drift there is still mostly a human review problem.
- `.github/release.yml` can drift in category wording or label mapping without breaking the curated release header/body path.
- `.github/PULL_REQUEST_TEMPLATE.md` can drift from `.github/release.yml` label categories even when generated notes still work.
- `render_release_worksheet()` owns a concrete maintainer checklist, and tests assert key strings, but the list is still easy to forget if the owner boundaries change and the helper plus tests are not updated together.

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. This plan is about release, package, workflow, and docs alignment, not a product UI.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

Keep the current release spine. Do not add a new release manifest, a docs-testing framework, or another policy file.

The future file roles should be:

- `docs/VERSIONING.md`: policy-only owner for version rules, release classes, changelog header shape, and the maintainer release process.
- `CHANGELOG.md`: public release record and curated release-note source.
- `pyproject.toml`: single editable source for package name, package version, import name, and publish environment names.
- `doctrine/_package_release.py`: single executable projection from `pyproject.toml` into workflow outputs, project URLs, and package smoke behavior.
- `doctrine/_release_flow/*.py`: single executable owner for release validation, worksheet rendering, tag rules, and `gh release` behavior.
- `Makefile` and `doctrine/release_flow.py`: thin adapters only.
- `.github/workflows/publish.yml`: workflow adapter that consumes metadata outputs instead of restating project-specific values.
- `.github/workflows/ci.yml` and `.github/workflows/pr.yml`: proof adapters that keep reusing `make verify-package`.
- `.github/release.yml`: supplementary generated-notes categorizer only.
- `.github/PULL_REQUEST_TEMPLATE.md`: contributor-facing label signpost that mirrors the generated-note taxonomy but does not define release policy.
- `README.md`, `CONTRIBUTING.md`, and `docs/README.md`: signposts with only the minimum live facts they truly need.

## 5.2 Control paths (future)

The future control path should be simple:

1. Maintainer edits only the approved release inputs:
   - `pyproject.toml` for package version and package metadata
   - `CHANGELOG.md` for the public release record
   - `docs/VERSIONING.md` only when release policy or language-version guidance changed
2. Maintainer runs the repo-owned command surface:
   - `make release-prepare`
   - required proof including `make verify-package`
   - `make release-tag`
   - `make release-draft`
   - `make release-publish`
3. The GitHub publish workflow reads project-specific package facts only from `_package_release.py` outputs.
4. Human-facing docs stay out of the executable decision path. They point back to the owners above instead of restating process logic.

## 5.3 Object model + abstractions (future)

Keep the current abstractions and sharpen their boundaries:

- `HEADER_FIELD_ORDER` stays the release-entry header contract.
- The changelog header shape remains a deliberate two-layer contract:
  - `docs/VERSIONING.md` owns the human policy and documented shape.
  - `HEADER_FIELD_ORDER` plus the parsing validators own the executable enforcement of that shape.
- `PackageReleaseMetadata` stays the workflow metadata contract.
- `render_release_worksheet()` stays the owner of the maintainer worksheet text.
- `tests/test_release_flow.py` should keep asserting the worksheet and release-note behavior as shipped output, not as imported shared constants.
- `.github/release.yml` remains the owner of generated-note categories, while `.github/PULL_REQUEST_TEMPLATE.md` stays a signpost that must list the same label taxonomy for contributors.
- If implementation finds real executable duplication, factor it inside the existing `doctrine/_release_flow` or `_package_release.py` modules only. Do not add a new cross-repo config layer to solve wording drift in docs.

This resolves the open design choices from research:

- `README.md` should keep package install and source-bootstrap facts because users need them there, but deeper release policy should stay in `docs/VERSIONING.md`.
- `CONTRIBUTING.md` should keep contributor proof commands, but release process details should point to `docs/VERSIONING.md` instead of becoming a second owner.
- `docs/README.md` should remain a pure index and should not grow release-process prose.
- `.github/release.yml` should remain supplementary. It may group generated notes, but it must not become the owner of release-note headers, release classes, or release policy.
- `.github/PULL_REQUEST_TEMPLATE.md` should keep the contributor-facing label checklist, but its label list should be treated as a maintained reflection of `.github/release.yml`, not as a separate taxonomy owner.
- The worksheet list in `doctrine/_release_flow/ops.py` plus targeted assertions in `tests/test_release_flow.py` should stay the contract for now. A new shared constant would add framework without solving a second production-path problem.
- The documented changelog header shape in `docs/VERSIONING.md` and the executable `HEADER_FIELD_ORDER` in code should stay deliberately duplicated because they serve different audiences. The implementation should keep them aligned directly, not introduce a new abstraction just to avoid two short ordered lists.

## 5.4 Invariants and boundaries

- One owner per release fact.
- No README, contributing guide, or docs index may become a second policy source.
- No workflow may hardcode project-specific package facts that already come from `_package_release.py`.
- No new release manifest, docs linter, grep gate, or document unit-test system.
- No fallback or shim path for mismatched release truth.
- The repo-root `make release-*` commands stay stable unless there is a clear user-facing reason to change them.
- Package smoke proof stays shared across local runs, PR, CI, and publish.

## 5.5 UI surfaces (ASCII mockups, if UI work)

Not applicable. No product UI is part of this plan.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Release policy | `docs/VERSIONING.md` | version lines, release process, changelog shape | Canonical policy guide | Tighten policy-only role and remove any prose that tries to own executable behavior already enforced in code | Keep one policy owner | Policy stays in `docs/VERSIONING.md`; executable truth stays in code | `tests/test_release_flow.py` if policy-driven worksheet text changes |
| Public release record | `CHANGELOG.md` | release entry template and real release sections | Canonical public release record and curated release-note body | Keep exact header/body ownership and align any touched wording with the target owner boundaries | Keep release notes curated and executable validation honest | `CHANGELOG.md` remains the release record | `tests/test_release_flow.py` |
| Package metadata | `pyproject.toml` | `[project]`, `[tool.doctrine.package]` | Single editable package and publish metadata source | Keep this as the only project-specific package metadata input; add fields only if another executable consumer truly needs them | Avoid parallel metadata | `_package_release.py` remains the projection path | `tests/test_package_release.py`, `make verify-package` |
| Package projection | `doctrine/_package_release.py` | `load_package_release_metadata`, `write_github_outputs`, `smoke_test_distribution` | Projects package metadata into workflow outputs and smoke proof | Keep as the only metadata projection path; extend only if another executable consumer needs one more field | Prevent workflow drift and duplicate readers | `PackageReleaseMetadata` remains the metadata contract | `tests/test_package_release.py`, `make verify-package` |
| Release parsing | `doctrine/_release_flow/parsing.py` | `load_current_language_version`, `expected_package_metadata_version`, `describe_changelog_status`, `require_validated_release_entry` | Reads and validates policy, changelog, and package metadata | Reuse existing mapping and validation instead of re-implementing release truth elsewhere | Keep tag-to-package and changelog rules single-sourced | `parsing.py` remains the validation owner | `tests/test_release_flow.py` |
| Tag rules | `doctrine/_release_flow/tags.py` | `parse_release_tag`, `validate_release_move`, `require_*_tag` | Owns tag grammar and git truth checks | Do not duplicate release-move or tag-verification logic elsewhere | Keep release move rules single-sourced | `tags.py` remains the tag owner | `tests/test_release_flow.py` |
| Release orchestration | `doctrine/_release_flow/ops.py` | `prepare_release`, `render_release_worksheet`, `tag_release`, `draft_release`, `publish_release` | Owns maintainer worksheet, release-note rendering, and `gh` command behavior | Keep worksheet output as the one maintainer checklist owner; update it if owner boundaries change; do not create a second checklist in docs | Stop drift between code and prose | `ops.py` remains the maintainer-path owner | `tests/test_release_flow.py` |
| CLI adapter | `doctrine/release_flow.py` | CLI subcommands | Thin entrypoint over release ops | Keep thin; do not move business logic here | Preserve one logic owner | CLI stays an adapter | `tests.test_release_flow` indirectly |
| Repo-root commands | `Makefile` | `release-prepare`, `release-tag`, `release-draft`, `release-publish`, `verify-package` | Thin repo-root wrappers | Keep wrappers simple and in sync with the Python release engine | Preserve easy maintainer commands | `Makefile` stays adapter-only | Manual command read; `tests/test_release_flow.py` if worksheet commands change |
| GitHub publish workflow | `.github/workflows/publish.yml` | `metadata`, `build`, `publish-testpypi`, `publish-pypi` jobs | Consumes metadata outputs and publishes package artifacts | Keep workflow project-specific values sourced from `_package_release.py`; remove or avoid any hardcoded duplicates that overlap with metadata outputs | Keep publish flow in sync with package metadata | Workflow consumes metadata outputs only for project-specific facts | `tests/test_package_release.py`, `make verify-package` |
| Packaging proof reuse | `.github/workflows/ci.yml`, `.github/workflows/pr.yml` | packaging jobs | Reuse `make verify-package` in automation | Keep this shared proof path; do not add custom package smoke logic elsewhere | One package proof path | `make verify-package` remains shared | Workflow review plus `make verify-package` |
| GitHub generated notes | `.github/release.yml` | `changelog.categories` | Groups generated GitHub notes by label | Keep as supplementary only; align labels/categories only where that improves release notes, not policy | Prevent a second release-note owner | Generated-note categories stay supplemental | Manual review of draft release body |
| Release-note label signpost | `.github/PULL_REQUEST_TEMPLATE.md` | `Release note label` checklist | Contributor-facing label taxonomy | Keep the listed labels aligned with `.github/release.yml` categories and shipped label names | Prevent contributor drift around generated-note labels | PR template stays a signpost, not a taxonomy owner | Manual review of template and draft notes flow |
| Public install docs | `README.md` | Quickstart and install section | Carries install name and source-bootstrap facts | Keep only the minimum live install facts users need here; link deeper release policy to `docs/VERSIONING.md` or contributor proof to `CONTRIBUTING.md` | Reduce doc drift without hurting usability | README becomes install and quickstart signpost | Manual doc review |
| Contributor docs | `CONTRIBUTING.md` | setup and proof commands | Carries contributor proof guidance | Keep contributor-proof role; point release process details back to `docs/VERSIONING.md` if needed | Avoid a second maintainer process owner | CONTRIBUTING stays contributor-proof signpost | Manual doc review |
| Docs index | `docs/README.md` | docs index entries | Points to canonical docs | Keep pure index/signpost role; do not repeat release-process prose | Keep doc navigation separate from release policy | docs index stays signpost-only | Manual doc review |
| Release worksheet tests | `tests/test_release_flow.py` | worksheet and notes assertions | Guards release behavior and some maintainer-surface text | Update targeted assertions when owner boundaries or worksheet text change; keep output-level assertions instead of new shared constants | Protect shipped release UX without framework creep | Test output stays behavior contract | `uv run --locked python -m unittest tests.test_release_flow` |
| Package metadata tests | `tests/test_package_release.py` | metadata and GitHub output assertions | Guards metadata projection contract | Update if exported metadata surface changes | Protect publish metadata contract | Test output stays metadata contract | `uv run --locked python -m unittest tests.test_package_release` |

## 6.2 Migration notes

- Canonical owner path / shared code path:
  - Release policy: `docs/VERSIONING.md`
  - Public release record: `CHANGELOG.md`
  - Executable release flow: `doctrine/_release_flow/*.py`
  - Package and publish metadata: `pyproject.toml` -> `doctrine/_package_release.py`
  - Publish execution: `.github/workflows/publish.yml`
- Deprecated APIs (if any):
  - None planned. The target keeps the current `make release-*` and `python -m doctrine.release_flow` surfaces.
- Delete list (what must be removed; include superseded shims/parallel paths if any):
  - Stale release-process or package-publish prose in `README.md`, `CONTRIBUTING.md`, or `docs/README.md` that duplicates stronger owners.
  - Any hardcoded project-specific package metadata in executable consumers if the same fact already comes from `_package_release.py`.
  - No new compatibility shim or second release manifest is allowed.
- Capability-replacing harnesses to delete or justify:
  - None. This plan explicitly rejects adding docs-audit scripts, grep gates, or document unit tests.
- Live docs/comments/instructions to update or delete:
  - `README.md`
  - `CONTRIBUTING.md`
  - `docs/README.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md` when release template wording needs owner-boundary cleanup
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `AGENTS.md` only if implementation changes the maintainer proof commands or release-flow instructions
- Behavior-preservation signals for refactors:
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `uv run --locked python -m unittest tests.test_package_release`
  - `make verify-package`
  - Short manual read of touched signpost docs against the final command surface

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Package metadata | `pyproject.toml` -> `doctrine/_package_release.py` -> `.github/workflows/publish.yml` | one metadata projection path | Prevents workflow drift on package name, version, env names, and project URLs | include |
| Maintainer command surface | `Makefile` + `doctrine/release_flow.py` + `doctrine/_release_flow/ops.py` | thin wrappers over one release engine | Prevents shell-level command drift | include |
| Package proof | `make verify-package`, `.github/workflows/ci.yml`, `.github/workflows/pr.yml`, `.github/workflows/publish.yml` | one package smoke path reused everywhere | Prevents package proof drift across local and CI surfaces | include |
| Signpost docs | `README.md`, `CONTRIBUTING.md`, `docs/README.md` | signpost-only release guidance outside canonical owners | Prevents human-facing docs from becoming shadow policy | include |
| Generated GitHub notes | `.github/release.yml` | supplementary category surface only | Prevents GitHub labels from becoming release-policy truth | include |
| Contributor release-note labels | `.github/PULL_REQUEST_TEMPLATE.md` + `.github/release.yml` | one generated-note label taxonomy with one human signpost | Prevents contributor-facing label drift from generated-note categories | include |
| Worksheet contract | `doctrine/_release_flow/ops.py` + `tests/test_release_flow.py` | output-level contract instead of new shared constant layer | Prevents framework creep while keeping maintainer UX tested | include |
| Changelog header shape | `docs/VERSIONING.md` + `doctrine/_release_flow/models.py` + `doctrine/_release_flow/parsing.py` | policy doc plus executable enforcement | Prevents header-shape drift without a new config layer | include |
| Private npm packages | `package.json`, `editors/vscode/package.json` | keep separate private version lines | Prevents scope creep into unrelated private package versioning | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; every phase has exit criteria + explicit verification plan (tests optional). Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — Tighten executable release owners

Status: COMPLETE

Completed work:
- Made `doctrine/_package_release.py` fail loud when `[tool.doctrine.package]` or its release fields are missing, so package publish metadata stays explicitly owned by `pyproject.toml`.
- Added `tests.test_package_release` to the release worksheet proof path and tightened the breaking-release worksheet wording around contributor instructions.
- Updated `tests/test_package_release.py` and `tests/test_release_flow.py` to preserve the new executable-owner contract.

* Goal:
  Make the executable release path use one clear owner per fact before touching the wider signpost layer.
* Work:
  - Tighten `doctrine/_package_release.py` and `.github/workflows/publish.yml` so project-specific package and publish facts come from one metadata projection path.
  - Tighten `doctrine/_release_flow/parsing.py`, `doctrine/_release_flow/ops.py`, `doctrine/_release_flow/models.py`, `doctrine/_release_flow/tags.py`, `doctrine/release_flow.py`, and `Makefile` only where owner boundaries or duplicated executable truth are still muddy.
  - Keep `HEADER_FIELD_ORDER`, worksheet rendering, changelog validation, tag validation, and repo-root commands stable unless a concrete drift fix requires a small change.
  - Update `tests/test_release_flow.py` and `tests/test_package_release.py` in the same phase for any changed executable contract.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `uv run --locked python -m unittest tests.test_package_release`
  - `make verify-package`
* Docs/comments (propagation; only if needed):
  - Update `docs/VERSIONING.md` only where executable owner boundaries or changelog-header policy wording must be clarified to match the shipped code.
  - Add a short code comment only if one boundary becomes non-obvious after the refactor.
* Exit criteria:
  - The executable release path has one clear owner for release validation, package metadata projection, and publish workflow inputs.
  - No executable consumer still hardcodes a project-specific fact that should come from `_package_release.py` or the release engine.
  - The release and package tests plus package smoke proof pass.
* Rollback:
  - Revert the executable owner-boundary patch as one unit if release behavior, metadata export, or package smoke proof regresses.

## Phase 2 — Converge signposts and deliberate reflections

Status: COMPLETE

Completed work:
- Tightened `README.md`, `CONTRIBUTING.md`, and `docs/README.md` so they point back to `docs/VERSIONING.md`, `CHANGELOG.md`, and contributor proof owners instead of restating release policy.
- Updated `docs/VERSIONING.md` to name the explicit package publish fields in `pyproject.toml` and to match the tighter release proof path.
- Updated `.github/PULL_REQUEST_TEMPLATE.md` so the release-note label surface mirrors `.github/release.yml` more closely and includes `make verify-package` in the contributor proof checklist.
- Recorded the release-surface alignment in `CHANGELOG.md`.

* Goal:
  Bring human-facing release surfaces into line with the executable owners without turning them into second policy sources.
* Work:
  - Trim `README.md`, `CONTRIBUTING.md`, and `docs/README.md` back to their signpost roles while keeping the minimum install, contributor-proof, and docs-index facts users need.
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` only where policy wording or the release template must better describe the already chosen owner boundaries.
  - Align `.github/PULL_REQUEST_TEMPLATE.md` with `.github/release.yml` so contributor-facing release-note labels reflect the generated-note taxonomy.
  - Delete stale duplicate prose or checklist language in touched docs and templates instead of preserving shadow instructions.
* Verification (required proof):
  - Short manual read of `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/VERSIONING.md`, `CHANGELOG.md`, `.github/PULL_REQUEST_TEMPLATE.md`, and `.github/release.yml` against `Makefile`, `doctrine/_release_flow/ops.py`, `doctrine/_release_flow/parsing.py`, and `.github/workflows/publish.yml`
  - `uv run --locked python -m unittest tests.test_release_flow`
* Docs/comments (propagation; only if needed):
  - Rewrite the touched signpost docs and template to present truth directly.
  - Do not add legacy explanation comments or extra helper docs.
* Exit criteria:
  - Touched docs and templates point to the correct owner surfaces and no longer restate stale release or label-taxonomy truth.
  - The release-note label list in `.github/PULL_REQUEST_TEMPLATE.md` matches `.github/release.yml`.
* Rollback:
  - Revert the signpost-convergence patch if the edited docs or template become less clear or contradict the executable release path.

## Phase 3 — Final proof and cleanup

Status: COMPLETE

Completed work:
- Ran the full proof set for the changed release surfaces.
- Manually checked the touched release, maintainer, install, and release-label signpost surfaces against `Makefile`, `doctrine/_release_flow/ops.py`, `doctrine/_release_flow/parsing.py`, `.github/workflows/publish.yml`, and `.github/release.yml`.
- Confirmed that the touched surfaces now agree on the package publish owner path, release proof path, and contributor label guidance.

Manual QA (non-blocking):
- README, CONTRIBUTING, docs index, versioning guide, changelog, PR template, and GitHub release-note config were read together after the final proof run.

* Goal:
  Prove the aligned release path end to end and remove any leftover stale truth from the touched surfaces.
* Work:
  - Run the full proof set for the changed surfaces.
  - Fix any final drift found by the proof run or the final manual read.
  - Remove any touched stale wording, checklist fragments, or release-label mismatches that survived earlier phases.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_release_flow`
  - `uv run --locked python -m unittest tests.test_package_release`
  - `make verify-package`
  - Short final manual read of the touched release, maintainer, install, and release-label signpost surfaces against the shipped commands, workflow wiring, and generated-note taxonomy
* Docs/comments (propagation; only if needed):
  - Sync any touched release instructions that the proof run showed were still stale.
  - No new comments are expected.
* Exit criteria:
  - The repo has one clear release spine, touched signpost surfaces agree with it, and the proof set passes.
  - No touched live surface still carries stale duplicate release or label-taxonomy truth.
* Rollback:
  - Revert the final cleanup patch or the smallest failing phase if the proof run exposes a regression that cannot be fixed inside the same change.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

This plan should avoid verification bureaucracy, prefer existing credible signals that genuinely prove the claim, and stay away from doc-audit scripts, stale-term greps, absence checks, or other negative-value gates.

## 8.1 Unit tests (contracts)

- Reuse `tests.test_release_flow` for release policy, tag, draft, and publish contract checks.
- Reuse `tests.test_package_release` for package metadata ownership and GitHub workflow output contract checks.
- Add targeted tests only when a real owner-path change or new fail-loud guard would otherwise be unprotected.

## 8.2 Integration tests (flows)

- Use `make verify-package` as the main package-build and fresh-install smoke path.
- Use the repo's existing release worksheet and helper flow as the integration truth instead of adding a second harness.

## 8.3 E2E / device tests (realistic)

- No device testing is expected.
- A short final manual check should compare the touched release, maintainer, install, and release-label signpost surfaces against the shipped repo-root commands, publish wiring, and generated-note taxonomy.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

This is maintainer-facing internal convergence work. Rollout should be a normal repo change that lands with updated release docs, release helpers, workflow wiring, and proof in the same change.

## 9.2 Telemetry changes

No new telemetry is expected. The main operational signals are the release helper outputs, CI/package smoke results, and GitHub publish workflow behavior.

## 9.3 Operational runbook

Keep the maintainer runbook small: update the approved release inputs, run `make release-prepare`, run the required proof including `make verify-package`, then run `make release-tag`, `make release-draft`, and `make release-publish`. Review the draft release body before publish. This plan should tighten that runbook only where real drift still exists.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: self-integrator
- Scope checked:
  - TL;DR, Sections 0 through 10, the planning ledger, and helper-block drift
  - owner boundaries across policy docs, executable release helpers, workflow adapters, and signpost docs
  - execution order, proof burden, and rollout/runbook alignment
- Findings summary:
  - The plan was structurally strong, but the planning ledger still omitted the required `consistency-pass` stage and left external research looking accidentally unfinished instead of intentionally skipped.
  - The acceptance-evidence and final-manual-read language undercounted touched release docs even though `docs/VERSIONING.md` and `CHANGELOG.md` are in scope.
  - The operational runbook still spoke about earlier planning stages and did not state the exact proof-bearing maintainer path clearly enough.
- Integrated repairs:
  - Marked external research as intentionally skipped in `planning_passes` and updated the recommended planning flow to include `consistency-pass`.
  - Broadened the manual-read evidence language in Section 0, Section 7, and Section 8 to cover touched release docs as well as signpost surfaces.
  - Tightened the operational runbook to the exact approved command order and required proof story.
- Remaining inconsistencies:
  - none
- Unresolved decisions:
  - none
- Unauthorized scope cuts:
  - none
- Decision-complete:
  - yes
- Decision: proceed to implement? yes
<!-- arch_skill:block:consistency_pass:end -->

# 10) Decision Log (append-only)

## 2026-04-14 - Keep release alignment lean

Context

The user asked for versioning, publication, GitHub, PyPI, docs, and scripts to stay aligned and move in sync where that is easy, but explicitly rejected turning this into a monstrous framework or document-testing scheme.

Options

- Add broad docs-audit or repo-policing automation to force every release surface to match.
- Converge onto the existing release spine, delete duplicate truth where it hurts, and add only narrow fail-loud guards around the real release path.
- Leave the current split mostly alone and rely on maintainer care.

Decision

Choose the lean convergence path. Use the current release spine as the base, tighten ownership, and reject framework creep.

Consequences

The plan will prefer single-source release facts, small executable checks, and direct doc cleanup. It will not treat every repeated sentence as a reason to add new tooling.

Follow-ups

- Use `research` to name the canonical owners and true drift points.
- Use `deep-dive` to map the touched files, delete list, and proof surfaces before implementation.

## 2026-04-14 - Keep the release spine and shrink signpost drift

Context

The first deep-dive pass showed that Doctrine already has a healthy release engine. The main drift risk is the human signpost layer around it, plus the boundary between curated release notes and GitHub generated notes.

Options

- Add a new release manifest or docs-testing layer so every surface is derived.
- Keep the current owners, shrink signpost docs back to their smallest useful role, and keep the worksheet plus tests as the maintainer contract.
- Spread more release-process detail into `README.md`, `CONTRIBUTING.md`, and `docs/README.md`.

Decision

Keep the current release spine. Treat `README.md`, `CONTRIBUTING.md`, and `docs/README.md` as signposts. Keep `.github/release.yml` as a supplementary generated-notes surface. Keep the worksheet behavior local to `doctrine/_release_flow/ops.py` and `tests/test_release_flow.py` instead of adding a new abstraction.

Consequences

Implementation should focus on tightening boundaries and deleting stale duplicate prose, not on inventing a new framework. If a second real executable consumer appears later, the code can factor a shared helper then.

Follow-ups

- Use the second deep-dive pass to harden the owner boundaries and final delete/update list.
- Use `phase-plan` to turn these boundaries into a small implementation sequence.

## 2026-04-14 - Keep deliberate small duplicates where audiences differ

Context

The second deep-dive pass found two short duplicated contracts that are easy to mistake for drift: the changelog header shape exists in both `docs/VERSIONING.md` and executable code, and the generated-note label taxonomy appears in both `.github/release.yml` and the PR template.

Options

- Remove the duplicates by adding a new shared config or generation layer.
- Keep the duplicates, but make one owner explicit and keep the other as a small reflection for a different audience.
- Let both sides evolve independently and rely on review.

Decision

Keep the duplicates, but make their roles explicit. `docs/VERSIONING.md` remains the human policy owner and `HEADER_FIELD_ORDER` plus parsing remain the executable enforcement. `.github/release.yml` remains the generated-note taxonomy owner and `.github/PULL_REQUEST_TEMPLATE.md` remains the contributor signpost.

Consequences

The implementation can tighten these pairs directly without introducing a new abstraction layer. The plan stays lean while still naming the surfaces that must move together.

Follow-ups

- Reflect these owner/reflection pairs clearly in the implementation checklist.
- Update both sides together if this work changes either contract.

## 2026-04-14 - Ship in three phases and skip external research

Context

After two deep-dive passes, the repo-local evidence was enough to choose owner boundaries and the implementation order. No external best-practice question remained that would change the architecture.

Options

- Pause for external research before writing the implementation plan.
- Move straight into a small three-phase plan: executable owners first, signposts second, final proof and cleanup last.
- Split the work into many small mixed code-and-doc phases.

Decision

Skip external research for this plan and use a three-phase sequence. Tighten the executable release path first, then align human signposts and deliberate reflections, then run final proof and cleanup.

Consequences

The plan stays bounded and execution-focused. The controller can move straight to `consistency-pass` after this phase plan instead of spending another turn on outside references that are unlikely to change the chosen design.

Follow-ups

- Keep the authoritative checklist limited to ship-blocking work.
- Use `consistency-pass` to cold-read the full artifact before implementation starts.
