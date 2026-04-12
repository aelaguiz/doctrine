---
title: "Doctrine - Big Ass Dump Exhaustive Implementation Audit - Second Pass"
date: 2026-04-12
status: active
doc_type: implementation_audit
owners: ["aelaguiz"]
reviewers: []
related:
  - docs/big_ass_dump.md
  - docs/BIG_ASS_DUMP_EXHAUSTIVE_IMPLEMENTATION_AUDIT_2026-04-12.md
  - docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/WORKFLOW_LAW.md
  - docs/REVIEW_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/COMPILER_ERRORS.md
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - examples/README.md
---

# Executive Verdict

This second pass is stricter than the first audit and corrects places where the
earlier writeup was too coarse.

The repo has implemented most of the big Doctrine families proposed in
`docs/big_ass_dump.md`. That broad conclusion still stands. But the first audit
flattened several finer-grained requirements into "family shipped" verdicts
when the detail-level truth is more mixed.

The most important corrected findings are:

- `analysis` is shipped as a family, but the dump's early pseudo-operators
  `prove`, `require`, and `screen ... with ...` are not shipped as first-class
  analysis operators.
- `decision` is shipped as a family, but the richer dump tail
  `winner required`, `sequencing_proof required`, and `solver_screen
  graded_reps` is not shipped.
- `schema:` plus local `must_include:` is a real shipped overlap ban.
- `schema:` plus `structure:` is not banned or warned today; the repo allows
  both and renders both.
- `render_profile` is shipped as a family, but the specific targets
  `current_artifact`, `own_only`, and `preserve_exact` are only partial: the
  compiler recognizes them, but the shipped renderer and proof corpus do not
  give them the same explicit treatment as the other semantic profile targets.

So the corrected verdict is:

- most major families in the dump are shipped
- several finer-grained operators and guardrails are not
- the earlier first-pass audit was directionally right, but not fully
  authoritative at the detail level you asked for

# Verification Run Used For This Audit

These were rerun in the current tree during this second pass:

- `uv sync`
- `npm ci`
- `make verify-examples`
- `make verify-diagnostics`
- `cd editors/vscode && make`

All passed.

# Method

This pass audits `docs/big_ass_dump.md` at the component level, not just the
family level.

That means it distinguishes:

- a shipped family from a richer draft-only variant inside the same family
- a shipped guardrail from a different overlap guardrail that was never
  actually implemented
- a real language surface from a domain-specific example key or a draft-only
  shape name

This pass also includes one user-requested check that is not clearly a dump
requirement on its own: the `schema:` + `structure:` overlap case.

Status labels used below:

- `shipped`
- `partial`
- `not shipped`
- `shipped under different final shape`
- `draft-only naming`
- `intentionally not shipped as separate surface`
- `domain/example content, not language surface`
- `not in dump but audited because requested`

# What The First Audit Missed

The earlier audit undercalled several concrete things:

1. It treated `analysis` as simply shipped without separating the dump's
   early pseudo-operator set from the narrower shipped verb set.
2. It treated `decision` as simply shipped without separating the richer
   dump-only tail from the narrower shipped operator set.
3. It did not surface the absence of any shipped `schema:` + `structure:`
   overlap warning or ban.
4. It only partly surfaced the `render_profile` detail gap around
   `current_artifact`, `own_only`, and `preserve_exact`.
5. It did not separate the dump's top-level `analysis` `basis:` sketch and
   analysis-side `rank_by` sketch from the narrower shipped design, where
   basis rides on individual analysis verbs and `rank_by` belongs to
   `decision`.
6. It did not separate shipped typed-markdown kinds and descendants
   (`properties`, `guard`, `item_schema`, `row_schema`, raw `markdown`,
   raw `html`, `footnotes`, `image`) from draft-only shape names such as
   `ProductionArtifactDocument`.
7. It did not call out that `review_family`, `route_only`, and `grounding`
   are shipped capabilities, but not in the dump's literal framing.
8. It did not call out the stronger schema-group detail: invalidations expand
   to concrete members in authored group order.

# Component-Level Audit

## 1. `analysis`

### Shipped core

- Top-level `analysis` declaration: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:85`, `93`, `481`, `681`, `1321`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:46`
    - `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md:82-176`
    - `examples/54_analysis_attachment/prompts/AGENTS.prompt`

