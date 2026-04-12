---
title: "Doctrine - Big Ass Dump Exhaustive Implementation Audit"
date: 2026-04-12
status: active
doc_type: implementation_audit
owners: ["aelaguiz"]
reviewers: []
related:
  - docs/big_ass_dump.md
  - docs/BIG_ASS_DUMP_IMPLEMENTATION_GAP_AUDIT_2026-04-12.md
  - docs/01_TYPED_MARKDOWN_FOUNDATION_AND_DOCUMENT_SYSTEM.md
  - docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md
  - docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md
  - docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md
  - docs/README.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/WORKFLOW_LAW.md
  - docs/REVIEW_SPEC.md
  - docs/AGENT_IO_DESIGN_NOTES.md
  - examples/README.md
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/model.py
  - doctrine/compiler.py
  - doctrine/renderer.py
  - doctrine/verify_corpus.py
  - editors/vscode/README.md
---

# Executive Verdict

`docs/big_ass_dump.md` is not an accurate open-gap list anymore. In the current
2026-04-12 repo state, Doctrine ships essentially every materially distinct
Doctrine-side feature family proposed in that dump, with one narrow partial
edge around specific `render_profile` targets for `current_artifact`,
`own_only`, and `preserve_exact`.

The main reason the dump still feels "unfinished" is that it is a stitched
archive of multiple recommendation passes, not one stable spec. It repeats the
same families several times and, in a few places, directly contradicts itself.
Once you dedupe by real language surface instead of by repeated prose, the only
clear Doctrine-side idea that is not shipped as a separate primitive is a
dedicated reusable `preservation` bundle declaration. That is not an accidental
miss. The repo explicitly closes that seam through workflow-law reuse,
inheritance, and patching instead of adding a new declaration family.

## Verification Run Used For This Audit

All of these were run in the current tree during this audit:

- `uv sync`
- `npm ci`
- `make verify-examples`
- `make verify-diagnostics`
- `cd editors/vscode && make`

All passed.

# Audit Method

This audit does not treat every repeated paragraph in `docs/big_ass_dump.md` as
a separate requirement. The unit of audit is the materially distinct Doctrine
feature family.

Status labels:

- `shipped`: the current repo implements and proves the family
- `shipped under different final shape`: the capability is present, but the
  dump described it with draft-era framing or a draft-only name
- `intentionally not shipped as separate surface`: the repo closes the seam,
  but by reusing an existing owner path instead of adding the exact primitive
  the dump proposed
- `not a doctrine feature`: the dump item is a Lessons-specific artifact name,
  phase-local naming choice, or draft-era shape name, not a language contract

# What The Dump Actually Is

`docs/big_ass_dump.md` is a 4,747-line pasted design dump with repeated and
conflicting passes.

Repeated headings alone show that it is not one clean spec:

- `## Shared Lesson Plan Review Contract` appears 6 times
- `## Lesson Plan Review` appears 4 times
- `## Lesson Plan Review Rules` appears 4 times
- `## Routing-Only Turns` appears 4 times
- `## Lesson Promise` appears 4 times

It also contradicts itself on key surface decisions:

- `review_family` is proposed as a new surface at `docs/big_ass_dump.md:149`,
  then later rejected as unnecessary at `docs/big_ass_dump.md:1258`
- `route_only` is proposed as a new declaration at
  `docs/big_ass_dump.md:976`, then later rejected as unnecessary at
  `docs/big_ass_dump.md:1255`, then proposed again at
  `docs/big_ass_dump.md:3985`
- `grounding` is proposed at `docs/big_ass_dump.md:1057`, described as "not
  yet" at `docs/big_ass_dump.md:1822`, then proposed again at
  `docs/big_ass_dump.md:4066`
- `render_profile` is proposed at `docs/big_ass_dump.md:1078`, described as
  "not yet" at `docs/big_ass_dump.md:1825`, then proposed again at
  `docs/big_ass_dump.md:4087`

