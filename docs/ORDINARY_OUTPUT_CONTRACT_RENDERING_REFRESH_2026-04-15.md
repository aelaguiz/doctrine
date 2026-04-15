---
title: "Doctrine - Ordinary Output Contract Rendering Refresh - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: phased_refactor
related:
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/AUTHORING_PATTERNS.md
  - docs/EMIT_GUIDE.md
  - examples/09_outputs/prompts/AGENTS.prompt
  - examples/56_document_structure_attachments/prompts/AGENTS.prompt
  - examples/58_readable_document_blocks/prompts/AGENTS.prompt
---

# TL;DR

## Outcome

Doctrine will emit ordinary `## Outputs` Markdown as coherent contract blocks with grouped tables instead of flattened ladders of bullets and peer headings. This will work for both simple contract-style outputs and structure-backed artifact-note outputs without any input-side syntax changes.

## Problem

The current ordinary output compiler flattens metadata, owned sections, current-truth carriers, and attached `structure:` content into sibling headings and loose bullets. Consumer flows like the `psflows` lessons agents show that this makes one logical output look like several unrelated mini-docs.

## Approach

Keep the prompt language and the renderer surface stable. Change only ordinary output compilation in Doctrine so `output` declarations compile into grouped contract tables, output-side contract sections, and structure summaries with retained detail blocks where detail still matters.

## Plan

1. Move ordinary-output layout ownership fully into `doctrine/_compiler/compile/outputs.py` and ship the grouped top contract table for simple outputs first.
2. Extend that grouped contract shape to multi-file outputs and contract-data sections without changing inheritance, imports, or trust semantics.
3. Add the richer artifact-note path for parseable support notes and attached `structure:` so the curator-style output class also reads as one coherent block.
4. Prove schema-backed, route-bound, and review-bound ordinary outputs still preserve their current semantics on the new grouped path.
5. Regenerate refs and align docs, diagnostics, versioning notes, and changelog truth in the final sync phase.

## Non-negotiables

- No Doctrine grammar, parser, or input rendering changes.
- No ordinary output semantics changes. Only emitted Markdown presentation changes.
- `final_output:` stays unchanged in this pass.
- The plan must prove the two consumer classes already discussed:
  - simple inherited contract-style outputs like the lessons lead handoff
  - structure-backed artifact-note outputs like the section concepts-and-terms curator handoff

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-15
Verdict (code): COMPLETE
Manual QA: pending (non-blocking)

## Code blockers (why code is not done)
- None. Fresh proof passed on 2026-04-15: `uv sync`, `npm ci`, `uv run --locked python -m unittest tests.test_output_rendering tests.test_output_inheritance tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_final_output tests.test_emit_docs`, `make verify-diagnostics`, and `make verify-examples`.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Compare one simple inherited handoff, one schema-backed output, and one structure-backed artifact-note output against the Section 3.1 consumer anchors in a cold read.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
external_research_grounding: done 2026-04-15
deep_dive_pass_2: done 2026-04-15
recommended_flow: implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can render ordinary outputs as one coherent contract per output, using grouped contract tables and structure summaries, while preserving the same prompt syntax and the same downstream trust semantics.

This claim is false if, after implementation, any of these remain true:

- the two target output classes still read as split ladders of unrelated sections
- the change requires prompt-language edits to existing examples
- ordinary output semantics, trust-surface behavior, or final-output behavior change
- the updated example corpus and tests cannot prove the new grouped render shape

## 0.2 In scope

- Ordinary `outputs` Markdown rendering for single-artifact outputs.
- Ordinary `outputs` Markdown rendering for multi-file outputs.
- Ordinary `outputs` Markdown rendering when `schema`, `must_include`, `properties`, `support_files`, `trust_surface`, `standalone_read`, `notes`, `example`, `owns`, or attached `structure:` are present.
- Compiler-owned output formatting changes in Doctrine only.
- Example, test, and doc updates needed to make the new emitted surface the shipped truth.
- Concrete acceptance anchors in this plan using the two discussed `psflows` examples.

Allowed architectural convergence scope:

- Move ordinary-output-specific formatting logic out of the current shared path if needed so ordinary outputs no longer depend on `final_output.py` formatting helpers.
- Add narrow helper functions inside the ordinary-output compile path for table-building, prose flattening, and structure summarization.
- Reuse existing compiled table and section block types plus the shared inline table helper instead of introducing new prompt-language or public model concepts.

## 0.3 Out of scope

- Input rendering.
- Doctrine prompt grammar or parser changes.
- New prompt keywords, output block kinds, or authored syntax for tables, callouts, or collapsible sections.
- `final_output:` presentation changes.
- Flow render or D2 render changes.
- Any changes in sibling repos, including `psflows`.

## 0.4 Definition of done (acceptance evidence)

- Ordinary outputs in Doctrine emit grouped contract tables instead of flat metadata bullets.
- Attached `schema:` and `structure:` titles appear in the top contract table while their detailed sections still render below it.
- `must_include`, `properties current_truth`, and `support_files` render as readable contract tables in ordinary outputs.
- Support-note guidance that names one clear support surface per line can render as one coherent support table without any input-side syntax change.
- Attached `structure:` on ordinary outputs renders as one artifact-structure block with a summary table plus detail blocks where needed.
- The emitted output shape is proven by updated unit tests and updated example snapshots.
- The plan's two external acceptance anchors are visibly supported by the new Doctrine output shape:
  - lessons lead / coordination handoff class
  - section concepts and terms curator / durable section truth class
- `make verify-examples` passes after regenerating affected refs.
- Docs and public versioning notes say plainly that ordinary emitted output Markdown changed shape while prompt syntax did not.

Behavior-preservation evidence:

- Existing ordinary output semantics remain unchanged.
- Existing `trust_surface` carrier behavior remains unchanged.
- Existing `final_output:` tests stay green without layout rewrites in that surface.

## 0.5 Key invariants (fix immediately if violated)

- No new prompt syntax.
- No new parallel output presentation model for ordinary outputs. The new grouped render is the one shipped ordinary-output shape.
- No silent behavior drift in trust-surface semantics, output inheritance, output import resolution, schema attachment legality, or structure attachment legality.
- No ordinary output dependence on `final_output:`-specific formatting rules after this change.
- No doc, example, or test drift after the compiler change lands.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Make one ordinary output read like one coherent contract.
2. Preserve all current prompt-side authoring surfaces.
3. Keep the implementation compiler-owned and narrow.
4. Prove the new output shape through corpus refs and focused tests.
5. Avoid coupling ordinary-output rendering changes to `final_output:`.

## 1.2 Constraints

- The repo's shipped truth says Doctrine code and manifest-backed examples are authoritative.
- The change is public emitted-surface work, so docs and versioning notes must stay aligned.
- Existing tests already assert old headings like `#### Must Include` and `#### Trust Surface`; those assertions must be deliberately updated, not worked around.
- Some checked-in refs already lag current compile truth, so regenerated refs must become the new baseline.

## 1.3 Architectural principles (rules we will enforce)

- Ordinary output rendering is compiler-owned.
- The compiler may improve output grouping, but it may not invent new authored semantics.
- Use existing compiled readable block types and the shared inline table helper before adding any new internal render model.
- Keep ordinary output formatting logic local to ordinary output compilation.
- Keep final-output compilation isolated unless the change is explicitly in scope.

## 1.4 Known tradeoffs (explicit)

- The new grouped render will change many checked-in refs and several assertion strings at once.
- Tables improve coherence, but some authored prose must be flattened into one-sentence summaries. The compiler must fall back to detail sections when flattening would hide meaning.
- Structure-backed outputs become longer in some cases because the summary table and retained detail sections both appear. That verbosity is acceptable when it prevents ambiguity.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine ordinary outputs compile metadata as bullet strings and support sections as generic titled blocks. This works mechanically, but it does not respect the fact that many output sections are contract data that belong together.

The main ordinary-output path is:

- `doctrine/_compiler/compile/outputs.py`
  - `_compile_output_decl`
  - `_compile_output_files`
  - `_compile_trust_surface_section`