- Concrete-agent `analysis:` attachment: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:2097`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:171-193`
    - `examples/54_analysis_attachment/prompts/AGENTS.prompt:45-54`

- Shipped analysis verbs `derive`, `classify`, `compare`, `defend`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1294-1490`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:293-301`
    - `examples/54_analysis_attachment/prompts/AGENTS.prompt:15-25`

- `stages:` analysis shell and stage addressability: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:16`, `23`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:287-290`
    - `docs/LANGUAGE_REFERENCE.md:225-226`
    - `examples/54_analysis_attachment/prompts/AGENTS.prompt:16-23`

- Analysis inheritance / explicit patching: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1490-1507`
  - Shipped evidence:
    - `doctrine/compiler.py:10083-10108`
    - `doctrine/compiler.py:10653-10748`

### Not shipped from the dump

- `prove ... from ...` analysis operator: `not shipped`
  - Dump evidence: `docs/big_ass_dump.md:85`
  - Shipped evidence:
    - shipped grammar only exposes `derive`, `classify`, `compare`, `defend`
      at `doctrine/grammars/doctrine.lark:293-301`
  - Note:
    - This is not just a wording difference. There is no shipped `prove`
      operator.

- `require ...` analysis operator: `not shipped`
  - Dump evidence: `docs/big_ass_dump.md:87-89`, `94-97`
  - Shipped evidence:
    - no shipped `analysis_section_item` variant for `require` in
      `doctrine/grammars/doctrine.lark:291-301`
  - Note:
    - The dump uses `require` both for proof obligations and staged analysis
      obligations. That surface did not ship.

- `screen ... with ...` analysis operator: `not shipped`
  - Dump evidence: `docs/big_ass_dump.md:98`
  - Shipped evidence:
    - no shipped `screen` operator in `doctrine/grammars/doctrine.lark:291-301`
  - Note:
    - This was undercalled in the first audit.

### Partial / dump-only framing inside `analysis`

- Top-level `basis:` analysis shell: `partial`
  - Dump evidence: `docs/big_ass_dump.md:681`, `733`
  - Current repo truth:
    - shipped grammar carries basis on individual analysis verbs at
      `doctrine/grammars/doctrine.lark:293-301`
    - shipped docs describe verb-local basis at
      `docs/LANGUAGE_REFERENCE.md:217-223`
  - Note:
    - There is real shipped basis support, but not as the dump's top-level
      `analysis` shell.

- `rank_by` inside `analysis`: `partial`
  - Dump evidence: `docs/big_ass_dump.md:533-534`
  - Current repo truth:
    - shipped `rank_by` lives in `decision`, not `analysis`, at
      `doctrine/grammars/doctrine.lark:325`
    - shipped language docs place it under `decision` at
      `docs/LANGUAGE_REFERENCE.md:239`, `251`
  - Note:
    - This was one of the specific flattening mistakes in the earlier audit.

### Domain/example content, not language surface

- `LessonCountDerivation`, `RepSelection`, `LessonPlanning`,
  `PlayableStrategyRanking`, `strawman_sizing_pass`, `why_not_shorter`,
  `why_not_longer`, `graded_reps`, `solver_clarity`: `domain/example content,
  not language surface`
  - These are example declaration names, keys, and domain payloads, not
    missing Doctrine primitives on their own.

## 2. `decision`

### Shipped core

- Top-level `decision` declaration: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:110`, `116`, `527`, `536`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:47`
    - `examples/74_decision_attachment/prompts/AGENTS.prompt`

- `candidates minimum <n>`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:111`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:317`
    - `docs/LANGUAGE_REFERENCE.md:234-251`

- `rank required`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:112`, `529`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:318`

- `rejects required`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:113`, `530`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:319`

- `candidate_pool required`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:117`, `537`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:320`

- `kept required`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:118`, `538`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:321`

- `rejected required`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:119`, `539`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:322`

- `winner_reasons required`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:120`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:323`
    - `examples/74_decision_attachment/prompts/AGENTS.prompt:13-16`

- `choose one winner`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:114`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:324`
    - `docs/LANGUAGE_REFERENCE.md:238-251`

- `rank_by { ... }`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:123`, `534`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:325`
    - `examples/74_decision_attachment/prompts/AGENTS.prompt:10`

### Not shipped from the dump

- `winner required`: `partial`
  - Dump evidence: `docs/big_ass_dump.md:531`
  - Shipped evidence:
    - shipped grammar has `winner_reasons required` and `choose one winner`,
      not `winner required`, at `doctrine/grammars/doctrine.lark:323-324`
  - Note:
    - Winner selection is shipped, but the dump's explicit required winner
      slot is not.

- `sequencing_proof required`: `not shipped`
  - Dump evidence: `docs/big_ass_dump.md:540`
  - Shipped evidence:
    - no such operator in `doctrine/grammars/doctrine.lark:303-325`

- `solver_screen graded_reps`: `not shipped`
  - Dump evidence: `docs/big_ass_dump.md:541`
  - Shipped evidence:
    - no such operator in `doctrine/grammars/doctrine.lark:303-325`

### Corrected verdict

`decision` is `shipped` as a family, but the richer dump-specific operator tail
is `not shipped`. The first audit should have drawn that line explicitly.

## 3. `schema`

### Shipped core

- Top-level `schema` declaration: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1599`, `1625`, `1889`, `2114`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:48`
    - `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md:176-308`

- `sections:` block: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1656`, `1599-1618`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:341`
    - `examples/55_owner_aware_schema_attachments/prompts/AGENTS.prompt`

- `gates:` block: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1657`, `1625-1643`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:342`
    - `examples/57_schema_review_contracts/prompts/AGENTS.prompt`

- Inheritance / override of schema blocks: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1665-1667`, `1735`
  - Shipped evidence:
    - `doctrine/compiler.py:10132-10160`
    - `doctrine/compiler.py:10842-10969`