So the only defensible audit method is:

1. collapse the dump to one list of real feature families
2. ground each family in shipped code, shipped docs, and manifest-backed proof
3. call out draft-only names and superseded framing as such

# Authoritative Family Audit

## 1. Typed Markdown And `document`

Status: `shipped`

This entire family is in the repo now:

- top-level `document` declarations
- `structure:` attachment on markdown-bearing inputs and outputs
- rich readable block kinds
- multiline payload support for rich readable blocks
- keyed descendant addressability
- document inheritance and explicit patch accounting
- rendered markdown/readback through the shared renderer path

Representative dump asks:

- `document LessonPlan` at `docs/big_ass_dump.md:50`, `469`, `2403`, `2629`
- typed markdown / rich block rendering at `docs/big_ass_dump.md:2381-2453`
- addressable document descendants at `docs/big_ass_dump.md:2579-2590`
- explicit document inheritance and override rules at
  `docs/big_ass_dump.md:2982-3018`
- row and item schemas on readable children at `docs/big_ass_dump.md:4471-4511`

Current shipped proof:

- grammar: `doctrine/grammars/doctrine.lark:49`, `365-477`
- parser/model/compiler support:
  - `doctrine/parser.py:994-1069`
  - `doctrine/model.py:857-891`
  - `doctrine/compiler.py:4259-4390`
  - `doctrine/compiler.py:10168-10486`
  - `doctrine/compiler.py:11218-12398`
  - `doctrine/compiler.py:13034-14130`
- renderer support:
  - `doctrine/renderer.py:71-127`
  - `doctrine/renderer.py:221-609`
- proof corpus:
  - `examples/56_document_structure_attachments`
  - `examples/58_readable_document_blocks`
  - `examples/59_document_inheritance_and_descendants`
  - `examples/61_multiline_code_and_readable_failures`
  - `examples/65_row_and_item_schemas`
  - `examples/66_late_extension_blocks`

Audit note:

The dump's typed-markdown direction is no longer missing. It is shipped, and it
is proved by manifest-backed examples rather than only by phase-doc prose.

## 2. `analysis`

Status: `shipped`

Representative dump asks:

- first-class analysis obligations at `docs/big_ass_dump.md:65-104`
- `analysis LessonPlanning` at `docs/big_ass_dump.md:681`, `733`, `1321`,
  `1865`, `3690`, `3742`
- structured analysis verbs at `docs/big_ass_dump.md:1294-1567`

Current shipped proof:

- phase doc: `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md:82-176`
- language surface:
  - `doctrine/grammars/doctrine.lark:46`
  - `doctrine/model.py:695`
  - `doctrine/compiler.py:4123`
  - `doctrine/compiler.py:10628-10792`
- proof corpus:
  - `examples/54_analysis_attachment/prompts/AGENTS.prompt:15-54`
  - `examples/54_analysis_attachment/ref/release_analysis_demo/AGENTS.md:1`
  - `examples/67_semantic_profile_lowering/prompts/AGENTS.prompt:13-19`

Audit note:

This family is not partial. The reusable declaration, concrete-agent
attachment, addressability, and readable lowering path are all shipped.

## 3. `decision` / Candidate Pools / Ranking

Status: `shipped`

Representative dump asks:

- first-class decision scaffolds at `docs/big_ass_dump.md:104-125`
- `decision PlayableStrategyChoice` at `docs/big_ass_dump.md:110`, `527`
- `candidate_pool required` and `rank_by` at
  `docs/big_ass_dump.md:117`, `123`, `537`

Current shipped proof:

- language surface:
  - `doctrine/grammars/doctrine.lark:47`, `320-325`
  - `doctrine/model.py:715`
  - `doctrine/parser.py:738-799`
  - `doctrine/compiler.py:4133-4183`
- public docs:
  - `docs/LANGUAGE_REFERENCE.md:171-208`
  - `examples/README.md:140`