- `doctrine/_compiler/compile/records.py`
  - generic record-item compilation for titled sections and scalar fallbacks
- `doctrine/_renderer/blocks.py`
  - generic section, table, definitions, properties, and list rendering

## 2.2 What’s broken / missing (concrete)

- Single-artifact ordinary outputs render target, shape, and requirement as flat bullets.
- `must_include` entries render as nested heading ladders instead of a compact contract table.
- `properties current_truth` becomes either loose bullets or separate peer sections, so current truth and trust surface feel detached from the artifact they qualify.
- `structure:` on ordinary outputs renders as a full peer section rather than as part of the owning artifact contract.
- Multi-file outputs render as alternating path and shape bullets instead of one file-set contract.

Consumer proof from the lessons flow:

- the lessons lead output reads like several separate parts rather than one handoff contract
- the section concepts-and-terms curator output is worse because the output contract, attached structure, current truth, trust surface, and support-note guidance all flatten into a long staircase

## 2.3 Constraints implied by the problem

- The fix must happen in ordinary output compilation, not in prompt syntax.
- The fix must preserve inheritance and import resolution automatically.
- The fix must support both minimal and rich output contracts from one shared ordinary-output path.
- The fix must not leak into final-output rendering.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- `psflows` lessons project-lead handoff surface — adopt as the consumer acceptance anchor for simple inherited contract-style ordinary outputs — it is the clearest real downstream proof that the current flat render makes one logical handoff look like several separate parts.

  Source files:

  - `/Users/aelaguiz/workspace/psflows/flows/lessons/prompts/AGENTS.prompt`
  - `/Users/aelaguiz/workspace/psflows/flows/lessons/build/agents/project_lead/AGENTS.md`

  Relevant input excerpt:

  ```prompt
  output LessonsLeadOutput[shared.review.HandoffOutput]: "Lessons Lead Output"
      inherit target
      inherit shape
      inherit requirement
      inherit must_include
      inherit current_truth
      inherit trust_surface
      inherit standalone_read

      section_edit_type: "Section Edit Type"
          "Indicate if the requested section edit is a full rewrite, new section, or existing section edit."

  outputs LessonsLeadOutputs: "Your Outputs"
      "Always produce the outputs this role declares."

      coordination_handoff: "Coordination Handoff"
          "Use this note body to fill `{{shared.review.HandoffOutput:must_include.what_changed}}`, `{{shared.review.HandoffOutput:current_truth.current_artifact}}`, `{{shared.review.HandoffOutput:must_include.use_now}}`, and `{{LessonsLeadOutput:section_edit_type}}` for the next person."
          LessonsLeadOutput
  ```

  Target Markdown output to emulate:

  ```md
  ## Your Outputs

  Always produce the outputs this role declares.

  ### Coordination Handoff

  Use this note body to fill `Findings First`, `Current Artifact`, `Use Now`, and `Section Edit Type` for the next person.

  > **Lessons Lead Output**
  >
  > This is one issue note. It should stand on its own.

  | Contract | Value |
  | --- | --- |
  | Target | Issue Note |
  | Issue | `What you're working on in plain language` |
  | Shape | Lessons Issue Note Text |
  | Requirement | Required |

  #### Must Include

  | Field | What to write |
  | --- | --- |
  | **Findings First** | Say what this turn changed. |
  | **Decisions Now Locked** | Say which decisions are now locked. |
  | **Analysis Performed** | Put the real analysis here. Do not hide behind a heading or a one-line label. |
  | **Output Contents That Matter** | Put the real output readback here. Make it easy for the next person to pick up the work. |
  | **Use Now** | Name the main thing the next person should read now. For issue-ledger work, say `home:issue.md` and name the exact note or headings they should start with there. Name the real file path when the current work lives in a real file. If the next person still needs extra proof after opening that main surface, name that proof plainly. |
  | **Failing Gate If Blocked** | If the work is blocked, name the exact failing gate. If it is not blocked, say that plainly. |
  | **Next Owner** | Name the next owner when ownership is changing now. |

  #### Current Truth

  | Field | What to write |
  | --- | --- |
  | **Current Artifact** | Name the current surface for this lane. Use `home:issue.md` when this lane keeps work in the issue ledger. |
  | **Invalidations** | Name downstream work that is no longer current because this turn changed the upstream basis. Use `[]` when nothing was invalidated. |

  #### Trust Surface

  - `Current Artifact`
  - `Invalidations`

  #### Readable On Its Own

  A later reader should be able to read this note alone and know what changed, what is current now, what is no longer current, what to read next, and who owns the next pass.

  #### Section Edit Type

  Indicate if the requested section edit is a full rewrite, new section, or existing section edit.
  ```

- `psflows` lessons section concepts-and-terms curator handoff surface — adopt as the consumer acceptance anchor for structure-backed artifact-note ordinary outputs — it proves the richer case where attached `structure:`, current-truth properties, trust-surface carriers, and support-note guidance all have to read as one artifact contract.

  Source files:

  - `/Users/aelaguiz/workspace/psflows/flows/lessons/prompts/contracts/section_concepts_terms.prompt`
  - `/Users/aelaguiz/workspace/psflows/flows/lessons/build/agents/section_concepts_terms_curator/AGENTS.md`

  Relevant input excerpt:

  ```prompt
  document SectionConceptsTermsIssueArtifactDocument[SectionConceptsTermsDocument]: "Section Concepts And Terms"
      inherit analysis_output
      inherit semantic_tests
      inherit concept_ladder_table
      inherit ordered_concepts
      inherit capability_sentences
      inherit terms_under_concepts
      inherit new_vs_existing
      inherit serious_candidate_decisions
      inherit dependency_notes
      inherit validation_and_stop_lines

      section findings_first: "Findings First" required
          "Say what this turn changed and what now holds as the locked concepts-and-terms truth."

      section analysis_performed: "Analysis Performed" required
          "Put the actual analysis in this section, such as the semantic tests, no-bad-match checks, provenance calls, and dependency-order reasoning that drove the lock."

      section output_contents_that_matter: "Output Contents That Matter" required
          "Put the actual locked concepts-and-terms contents that matter for pickup in this section."

      section use_now: "Use Now" required
          "Say `home:issue.md` and name the exact concepts-and-terms note or headings the next person should read there."

  output SectionConceptsTermsFileOutput: "Section Concepts And Terms Artifact Note"
      target: shared.review.IssueComment
          issue: "The current section concepts and terms work in plain language"
      shape: MarkdownDocument
      requirement: Required
      structure: SectionConceptsTermsIssueArtifactDocument

      owns: "Owns"
          "This issue-backed artifact owns `{{SectionConceptsTermsSchema:sections.semantic_tests.title}}`, ... and `{{SectionConceptsTermsSchema:sections.validation_and_stop_lines.title}}`."

      properties current_truth: "Current Truth"
          current_artifact: "Current Artifact"
              "Set this to `home:issue.md`."

          invalidations: "Invalidations"
              "Name any downstream artifacts that are no longer current because this concepts-and-terms lock changed their upstream basis."

      trust_surface:
          current_truth.current_artifact
          current_truth.invalidations

      standalone_read: "Standalone Read"
          "A downstream reader should be able to read this issue-backed artifact alone and understand what the section is really teaching..."

      notes: "Notes"
          "Use `CONCEPTS.md` only as scratch evidence while the map is being earned."
          "Use `TERM_DECISIONS.md` only when a registry, alias, or continuity call needs extra evidence."
  ```

  Target Markdown output to emulate:

  ```md
  ## Your Outputs

  Always produce the outputs this role declares.

  ### Durable Section Truth

  Use this artifact note as the durable concepts-and-terms handoff for the next lane.

  > **Section Concepts And Terms Artifact Note**
  >
  > This is one issue-backed artifact.
  > It carries the locked concepts-and-terms truth for the section.

  | Contract | Value |
  | --- | --- |
  | Target | Issue Note |
  | Issue | `The current section concepts and terms work in plain language` |
  | Shape | Markdown Document |
  | Requirement | Required |
  | Structure | Section Concepts And Terms |

  #### Artifact Structure

  This artifact must follow the `Section Concepts And Terms` structure below.

  | Required Section | Kind | What it must do |
  | --- | --- | --- |
  | **Analysis Output** | Section | Document the decision work you ran and the decisions that came out of it. |
  | **Semantic Tests** | Definitions | Define what counts as `concept`, `defined term`, `both`, `writer vocabulary`, and `reject` for this section. |
  | **Concept Ladder Table** | Table | Show why each kept concept belongs here now by linking learner readiness, unlocked next capability, and why-this-belongs-here-now reasoning. |
  | **Ordered Concepts** | Ordered List | Lock the dependency-order path later lanes must preserve. |
  | **Capability Sentences** | Section | Give each kept concept one plain-English capability sentence. |
  | **Terms Under Concepts** | Section | Group the terms, glossary calls, and alias calls under the concept they support. |
  | **New Vs Existing** | Section | Say what already exists, what is new, and what stays supporting-only vocabulary. |
  | **Serious Candidate Decisions** | Section | Record whether each serious candidate is `concept`, `defined term`, `both`, `writer vocabulary`, or `reject`, and why. |
  | **Dependency Notes** | Section | Name any prerequisite or teaching-order dependency later lanes must preserve. |
  | **Validation And Stop Lines** | Section | Say exactly what must stop here when ontology truth, term-registry truth, or validation or compile truth is missing. |
  | **Findings First** | Section | Say what this turn changed and what now holds as the locked concepts-and-terms truth. |
  | **Analysis Performed** | Section | Put the actual analysis here. |
  | **Output Contents That Matter** | Section | Put the actual locked concepts-and-terms contents that matter for pickup here. |
  | **Use Now** | Section | Point the next person at the exact `home:issue.md` note or headings to open first. |

  #### Semantic Tests Definitions

  | Definition | Meaning |
  | --- | --- |
  | **concept** | Define what counts as `concept` for this section. |
  | **defined term** | Define what counts as `defined term` for this section. |
  | **both** | Define what counts as `both` for this section. |
  | **writer vocabulary** | Define what counts as `writer vocabulary` for this section. |
  | **reject** | Define what counts as `reject` for this section. |
  | **Counterexample Rule** | Include counterexamples when a nearby noun, phrase, existing slug, or stale section name could tempt a bad match. |

  #### Concept Ladder Table Contract

  | Column | Meaning |
  | --- | --- |
  | **What Makes The Learner Ready Now** | Say what in `Learner History By Section` makes the learner ready now. |
  | **Unlocked Next Capability** | Say which row in `Next Capabilities` this concept unlocks. |
  | **Why It Belongs Here Now** | Say why the concept belongs here instead of earlier or later. |

  #### Owns

  This issue-backed artifact owns `Semantic Tests`, the `Concept Ladder Table` that links `Learner History By Section` and `Next Capabilities` to the kept concepts, `Ordered Concepts`, `Capability Sentences`, `Terms Under Concepts`, `New Vs Existing`, `Serious Candidate Decisions`, `Dependency Notes`, and `Validation And Stop Lines`.

  #### Current Truth

  | Field | What to write |
  | --- | --- |
  | **Current Artifact** | Set this to `home:issue.md`. |
  | **Invalidations** | Name any downstream artifacts that are no longer current because this concepts-and-terms lock changed their upstream basis. |

  #### Trust Surface

  - `Current Artifact`
  - `Invalidations`

  #### Standalone Read

  A downstream reader should be able to read this issue-backed artifact alone and understand what the section is really teaching, which concepts are the right next learner move now, which words carry that meaning, why each concept or term call was made, and what dependency order later lanes should preserve.

  #### Notes

  | Support Surface | Rule |
  | --- | --- |
  | `CONCEPTS.md` | Use only as scratch evidence while the map is being earned. |
  | `TERM_DECISIONS.md` | Use only when a registry, alias, or continuity call needs extra evidence. |
  ```

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - `doctrine/_compiler/compile/outputs.py` — current owner for ordinary output compilation and the canonical place to move ordinary-output grouping logic
  - `doctrine/_compiler/compile/final_output.py` — current owner of `_compile_output_support_items`, which ordinary outputs currently borrow even though final-output layout is out of scope
  - `doctrine/_compiler/compile/records.py` — generic record-item lowering that should stay semantically stable while ordinary outputs gain dedicated grouping
  - `doctrine/_renderer/blocks.py` — existing section, table, definitions, properties, and list renderers that can print the new grouped compiled blocks without prompt changes
- Canonical path / owner to reuse:
  - `doctrine/_compiler/compile/outputs.py` — ordinary output compilation should fully own the new grouped contract render
- Existing patterns to reuse:
  - `doctrine/_compiler/types.py` — `CompiledTableBlock`, `CompiledSection`, and existing compiled readable block types are sufficient for retained detail sections and titled readable sections
  - `doctrine/_compiler/validate/__init__.py` — shared `_pipe_table_lines(...)` already gives the compiler a heading-free inline table path for top contract tables and support tables
  - `doctrine/_renderer/blocks.py` — existing titled-table and titled-section rendering already supports retained detail blocks once the compiler groups the data correctly
- Prompt surfaces / agent contract to reuse:
  - `examples/09_outputs/prompts/AGENTS.prompt` — minimal ordinary-output authoring surface that must continue to compile unchanged
  - `examples/55_owner_aware_schema_attachments/prompts/AGENTS.prompt` — schema-backed ordinary outputs that must move onto the same grouped contract path
  - `examples/56_document_structure_attachments/prompts/AGENTS.prompt` — minimal `structure:`-attached ordinary output that must continue to compile unchanged
  - `examples/58_readable_document_blocks/prompts/AGENTS.prompt` — richer `structure:`-attached output proving definitions, tables, and checklists under ordinary outputs
  - `examples/60_shared_readable_bodies/prompts/AGENTS.prompt` — readable-block `definitions must_include` proof that should stay on the generic readable path
  - `examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt` — schema-backed ordinary outputs with richer schema detail that must stay coherent
- Native model or agent capabilities to lean on:
  - not agent-backed — no model-capability constraint changes are part of this work
- Existing grounding / tool / file exposure:
  - `doctrine.emit_docs` and `doctrine.renderer.render_markdown` — the emitted Markdown path that this change must preserve semantically while changing presentation
  - emitted `.contract.json` companions from `doctrine.emit_docs` — adjacent machine-readable output that this plan keeps unchanged
  - manifest-backed examples under `examples/**/cases.toml` — the repo-owned proof surface for emitted docs
- Duplicate or drifting paths relevant to this change:
  - `doctrine/_compiler/compile/final_output.py` helper reuse from ordinary outputs — current cross-path coupling that should be removed so ordinary output formatting does not ride on final-output helpers
  - checked-in example refs versus current in-memory compile truth — some refs already lag current compiler output and must be regenerated as part of this change
- Capability-first opportunities before new tooling:
  - compiler-owned grouping using existing compiled readable blocks plus the shared inline table helper — solves the problem without new syntax, new harnesses, or new renderer modes
- Behavior-preservation signals already available:
  - `tests/test_output_inheritance.py` — inherited and imported ordinary-output proof
  - `tests/test_review_imported_outputs.py` — imported review-output proof
  - `tests/test_final_output.py` — regression proof that ordinary-output changes do not spill into final-output behavior
  - `tests/test_emit_docs.py` — proof that emitted `.contract.json` does not drift while Markdown layout changes
  - `make verify-examples` — end-to-end emitted-surface proof
  - `examples/09_outputs`, `examples/31_currentness_and_trust_surface`, `examples/55_owner_aware_schema_attachments`, `examples/56_document_structure_attachments`, `examples/58_readable_document_blocks`, `examples/60_shared_readable_bodies`, and `examples/63_schema_artifacts_and_groups` — ordinary-output corpus proof surfaces that must move with the change or prove adjacent behavior stays stable

## 3.3 Decision gaps that must be resolved before implementation

- None. Repo evidence checked first: `doctrine/_compiler/compile/outputs.py`, `doctrine/_compiler/compile/final_output.py`, `doctrine/_compiler/compile/records.py`, `doctrine/_renderer/blocks.py`, current unit tests, current examples, and the two `psflows` consumer anchors already settle the implementation path.
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/_compiler/compile/outputs.py` owns ordinary `input` and `output` compilation. The ordinary output path lives in `_compile_output_decl`, `_compile_output_files`, and `_compile_trust_surface_section`.
- `doctrine/_compiler/compile/final_output.py` owns the dedicated `## Final Output` render. Ordinary outputs currently borrow `_compile_output_support_items` from this file for support-item ordering.
- `doctrine/_compiler/compile/records.py` owns generic record lowering. It turns titled sections into `CompiledSection`, bare scalars into bullet lines, and readable blocks into their compiled readable forms.
- `doctrine/_compiler/compile/readables.py` owns document and schema lowering. Ordinary outputs reuse `_compile_schema_sections_block` and `_compile_document_body` for attachments.
- `doctrine/_renderer/blocks.py` renders strings, sections, and readable blocks. It has no special notion of an ordinary output contract today.