- Schema-backed `review contract:`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1728`
  - Shipped evidence:
    - `docs/REVIEW_SPEC.md:48-63`
    - `examples/57_schema_review_contracts`

- Schema `artifacts:` and `groups:`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:2276-2286`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:343-344`
    - `examples/63_schema_artifacts_and_groups`
    - `examples/72_schema_group_invalidation`

- `structure:` on markdown-bearing inputs and outputs: `shipped`
  - Dump evidence:
    - `docs/big_ass_dump.md:2451`
    - `docs/big_ass_dump.md:2915`
    - `docs/big_ass_dump.md:2940`
    - `docs/big_ass_dump.md:3282`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:616`
    - `docs/LANGUAGE_REFERENCE.md:325-328`
    - `examples/56_document_structure_attachments`

- `item_schema:` / `row_schema:` readable descendants: `shipped`
  - Dump evidence:
    - `docs/big_ass_dump.md:4480`
    - `docs/big_ass_dump.md:4484`
    - `docs/big_ass_dump.md:4505`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:462-477`
    - `docs/LANGUAGE_REFERENCE.md:316`, `318`, `333`, `335`
    - `examples/65_row_and_item_schemas`

- Schema must export at least one `sections:` or `artifacts:` block: `shipped`
  - Dump evidence:
    - `docs/big_ass_dump.md:1712`
    - `docs/big_ass_dump.md:1716`
    - `docs/big_ass_dump.md:2303`
    - `docs/big_ass_dump.md:2305`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:284`
    - `docs/AGENT_IO_DESIGN_NOTES.md:95-96`
    - `examples/63_schema_artifacts_and_groups/prompts/INVALID_OUTPUT_SCHEMA_WITHOUT_SECTIONS.prompt`

