---
title: "Doctrine - Language Audit - Conventions, Inference Traps, And Proof Gaps"
date: 2026-04-16
status: active
doc_type: audit
owners: [aelaguiz]
reviewers: []
related:
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/_parser
  - doctrine/_model
  - doctrine/_compiler
  - doctrine/emit_docs.py
  - doctrine/verify_corpus.py
  - docs/LANGUAGE_REFERENCE.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/WORKFLOW_LAW.md
  - docs/REVIEW_SPEC.md
  - docs/EMIT_GUIDE.md
  - docs/COMPILER_ERRORS.md
  - docs/FAIL_LOUD_GAPS.md
  - examples/README.md
  - ../rally
  - ../psflows
---

# TL;DR

## Outcome

Doctrine already covers most of the big language ideas that Rally and PSFlows
users want. The biggest problems are not missing headline features. The real
problems are uneven conventions, fail-loud gaps, and proof or docs that teach
a tighter story than the shipped code actually enforces.

## Main call

The highest-risk unevenness is this:

1. Some surfaces feel compiler-owned, but still compile through open or lossy
   paths.
2. Some first-class singleton surfaces silently replace earlier values instead
   of failing loud.
3. Some docs promise stronger typed or fail-loud behavior than the shipped
   proof shows.
4. One real cross-repo feature gap stands out: Doctrine still does not ship a
   first-class typed previous-turn-output input surface.

## What I audited

- Shipped grammar, parser, model, compiler, emitter, diagnostics, and corpus
- Live docs and the numbered examples
- `../rally` and `../psflows` as expectation-setting comparison repos
- Direct local repros for high-risk behaviors
- Four parallel `xhigh` audit passes with disjoint scopes

## Checks run

Parallel audit passes ran targeted proof, not the full repo verify path:

- Unit tests:
  `tests.test_output_schema_lowering`,
  `tests.test_output_schema_validation`,
  `tests.test_emit_docs`,
  `tests.test_final_output`,
  `tests.test_route_output_semantics`
- Focused manifests:
  `examples/39_guarded_output_sections/cases.toml`,
  `examples/92_route_from_basic/cases.toml`,
  `examples/104_review_final_output_output_schema_blocked_control_ready/cases.toml`,
  `examples/106_review_split_final_output_output_schema_partial/cases.toml`,
  `examples/119_route_only_final_output_contract/cases.toml`
- Local repros through `uv run --locked python` for:
  open-slot `workflow` behavior,
  typo acceptance,
  literal guard acceptance,
  parser singleton overwrite behavior,
  emitted artifact overwrite behavior,
  output-schema nullability wording,
  mixed review-verdict vocab,
  and diagnostics quality

I did not run `uv sync`, `npm ci`, or `make verify-examples` because this task
was a read-only audit plus one new dated doc.

# 1) Ranked Findings

## 1.1 High - `workflow:` and `handoff_routing:` behave like typed fields, but they still ride the open authored-slot path

- User inference:
  `workflow:` and `handoff_routing:` read like compiler-owned agent fields.
  The live language docs talk about them that way.
- Shipped behavior:
  The grammar does not define a dedicated `workflow_field`.
  `workflow:` is parsed through the generic `agent_slot_field` path in
  `doctrine/grammars/doctrine.lark` and `doctrine/_parser/workflows.py`.
  The compiler later special-cases slot keys named `workflow` and
  `handoff_routing` in `doctrine/_compiler/compile/agent.py`.
- Direct repro:
  `worklfow:` compiled and rendered as a normal authored section.
  A two-field agent with `workflow` before `role` failed with
  `expected role followed by workflow`, but the same order compiled once a
  third field was present.
- Why this matters:
  This is the sharpest inference trap in the language.
  One typo can drop compiler semantics while still producing plausible output.
  One order rule applies only to one narrow shape, which teaches a fake rule.
- Evidence:
  `doctrine/grammars/doctrine.lark`,
  `doctrine/_parser/workflows.py`,
  `doctrine/_model/agent.py`,
  `doctrine/_compiler/compile/agent.py`,
  `doctrine/_compiler/validate/__init__.py`,
  `docs/LANGUAGE_REFERENCE.md`,
  `docs/FAIL_LOUD_GAPS.md`
- Fix direction:
  Pick one story and make it true.
  Either make `workflow` and `handoff_routing` real typed fields at parse
  time, or stop documenting them like typed fields.
  Do not keep the current split story.

## 1.2 High - First-class singleton control surfaces silently overwrite earlier values

