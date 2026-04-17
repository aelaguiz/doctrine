---
title: "Doctrine - Agent Linter Skill Package - Mini Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: new_system
related:
  - docs/GARRY_FAT_THIN.md
  - docs/LLM_AGENT_LINTER_FOR_AUTHORING_2026-04-16.md
  - docs/AGENT_LINTER_PROMPT_2026-04-16.md
  - docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json
  - docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json
  - docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json
  - docs/AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md
  - docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json
  - docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v2.json
  - docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json
  - skills/agent-linter/prompts/SKILL.prompt
  - skills/agent-linter/prompts/references/product-boundary.md
  - skills/agent-linter/prompts/references/finding-catalog.md
  - skills/agent-linter/prompts/references/report-contract.md
  - skills/agent-linter/prompts/references/examples.md
  - skills/agent-linter/prompts/references/install.md
  - skills/agent-linter/prompts/schemas/agent_linter_output_schema.json
  - tests/fixtures/skill_agent_linter/batch_review_packet.json
  - tests/fixtures/skill_agent_linter/batch_report.json
  - pyproject.toml
---

# TL;DR

- Outcome: ship a Doctrine-authored `agent-linter` skill package that feels
  genuinely high value when someone says "audit this agent", "audit this flow",
  or "audit our repo's agent surfaces".
- Core product intent: the skill should work naively or specifically. It should
  pick the full honest scope on its own, but still honor explicit asks such
  as "compare authored vs emitted", "audit this one file", or "give me JSON".
- Quality bar: the skill must be massively human-helpful. The default result is
  a layered markdown report that says what is wrong, why it matters, what to
  fix first, what good looks like, and what to do next.
- Architecture rule: fold the old linter prompt, schema, fixtures, proof docs,
  and large linter plan into one self-contained skill package. Keep the harness
  thin. Do not rebuild the audit brain as heuristics or scripts.
- Install rule: target the current skills ecosystem shape for public install
  (`npx skills add <repo> --skill agent-linter`) once that path is proven, and
  keep the Doctrine emitted-bundle install path as the first honest proof path
  until then.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
mini_replan_intent_capture: done 2026-04-16
recommended_flow: miniarch-step implement
note: This mini plan replaces the stripped-down scriptless replan and captures the full skill-first product intent.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can ship one bundled `agent-linter` skill that:

- works when invoked naively or with a very specific ask
- audits a single prompt, a runtime home, a skill package, a flow, or a repo's
  instruction-bearing surfaces without requiring a giant option menu
- reads authored prompt text and emitted Markdown when that comparison matters
- returns one human-first report with verdict, scope, top fixes, scorecard,
  findings, evidence, rewrite help, and next moves
- returns structured JSON that matches the existing schema only when the user
  explicitly asks for machine-readable output
- installs cleanly through Doctrine's emitted bundle path now and through the
  current `npx skills add ... --skill ...` ecosystem once that public path is
  proven

The claim is false if the skill becomes a thin wrapper around heuristics, if it
needs a parameter matrix to be useful, if it stops being deeply helpful to a
human reader, or if the package relies on the old docs as runtime truth instead
of carrying that doctrine inside the skill.

## 0.2 In scope

- Keep `skills/agent-linter/` as the one package owner path.
- Author the shipped surface as a real Doctrine skill package.
- Use `skill-authoring` quality bars for trigger quality, scope discipline,
  progressive disclosure, and self-containment.
- Fold the learnings from these artifacts into the package itself instead of
  relying on cross-reference at runtime:
  - `docs/AGENT_LINTER_PROMPT_2026-04-16.md`
  - `docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json`
  - `docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json`
  - `docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json`
  - `docs/AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md`
  - `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json`
  - `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v2.json`
  - `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json`
  - `docs/LLM_AGENT_LINTER_FOR_AUTHORING_2026-04-16.md`
  - `docs/GARRY_FAT_THIN.md`