- Schema-group invalidation expansion in authored group order: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:191-192`, `2284`
  - Shipped evidence:
    - `docs/WORKFLOW_LAW.md:191`, `280`
    - `doctrine/compiler.py:16025-16044`
    - `examples/72_schema_group_invalidation`
  - Note:
    - Earlier audits usually stopped at "schema-group invalidation exists."
      The shipped behavior is stronger and narrower than that.

### Overlap guardrails

- `schema:` + local `must_include:` ban: `shipped`
  - Dump evidence:
    - `docs/big_ass_dump.md:1720`
    - `docs/big_ass_dump.md:1796`
    - `docs/big_ass_dump.md:2110`
    - `docs/big_ass_dump.md:2305`
  - Shipped evidence:
    - `doctrine/parser.py:585-594`
    - `docs/COMPILER_ERRORS.md:112`
  - Note:
    - This is a real overlap guardrail and the first audit should have made it
      explicit.

- `schema:` + `structure:` ban or warning: `not shipped`
  - Dump evidence:
    - no explicit shipped-level ban found in the dump
    - the dump separately describes `schema:` ownership and `structure:`
      document attachment at `docs/big_ass_dump.md:2569`, `2915`, `2934`,
      `4382`
  - Current repo truth:
    - docs explicitly show both together in
      `docs/AGENT_IO_DESIGN_NOTES.md:132-138`
    - parser bans only `schema:` + local `must_include:` at
      `doctrine/parser.py:585-594`
    - compiler renders both when both are attached at
      `doctrine/compiler.py:4696-4728`
  - Note:
    - This is the additional overlap thing you asked to add. It is not a
      shipped guardrail today.

## 4. `document`, `structure:`, And Typed Markdown

### Shipped core

- Top-level `document`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:50`, `469`, `2348`, `2403`, `2629`,
    `2679`, `3191`, `4215`, `4471`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:49`
    - `examples/56_document_structure_attachments`

- `structure:` on markdown-bearing inputs/outputs: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:2451`, `2655`, `2922`, `2930`,
    `3282`, `4264`, `4518`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:325-328`
    - `examples/56_document_structure_attachments`

- Readable block palette: `shipped`
  - Dump evidence:
    - `section`, `sequence`, `table`, `callout` around
      `docs/big_ass_dump.md:2408-2436`
    - `properties`, `guard`, `render_profile` around
      `docs/big_ass_dump.md:4443-4449`
    - `item_schema` / `row_schema` around `docs/big_ass_dump.md:4480-4505`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:316-330`
    - `doctrine/grammars/doctrine.lark:419-477`

- Raw `markdown`, raw `html`, `footnotes`, `image`: `shipped`
  - Dump evidence: later typed-markdown rendering sections
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:320-321`
    - `examples/66_late_extension_blocks`

- Addressable descendants and explicit document inheritance: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:2956-3018`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:330-336`
    - `examples/59_document_inheritance_and_descendants`
  - Note:
    - This includes keyed descendants, table rows, and table columns, not just
      document roots.

- Identity projections `title`, `key`, `wire` and render-mode display split:
  `shipped`
  - Dump evidence: `docs/big_ass_dump.md:2960-2963`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:543-550`
    - `doctrine/compiler.py:13723-13961`

### Draft-only naming

- `ProductionArtifactDocument`: `draft-only naming`
  - Dump evidence: `docs/big_ass_dump.md:2450`, `4263`
  - Current repo truth:
    - shipped docs use `MarkdownDocument` / `AgentOutputDocument` for
      markdown-bearing shapes via `docs/LANGUAGE_REFERENCE.md:326-327`
    - compiler shape handling lives in `doctrine/compiler.py:9347-9375`

- `contract_render_profile`: `not shipped`
  - Dump evidence: `docs/big_ass_dump.md:4519-4520`
  - Current repo truth:
    - the shipped surface has `render_profile`, not a separate
      `contract_render_profile`, at `docs/LANGUAGE_REFERENCE.md:340-370`
    - built-in profiles are resolved through `doctrine/compiler.py:819-823`
      and `doctrine/renderer.py:26-57`

## 5. `render_profile`, `properties`, Guard Shells, Semantic Targets

### Shipped core

- Built-in profile families `ContractMarkdown`, `ArtifactMarkdown`,
  `CommentMarkdown`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:4461-4463`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:353-365`
    - `doctrine/renderer.py:27-57`

- Profile attachment to `analysis`, `schema`, `document`, markdown outputs:
  `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1086-1092`, `4095-4101`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:362-370`
    - `doctrine/grammars/doctrine.lark:315`, `339`, `371`, `617`
  - Note:
    - The attachment family is shipped, but the proof corpus is strongest for
      `analysis`, `document`, and output attachments. The dump's more ambitious
      target set still outruns the fully proven renderer behaviors.

- `properties`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:4443-4449`, `4533`, `4584`, `4676`
  - Shipped evidence:
    - `doctrine/grammars/doctrine.lark:419-420`
    - `examples/64_render_profiles_and_properties`