- User inference:
  `route_only` and `grounding` look like explicit first-class declarations.
  Users should expect them to fail loud on duplicate singleton parts the same
  way many nearby surfaces already do.
- Shipped behavior:
  `route_only_body()` and `grounding_body()` in
  `doctrine/_parser/reviews.py` keep the last `facts:`, `when:`,
  `handoff_output:`, `guarded:`, `routes:`, `source:`, `target:`, or
  `policy:` block instead of failing.
- Why this matters:
  These are control-plane declarations.
  Silent replacement here changes route truth and grounding policy.
  That is much worse than a cosmetic render drift.
- Evidence:
  `doctrine/grammars/doctrine.lark`,
  `doctrine/_parser/reviews.py`,
  `examples/71_grounding_declaration/prompts/AGENTS.prompt`,
  `examples/119_route_only_final_output_contract/prompts/AGENTS.prompt`,
  `docs/FAIL_LOUD_GAPS.md`
- Fix direction:
  Add duplicate-singleton parse failures here and add focused negative proof.

## 1.3 High - Runtime-package cargo can overwrite compiler-owned emitted artifacts

- User inference:
  Generated files like `final_output.contract.json` and emitted schemas under
  `schemas/` are compiler-owned and reserved.
  Package cargo should not be able to shadow them.
- Shipped behavior:
  `emit_target()` writes generated contract and schema files, then copies
  bundled runtime-package files later.
  The package layout only reserves `AGENTS.md` and `SOUL.md`.
  A bundled `final_output.contract.json` or `schemas/*.json` can overwrite the
  compiler output.
- Why this matters:
  This breaks the trust boundary between authored package cargo and
  compiler-owned metadata.
  Downstream harnesses can read a file that looks official but was not
  generated by Doctrine.
- Evidence:
  `doctrine/emit_docs.py`,
  `doctrine/_compiler/package_layout.py`
- Fix direction:
  Reserve compiler-owned artifact paths and fail loud on collisions before
  write time.

## 1.4 Medium-High - Review semantics are documented as stronger than the shipped compiler and proof currently make true

- User inference:
  Review semantic bindings and trusted carriers are compiler-owned truth.
  If they point at the wrong field, Doctrine should fail loud.
- Shipped behavior:
  The live docs say this area is compiler-owned and fail-loud.
  The shipped gap doc says several parts still only validate liveness,
  existence, or trust-surface membership, not payload meaning.
- Why this matters:
  Review, `current artifact`, and `invalidate` are control truth.
  If Doctrine treats the wrong field as trusted semantic data, the runtime
  contract looks stronger than it is.
- Evidence:
  `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/REVIEW_SPEC.md`,
  `docs/FAIL_LOUD_GAPS.md`,
  `examples/104_review_final_output_output_schema_blocked_control_ready/cases.toml`,
  `examples/105_review_split_final_output_output_schema_control_ready/cases.toml`,
  `examples/106_review_split_final_output_output_schema_partial/cases.toml`
- Missing proof:
  There is no manifest-backed `compile_fail` case for a review semantic bound
  to the wrong field, or for `current artifact` and `invalidate` routed
  through an unrelated trusted field.
- Fix direction:
  Add proof first, then tighten the checker or narrow the docs story.

## 1.5 Medium - Guard conditions are looser than the docs teach

- User inference:
  Guards are typed conditions over known refs and known helpers.
- Shipped behavior:
  Literal conditions such as `when "sometimes":` compile.
  Unknown helpers and wrong helper arity also compile today according to the
  shipped gap doc and direct repros.
- Why this matters:
  Guards look like logic, but the compiler quietly stops reasoning about some
  forms.
  That makes the emitted prompt look more trustworthy than the validator.
- Evidence:
  `docs/WORKFLOW_LAW.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/FAIL_LOUD_GAPS.md`,
  `examples/39_guarded_output_sections/cases.toml`
- Missing proof:
  No focused `compile_fail` examples for literal guards, unknown helpers, or
  wrong helper arity.
- Fix direction:
  Decide the legal helper surface and enforce it in one place.

## 1.6 Medium - `route_from` and `mode` are taught as typed selectors more strongly than the shipped proof supports

- User inference:
  `mode` and `route_from` are typed enum-backed selectors.
  If the selector is not enum-safe, Doctrine should reject it.
- Shipped behavior:
  The route docs teach a typed story, but the gap doc says dynamic selectors
  are still shallow-checked and some non-enum `mode` expressions can slip
  through.