## 4.2 Control paths (runtime)

Current single-artifact output flow:

1. `_compile_output_decl` validates guards, splits `target` / `shape` / `requirement` / `files`, and resolves the active render profile.
2. For non-`files` outputs, it appends raw string lines for `Target`, target config keys such as `Path` or `Issue`, `Shape`, and `Requirement`.
3. When `schema:` is attached, it appends `- Schema: ...` and then a peer section from `_compile_schema_sections_block`.
4. When `structure:` is attached, it appends `- Structure: ...` and then a peer section named `Structure: <Title>` whose body comes from `_compile_document_body`.
5. `trust_surface` compiles separately through `_compile_trust_surface_section`.
6. Extra authored items go through borrowed final-output helper `_compile_output_support_items`, which injects `Trust Surface` before `Standalone Read` when both exist and otherwise appends it at the end.
7. The renderer prints the items in authored order, so one logical output becomes a staircase of bullets and peer headings.

Current multi-file output flow:

1. `_compile_output_decl` hands the titled `files:` section to `_compile_output_files`.
2. `_compile_output_files` expects `path` and `shape` under each titled file entry.
3. It emits two loose bullet lines per file entry: one for `Title: path` and one for `Title Shape: shape`.
4. Any per-file extra prose becomes a nested titled section for that file.
5. The parent output still appends `Requirement` and all extra support sections separately after the file bullets.