- Support three core user asks well:
  - "Audit this `AGENTS.prompt` / `SOUL.prompt` / `SKILL.prompt`."
  - "Audit this flow or skill package and tell me what is weak, duplicated, or
    confusing."
  - "Audit our repo's agent surfaces and tell me what to fix first."
- Keep the skill valuable in both naive and specific modes:
  - naive: plain ask, full honest scope, human report
  - specific: explicit path, authored-vs-emitted comparison, or JSON output
- Keep the existing structured schema as the machine contract.
- Keep Codex as the first proven install host.
- Shape the package so it can be installed through the current public skills
  ecosystem once the repo-published installer path is real.

## 0.3 Out of scope

- compiler-owned parse, type, schema, route, or emit errors
- a heuristic or script-owned audit engine
- a giant flag surface for every audit behavior
- repo-local overlay rules as core Doctrine law
- VS Code integration in this cut
- auto-fix by default
- claiming a public installer path before it is proven

## 0.4 Definition of done

- The package teaches a powerful audit workflow inside `SKILL.prompt` and
  bundled references.
- The old prompt, schema, proof, and large-plan learnings are folded into the
  package-owned doctrine, not left as required runtime dependencies.
- The skill clearly handles naive and specific invocation without a giant
  parameter menu.
- The default output is a layered, human-helpful markdown report.
- The structured JSON path still matches the existing schema.
- The package has one Doctrine emit target.
- The install story is honest:
  - local Doctrine emitted-bundle install is proven
  - the `npx skills add ... --skill agent-linter` path is either proven and
    documented or explicitly deferred without pretending
- Live docs teach the skill as the canonical path.

## 0.5 Key invariants

- The skill is the auditor.
- Judgment stays in the skill, not in scripts.
- The `description` is resolver logic, not marketing copy.
- The skill must stay self-contained at runtime.
- Human helpfulness is the main output bar.
- Exact evidence is mandatory for findings.
- Batch duplication and contradiction matter.
- Naive use must work well.
- Specific use must stay possible.
- No public claim is made without proof.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding

## 3.1 Internal anchors inspected

- `docs/GARRY_FAT_THIN.md`
- `docs/AGENT_LINTER_PROMPT_2026-04-16.md`
- `docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json`
- `docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json`
- `docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json`
- `docs/AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md`
- `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16.json`
- `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v2.json`
- `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16_v3.json`
- `docs/LLM_AGENT_LINTER_FOR_AUTHORING_2026-04-16.md`
- `skills/agent-linter/prompts/SKILL.prompt`
- `skills/agent-linter/prompts/references/**`
- `skills/agent-linter/prompts/schemas/agent_linter_output_schema.json`
- `tests/fixtures/skill_agent_linter/batch_review_packet.json`
- `tests/fixtures/skill_agent_linter/batch_report.json`
- `pyproject.toml`

## 3.2 External and runtime grounding

- The current public skills ecosystem still uses install commands shaped like
  `npx skills add <repo> --skill <name>`. That matches the local
  `skill-authoring` install contract and should shape the public installer goal
  for this skill.
- `skill-authoring` says to start from concrete user asks, keep the runtime
  package self-contained, keep `SKILL.md` lean, move heavy doctrine into
  `references/`, and add scripts only when determinism is truly earned.

## 3.3 What the older linter artifacts already prove

- `AGENT_LINTER_PROMPT_2026-04-16.md` already contains a strong audit method,
  a clear compiler-vs-linter boundary, a stable `AL###` catalog, and a strong
  evidence-first standard.
- `AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json` already defines the structured
  result shape well enough to keep as the machine contract.
- `AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md` plus the v2 and v3 outputs prove
  that the prompt-and-schema path worked under `codex exec`.
- `LLM_AGENT_LINTER_FOR_AUTHORING_2026-04-16.md` contains broader ambition that
  still matters here: single-target and batch value, repo and flow audit value,
  human-first reporting, and the need to keep Doctrine law generic.

## 3.4 Grounded conclusions