- Why this matters:
  Users will build control logic on top of this surface.
  Shallow checking on a control selector is an inference trap, not a minor DX
  issue.
- Evidence:
  `docs/WORKFLOW_LAW.md`,
  `docs/FAIL_LOUD_GAPS.md`,
  `examples/92_route_from_basic/cases.toml`
- Missing proof:
  No focused `compile_fail` proof for non-enum selector paths, bad explicit
  arms on dynamic selectors, or non-enum `mode` bindings.
- Fix direction:
  Tighten the checker or narrow the public claim.
  Do not leave the current mismatch in place.

## 1.7 Medium - `output schema` nullability cleanup direction is now clear; finish the cut cleanly

- Current direction:
  `nullable` is the authored nullability flag on this surface.
  Legacy `required` and `optional` are now targeted hard errors with upgrade
  guidance.
  The wire contract stays the same for the current structured-output profile:
  object properties are still present on the wire, and `nullable` only means
  the value may be `null`.
- Why this still matters:
  The language question is no longer open, but the cleanup is not fully done
  until docs, examples, and emitted-surface wording stop teaching the old
  terms.
- Evidence:
  `doctrine/_compiler/resolve/output_schemas.py`,
  `tests/test_output_schema_surface.py`,
  `tests/test_output_schema_lowering.py`,
  `tests/test_final_output.py`
- Fix direction:
  Finish the migration and keep the story consistent:
  `nullable` for nullability, no authored `required` on `output schema`,
  and no return to `optional` as a synonym on this surface.

## 1.8 Medium - The emitted contract uses two review-verdict vocabularies in one file

- User inference:
  One concept called `review verdict` should have one stable enum vocabulary in
  one emitted contract.
- Shipped behavior:
  `review.outcomes.*.verdict` uses machine-style values like `accept` and
  `changes_requested`.
  Route-facing review verdict fields use prose-style values like `accepted`
  and `changes requested`.
- Why this matters:
  Downstream code will naturally compare these values.
  Mixed vocab in one contract invites subtle bugs.
- Evidence:
  `doctrine/_compiler/constants.py`,
  `doctrine/_compiler/compile/review_contract.py`,
  `doctrine/_compiler/compile/agent.py`,
  `doctrine/emit_docs.py`,
  `docs/EMIT_GUIDE.md`
- Fix direction:
  Normalize on one vocabulary or clearly rename the route-facing field to
  signal that it is not the same enum.

## 1.9 Medium - Diagnostics quality is uneven on key authored surfaces

- User inference:
  First-class authored surfaces like `final_output`, route semantics, and
  output-schema errors should fail with stable codes and exact authored
  locations.
- Shipped behavior:
  Some of these failures still fall back to generic `CompileError` and lose
  exact line and column data.
  A direct repro showed unguarded `route.next_owner` falling back to generic
  `E299` with no line or column.
- Why this matters:
  Doctrine’s value is not just correctness.
  It is also reviewable, exact author feedback.
  Losing source location on these newer surfaces weakens the language story.
- Evidence:
  `doctrine/_compiler/validate/route_semantics_reads.py`,
  `doctrine/_compiler/resolve/output_schemas.py`,
  `doctrine/_compiler/compile/final_output.py`,
  `doctrine/_compiler/diagnostics.py`,
  `tests/test_compile_diagnostics.py`
- Fix direction:
  Route these failures through the structured diagnostics helpers and add
  focused exact-location tests.

## 1.10 Medium - Some typed parser surfaces accept lossy or narrower input than users would expect

- User inference:
  Typed numeric and example surfaces should reject wrong-shape input, not
  quietly coerce it or narrow it.
- Shipped behavior:
  `decision candidates minimum` accepts any `SIGNED_NUMBER` and then truncates
  with `int(count)`.
  `output schema example:` only allows an object at the root even though nested
  examples may contain arrays and scalars.
- Why this matters:
  These are not style issues.
  They are shape claims on typed surfaces.
- Evidence:
  `doctrine/_parser/analysis_decisions.py`,
  `doctrine/grammars/doctrine.lark`,
  `tests/test_parse_diagnostics.py`,
  `tests/test_output_schema_surface.py`,
  `examples/74_decision_attachment/prompts/AGENTS.prompt`
- Fix direction:
  Reject non-integer candidate minimum values.
  Decide whether root examples are object-only by design; if yes, document that
  bluntly. If no, widen the grammar.

## 1.11 Medium-Low - Readable-block singleton handling is uneven