## 4.3 Object model and ownership today

- The compiler already has the low-level pieces this change needs:
  - `CompiledSection`
  - `CompiledDefinitionsBlock`
  - `CompiledPropertiesBlock`
  - `CompiledTableBlock`
  - shared `_pipe_table_lines(...)` for inline Markdown tables
- Ordinary outputs do not use those table helpers for their contract metadata today.
- `_render_table_block` in `doctrine/_renderer/blocks.py` always emits a titled table block. That means `CompiledTableBlock` is right for retained detail sections, but not for the heading-free top contract table the user wants.
- `_compile_record_item` is intentionally generic. It does not know that `must_include`, `current_truth`, and `support_files` are contract data that should be grouped as tables on ordinary outputs.
- `_compile_document_body` preserves attached document detail faithfully. It does not add a summary layer for structure-backed outputs.
- The shipped compiler already solves heading-free inline tables on the final-output path by calling shared `_pipe_table_lines(...)`.
- `trust_surface` meaning is owned by output field resolution. Only its display order is affected by the borrowed final-output helper.

## 4.4 Failure behavior and proof surface today

Hard failures already covered by the compiler:

- outputs may not mix `files` with `target` or `shape`
- non-file outputs still need `target` and `shape`
- `schema:` still needs at least one schema section
- `structure:` still needs one markdown-bearing artifact
- guarded output items still fail loudly on disallowed refs

Soft failure that drives this plan:

- the emitted Markdown is valid, but it reads like several unrelated mini-contracts instead of one coherent output block

Existing proof surfaces that will catch drift:

- `tests/test_output_inheritance.py`
- `tests/test_route_output_semantics.py`
- `tests/test_review_imported_outputs.py`
- `tests/test_final_output.py`
- `tests/test_emit_docs.py`
- `doctrine/_diagnostic_smoke/compile_checks.py`
- manifest-backed refs under `examples/**/ref/**` and `examples/**/build_ref/**` that still render ordinary outputs

## 4.5 Current architecture gaps that matter

- Contract metadata is emitted as loose bullets instead of one grouped table.
- `schema:` and `structure:` attachment labels are split between one bullet row and one peer detail section.
- Multi-file outputs do not present one file-set contract.
- `must_include`, `current_truth`, and `support_files` use generic record lowering even when the content is clearly table-shaped contract data.
- Ordinary outputs depend on a final-output helper for support-item ordering. That coupling is not part of the public model, but it is a real owner-path smell in code.
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 Canonical owner path and file boundaries

- `doctrine/_compiler/compile/outputs.py` becomes the full owner of ordinary output render grouping.
- `doctrine/_compiler/compile/final_output.py` keeps the dedicated `## Final Output` contract and does not pick up ordinary-output concerns in this change.
- `doctrine/_compiler/compile/records.py` stays the generic fallback path for ordinary authored prose and readable blocks that are not being regrouped as contract tables.
- `doctrine/_compiler/compile/readables.py` stays the owner of schema and document detail lowering that ordinary outputs reuse.
- `doctrine/_renderer/blocks.py` stays unchanged unless a small bug fix is proven necessary. The chosen design should render through existing strings, sections, and readable blocks.

## 5.2 Chosen control path

Future single-artifact output flow:

1. `_compile_output_decl` keeps the current validation and render-profile resolution.
2. It gathers top-level contract rows into one inline pipe table by reusing shared `_pipe_table_lines(...)`.
3. That contract table carries the resolved ordinary-output facts in one place:
   - `Target`
   - target config rows such as `Path` or `Issue`
   - `Shape`
   - `Requirement`
   - `Schema` when present
   - `Structure` when present
4. If `schema:` is attached, the output keeps one detailed schema section below the contract table by reusing `_compile_schema_sections_block`.
5. If `structure:` is attached, the output emits one `Artifact Structure` section below the contract table:
   - first a summary table with `Required Section`, `Kind`, and `What it must do`
   - then only the detail blocks that still add signal
6. Extra authored items go through a new ordinary-output-local support-item compiler in `outputs.py`, not through `final_output.py`.
7. The output returns one `CompiledSection` whose body already reads like one contract.

Future multi-file output flow:

1. `_compile_output_decl` still recognizes titled `files:`.
2. The output starts with a small contract table for shared facts:
   - `Target` = `File Set`
   - `Requirement` when present
3. It then emits one `Artifacts` table with `Artifact`, `Path`, and `Shape`.
4. Per-file extra prose stays attached to the named artifact below that table only when such detail exists.
5. Shared extra sections like `must_include`, `support_files`, `notes`, and `standalone_read` render after the artifacts table on the same ordinary-output path.

## 5.3 Output-side formatting rules

Chosen ordinary-output rules:

- record-section `must_include` compiles to one titled table with columns `Field` and `What to write`
- titled `properties` blocks that behave like contract data, especially `current_truth`, compile to one titled table with columns `Field` and `What to write`
- titled `notes` blocks whose prose lines each name exactly one support surface in inline code compile to one titled table with columns `Support Surface` and `Rule`
- `support_files` compiles to one titled table with columns `Support Surface`, `Path`, and `Use When`
- the top contract table and these heading-owned support tables emit raw pipe-table lines under the owning section instead of `CompiledTableBlock`, because those rows must appear without an extra nested table heading
- `trust_surface` stays a titled bullet list with inline-code field labels
- readable-block forms such as `definitions must_include` stay on the generic readable path
- `standalone_read`, ordinary prose `notes`, `owns`, `path_notes`, `example`, and other ordinary prose sections stay on the generic section path
- guarded output sections and guarded output scalars stay on the existing generic guard path
- attached `schema:` keeps its detailed schema section, but its title also appears in the top contract table
- attached `structure:` keeps one summary-plus-detail section, and its title also appears in the top contract table

Flattening rule for table rows:

- when a row body can be said honestly in one sentence, put that sentence in the table cell
- when that would hide real structure, keep the row short in the table and emit a nearby detail section right after the table

## 5.4 Structure summary and retained detail rules

`Artifact Structure` uses one fixed summary layer plus targeted retained detail:

- document `section` blocks become summary rows; keep no extra detail section unless the section body cannot be flattened honestly
- `definitions` blocks keep a detail section titled `<Title> Definitions`
- `table` blocks keep a detail section titled `<Title> Contract`
- `sequence`, `bullets`, and `checklist` blocks keep a detail section only when the list contents matter beyond the summary row
- `callout`, `code`, `raw markdown`, `raw html`, `footnotes`, and `image` blocks keep a detail section when the block itself carries meaning that cannot fit the summary row
- retained detail blocks reuse existing document lowering and current render profiles; this plan does not create a second document renderer

## 5.5 Internal helper shape

Add narrow ordinary-output-local helpers in `doctrine/_compiler/compile/outputs.py`:

- `_compile_ordinary_output_contract_rows(...)`
- `_compile_ordinary_output_contract_table(...)`
- `_compile_output_files(...)`
- `_compile_ordinary_output_support_items(...)`
- `_compile_output_record_table(...)`
- `_compile_output_properties_table(...)`
- `_compile_output_notes_table(...)`
- `_compile_output_support_files_table(...)`
- `_compile_output_structure_section(...)`
- `_compile_output_structure_summary_rows(...)`

These helpers:

- return existing compiled body items or raw pipe-table lines
- reserve `CompiledTableBlock` for retained detail tables that should keep their own titled section
- do not change parsing or validation rules
- run after inheritance and imported-output resolution, so children and imported parents pick up the new render automatically

## 5.6 Invariants and boundaries

- No prompt syntax change.
- No new renderer mode.
- No new public compiled block type.
- No legacy ordinary-output render mode kept beside the new grouped render.
- `final_output:` stays on its current code path and keeps its current headings, tables, and support-item behavior.
- `trust_surface` keeps the same semantic carrier rules and the same placement before `standalone_read` when both are present.
- Attached schema and document legality stays the same. Only the emitted Markdown shape changes.
- If a compiler helper is shared only because final outputs needed it first, ordinary outputs may stop borrowing it. The canonical owner for ordinary outputs is still `outputs.py`.

## 5.7 Why this is the one chosen architecture

- It reuses the shipped compiler and renderer pieces that already exist.
- It keeps output grouping on the real ordinary-output owner path.
- It keeps `final_output:` out of scope.
- It gives one coherent Markdown block for both user-provided acceptance classes and the repo's own schema-backed and structure-backed ordinary outputs.
- It avoids inventing a second output model or a renderer-only patch that would hide ownership drift.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Ordinary output compile | `doctrine/_compiler/compile/outputs.py` | `_compile_output_decl` | Builds flat bullet metadata, then appends attachment bullets and peer sections | Gather ordinary output facts into one top contract table and route extra items through ordinary-output-local grouping helpers | This is the canonical owner path for ordinary outputs | No public API change | new `tests/test_output_rendering.py`, `tests/test_output_inheritance.py`, `make verify-examples` |
| File-set ordinary outputs | `doctrine/_compiler/compile/outputs.py` | `_compile_output_files` | Emits one loose path bullet and one loose shape bullet per file entry | Emit one `Artifacts` table plus optional per-file detail sections only when needed | Multi-file outputs need the same coherence as single outputs | No public API change | new `tests/test_output_rendering.py`, `examples/09_outputs` |
| Trust-surface placement | `doctrine/_compiler/compile/outputs.py` | `_compile_trust_surface_section` plus new local support-item ordering | Trust-surface placement is controlled indirectly by borrowed final-output helper | Keep the same placement rule, but own it locally in `outputs.py` | Removes cross-owner coupling without changing semantics | No public API change | new `tests/test_output_rendering.py`, `tests/test_route_output_semantics.py` |
| Output contract helpers | `doctrine/_compiler/compile/outputs.py` | helper family from Section 5.5 | No ordinary-output-local grouping helpers exist today | Add local helpers for contract rows, inline tables, support tables, and structure summaries | Keeps the change narrow and owner-correct | Internal only | new `tests/test_output_rendering.py`, `tests/test_output_inheritance.py` |
| Shared inline table helper | `doctrine/_compiler/validate/__init__.py` | `_pipe_table_lines` | Shared helper is used today by `final_output.py` only | Reuse it from ordinary outputs without changing its contract | Gives heading-free inline tables without inventing a new helper or renderer mode | No public API change | `tests/test_output_rendering.py`, `tests/test_final_output.py` |
| Final-output boundary | `doctrine/_compiler/compile/final_output.py` | `_compile_output_support_items` use by ordinary outputs | Ordinary outputs borrow final-output support-item ordering | Remove ordinary-output dependence and leave final-output behavior unchanged | Scope isolation and owner cleanup | No public API change | `tests/test_final_output.py`, `tests/test_review_imported_outputs.py` |
| Renderer boundary | `doctrine/_renderer/blocks.py` | `_render_table_block` | Every `CompiledTableBlock` renders with its own heading | Leave unchanged and rely on raw inline table lines where a heading-free contract table is required | Keeps renderer scope stable and makes the compiler own the layout choice | No public API change | indirect via `tests/test_output_rendering.py`, `make verify-examples` |
| Schema-backed ordinary outputs | `doctrine/_compiler/compile/outputs.py` | `_compile_schema_sections_block` call site inside `_compile_output_decl` | Schema title appears as a loose bullet before the detailed schema section | Surface the schema title in the top contract table and keep the detailed schema section below it | Schema-backed ordinary outputs must read as one contract too | No public API change | `tests/test_output_inheritance.py`, `examples/55_owner_aware_schema_attachments`, `examples/63_schema_artifacts_and_groups` |
| Structure-backed ordinary outputs | `doctrine/_compiler/compile/outputs.py` | `_compile_document_body` call site inside `_compile_output_decl` | Structure title appears as a loose bullet and the full document body sits under peer `Structure: ...` section | Replace that with one `Artifact Structure` summary-plus-detail section | Structure-backed outputs are one of the main acceptance classes | No public API change | new `tests/test_output_rendering.py`, `examples/56_document_structure_attachments`, `examples/58_readable_document_blocks` |
| Support-note guidance | `doctrine/_compiler/compile/outputs.py` | titled `notes` handling on ordinary outputs | Support-surface guidance in `notes` currently stays generic prose | Lower parseable support-note lines into `Support Surface / Rule` tables and leave ordinary prose notes alone | Preserves the richer external acceptance anchor without widening syntax | No public API change | `tests/test_output_rendering.py`, section-concepts inline case |
| Focused render proof | `tests/test_output_rendering.py` | new test file | No dedicated ordinary-output render tests exist | Add focused render cases for single-artifact, file-set, schema-backed, structure-backed, `support_files`, and `properties current_truth` outputs | Keeps render regressions local and readable | Internal only | self |
| Inheritance proof | `tests/test_output_inheritance.py` | existing output inheritance assertions | Asserts old flat bullets like `- Target:` and attachment bullet lines | Update assertions to grouped contract tables and keep inherited schema and structure proof | Inherited and imported outputs must pick up the new render automatically | No public API change | self |
| Route-bound ordinary outputs | `tests/test_route_output_semantics.py` | rendered ordinary-output assertions | Covers ordinary output field and guard rendering, but not grouped contract tables | Add one regression that a route-bound ordinary output still renders the grouped contract table plus guard shells together | Ordinary outputs still share route semantics after the render change | No public API change | self |
| Corpus proof surfaces | `examples/09_outputs`, `examples/31_currentness_and_trust_surface`, `examples/41_route_only_reroute_handoff`, `examples/55_owner_aware_schema_attachments`, `examples/56_document_structure_attachments`, `examples/58_readable_document_blocks`, `examples/60_shared_readable_bodies`, `examples/63_schema_artifacts_and_groups`, plus manifest-backed `examples/**/cases.toml` expectations and generated ordinary-output refs under `examples/**/ref/**` and `examples/**/build_ref/**` | manifest-backed emitted `AGENTS.md` refs and exact-line expectations | Checked-in refs and manifest expectations still show the flat ordinary-output layout | Regenerate affected refs and update affected `cases.toml` expectations in the same change set | Emitted refs and manifest expectations are shipped truth, not optional snapshots | No public API change | `make verify-examples` |
| Diagnostic smoke | `doctrine/_diagnostic_smoke/compile_checks.py` | ordinary-output smoke expectations for schema and structure attachments | Smoke checks still assert old `- Schema:` and `- Structure:` strings | Update smoke expectations to the new grouped ordinary-output layout | Keeps the repo's compiler smoke proof aligned with shipped output | No public API change | `make verify-diagnostics` |
| Public docs | `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, `examples/README.md` | emitted output guidance and example summaries | Docs do not yet explain grouped ordinary-output contract blocks | Update docs to say ordinary outputs now group contract data into tables with no input-side syntax change | Keep public docs aligned with shipped output | Public doc update | docs review |
| Release notes | `docs/VERSIONING.md`, `CHANGELOG.md` | versioning and changelog guidance | No note yet about the emitted ordinary-output surface change | Add release note and upgrade guidance for the new ordinary-output Markdown layout | This is a public emitted-surface change | Public doc update | release docs review |

## 6.2 Migration notes

* Canonical owner path / shared code path: `doctrine/_compiler/compile/outputs.py` owns ordinary output grouping. Reuse shared `_pipe_table_lines(...)`, `_compile_schema_sections_block(...)`, `_compile_document_body(...)`, and generic record lowering only where the content is still ordinary prose.
* Deprecated APIs (if any): none. This is a rendered Markdown surface change, not a prompt-language or Python API change.
* Delete list (what must be removed; include superseded shims/parallel paths if any): ordinary-output calls into `final_output._compile_output_support_items`; flat ordinary-output snapshot expectations such as `- Target: ...`, `- Schema: ...`, and `- Structure: ...` where the new grouped contract table now owns those facts; any attempt to add a second heading-free table renderer or a parallel legacy ordinary-output mode; stale doc examples that still show the bullet-first layout.
* Capability-replacing harnesses to delete or justify: none. No new harness, wrapper, or compatibility mode should be added for this change.
* Live docs/comments/instructions to update or delete: `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, `examples/README.md`, `docs/VERSIONING.md`, and `CHANGELOG.md`.
* Release class: `breaking` on the emitted ordinary-output Markdown surface, with Doctrine language version unchanged. The plan must ship the full breaking-change payload in `CHANGELOG.md` and aligned upgrade guidance in `docs/VERSIONING.md`.
* Behavior-preservation signals for refactors: `tests/test_final_output.py` stays green; `tests/test_review_imported_outputs.py` stays green; `tests/test_route_output_semantics.py` stays green; `tests/test_emit_docs.py` stays green so emitted `.contract.json` does not drift; manifest-backed ordinary-output refs regenerate cleanly under `make verify-examples`.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | ---------------------- | ------------------------------------- |
| Inline contract tables | `doctrine/_compiler/compile/outputs.py` using shared `_pipe_table_lines(...)` | Reuse the shipped inline table pattern already used by `final_output.py` | Avoids a new renderer mode or a second table-string helper | include |
| Schema-backed ordinary outputs | `_compile_output_decl` plus `_compile_schema_sections_block(...)` | Keep one top contract table plus one detailed schema section | Prevents schema-backed outputs from drifting into a third layout | include |
| Structure-backed ordinary outputs | `_compile_output_decl` plus `_compile_document_body(...)` | Add one structure summary layer while reusing current detail lowering | Prevents structure-backed outputs from staying a peer-document ladder | include |
| Support-note guidance | ordinary output `notes` lowering | Turn parseable support-surface rule lines into a support table and leave ordinary prose notes alone | Preserves the richer external acceptance anchor without forcing all notes into one mode | include |
| Route-bound and review-bound ordinary outputs | `tests/test_route_output_semantics.py`, `tests/test_review_imported_outputs.py` | Keep the same grouped ordinary-output path even when route or review semantics are live | Prevents semantic variants from keeping the old layout by accident | include |
| `emit_docs` companion contract | `doctrine.emit_docs`, `tests/test_emit_docs.py` | Keep emitted `.contract.json` unchanged while Markdown layout changes | Prevents the Markdown refresh from widening into a machine-readable contract change | include |
| Diagnostic smoke | `doctrine/_diagnostic_smoke/compile_checks.py` | Keep smoke expectations aligned with the new ordinary-output layout | Prevents the repo's local smoke proof from silently drifting behind shipped output | include |
| Inputs | `doctrine/_compiler/compile/outputs.py::_compile_input_decl` | Apply the same grouped-contract idea to inputs | Similar surface, but the user asked for ordinary outputs only | defer |
| Dedicated final output render | `doctrine/_compiler/compile/final_output.py` | Pull ordinary-output grouping into `final_output:` too | Would blur two deliberately separate public surfaces | exclude |
| New anonymous table type or renderer mode | compiler or renderer new abstraction | Add a new compiled block just to hide a heading | Shared `_pipe_table_lines(...)` already solves the inline table need | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the smallest reasonable sequence of coherent self-contained units that can be completed, verified, and built on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit; `Checklist (must all be done)` is the authoritative must-do list inside the phase; `Exit criteria (all required)` names the concrete done conditions. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. No fallbacks/runtime shims. The authoritative checklist must name the actual chosen work, not unresolved branches or `if needed` placeholders. Prefer programmatic checks per phase and defer manual output reading to finalization.