- The real missing work is not inventing more detector code. It is packaging
  the existing linter intelligence into one excellent skill.
- The package currently undercaptures the original ambition. It needs a richer
  skill contract, richer references, and a clearer install and proof story.
- Garry's framing and `skill-authoring` agree on the key design rule: put the
  reasoning in the skill, keep the harness thin, and avoid scripts unless they
  are clearly earned.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture

## 4.1 What exists now

- A bundled package already exists under `skills/agent-linter/`.
- The package already has:
  - `SKILL.prompt`
  - `references/`
  - `schemas/agent_linter_output_schema.json`
  - `agents/openai.yaml`
- Package-local scripts were removed.
- Proof fixtures already exist under `tests/fixtures/skill_agent_linter/`.

## 4.2 What is weak today

- The current package wording is too thin compared with the value bar in the
  older linter prompt and large linter plan.
- The package does not yet clearly encode the three core user asks and the one
  strong anti-case.
- The package does not yet fully carry the old doctrine inside its own
  references, so the richer thinking still mostly lives in dated docs.
- `pyproject.toml` does not yet define the promised emit target.
- The live docs path is not yet cut over.
- The public installer story is not yet explicit enough.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture

## 5.1 Package shape

Ship one first-party Doctrine skill package with this ownership split:

- `SKILL.prompt`
  owns:
  - trigger language
  - core workflow
  - naive vs specific invocation behavior
  - scope-picking doctrine
  - output expectations
  - the strong anti-case boundary
- `references/`
  own:
  - deeper audit method
  - Doctrine-specific law and boundaries
  - report contract
  - finding catalog and examples
  - installer and proof guidance
  - scope and mode guidance for agent, flow, skill, and repo audits
- `schemas/agent_linter_output_schema.json`
  owns the structured JSON contract
- `agents/openai.yaml`
  owns display and invocation metadata when it helps routing

## 5.2 Skill behavior

The skill should feel like a method call for thoughtful audit work.

It should:

- default to the full honest scope the ask deserves
- widen to batch only when the ask or evidence says duplication or
  contradiction matters
- inspect authored prompt text directly
- inspect emitted Markdown when that comparison materially improves the audit
- explain exactly what it checked
- lead with what to fix first
- show why each finding matters
- give rewrites or concrete better patterns when that helps
- end with clear next moves

## 5.3 Canonical user asks and anti-case

Canonical asks:

- "Audit this `AGENTS.prompt`."
- "Audit this flow and tell me where the agent design is weak or duplicated."
- "Audit our repo's agent surfaces and tell me what to fix first."

Strong anti-case:

- generic code review or compiler-error review that is not really about agent
  authoring doctrine

## 5.4 Output shape

Default:

- layered markdown report
- verdict and scope first
- top fixes first
- scorecard
- grouped findings
- exact evidence
- rewrite help or concrete improvement patterns where useful
- packet or evidence gaps
- next moves

Explicit opt-in:

- structured JSON matching the existing schema

## 5.5 Install shape

Two install surfaces matter:

- Doctrine proof path:
  - emit the skill from this repo
  - install it locally in Codex from the emitted bundle
- public installer target:
  - shape the package so it can be installed with the current
    `npx skills add <repo> --skill agent-linter` ecosystem once that path is
    published and proven

The plan must not blur those two. First proof can be local. Public installer
claims require public proof.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit

## 6.1 Inputs to absorb into the skill package

- `docs/AGENT_LINTER_PROMPT_2026-04-16.md`
  - mission
  - compiler boundary
  - operating principles
  - `AL###` catalog
  - report expectations
- `docs/AGENT_LINTER_OUTPUT_SCHEMA_2026-04-16.json`
  - machine contract
- `docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16.json`
  - historical fixture
- `docs/AGENT_LINTER_PROOF_FIXTURE_2026-04-16_v2.json`
  - current stronger fixture
- `docs/AGENT_LINTER_CODEX_CLI_PROOF_2026-04-16.md`
  - proof path and validation method