- User inference:
  Repeated singleton fields on sibling readable blocks should behave the same
  way.
- Shipped behavior:
  `callout` and `code` keep the last `kind:`, `language:`, or `text:` value,
  while sibling blocks like raw text and image already fail loud on repeated
  singletons.
- Why this matters:
  This teaches authors that the readable surface is regular when it is not.
- Evidence:
  `doctrine/_parser/readables.py`,
  `examples/58_readable_document_blocks/prompts/AGENTS.prompt`,
  `examples/61_multiline_code_and_readable_failures/prompts/AGENTS.prompt`
- Fix direction:
  Align singleton rules across readable block kinds.

## 1.12 Medium-Low - The docs and example ladders hide the real proof story on newer surfaces

- User inference:
  The examples index and canonical docs should point readers to the examples
  that actually prove the shipped feature.
- Shipped behavior:
  Several indices stop too early or group important proof under the wrong band.
  The root repo instructions also still say the shipped corpus stops at
  `116_first_class_named_tables`, while the live examples index teaches through
  `119_route_only_final_output_contract`.
- Why this matters:
  This makes later features feel less shipped than they really are.
  It also makes audits and reviews harder because the proof path is hard to
  follow.
- Evidence:
  `AGENTS.md`,
  `examples/README.md`,
  `docs/REVIEW_SPEC.md`,
  `docs/AGENT_IO_DESIGN_NOTES.md`,
  `docs/COMPILER_ERRORS.md`,
  `examples/106_review_split_final_output_output_schema_partial/cases.toml`
- Specific drifts:
  `E299` is described in `docs/COMPILER_ERRORS.md` as not used by a manifest
  fail case, but example `106` now pins a negative case to `E299`.
  The example ladders hide `104` through `106` and `119` from the most obvious
  guide paths.

## 1.13 Low - Late examples drift from Doctrine’s own human-facing style rules

- User inference:
  The examples are the teaching surface, so later examples should still read
  like polished public examples.
- Shipped behavior:
  Some later examples use placeholder text like `#### Test` and `blah blah
  blah`, and there is a render-style shift on `trust_surface` formatting
  between nearby checked-in outputs.
- Why this matters:
  This is low severity, but it weakens the “examples teach the language” story.
- Evidence:
  `examples/107_output_inheritance_basic/cases.toml`,
  `examples/109_imported_review_handoff_output_inheritance/cases.toml`,
  `examples/104_review_final_output_output_schema_blocked_control_ready/build_ref/acceptance_review_blocked_json_demo/AGENTS.md`,
  `examples/106_review_split_final_output_output_schema_partial/build_ref/acceptance_review_split_partial_demo/AGENTS.md`,
  `examples/README.md`

# 2) Comparison Pressure From Rally And PSFlows

## 2.1 Real missing surface - previous-turn output reuse

- Rally and PSFlows treat the previous turn result as first-order run truth.
- Doctrine now documents the compile and emit side of previous-turn reuse in
  its live I/O and emit docs.
- The remaining gap is front-door discoverability and sibling runtime
  follow-through, not the shipped Doctrine compile and emit contract itself.
- This is the one comparison-driven issue that looks like a real missing
  language or runtime affordance, not just a docs problem.

Evidence:

- `../rally/docs/RALLY_PORTING_GUIDE.md`
- `../rally/docs/RALLY_MASTER_DESIGN.md`
- `../psflows/flows/lessons/prompts/shared/contracts.prompt`
- `docs/LANGUAGE_REFERENCE.md`
- `docs/AGENT_IO_DESIGN_NOTES.md`
- `docs/EMIT_GUIDE.md`

## 2.2 Discoverability gap - provider roots and stdlib imports

- Rally and PSFlows teach provider-root imports as a front-door pattern.
- Doctrine supports additional prompt roots, but the integration story is
  buried too deep in the emit docs.
- For framework users, this feels like a first-step concept, not an edge case.

Evidence:

- `../rally/README.md`
- `../rally/flows/software_engineering_demo/prompts/AGENTS.prompt`
- `../psflows/flows/lessons/prompts/agents/project_lead/AGENTS.prompt`
- `docs/EMIT_GUIDE.md`
- `docs/README.md`

## 2.3 Discoverability gap - rooted runtime path conventions

- Rally and PSFlows are explicit about rooted path tokens like `home:`,
  `flow:`, `workspace:`, and `host:`.
- Doctrine correctly keeps harness behavior outside the language, but the live
  docs do not say plainly that these rooted tokens are harness-owned opaque
  strings, not Doctrine semantics.