- Explicit readable `guard`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:4445`, `4731`
  - Shipped evidence:
    - `examples/64_render_profiles_and_properties`
    - `doctrine/renderer.py:30`, `40`, `50`

- Semantic targets `analysis.stages`, `review.contract_checks`,
  `control.invalidations`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1090-1092`, `4099-4101`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:356-361`
    - `doctrine/renderer.py:31-33`, `41-43`, `51-53`

- Identity-aware targets `identity.owner`, `identity.debug`,
  `identity.enum_wire`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:1089`, `4461-4463`
  - Shipped evidence:
    - `docs/LANGUAGE_REFERENCE.md:366-367`
    - `doctrine/renderer.py:34-36`, `44-46`, `54-56`

### Partial

- `current_artifact` render-profile target: `partial`
  - Dump evidence: `docs/big_ass_dump.md:1087`, `4096`
  - Current repo truth:
    - compiler recognizes it in `_KNOWN_RENDER_PROFILE_TARGETS` at
      `doctrine/compiler.py:820-823`
    - built-in renderer tables do not special-case it in
      `doctrine/renderer.py:27-57`
  - Note:
    - Recognized target name, but not fully realized/proved like the other
      semantic targets.

- `own_only` render-profile target: `partial`
  - Dump evidence: `docs/big_ass_dump.md:1088`, `4097`
  - Current repo truth:
    - same compiler recognition at `doctrine/compiler.py:820-823`
    - no explicit built-in renderer mode at `doctrine/renderer.py:27-57`

- `preserve_exact` render-profile target: `partial`
  - Dump evidence: `docs/big_ass_dump.md:1089`, `4098`
  - Current repo truth:
    - same compiler recognition at `doctrine/compiler.py:820-823`
    - no explicit built-in renderer mode at `doctrine/renderer.py:27-57`

### Important distinction

`current_artifact`, `own_only`, and `preserve_exact` are real shipped workflow
law and currentness terms elsewhere in Doctrine. What is only partial is their
use as first-class render-profile targets in the dump's style.

## 6. `review`, `review_family`, `route_only`, `grounding`, Currentness, Preservation

### Shipped core

- `review_family`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:149`, `384`, `576`
  - Shipped evidence:
    - `docs/REVIEW_SPEC.md:28-44`
    - `docs/REVIEW_SPEC.md:121-132`
  - Note:
    - The capability ships, but the dump's literal framing such as
      `abstract review_family` is not the exact shipped syntax.

- `review contract:` to workflow or schema, exact gate export: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:808`, `1728`, `3817`
  - Shipped evidence:
    - `docs/REVIEW_SPEC.md:48-87`
    - `examples/45_review_contract_gate_export_and_exact_failures`
    - `examples/57_schema_review_contracts`

- Case-selected `review_family` with exhaustive cases and case-owned contract /
  currentness / routing: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:137-155`
  - Shipped evidence:
    - `docs/REVIEW_SPEC.md:134-179`
    - `doctrine/compiler.py:5090-5188`
  - Note:
    - The shipped surface is stricter than the sketch. Selectors are closed,
      cases are total, and each case owns its subject, contract, currentness,
      and routing explicitly.

- Exact `failing_gates` export: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:400-402`
  - Shipped evidence:
    - `docs/REVIEW_SPEC.md:225-239`
    - `doctrine/compiler.py:5190-5205`
    - `doctrine/compiler.py:6983-6999`

- `route_only`: `shipped under different final shape`
  - Dump evidence: `docs/big_ass_dump.md:984-1029`, `3993-4038`
  - Shipped evidence:
    - `docs/WORKFLOW_LAW.md:137-140`
    - `docs/LANGUAGE_REFERENCE.md:160-175`
  - Note:
    - Capability is shipped. The dump sometimes frames it like a fresh engine;
      the shipped implementation lowers it through existing workflow-law and
      output paths.

- `grounding`: `shipped under different final shape`
  - Dump evidence: `docs/big_ass_dump.md:1064`, `4073`
  - Shipped evidence:
    - `docs/WORKFLOW_LAW.md:252-253`
    - `docs/LANGUAGE_REFERENCE.md:151-156`
  - Note:
    - Grounding is an explicit control-plane declaration, not a hidden receipt
      channel.