- proof corpus:
  - `examples/74_decision_attachment/prompts/AGENTS.prompt:5-29`
  - `examples/74_decision_attachment/cases.toml:5`

Audit note:

This was the real late-arriving gap family. It is now shipped and covered by
the public corpus.

## 4. `schema`, Owner-Aware `schema:`, Sections, Gates

Status: `shipped`

Representative dump asks:

- first-class `schema` at `docs/big_ass_dump.md:1223`, `1567-1820`
- reusable section/gate contracts at `docs/big_ass_dump.md:1599-1730`
- owner-aware `output.schema` vs `output shape.schema` split at
  `docs/big_ass_dump.md:1223-1237`

Current shipped proof:

- phase doc: `docs/02_ANALYSIS_SCHEMA_AND_OUTPUT_CONTRACTS.md:176-308`
- language surface:
  - `doctrine/grammars/doctrine.lark:48`, `612-617`
  - `doctrine/model.py:839`, `1285-1292`
  - `doctrine/parser.py:547-598`
  - `doctrine/compiler.py:4696-4726`
  - `doctrine/compiler.py:5423-5447`
- public docs:
  - `docs/AGENT_IO_DESIGN_NOTES.md:91-99`
  - `docs/REVIEW_SPEC.md:48-63`
- proof corpus:
  - `examples/55_owner_aware_schema_attachments`
  - `examples/57_schema_review_contracts`

Audit note:

The owner-aware `schema:` split is shipped. This is not still living only in
the phase doc.

## 5. Schema Artifacts, Groups, And Group-Based Invalidation

Status: `shipped`

Representative dump asks:

- reusable artifact inventories and groups at `docs/big_ass_dump.md:2088-2295`

Current shipped proof:

- public docs:
  - `examples/README.md:129`
  - `docs/WORKFLOW_LAW.md:189-192`
- language surface:
  - `doctrine/grammars/doctrine.lark:343`
  - `doctrine/compiler.py:10833-11177`
  - `doctrine/compiler.py:15551-15620`
  - `doctrine/compiler.py:16025`
- proof corpus:
  - `examples/63_schema_artifacts_and_groups`
  - `examples/72_schema_group_invalidation`

Audit note:

This family is fully implemented, including authored-order expansion of schema
group invalidations.

## 6. `review`, `review_family`, Review Contracts, Exact Gates

Status: `shipped`

Representative dump asks:

- first-class `review_family` at `docs/big_ass_dump.md:149-158`
- shared lesson-plan review contracts and exact gate language throughout
  `docs/big_ass_dump.md:797-976`, `3806-3981`
- current artifact carriage and failure-detail fields at
  `docs/big_ass_dump.md:897-972`, `3906-3981`

Current shipped proof:

- public docs:
  - `docs/REVIEW_SPEC.md:28-44`
  - `docs/REVIEW_SPEC.md:48-89`
  - `docs/REVIEW_SPEC.md:121-150`
  - `docs/REVIEW_SPEC.md:222-297`
- language surface:
  - `doctrine/grammars/doctrine.lark:54`
  - `doctrine/compiler.py:4817`
  - `doctrine/compiler.py:4998-5108`
  - `doctrine/compiler.py:5447`
  - `doctrine/compiler.py:6597-7120`
  - `doctrine/compiler.py:7762`
- proof corpus:
  - `examples/45_review_contract_gate_export_and_exact_failures`
  - `examples/46_review_current_truth_and_trust_surface`
  - `examples/47_review_multi_subject_mode_and_trigger_carry`
  - `examples/49_review_capstone`
  - `examples/57_schema_review_contracts`
  - `examples/68_review_family_shared_scaffold`
  - `examples/69_case_selected_review_family`

Audit note:

The dump's review-family pressure is closed. The repo did not just ship a
minimal `review` core; it also shipped reusable review families, case-selected
families, carried state, and schema-backed contracts.

## 7. `route_only`

Status: `shipped under different final shape`

Representative dump asks:

- add a first-class `route_only` surface at `docs/big_ass_dump.md:976-1050`
- later draft says not to add it at `docs/big_ass_dump.md:1255`
- then later proposes it again at `docs/big_ass_dump.md:3985-4059`

Current shipped proof:

- public docs:
  - `docs/WORKFLOW_LAW.md:137-140`
  - `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md:252-286`
- language surface:
  - `doctrine/grammars/doctrine.lark:51`
  - `doctrine/compiler.py:3380-3440`
  - `doctrine/compiler.py:14810`
- proof corpus:
  - `examples/70_route_only_declaration`
  - `examples/41_route_only_reroute_handoff`
  - `examples/42_route_only_handoff_capstone`

Audit note:

The capability is shipped. The only mismatch is framing: the dump sometimes
talks about `route_only` like a brand-new routing engine, but the shipped
implementation lowers it through the existing workflow-law path rather than
inventing a second engine.

## 8. `grounding`

Status: `shipped under different final shape`

Representative dump asks:

- add a first-class `grounding` surface at `docs/big_ass_dump.md:1057-1077`
- later says "No first-class grounding declaration yet" at
  `docs/big_ass_dump.md:1822-1823`
- later proposes it again at `docs/big_ass_dump.md:4066-4086`

Current shipped proof:

- public docs:
  - `docs/WORKFLOW_LAW.md:252-253`
  - `docs/04_REVIEW_ROUTE_ONLY_GROUNDING_AND_CONTROL_PLANE_INTEGRATION.md:295-316`
  - `docs/LANGUAGE_REFERENCE.md:151-160`
- language surface:
  - `doctrine/grammars/doctrine.lark:52`
  - `doctrine/compiler.py:3388-3477`
  - `doctrine/compiler.py:16187`
- proof corpus:
  - `examples/71_grounding_declaration`

Audit note:

Same story as `route_only`: shipped capability, draft-era framing drift.

## 9. `render_profile`, `properties`, Guard Shells, Semantic Lowering

Status: `shipped`, with one `partial` sub-edge

Representative dump asks:

- `render_profile` and natural readback templates at
  `docs/big_ass_dump.md:1078-1116`, `4087-4125`
- typed fact panels / compact metadata shapes at
  `docs/big_ass_dump.md:4447-4466`
- semantic lowerers for analysis/review/route-only style surfaces at
  `docs/big_ass_dump.md:4412-4739`

Current shipped proof:

- phase doc:
  - `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md:56-132`
  - `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md:166-225`
  - `docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md:225-260`
- language surface:
  - `doctrine/grammars/doctrine.lark:42`, `419-420`
  - `doctrine/compiler.py:825-856`
  - `doctrine/renderer.py:27-57`
- proof corpus:
  - `examples/64_render_profiles_and_properties/prompts/AGENTS.prompt:4-35`
  - `examples/67_semantic_profile_lowering/prompts/AGENTS.prompt:4-27`

Audit note:

This family is materially shipped. The built-in profiles, authored
`render_profile`, `properties`, readable `guard`, and semantic lowering targets
for `analysis.stages`, `review.contract_checks`, and `control.invalidations`
are all present in code and examples.

The one real edge I found is the specific profile-target trio
`current_artifact`, `own_only`, and `preserve_exact`. The phase-3 doc and the
dump both show those target names in authored examples
(`docs/03_ADVANCED_TYPED_MARKDOWN_RENDER_POLICY_AND_EXTENSION_SURFACES.md:186-188`,
`docs/big_ass_dump.md:1087-1089`, `4096-4098`), and the compiler recognizes
them as valid render-profile targets via
`doctrine/compiler.py:820-823`. But the shipped renderer's built-in profile
tables only special-case `properties`, `guarded_sections`,
`analysis.stages`, `review.contract_checks`, `control.invalidations`, and the
identity modes via `doctrine/renderer.py:27-57`, and I did not find a manifest
case that proves a dedicated render path for those three target names. So the
family is shipped, but that exact sub-path is only partial.