Evidence:

- `../rally/AGENTS.md`
- `../psflows/flows/lessons/flow.yaml`
- `README.md`
- `PRINCIPLES.md`
- `docs/LANGUAGE_REFERENCE.md`
- `docs/AGENT_IO_DESIGN_NOTES.md`

## 2.4 Discoverability gap - control-ready review patterns are present but fragmented

- Rally and PSFlows explain the “readable comment plus final JSON control
  surface” pattern in one place.
- Doctrine ships all needed parts, but the teaching path is split across
  `AUTHORING_PATTERNS`, `REVIEW_SPEC`, and several examples.

Evidence:

- `../rally/docs/RALLY_MASTER_DESIGN.md`
- `../psflows/flows/lessons/prompts/shared/contracts.prompt`
- `docs/AUTHORING_PATTERNS.md`
- `docs/REVIEW_SPEC.md`
- `examples/104_review_final_output_output_schema_blocked_control_ready`
- `examples/105_review_split_final_output_output_schema_control_ready`
- `examples/119_route_only_final_output_contract`

## 2.5 Discoverability gap - skill packages lack one obvious “real skill” teaching template

- Doctrine’s narrow-example rule is good, but a porter from Rally or PSFlows
  will look for one realistic skill template with stronger operating sections.
- Today they mostly get minimal examples plus the authoring guide.

Evidence:

- `docs/SKILL_PACKAGE_AUTHORING.md`
- `examples/95_skill_package_minimal/prompts/SKILL.prompt`
- `examples/100_skill_package_bundled_agents/prompts/SKILL.prompt`
- `../rally/skills/repo-search/SKILL.md`
- `../psflows/skills/psmobile-lesson-poker-kb-interface/build/SKILL.md`

# 3) Pattern Summary

The audit points to four repeated failure modes:

1. Semantically special surfaces still parse or compile through generic paths.
2. Singleton bodies do not fail loud in a uniform way.
3. Docs and examples teach a stricter story than the proof surface currently
   protects.
4. Discoverability on real integration patterns lags behind shipped capability.

This matters because Doctrine sells small, typed, reviewable authoring. The
language does not need more magic. It needs a more uniform contract.

# 4) Recommended Follow-Up Order

## Phase 1 - Close the real semantic bugs

1. Make `workflow` and `handoff_routing` consistent with their public status.
2. Fail loud on duplicate singleton entries in `route_only` and `grounding`.
3. Reserve compiler-owned emitted artifact paths and reject package collisions.
4. Reject lossy numeric coercion on `decision candidates minimum`.

## Phase 2 - Fix the biggest inference traps

1. Finish the `output schema` `nullable` cleanup across language docs,
   examples, and proof.
2. Normalize review-verdict vocabulary inside emitted contracts.
3. Move route semantics, final output, and output-schema failures onto the
   exact-location diagnostics path.

## Phase 3 - Make the proof surface honest

1. Add focused negative proof for review semantic binding meaning.
2. Add focused negative proof for trusted carrier meaning.
3. Add focused negative proof for literal guards and bad helper calls.
4. Add focused negative proof for non-enum selector and `mode` cases.
5. Add focused negative proof for duplicate singleton blocks on readable and
   control surfaces.

## Phase 4 - Clean up the teaching path

1. Fix stale corpus-range and error-catalog statements.
2. Re-route the example ladders so `104` through `106` and `119` are easy to
   find from the canonical docs.
3. Add one short integration note for provider roots and rooted runtime paths.
4. Decide whether to ship the previous-turn-output input surface or to
   document its absence very plainly.

# 5) Suggested Audit Ledger For Future Work

If this audit turns into implementation work, I would track it as these
separate stories:

1. Agent field model consistency
2. Singleton fail-loud closure
3. Emitted artifact reservation
4. Output-schema presence semantics
5. Review truth validation hardening
6. Guard and selector typing hardening
7. Diagnostics exact-location coverage
8. Docs and corpus routing repair
9. Previous-turn-output feature decision

# 6) Bottom Line

Doctrine is not broadly missing the language power that Rally and PSFlows
users expect. The bigger issue is that a few core surfaces are less uniform and
less fail-loud than the public story implies.

The most important fixes are not cosmetic:

1. stop open-slot or silent-overwrite behavior on compiler-owned surfaces
2. stop package cargo from shadowing compiler-owned emitted metadata
3. align typed control docs with real proof
4. make a clear decision on previous-turn output reuse