- `docs/AGENT_LINTER_CODEX_CLI_OUTPUT_2026-04-16*.json`
  - real proof outputs
- `docs/LLM_AGENT_LINTER_FOR_AUTHORING_2026-04-16.md`
  - broader product intent, especially batch value, repo and flow audit value,
    and human report shape
- `docs/GARRY_FAT_THIN.md`
  - fat-skill, thin-harness doctrine

## 6.2 Package files to rewrite

- `skills/agent-linter/prompts/SKILL.prompt`
- `skills/agent-linter/prompts/references/product-boundary.md`
- `skills/agent-linter/prompts/references/finding-catalog.md`
- `skills/agent-linter/prompts/references/report-contract.md`
- `skills/agent-linter/prompts/references/examples.md`
- `skills/agent-linter/prompts/references/install.md`
- `skills/agent-linter/prompts/agents/openai.yaml`

## 6.3 Repo surfaces to wire

- `pyproject.toml`
  - add the named emit target
- `tests/test_emit_skill.py`
  - add proof for the package target and emitted bundle layout
- `docs/AGENT_LINTER.md`
  - add the live guide
- `docs/README.md`
  - point to the live guide
- `docs/SKILL_PACKAGE_AUTHORING.md`
  - teach this package as a first-party example
- `docs/EMIT_GUIDE.md`
  - teach the emit target and install path
- `docs/VERSIONING.md` and `CHANGELOG.md`
  - update only if the public bundled skill surface is now truly taught as
    shipped
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Phase Plan

## Phase 1 — Author the real skill package

Goal:
Turn the current thin package into the badass skill the user actually wanted.

Work:

- rewrite `SKILL.prompt` around the three canonical asks and one anti-case
- make the `description` strong enough to route naive asks correctly
- teach naive and specific usage without a giant option menu
- fold the old linter prompt, schema, proof, and large-plan learnings into
  package-owned references
- keep the package self-contained and script-free in this first cut
- keep the human-first report shape and the JSON schema shape aligned
- update `agents/openai.yaml` so the runtime metadata matches the stronger
  package contract

Verification:

- read-through validation against the three canonical asks and the anti-case
- check that the package can stand on its own without the old docs
- check that the schema and report-contract language still agree

Done bar:

- the package feels clearly stronger, broader, and more useful than the current
  stripped-down version
- the key intelligence from the old docs lives inside the skill package
- the package still does not depend on detector scripts

## Phase 2 — Wire emit, install, proof, and docs

Goal:
Make the stronger skill real, installable, and honestly taught.

Work:

- add the `emit_skill` target in `pyproject.toml`
- add targeted emit proof in `tests/test_emit_skill.py`
- prove the Doctrine emitted-bundle install path in Codex
- capture the public installer target for the current `npx skills add ...`
  ecosystem, and either:
  - prove it and document the exact command, or
  - defer it explicitly and keep public docs honest
- add `docs/AGENT_LINTER.md`
- update `docs/README.md`, `docs/SKILL_PACKAGE_AUTHORING.md`, and
  `docs/EMIT_GUIDE.md`
- keep the old `docs/AGENT_LINTER_*` artifacts as history or support, not live
  owner paths

Verification:

- targeted `emit_skill` proof
- representative install proof
- reuse the existing Codex CLI proof shape against package-owned surfaces
- `make verify-package`
- `make verify-examples` if the changed docs or emit path require it

Done bar:

- the package emits cleanly
- the install story is honest and useful
- the live docs and proof path point at the bundled skill as the canonical
  surface
<!-- arch_skill:block:phase_plan:end -->

# Ready Verdict

Ready for `miniarch-step implement docs/DOCTRINE_AGENT_LINTER_SKILL_PACKAGE_2026-04-16.md`.

Why:

- the real product intent is captured again
- the package shape is clear
- the fold-in sources are explicit
- the next implementation work is tight enough for miniarch execution