## Phase 1: Owner split and single-artifact contract-table foundation

Status: COMPLETE

Goal:

Move ordinary output layout ownership fully into `doctrine/_compiler/compile/outputs.py` and ship the grouped top contract table for single-artifact outputs before widening the change to richer shapes.

Work:

Establish the ordinary-output-local helper boundary and prove the simple output class can render one coherent top contract block without borrowing `final_output:` support-item ordering.

Checklist (must all be done):

- Add ordinary-output-local helpers in `doctrine/_compiler/compile/outputs.py` for contract row collection, heading-free inline table emission, and ordinary-output support-item ordering.
- Remove ordinary-output dependence on `doctrine/_compiler/compile/final_output.py::_compile_output_support_items` while preserving current `trust_surface` placement behavior.
- Update `_compile_output_decl` so single-artifact outputs emit one top contract table with target rows, shape, requirement, and any attached `Schema` or `Structure` title.
- Keep attachment legality, target-config order, import resolution, inheritance legality, and trust-surface semantics unchanged.
- Add the first focused proof in new `tests/test_output_rendering.py` for the simple single-artifact grouped contract shape.

Verification (required proof):

- `uv run --locked python -m unittest tests.test_output_rendering`
- `uv run --locked python -m unittest tests.test_output_inheritance`
- `uv run --locked python -m unittest tests.test_emit_docs`

Docs/comments (propagation; only if needed):

- Add one short code comment at the ordinary-output contract-table helper boundary if the raw inline-table choice would otherwise be easy to regress.

Exit criteria (all required):

- Single-artifact ordinary outputs no longer start with flat `- Target:` / `- Shape:` / `- Requirement:` bullets.
- Ordinary outputs no longer borrow final-output support-item ordering.
- The new simple grouped contract path is covered by focused proof in `tests/test_output_rendering.py`.
- `tests.test_emit_docs` still proves the emitted `.contract.json` companion did not change.

Rollback:

- Revert the `outputs.py` owner split and single-artifact contract-table changes if ordinary-output emission loses artifact facts or if final-output behavior starts moving with it.

## Phase 2: Multi-file output contracts

Status: COMPLETE

Goal:

Move multi-file ordinary outputs onto the same grouped contract model after the single-artifact foundation is stable.

Work:

Ship one coherent file-set contract for output collections, using the Phase 1 helper boundary instead of reintroducing a second layout path.

Checklist (must all be done):

- Update `_compile_output_files` so multi-file outputs emit one shared top contract table plus one `Artifacts` table instead of alternating path and shape bullets.
- Keep file-order semantics, path binding, and existing file-target legality checks unchanged.
- Cover the multi-file grouped contract shape in `tests/test_output_rendering.py`.
- Confirm the Phase 1 helper boundary still owns both simple and file-set output layout.