## 10. Currentness, `trust_surface`, Scope, Preservation, Invalidation

Status: `shipped`

Representative dump asks:

- current artifact / trust surface / current-none / invalidation language
  throughout `docs/big_ass_dump.md:29`, `173`, `257`, `299`, `1116`, `4125`,
  `4661-4698`
- preservation and rewrite-evidence rules at `docs/big_ass_dump.md:201-223`,
  `326-338`, `3811`

Current shipped proof:

- public docs:
  - `docs/WORKFLOW_LAW.md:142-192`
  - `docs/AGENT_IO_DESIGN_NOTES.md:141-159`
- language surface:
  - `doctrine/grammars/doctrine.lark:631`
  - `doctrine/compiler.py:14870-15553`
  - `doctrine/compiler.py:16007`
- proof corpus:
  - `examples/31_currentness_and_trust_surface`
  - `examples/33_scope_and_exact_preservation`
  - `examples/34_structure_mapping_and_vocabulary_preservation`
  - `examples/35_basis_roles_and_rewrite_evidence`
  - `examples/36_invalidation_and_rebuild`
  - `examples/37_law_reuse_and_patching`
  - `examples/38_metadata_polish_capstone`
  - `examples/49_review_capstone`
  - `examples/72_schema_group_invalidation`

Audit note:

This seam is not missing. It is one of the most heavily proved parts of the
current language.

## 11. Reusable `preservation` Bundles

Status: `intentionally not shipped as separate surface`

Representative dump asks:

- dedicated preservation bundles at `docs/big_ass_dump.md:201-223`

Current shipped closure:

- workflow law already ships:
  - `own only`
  - `preserve exact`
  - `preserve decisions`
  - `preserve structure`
  - `preserve mapping`
  - `preserve vocabulary`
  - `ignore ... for rewrite_evidence`
- reusable law sections and inheritance are already shipped:
  - `docs/WORKFLOW_LAW.md:146-163`
  - `examples/37_law_reuse_and_patching`

Audit note:

This is the one place where the dump's literal surface did not ship. But this
is not a forgotten implementation. It is an explicit architectural choice to
reuse existing workflow-law semantics plus inheritance instead of adding a new
`preservation SomeBundle:` declaration family.

## 12. Draft-Only Names And Non-Language Shapes

Status: `not a doctrine feature`

Two recurrent kinds of false gap showed up in the dump:

1. Lessons-specific artifact names that imply a generic feature but are not
   themselves Doctrine contracts
2. draft-only shape names that never became public language surface

The clearest example I found is `ProductionArtifactDocument` in the dump around
`docs/big_ass_dump.md:2450` and `4263`. Current shipped code does not recognize
that as a Doctrine output shape. The shipped markdown-bearing output shapes are
the actual public ones such as `MarkdownDocument`, `AgentOutputDocument`,
`Comment`, and `CommentText` via `doctrine/compiler.py:9347-9375` and the docs
under `docs/AGENT_IO_DESIGN_NOTES.md:109-118`.

That is not missing functionality. It is draft naming drift.

# Bottom Line

If the question is "did Doctrine habitually narrow implementation and leave
huge portions of the dump unshipped?", the current repo evidence says no.

What actually happened is:

1. many dump families were already shipped under the second-wave examples and
   live docs
2. the late real gap, `decision`, was shipped
3. one narrow phase-3 render-profile edge remains only partially proved:
   `current_artifact`, `own_only`, and `preserve_exact` are recognized targets,
   but they do not have the same explicit built-in render treatment or manifest
   proof as the other semantic targets
4. one draft idea, reusable preservation bundles, was intentionally closed by
   reuse instead of by a new declaration family
5. the dump itself still reads like an open gap list because it preserves old,
   repeated, and contradictory recommendation passes side by side

So the present problem is no longer missing language surface. The present
problem is source-of-truth hygiene: `docs/big_ass_dump.md` remains a noisy
historical design input, not a reliable statement of current Doctrine gaps.