- `current artifact ... via ...`, `current none`, `trust_surface`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:173`, `257`, `299`, `897-933`,
    `3906-3942`
  - Shipped evidence:
    - `docs/WORKFLOW_LAW.md`
    - `docs/REVIEW_SPEC.md`
    - `examples/31_currentness_and_trust_surface`
    - `examples/46_review_current_truth_and_trust_surface`

- Blocked branches and `current none` branches: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:409-410`, `971`, `991`
  - Shipped evidence:
    - `docs/REVIEW_SPEC.md:222`, `269`, `277`
    - `docs/WORKFLOW_LAW.md:130`
    - `doctrine/compiler.py:3414-3459`

- `next_owner` and `failure_detail`: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:390-391`, `4535`, `4593`
  - Shipped evidence:
    - `docs/REVIEW_SPEC.md:117-118`, `298`, `318`
    - `doctrine/compiler.py:7762-7796`

- Preservation and overlap law (`own only`, `preserve exact`, `forbid`,
  `support_only`, `ignore ...`): `shipped`
  - Dump evidence: `docs/big_ass_dump.md:205-224`, `299`, `3811`
  - Shipped evidence:
    - `docs/WORKFLOW_LAW.md:146-172`
    - `docs/COMPILER_ERRORS.md:127-134`
    - `examples/33_scope_and_exact_preservation`
    - `examples/35_basis_roles_and_rewrite_evidence`
  - Note:
    - The shipped preservation sublanguage is broader than the dump's example
      snippets. It also includes preserve-structure, preserve-mapping,
      preserve-vocabulary, and explicit comparison / rewrite bases.

- `invalidate` and schema-group invalidation: `shipped`
  - Dump evidence: `docs/big_ass_dump.md:565`, `2214`
  - Shipped evidence:
    - `docs/WORKFLOW_LAW.md:176-192`
    - `examples/72_schema_group_invalidation`

### Intentionally not shipped as separate surface

- Dedicated reusable `preservation` bundle declaration: `intentionally not
  shipped as separate surface`
  - Dump evidence: `docs/big_ass_dump.md:220-224`
  - Current repo truth:
    - same effect is closed through workflow-law reuse plus inheritance and
      patching, not through a new declaration family

## 7. Domain And Example Content That Is Not A Missing Language Surface

These appear throughout the dump but should not be misclassified as missing
Doctrine features:

- lesson-plan section names such as `lesson_promise`, `guidance_plan`,
  `why_not_shorter`, `why_not_longer`, `stable_vs_variable`
- domain row names and titles such as `Prior-Lessons Step-Count Table`,
  `Real Comparable Lessons`, `Guided-Walkthrough Beat-Count Table`
- review field names such as `reviewed_artifact`, `analysis_performed`,
  `what_you_reviewed`
- helper/facts names such as `route_only_turn_facts`
- Lessons-specific terms and example enum/domain names

Verdict: `domain/example content, not language surface`

# Additional User-Requested Overlap Audit

You asked to explicitly add the overlap thing.

Here is the clean answer:

- `schema:` + local `must_include:`: `shipped overlap ban`
- `schema:` + `structure:` on a markdown output: `not in dump as an explicit
  ban, and not shipped as a guardrail`

Current repo truth for `schema:` + `structure:`:

- docs explicitly model both together in `docs/AGENT_IO_DESIGN_NOTES.md:132-138`
- parser does not reject the pairing in `doctrine/parser.py:585-598`
- compiler renders both `- Schema:` and `- Structure:` in
  `doctrine/compiler.py:4696-4728`

So if you wanted a guardrail such as:

- a ban
- a warning
- a lint
- a dedupe policy

that is not in the shipped repo today.

# Bottom Line

The corrected second-pass answer is:

- the repo did not just fake the big families; most of them really are shipped
- but some finer-grained requirements in the dump are still not implemented
- the most important not-shipped detail tails are:
  - `analysis` pseudo-operators `prove`, `require`, `screen ... with ...`
  - `decision` operators `winner required`, `sequencing_proof required`,
    `solver_screen graded_reps`
  - `schema:` + `structure:` overlap guardrail
- the most important partial detail tail is:
  - `render_profile` targets `current_artifact`, `own_only`,
    `preserve_exact`

This is the doc I would treat as the authoritative correction to the first
pass, not the first pass itself.