Verification (required proof):

- `uv run --locked python -m unittest tests.test_output_rendering`
- `uv run --locked python -m unittest tests.test_emit_docs`

Docs/comments (propagation; only if needed):

- No public doc update in this phase.

Exit criteria (all required):

- Multi-file ordinary outputs render one coherent file-set contract with one top table and one `Artifacts` table.
- No separate multi-file-only layout path appears outside the ordinary-output owner boundary.
- Existing machine-readable emit behavior is still unchanged.

Rollback:

- Revert the multi-file grouped contract changes if output collections lose file facts or drift into a second ordinary-output layout path.

## Phase 3: Contract-data sections and inherited ordinary outputs

Status: COMPLETE

Goal:

Render contract-shaped ordinary output sections as grouped tables while keeping inherited and imported outputs on the same path.

Work:

Lower the contract-data sections that belong inside the output contract itself, but leave genuinely authored prose and readable blocks on their existing generic paths.

Checklist (must all be done):

- Implement ordinary-output-specific lowering for `must_include`, titled `properties` blocks used as contract data, especially `current_truth`, and `support_files`.
- Keep `trust_surface` as a titled bullet list with inline-code field labels.
- Keep `standalone_read`, `owns`, `path_notes`, `example`, guarded sections, guarded scalars, ordinary prose `notes`, and readable-block forms such as `definitions must_include` on the generic path.
- Apply the chosen flattening rule for contract rows and emit nearby detail sections when one-line flattening would hide meaning.
- Update inherited and imported ordinary output expectations so grouped tables appear after output resolution, not through prompt-side special cases.
- Add focused `tests/test_output_rendering.py` coverage for grouped contract-data sections.

Verification (required proof):

- `uv run --locked python -m unittest tests.test_output_rendering`
- `uv run --locked python -m unittest tests.test_output_inheritance`

Docs/comments (propagation; only if needed):

- Keep the Phase 1 boundary comment accurate if section-table lowering introduces a second ordinary-output gotcha worth noting at the same canonical boundary.

Exit criteria (all required):

- `must_include`, `current_truth`, and `support_files` render as grouped contract tables on ordinary outputs.
- Inherited and imported ordinary outputs pick up the new grouped section layout automatically.
- Readable blocks and ordinary prose still stay on their existing generic paths.

Rollback:

- Revert the section-specific helpers if grouped section compilation changes semantics instead of only presentation.

## Phase 4: Rich artifact-note outputs and support-note guidance

Status: COMPLETE

Goal:

Deliver the richer curator-style artifact-note output class as one coherent block, including parseable support-note guidance and attached `structure:`.

Work:

Use the grouped ordinary-output contract path to make the structure-backed artifact-note class read as one artifact instead of a peer-heading ladder.

Checklist (must all be done):

- Lower titled `notes` blocks to a `Support Surface / Rule` table only when each prose line names exactly one support surface in inline code.
- Keep ordinary prose notes on the generic prose path.
- Replace peer `Structure: <Title>` output sections with one `Artifact Structure` section that contains a summary table plus retained detail sections only where the document block still carries extra signal.
- Add the curator-style inline proof in `tests/test_output_rendering.py` that combines attached `structure:`, titled `properties current_truth`, `trust_surface`, and support notes.
- Confirm the richer artifact-note output still uses the same ordinary-output owner path established in earlier phases.

Verification (required proof):

- `uv run --locked python -m unittest tests.test_output_rendering`
- `uv run --locked python -m unittest tests.test_output_inheritance`

Docs/comments (propagation; only if needed):

- Add or update one short comment only if the retained-detail rule for document blocks becomes hard to infer from the code.

Exit criteria (all required):

- Parseable support-note guidance renders as a support table while ordinary prose notes stay plain prose.
- Structure-backed ordinary outputs read as one artifact contract with one summary layer and only the retained detail sections that still matter.
- The richer curator-style output class is directly covered by focused proof.

Rollback:

- Revert the support-note or structure-summary lowering if the richer artifact contract loses detail or starts changing non-parseable prose notes.

## Phase 5: Schema-backed and semantic-variant preservation

Status: COMPLETE

Goal:

Prove the grouped ordinary-output path still preserves schema-backed, route-bound, and review-bound behavior without spilling into `final_output:`.

Work:

Finish the semantic-preservation work after the grouped ordinary-output contract shape is stable for both simple and rich artifact classes.

Checklist (must all be done):

- Keep schema-backed ordinary outputs on the same grouped ordinary-output path and preserve their detailed schema section below the top contract table.
- Add focused `tests/test_output_rendering.py` coverage for the grouped schema-backed output shape.
- Update or confirm route-bound ordinary output expectations on the new grouped path.
- Update or confirm review-bound imported ordinary output expectations on the new grouped path.
- Keep final-output rendering untouched and prove that isolation with the existing final-output suite.

Verification (required proof):

- `uv run --locked python -m unittest tests.test_output_rendering`
- `uv run --locked python -m unittest tests.test_route_output_semantics`
- `uv run --locked python -m unittest tests.test_review_imported_outputs`
- `uv run --locked python -m unittest tests.test_final_output`

Docs/comments (propagation; only if needed):

- No public doc update in this phase.

Exit criteria (all required):

- Schema-backed ordinary outputs still read as one grouped contract with a detailed schema section below it.
- Route-bound and review-bound ordinary outputs still preserve their current semantics on the grouped path.
- Final-output regressions stay green, proving the ordinary-output refresh did not spill into that surface.

Rollback:

- Revert the schema-backed or semantic-variant changes if the grouped path stops preserving current behavior.

## Phase 6: Corpus, docs, and release-truth sync

Status: COMPLETE

Goal:

Make the new grouped ordinary-output layout the shipped repo truth across refs, diagnostics, docs, and release notes.

Work:

Close the change by updating the proof corpus and every live truth surface that still teaches the superseded bullet-first ordinary-output layout.

Checklist (must all be done):

- Regenerate affected ordinary-output refs under the example families named in Section 6 and any other ordinary-output refs that move under `make verify-examples`.
- Update affected manifest-backed `cases.toml` expectations for ordinary-output layout changes.
- Keep and expand the focused regression suite as needed until the changed output surface is fully covered.
- Update `doctrine/_diagnostic_smoke/compile_checks.py` anywhere it still asserts the superseded ordinary-output layout.
- Update `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, and `examples/README.md` to describe the new grouped ordinary-output layout and the unchanged input-side syntax.
- Update `docs/VERSIONING.md` and `CHANGELOG.md` so the public emitted-surface change ships as a `breaking` release on the emitted Markdown surface, with Doctrine language version unchanged and the full breaking-change payload filled in.
- Delete or rewrite any live doc snippets that still show the superseded bullet-first ordinary-output layout.

Verification (required proof):

- `uv sync`
- `npm ci`
- `uv run --locked python -m unittest tests.test_output_rendering tests.test_output_inheritance tests.test_route_output_semantics tests.test_review_imported_outputs tests.test_final_output tests.test_emit_docs`
- `make verify-diagnostics`
- `make verify-examples`

Docs/comments (propagation; only if needed):

- Update the public docs and release notes listed above in the same change set as code and refs.
- Do not leave any live snippet or instruction showing the old ordinary-output layout once the new refs are checked in.
- Keep manifest expectations and diagnostic smoke aligned in the same change set as the code and ref updates.

Exit criteria (all required):

- Tests and regenerated refs agree with the new ordinary-output render.
- Public docs say plainly that ordinary emitted output Markdown changed while prompt syntax did not.
- Release docs and changelog tell downstream users what changed and what did not, who must act, who does not need to act, and how to verify the upgrade.

Rollback:

- Revert docs, ref regeneration, and the code change together if the grouped ordinary-output render does not stabilize.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

This section does not create a second ship gate. It restates the required proof already locked in Section 7 so implementation and final verification use the same evidence.

## 8.1 Primary proof

- Focused unit tests for ordinary output compilation.
- Manifest-backed example regeneration for the affected example families named in Section 6 plus any other ordinary-output refs that move under `make verify-examples`.
- Diagnostic smoke stays aligned when ordinary-output string expectations move.

## 8.2 Required test cases

- Single-artifact ordinary output with `must_include` and `standalone_read`.
- Inherited ordinary output that keeps parent `must_include`, `current_truth`, `trust_surface`, and `standalone_read`.
- Imported ordinary output that preserves grouped rendering.
- Multi-file ordinary output.
- Schema-backed ordinary output that shows `Schema` in the top contract table and keeps the required-sections detail block below it.
- Structure-backed ordinary output with:
  - summary table
  - definitions detail table
  - table detail block
  - checklist or ordered-list detail block
- Curator-style inline output combining `structure:`, `properties current_truth`, `trust_surface`, and notes.
- Parseable support-note guidance that lowers to a `Support Surface / Rule` table while ordinary prose notes remain prose.
- Readable-block `definitions must_include` that stays on the generic readable path.
- Final-output regression test that proves ordinary-output changes did not spill into `final_output:`.
- `emit_docs` regression proof that the emitted `.contract.json` companion stays unchanged.

## 8.3 Manual review checklist

- Read one simple output and confirm it looks like one contract.
- Read one schema-backed output and confirm the contract table and detailed schema section still read as one block.
- Read one structure-backed output and confirm the owning artifact, structure summary, current truth, and trust surface read as one block.
- Compare the emitted shapes against the two Section 3.1 consumer anchors.

## 8.4 Commands

Run:

- `uv sync`
- `npm ci`
- `uv run --locked python -m unittest tests.test_output_rendering`
- `uv run --locked python -m unittest tests.test_output_inheritance`
- `uv run --locked python -m unittest tests.test_route_output_semantics`
- `uv run --locked python -m unittest tests.test_review_imported_outputs`
- `uv run --locked python -m unittest tests.test_final_output`
- `uv run --locked python -m unittest tests.test_emit_docs`
- `make verify-diagnostics`
- `make verify-examples`

Do not add new harnesses or repo-policing checks for this change.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout

This is a shipped emitted-Markdown surface change, not a runtime feature flag.

Release class:

- `breaking` on the emitted ordinary-output Markdown surface
- Doctrine language version stays unchanged

Rollout shape:

- land compiler changes, tests, refs, and docs together
- treat regenerated refs as the new baseline truth

## 9.2 Ops

No runtime ops change.

## 9.3 Telemetry

No product telemetry change.

## 9.4 Support burden

The main cost is snapshot churn and doc updates. There is no new runtime support surface.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: explorer 1, explorer 2, self-integrator
- Scope checked:
  - frontmatter, `# TL;DR`, `# 0)` through `# 10)`
  - architecture, call-site audit, phase plan, verification, rollout, and helper-block agreement
- Findings summary:
  - Section 3 under-specified the locked inline-table and schema-backed proof story.
  - The richer external anchor promised support-note guidance as part of the same coherent contract, but Section 5 and Section 7 had pushed `notes` back to generic prose.
  - The proof inventory had missed manifest-backed `cases.toml` expectations, diagnostic smoke, and one early-phase inheritance test dependency.
- Integrated repairs:
  - aligned Section 3 with the raw inline-table boundary, schema-backed surfaces, readable-block preservation, and `.contract.json` preservation
  - added compiler-owned lowering for parseable support-note guidance while keeping ordinary prose notes and readable-block `definitions must_include` on their existing generic paths
  - added manifest expectations, diagnostic smoke, `make verify-diagnostics`, and early-phase inheritance proof to Sections 6 through 8
  - locked the release class as `breaking` on the emitted ordinary-output Markdown surface with Doctrine language version unchanged
  - clarified that Section 8 restates required proof instead of creating a second optional gate
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

## 2026-04-15 - Initial canonical plan created

- Command: `arch-step new`
- Decision: scope this change to ordinary outputs only
- Why: the user asked for output-side rendering changes with no input-side syntax changes, and the current pain sits in ordinary `## Outputs`, not `## Final Output`
- Decision: use the two `psflows` lessons examples as explicit consumer acceptance anchors inside the plan
- Why: they are the exact real-world shapes the user wants Doctrine to support
- Decision: keep the implementation compiler-owned inside ordinary output compilation
- Why: this preserves prompt syntax, keeps final-output behavior stable, and avoids creating a second rendering model

## 2026-04-15 - North Star confirmed

- Command: `arch-step new`
- Decision: promote the plan from `draft` to `active` with no scope change
- Why: the user explicitly confirmed the drafted TL;DR and Holistic North Star

## 2026-04-15 - Deep-dive pass 1 locked the ordinary-output owner path

- Command: `arch-step deep-dive`
- Decision: keep ordinary output grouping in `doctrine/_compiler/compile/outputs.py` and stop borrowing final-output support-item ordering from `doctrine/_compiler/compile/final_output.py`
- Why: ordinary outputs and `final_output:` are separate public surfaces, and the current cross-owner helper reuse is the main code-path smell behind this render refresh
- Decision: reuse shared `_pipe_table_lines(...)` for top contract tables instead of adding a new renderer mode or a new compiled table type
- Why: the shipped compiler already has the inline table writer needed for heading-free contract tables
- Decision: treat schema-backed ordinary outputs as part of the same grouped-contract refresh, not as a special holdout
- Why: schema-backed ordinary outputs still show the same split bullet-plus-peer-section problem, and the grouped table can carry the `Schema` row without changing schema semantics

## 2026-04-15 - Deep-dive pass 2 locked the inline-table boundary

- Command: `arch-step deep-dive`
- Decision: use raw pipe-table lines only for heading-free contract tables and keep `CompiledTableBlock` for retained detail tables that should keep their own titled section
- Why: `doctrine/_renderer/blocks.py::_render_table_block` always emits a heading, so using `CompiledTableBlock` for the top contract table would reintroduce the split layout the plan is removing
- Decision: treat the emitted `.contract.json` companion as a preservation surface, not part of the render refresh
- Why: this work changes shipped Markdown layout only. It should not widen into a machine-readable contract change

## 2026-04-15 - Phase plan locked phase-local proof and final corpus sync

- Command: `arch-step phase-plan`
- Decision: keep early phases on focused unit proof and hold manifest-backed ref regeneration until the final sync phase
- Why: the implementation phases will intentionally change emitted Markdown before the checked-in refs are updated, so early full-corpus verification would create churn instead of clean signal
- Decision: make the one authoritative checklist explicit about the unchanged `.contract.json` companion and the exact regression suite that proves the boundary
- Why: the render refresh is public Markdown-only work, and the plan should name the proof that machine-readable emission did not drift

## 2026-04-15 - Consistency pass restored the richer support-note contract and final proof burden

- Command: `arch-step consistency-pass`
- Decision: keep parseable support-note guidance inside the grouped ordinary-output contract instead of leaving all `notes` on the generic prose path
- Why: the richer external acceptance anchor already depends on note-table behavior, so pushing all `notes` back to prose would silently cut approved behavior
- Decision: treat manifest-backed `cases.toml` expectations and diagnostic smoke as part of the same-change proof surface
- Why: refs alone are not the full shipped proof in this repo, and both surfaces still carry old ordinary-output string expectations
- Decision: classify this release as `breaking` on the emitted ordinary-output Markdown surface while keeping the Doctrine language version unchanged
- Why: the public emitted Markdown layout changes in a way downstream users may need to react to, even though the prompt language does not change

## 2026-04-15 - Phase re-audit split blended work into smaller coherent units

- Command: `arch-step phase-plan`
- Decision: split the old four-phase plan into six smaller phases: owner split and simple outputs, multi-file outputs, contract-data sections and inheritance, rich artifact-note outputs, schema and semantic preservation, then final corpus and release sync
- Why: the updated phase-plan doctrine now requires the smallest reasonable sequence of coherent self-contained units, and the earlier Section 7 still blended several independently shippable units together
- Decision: make each phase carry phase-local proof instead of leaning on one mostly end-state verification bundle
- Why: the new Section 7 bar says each phase should be completable and verifiable on its own before later phases build on it
