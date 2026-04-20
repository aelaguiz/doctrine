---
title: "Doctrine - Tighten AGENTS.md Render Of Typed Contracts - Architecture Plan"
date: 2026-04-19
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - doctrine/_compiler/compile/final_output.py
  - doctrine/_compiler/resolve/outputs.py
  - doctrine/emit_docs.py
  - docs/EMIT_GUIDE.md
  - docs/LANGUAGE_REFERENCE.md
  - examples/83_review_final_output_output_schema
  - examples/135_review_carrier_structured
---

# TL;DR

- **Outcome**: `AGENTS.md` rendering of **JSON-schema-backed Final Output** and **non-final `output` turn-response carriers** collapses to one compact shape — one table with `Field | Type | Null | Write` (or `Field | When | Write` for non-final output), one example when present, one trailing stand-alone paragraph that absorbs Trust Surface + Read on Its Own. Same information, roughly one-fifth the line count. Every shipped `ref/**` AGENTS.md touching these two surfaces regenerates; `make verify-examples` stays green.
- **Problem**: `_compile_final_output_section` and the non-final-output path emit three parallel representations of the same field-level information (Payload Fields table + Field Notes bullets + per-field `####` sections), plus an orphan `- Kind: Json Object` bullet and two runtime-only metadata rows (`Profile`, `Generated Schema`) the agent cannot act on. The `track_scope_critic` Final Output the user flagged is ~90 lines; the `examples/83` pilot is ~120 lines. Most content fits in ~18-20.
- **Approach**: One render path for JSON typed contracts with one table. Schema `note:` + output-decl short body meet in a `Write` column. Runtime-only rows stay in `final_output.contract.json` (they already live there). Consume `kind:` as a scalar at resolve time so it never leaks as an "extras" bullet. Nested-object fields render as dotted rows, not `#####` subsections. Trust Surface + Read on Its Own collapse into one trailing paragraph.
- **Scope discipline**: This change is intentionally narrow. Agent preamble, review workflow blocks, non-review workflow blocks, typed input renders, skills blocks, output-to-file with structure, and prose/no-schema Final Output are **already reasonable** and are explicitly out of scope. The only surfaces that move are F (Final Output — JSON schema-backed), H (Non-final `output` — structured), and the shared renderers those two depend on (J table conventions, K Trust Surface collapse, L guards). The `- Kind:` leak fix ships with them.
- **Plan**: Research the concrete call sites for F and H in the compiler. Lock target shape on one pilot (`examples/83_review_final_output_output_schema`). Regenerate every shipped `ref/**` AGENTS.md that renders F or H through the new path. Update `EMIT_GUIDE.md` and `LANGUAGE_REFERENCE.md` only where they quote the old F/H shape. Release as a `4.1.x` patch — no grammar, no schema, render surface only.
- **Non-negotiables**:
  - No schema, no grammar, no flow-routing semantics change. Render surface only, on F and H only.
  - Every shipped `ref/**` AGENTS.md that hits F or H regenerates in the same commit.
  - No new harness, linter, grep gate, or doc-audit script. Proof = shipped-corpus ref diffs.
  - No sidecar "compact_mode" flag. One render, one shape, hard cutover on F and H.
  - Do not churn surfaces that are already reasonable. If a ref's only change is cosmetic re-flow on a non-F/non-H surface, leave it alone.
  - Plain-language bar (AGENTS.md §"Plain Language Hard Requirement") holds on every new render.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-19
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Every AGENTS.md the doctrine compiler emits for a **JSON schema-backed Final Output** (family F) or **structured non-final `output`** (family H) carries its type + nullability + author guidance in one table, one example when present, and one trailing standalone paragraph that absorbs Trust Surface and Read on Its Own. No per-field `####` re-emission of fields already in that table. No orphan `- Kind: <shape-kind>` bullet. Runtime-only metadata (`Profile`, `Generated Schema`) does not appear in AGENTS.md — it stays in `final_output.contract.json` only. `examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md` drops from ~120 lines to roughly ~40, and the real-world `psflows/flows/curriculum_scope/build/agents/track_scope_critic/AGENTS.md` Final Output block drops from ~90 lines to roughly ~20, with zero behavior-semantics change. Agent preamble, review and non-review workflow blocks, typed input, skills, output-to-file, and prose Final Output do not move — they are already reasonable.

## 0.2 In scope

**Requested behavior scope** (agent-visible markdown render):

- **F. Final Output — JSON schema-backed.** All variants (F1 required w/ example, F2 optional no example, F3 split-review control-ready, F4 split-review carrier-authoritative, F5 nullable route, F6 enum route, F7 case-selector). Owner: `_compile_final_output_section` in `doctrine/_compiler/compile/final_output.py`.
- **H. Non-final `output` — structured turn-response carrier.** All variants (H1 turn-response with bullet fields, H2 field-level guards, H3 workflow route-binding). Owner: the analogous non-final output renderer under `doctrine/_compiler/compile/` (exact file confirmed at `research` time).

**Shared renderers F and H depend on** (move together):

- **J. Payload Fields table conventions.** Single `Field | Type | Null | Write` table for F; `Field | When | Write` for H. Nested objects as dotted rows with `&nbsp;&nbsp;` indent. Type grammar (`string | enum | object | string[] | int | bool`). `Null` column uses `—` / `✓`. `Write` column absorbs schema `note:`, output-decl short body, guard summaries, enum-case guidance.
- **K. Trust Surface + Read on Its Own collapse.** One trailing paragraph at the end of the output section.
- **L. Guards inside F / H tables.** Migrate into `When` column (H) or italic parenthetical / `Write`-cell prefix (F). No promoted `#### <Field>` or `##### <SubField>` sections whose only content is a guard + single-sentence body.

**`- Kind:` leak fix** (ships with F):

- Add `kind` to the scalar_keys set at the shape-resolve boundary in `doctrine/_compiler/resolve/outputs.py` so it is consumed as a shape scalar, not dropped into the extras bullet list. This is one line + its tests.

**Architectural convergence inside F and H**:

- Consolidate three parallel representations (Payload Fields table + Field Notes bullets + per-field `####` sections) into one render path per surface.
- Move `Profile` and `Generated Schema` rows out of the agent-facing metadata table; they stay in `final_output.contract.json`.
- Dotted-row rendering of nested-object fields (`failure_detail.blocked_gate`) instead of promoted `#####` subsections.

**Non-code sibling surfaces that move together**:

- Every `examples/**/ref/**/AGENTS.md` and `examples/**/build_ref/**/AGENTS.md` whose changed bytes come from F or H regenerates; commit the new goldens with the feature. Refs whose only diff would be on a non-F/non-H surface stay put.
- `docs/EMIT_GUIDE.md` updates its Final Output and structured-output render-shape sections.
- `docs/LANGUAGE_REFERENCE.md` updates its Final Output / structured-output render-shape examples only.

## 0.3 Out of scope

**Surfaces that already render reasonably and are not touched by this change:**

- **A.** Agent preamble (authored pass-through).
- **B.** Review workflow blocks (`review X` declarations). Current render is acceptable. Do not retouch.
- **C.** Non-review workflow blocks (`workflow X` declarations). Current render is acceptable. Do not retouch.
- **D.** Typed input renders (D1 File, D2 Prompt, D3 Previous Turn, D4 with Structure). Metadata bullet lists stay as-is. Even the 6-bullet stack in the flagged file is only ~7 lines and does not justify a render change on shipped examples 01-138.
- **E.** Skills block render. Bold-heading pairs + category subsections stay as-is. Current shape is structured and readable.
- **G.** Final Output — prose / no schema. Current render is acceptable; changes here are stylistic, not correctness.
- **I.** Output to File with Structure attachment. Stays as-is.
- **M.** Lens Discipline / Envelope Discipline (authored pass-through).

**Explicit non-goals:**

- Grammar change. `doctrine/grammars/doctrine.lark` is not touched.
- Schema shape, schema generation, `schemas/*.schema.json` emission, `final_output.contract.json` emission (they already hold the canonical field list).
- Flow rendering (`emit_flow.py`, `flow_renderer.py`, `flow_svg.mjs`).
- Editor extension (`editors/vscode/`).
- Release flow, package flow, publish flow.
- Compiler diagnostics catalog (`doctrine/diagnostics.py`).
- Any new surface authors opt into per-agent (no `compact:` field, no `render_profile:` knob). Hard cutover on F and H.
- Runtime harness behavior, agent orchestration, Rally / Codex hooks.
- Any render change that would create churn diffs on shipped refs that do not contain F or H surfaces. If a phase would regenerate an AGENTS.md whose only diff is cosmetic on an out-of-scope surface, the render path is wrong — fix the path, do not accept the churn.

## 0.4 Definition of done (acceptance evidence)

- `make verify-examples` is green on every manifest-backed case.
- `make verify-diagnostics` is green.
- `uv run --locked python -m unittest tests.test_release_flow` is green.
- `make verify-package` is green.
- `tests/test_emit_docs.py` (and any sibling emit-skill / emit-flow tests that assert F / H bytes) updates to the new shape and is green.
- Every `examples/**/ref/**/AGENTS.md` and `examples/**/build_ref/**/AGENTS.md` that renders an F or H surface shows the new compact render; the diff is the proof.
- Refs that do **not** render F or H show **zero** byte drift in this change. That is a hard check: if a ref with only A/B/C/D/E/G/I/M surfaces shows any diff, the render path leaked and the change must be narrowed before merge.
- One pilot (`examples/83_review_final_output_output_schema`) reads as compact: one metadata table (no `Profile` / `Generated Schema` rows), one Payload Fields table, one Example, zero `- Kind` bullet, zero duplicated `#### <Field>` sections for fields already in Payload Fields, dotted rows for nested objects, one trailing standalone paragraph.
- `docs/EMIT_GUIDE.md` and `docs/LANGUAGE_REFERENCE.md` updated where they quote the old F / H shape. Other sections are untouched.
- A local compile-only re-render of `psflows/flows/curriculum_scope/build/agents/track_scope_critic/AGENTS.md` (psflows stays read-only; compile runs from doctrine) shows the Final Output block at roughly ~20 lines.

## 0.5 Key invariants (fix immediately if violated)

- Scope stays narrow: F + H + Kind-leak + shared J / K / L renderers only. Any phase that proposes touching A, B, C, D, E, G, I, or M is out-of-scope and must be rejected at `phase-plan` time.
- No new parallel render path for F or H. One render shape per surface, no author opt-in knob, hard cutover.
- No silent behavior drift. Render-only change; schema / example / routing bytes unchanged.
- No fallbacks or runtime shims. The old bloated F / H emit code is deleted in the same commit that ships the new render.
- Fail-loud boundaries. If an authored F / H surface truly needs a long per-field body the `Write` column cannot carry, the compiler picks one representation, not two.
- Every `ref/**` AGENTS.md whose F or H bytes change updates in the same run. No stale goldens carried for archaeology.
- Refs that do not carry F or H surfaces show zero diff. If any non-F/non-H ref drifts, the render path leaked — narrow it before merge.
- No grep gates, stale-term scans, doc-inventory tests, or absence checks. Proof is the shipped corpus.
- Plain-language bar holds. Every line of new author-facing render text stays at ~7th-grade reading level.
- The author's field-level short body (current per-field `####` content) must survive into the new table's `Write` column. Do not drop authored intent when collapsing.
- Trust Surface and Read on Its Own always collapse into one trailing paragraph inside F / G / H surfaces. (G is out-of-scope for this change; the collapse rule is stated here because F / H touch the shared renderer.)
- Inline guards inside F / H render as italic parentheticals or table `When` cells, never as standalone `####` or `#####` subsections.
- Source → inventory for the in-scope surfaces lives in §0.6. `deep-dive` may sharpen target shapes for F / H / J / K / L there; it may not widen scope to A / B / C / D / E / G / I / M.

## 0.6 Target render shapes per language surface (narrowed)

Scope of this section: **F (Final Output — JSON schema-backed)**, **H (Non-final `output` — structured)**, and the shared renderers they depend on (**J** table conventions, **K** Trust Surface collapse, **L** guards). `deep-dive` may sharpen wording for these surfaces; it may not widen back to A / B / C / D / E / G / I / M.

For completeness: surfaces **A** (agent preamble) and **M** (Lens Discipline / Envelope Discipline) are authored pass-through — doctrine does not own their render and they do not change. Surfaces **B, C, D, E, G, I** are intentionally out of scope; see §0.3 for the scope boundary and rationale.

### F. Final Output — JSON schema-backed

The primary case. All JSON final-output variants share one render family.

**F1. Required, with example (`examples/83/.../AGENTS.md:37-120`)**

Current (~84 lines).

**Target (~18 lines):**

```markdown
## Final Output — Acceptance Review Response

Required. End the turn with one JSON message matching `schemas/acceptance_review_response.schema.json`.

| Field | Type | Null | Write |
| --- | --- | --- | --- |
| `verdict` | enum | — | `accepted` or `changes_requested`. Must align with the routed outcome. |
| `reviewed_artifact` | string | — | Name the reviewed artifact. |
| `current_artifact` | string | — | Name the artifact that remains current after review. |
| `next_owner` | string | — | `ReviewLead` when accepted; `PlanAuthor` when rejected. |

```json
{"verdict":"accepted","reviewed_artifact":"Draft Plan","current_artifact":"Draft Plan","next_owner":"ReviewLead"}
```

Trust surface: `Current Artifact`. This review should stand on its own — a downstream owner should know the acceptance verdict, current artifact, and next owner.
```

Rules:
- `## Final Output — <Title>` single heading (no `## Final Output` + `### <Title>` nesting).
- First line = requirement + schema-file reference in one sentence.
- One table, columns `Field | Type | Null | Write`. `Type` uses `string | enum | object | string[] | int | bool`. `Null` uses `—` (required) or `✓` (nullable).
- `Write` column absorbs: schema `note:`, output-decl short body, field-notes rules relevant to that field, guard summaries, enum-case guidance.
- Code-fenced example on its own (when present).
- Trust Surface + Read on Its Own collapse into one trailing paragraph led by `Trust surface: <fields>.` If no trust surface, just the standalone-read sentence.
- **Dropped:** `> **Final answer contract**` callout. `Contract | Value` metadata table. Orphan `- Kind: Json Object` bullet. Standalone `#### Field Notes` section. Per-field `####` subsections. Nested `#####` subsections.

**F2. Optional, no example (`examples/79/.../repo_status_agent_optional_no_example_AGENTS.md`)**

**Target:**

```markdown
## Final Output — Repo Status Final Response

Optional. End the turn with one JSON message matching `schemas/repo_status_final_response.schema.json`.

| Field | Type | Null | Write |
| --- | --- | --- | --- |
| `summary` | string | — | Short natural-language status; keep user-facing. |
| `status` | string | — | Current repo outcome. |
| `next_step` | string | ✓ | Null only when no follow-up is needed. |

The final answer should stand on its own as one structured repo-status result.
```

No example block. `Optional` replaces `Required` in first line.

**F3. Split review — separate carrier + control-ready control JSON (`examples/105/.../AGENTS.md:77-148`)**

**Target:**

```markdown
## Final Output — Acceptance Control Final Response

Required. End the turn with one JSON message matching `schemas/acceptance_control_final_response.schema.json`. Separate from the review carrier `AcceptanceReviewComment`; a host may read this response directly as the review outcome (control-ready).

| Field | Type | Null | Write |
| --- | --- | --- | --- |
| `verdict` | enum | — | Align with the review verdict. |
| `current_artifact` | string | ✓ | Current artifact after review; null when none. |
| `next_owner` | string | ✓ | Next owner after review; null when none. |
| `blocked_gate` | string | ✓ | Blocking gate when review stopped early; null otherwise. |

```json
{"verdict":"accept","current_artifact":"Draft Plan","next_owner":"ReviewLead","blocked_gate":null}
```

This final JSON should be enough for a host to read the review outcome.
```

Split-carrier + control-ready notes merge into the intro sentence.

**F4. Split review — separate carrier, NOT control-ready (carrier holds outcome)**

Same as F3 but intro sentence reads: `…Separate from the review carrier \`DraftReviewComment\` — read that carrier for the full review outcome.`

**F5. Nullable route field (`examples/121/.../writer_nullable_route_field_final_output_demo/AGENTS.md`)**

Per-route `####` subsections collapse into one table row with route guidance in the `Write` cell.

**Target:**

```markdown
## Final Output — Writer Turn Result

Required. End the turn with one JSON message matching `schemas/writer_turn_result.schema.json`.

| Field | Type | Null | Write |
| --- | --- | --- | --- |
| `kind` | enum | — | Say whether this turn hands off or finishes. |
| `next_route` | string | ✓ | `Revision Partner` when routing; `null` when finishing. |
| `summary` | string | — | Short handoff or closeout summary. |
```

**F6. Non-nullable route enum (`examples/120/.../writer_route_field_final_output_demo/AGENTS.md`)**

Per-enum-value `####` subsections collapse into enum-case lookup inside one `Write` cell.

**Target:**

```markdown
## Final Output — Writer Decision

Required. End the turn with one JSON message matching `schemas/writer_decision.schema.json`.

| Field | Type | Null | Write |
| --- | --- | --- | --- |
| `next_route` | enum | — | `seek_muse` → Muse (fresh inspiration). `ready_for_critic` → Poem Critic (judgment). |
| `summary` | string | — | Say what changed in this pass. |
```

**F7. Output shape case selector (`examples/138_output_shape_case_selector`)**

When the shape dispatches on a selector field, render one table with the selector field + one `Case` column grouping the case-specific fields. Exact target shape deferred to `deep-dive`; held invariant: still one table, no per-case `####` subsections.

### H. Non-final Output (on an agent's `outputs:` contract list)

**H1. Turn-response carrier with bullet-field list (`examples/105/.../AGENTS.md:42-75`)**

Current (~34 lines): bullet-list fields + nested `#### Failure Detail` + `##### Blocked Gate` + `##### Failing Gates` + `#### Trust Surface` + trailing Standalone Read bullet.

**Target (~12 lines):**

```markdown
## Outputs

### Acceptance Review Comment

Required. Target `Turn Response`; shape `Comment`.

| Field | When | Write |
| --- | --- | --- |
| Verdict | always | State whether the plan passed review or asked for changes. |
| Reviewed Artifact | always | Name the reviewed artifact. |
| Analysis Performed | always | Summarize the review analysis. |
| Output Contents That Matter | always | State what the next owner should read first. |
| Current Artifact | when present | Name the artifact that remains current after review. |
| Next Owner | when present | Name ReviewLead when the review accepts the plan. |
| Failure Detail | on `changes_requested` | Blocking gate (when present) + failing gates in authored order. |

Trust surface: `Current Artifact`. This review should stand on its own — a downstream owner should know the verdict, current artifact when one remains, and whether a next owner exists.
```

Rules:
- Bullet-list fields → one table with `Field | When | Write` columns.
- Guards migrate into `When` column (`always` / `when <cond>` / `on <value>`).
- Nested-object fields collapse into their parent row's `Write` cell.
- Trust Surface + trailing Standalone Read → one trailing paragraph.

**H2. Field-level guarded sections (`examples/39_guarded_output_sections/...`)**

Same table pattern as H1. Authored guard text (`Show this only when route facts section status is new or full rewrite`) maps directly to the `When` cell.

**H3. Workflow route output binding (`examples/87/.../AGENTS.md:1-26`)**

**Target:**

```markdown
### Workflow Route Binding Comment

Required. Target `Turn Response`; shape `Comment`.

- **Next Owner**: Review Lead (`ReviewLead`)
- **Route Summary**: Hand off to ReviewLead. Next owner: Review Lead.
```

Next Owner + Next Owner Key merge into one bullet with key in backticks.

### J. Payload Fields table — type conventions (shared across F/H)

Rules applied inside every `Field | Type | Null | Write` table:

- **Scalar types:** `string`, `int`, `bool`, `float`, `number`, `enum`.
- **Arrays:** `string[]`, `int[]`, `MyObject[]`. (Drop `array<string>` / `array<int>` long form.)
- **Nested objects:** parent row uses `Type: object`, then one dotted row per child field (`\`failure_detail.blocked_gate\``). Leading cell indented via `&nbsp;&nbsp;` for the dotted row only.
- **Enums:** `Type: enum`. `Write` column lists the case-by-case guidance when cases affect behavior (see F6).
- **Null column:** `—` for required/non-nullable, `✓` for nullable. Drop the split into `Required On Wire` and `Null Allowed`; both collapse into one column because the JSON schema already says every field is required on wire.
- **Write column:** absorbs schema `note:`, output-field-decl short body, per-field guards as `*(when X)*` italic prefix, nullable handling rules from `field_notes:`.

### K. Trust Surface + Read on Its Own (shared across F/H; renderer also serves G but G render is unchanged in this plan)

Always render as one trailing paragraph at the end of the output section.

- With trust surface: `Trust surface: \`Field A\`, \`Field B\`. <standalone-read sentence>`
- Without trust surface (standalone read only): `<standalone-read sentence>`
- Without standalone read (trust surface only): `Trust surface: \`Field A\`.`
- Without either: no trailing paragraph.

**Dropped:** `#### Trust Surface` heading + bullet list. `#### Read on Its Own` heading + separate paragraph. Inline `- Standalone Read: …` bullet.

### L. Guards and conditions (inside F / H)

Two render contexts for `when present(x)` / `when missing(x)` / `when <cond>` guards on in-scope surfaces:

1. **Inside an H-family `output` table:** migrate into the `When` column (`always` / `when present` / `when <cond>` / `on <value>`).
2. **Inside an F-family Final Output table:** migrate into the `Write` cell as an italic prefix (`*(when verdict is changes requested)* …`), or into enum-case guidance inside `Write` for route enums.

**Dropped inside F / H:** promoted `#### <Field>` / `##### <SubField>` sections whose only content is a guard + single-sentence body.

Guards inside B (review workflow), G (prose Final Output), and other out-of-scope surfaces keep their current rendering.

### N. Line-count budget (in-scope surfaces only)

| Surface family | Typical current | Typical target | Approx. reduction |
| --- | --- | --- | --- |
| F1. Final Output — JSON required w/ example | 80–120 | 14–20 | ~6x |
| F2. Final Output — JSON optional no example | 40–60 | 10–14 | ~4x |
| F3/F4. Final Output — split review (JSON) | 50–80 | 14–18 | ~4x |
| F5/F6. Final Output — routed (nullable / enum) | 40–60 | 10–14 | ~4x |
| F7. Final Output — case selector | 50–80 | 16–22 | ~3x |
| H1. Non-final Output — turn-response carrier | 30–50 | 10–14 | ~3x |
| H2. Non-final Output — with field-level guards | 30–50 | 12–16 | ~3x |
| H3. Non-final Output — workflow route binding | 15–20 | 6–8 | ~2x |
| K. Trust Surface + Read on Its Own (inside F / H) | 5–7 | 1 | ~6x |

Targets, not hard caps. A real agent with many fields or enum cases may exceed them; the invariant is the render shape, not the absolute line count. Out-of-scope surfaces (A, B, C, D, E, G, I, M) retain their current line counts — that is the point.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Preserve authored intent. Every per-field short body that exists in output declarations today must land somewhere in the new compact render (most likely the `Write` column).
2. Compactness. One representation per field, not three.
3. Cutover simplicity. One render shape, no per-agent opt-in, delete the old path.
4. Shipped-corpus fidelity. `make verify-examples` stays green at every phase boundary.

## 1.2 Constraints

- No grammar change.
- No schema change.
- No behavior-semantics change (routing, review verdict mapping, etc.).
- No new author-visible knobs.
- Must work for the full matrix of cases already covered by `examples/79–138` and the smoke-test fixtures in `doctrine/_diagnostic_smoke/`.

## 1.3 Architectural principles (rules we will enforce)

- The schema is the canonical field list. The output-decl short bodies are authoring guidance. The two meet in one render, not three.
- `kind:` is a scalar of the shape, not an extras record item. Consume it at resolve time.
- Agent-facing metadata rows carry agent-actionable information only. Runtime metadata lives in `final_output.contract.json`.
- Nested-object fields render as dotted rows, not promoted headings.
- Render helpers stay small and single-purpose (AGENTS.md §"Keep code files small and single-purpose" and ~500-line split rule).

## 1.4 Known tradeoffs (explicit)

- The compact render loses the ability to give a long-form prose section per field. If authors today rely on the per-field `####` subsection for paragraphs of guidance, they get one line in the `Write` column instead. TBD in research: does any shipped example actually use that surface for more than 1–2 sentences?
- Dotted rows for nested objects are less visually prominent than `#####` subsections. TBD in research: are any authors hanging substantive per-subfield prose off those subheadings?

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

`doctrine/_compiler/compile/final_output.py:209-401` is the authoritative final-output section compiler. Given a JSON-shape final output, it emits:

1. `> **Final answer contract**` callout (1 row of prose).
2. `Contract | Value` metadata table with up to 7 rows: Message type, Format, Shape, Schema, Profile, Generated Schema, Requirement.
3. `#### Payload Fields` table with 5 columns: Field, Type, Required On Wire, Null Allowed, Meaning (the schema's `note:`).
4. `#### Example` code block.
5. Inside `_compile_output_support_items`, the shape's "extras" (every non-scalar record item the shape declared) render as scalar bullets. For `BaseRallyReviewJson`, `kind: JsonObject` falls out as `- Kind: Json Object`, and `field_notes: "Field Notes"` falls out as a `#### Field Notes` section.
6. Every authored output field with a short body renders as its own `#### <Title>` section. For a 7-field review carrier, that's seven `####` sections restating the fields that already appeared in the Payload Fields table.
7. Nested objects (`failure_detail.blocked_gate`, `failure_detail.failing_gates`) render as `#####` subsections, again restating the dotted row already in the Payload Fields table.
8. `#### Trust Surface` + `#### Read on Its Own` trailing sections.

## 2.2 What's broken / missing (concrete)

- The user's flagged `psflows/flows/curriculum_scope/build/agents/track_scope_critic/AGENTS.md` shows a ~90-line Final Output block for a payload that renders compactly in ~20 lines without losing signal.
- `examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md:74` shows the orphan `- Kind: Json Object` bullet on every shipped JSON final output.
- `Profile | OpenAIStructuredOutput` and `Generated Schema | schemas/…json` rows on the metadata table are runtime/orchestrator metadata. The agent cannot do anything with them. They already exist in `final_output.contract.json`.
- Per-field `####` sections duplicate the Payload Fields table row for every typed field. The authored short body would fit in a `Write` column alongside `Type / Null / Meaning`.
- Typed inputs render their own metadata bullet stack (`- Source: File`, `- Path: ...`, `- Shape: ...`, `- Requirement: Required`) that could be one metadata line. The `Previous Producer Handoff` input in the flagged file also ships 6 bullet-formatted metadata items before the prose body.

## 2.3 Constraints implied by the problem

- Real-world agent context windows pay the cost of every duplicated field representation. The flagged critic is one of ~10 agents in a full curriculum run; a ~70-line-per-agent saving is material.
- Doctrine's own AGENTS.md guidance ("Keep agent homes thin", "Every emitted line must earn its keep") is violated by the current render. Fixing it aligns shipped behavior with shipped doctrine.
- The current render predates output shape / case selector features (examples 135–138); simplifying it before newer surfaces harden on top is cheap now and more expensive later.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- No external prior art to adopt. This is internal render-shape tightening on an in-repo compiler. Plain-language hard requirement (AGENTS.md §"Plain Language Hard Requirement", ~7th grade reading level) is the only external-ish anchor; it already binds all shipped render text and constrains `Write`-column phrasing. Adopt implicitly; no external borrow needed.

## 3.2 Internal ground truth (code as spec)

**Authoritative behavior anchors (do not reinvent)**:

- `doctrine/_compiler/compile/final_output.py:209-401` — `_compile_final_output_section`. The F-family authoritative renderer. Orchestrates metadata table, Payload Fields table, Example block, review-response note lines, schema/structure attachments, extras via `_compile_output_support_items` (same file lines 430-484), Trust Surface section.
- `doctrine/_compiler/compile/outputs.py:147-405` — `_compile_output_decl`. The H-family authoritative renderer. Handles `outputs:` contract list entries. Branches on `_should_compact_ordinary_output_contract` (line 285) between compact single-line bullets and table layout. Builds contract rows, optional schema/structure, Trust Surface, extras via `_compile_compact_ordinary_output_support_items` (lines 710-770) or `_compile_ordinary_output_support_items` (lines 772-808).
- `doctrine/_compiler/compile/outputs.py:407-444` — `_compile_trust_surface_section`. Renders Trust Surface as `CompiledSection("Trust Surface", <bullets>)`. Shared by F and H.
- `doctrine/_compiler/compile/records.py:161-326` — `_compile_record_item` and `_compile_fallback_scalar` (lines 328-364). Fallback that turns `RecordScalar` items into `- {label}: {value}` bullets or sections. This is the code path the `- Kind:` bullet leaks through today.
- `doctrine/_compiler/compile/records.py:233-286` — `GuardedOutputSection` / `GuardedOutputScalar` rendering. Emits `#### <Key>` + `Show this only when {condition}.` This is what the plan collapses into `When` columns / italic `Write`-cell prefixes for F and H.
- `doctrine/_compiler/validate/__init__.py:119-131` — `_pipe_table_lines`. Shared markdown pipe-table helper. Already the right primitive; no new table helper needed.
- `doctrine/_compiler/validate/__init__.py:133-205` — `_build_output_schema_payload_rows`. Recursively traverses JSON schema and produces `(field_name, type_label, required_on_wire, null_allowed, meaning)` tuples. Already emits dotted field names (e.g. `failure_detail.blocked_gate`) via recursive `field_prefix` (lines 145-205).
- `doctrine/_compiler/validate/__init__.py:207-268` — `_json_schema_type_label`. Produces the `Type` column values. Already returns the short-form type labels (`string`, `enum`, `string[]`, `int`, `bool`) the plan's J conventions require.
- `doctrine/_compiler/resolve/outputs.py:1692-1696` — `_split_record_items(shape_decl.items, scalar_keys={"schema", "example_file"}, owner_label=...)`. **The `- Kind:` leak.** `"kind"` is missing from `scalar_keys`, so `kind:` falls into extras and emits as a `- Kind: Json Object` bullet via `_compile_fallback_scalar`. Other `_split_record_items` call sites in this file (lines 1801, 2217, 2588, 2627) are for different surfaces and already include correct keys.
- `doctrine/emit_docs.py:379-396` — `_serialize_final_output_contract`. Emits `schema_profile` and `emitted_schema_relpath` into `final_output.contract.json`. The runtime-only facts already live here; the plan only removes them from the agent-facing metadata table in `final_output.py:236-241`, not from this contract JSON.

**Canonical owner path to reuse**:

- `_pipe_table_lines` (validate/__init__.py:119-131) stays the one markdown-table helper for both F and H new tables.
- `_build_output_schema_payload_rows` (validate/__init__.py:133-205) stays the one schema-to-rows traversal; the plan shrinks its output from 5 columns to 4 (drop `Required On Wire`) and extends the `Write` column to absorb extras body.
- `_compile_trust_surface_section` (outputs.py:407-444) becomes an inline-paragraph renderer instead of a separate `CompiledSection`; shared across F and H.

**Adjacent surfaces tied to the same contract family**:

- F-family refs (19 files carry the `- Kind: Json Object` bullet today; confirmed via grep of shipped refs):
  - F1 (required, w/ example): `examples/79_final_output_output_schema`, `examples/83_review_final_output_output_schema`.
  - F3 (split review, control-ready): `examples/104_review_final_output_output_schema_blocked_control_ready`, `examples/105_review_split_final_output_output_schema_control_ready`.
  - F4 (split review, carrier-authoritative): `examples/106_review_split_final_output_output_schema_partial`.
  - F5 (nullable route): `examples/121_nullable_route_field_final_output_contract`.
  - F6 (non-nullable route enum): `examples/120_route_field_final_output_contract`.
  - F-family (misc): `examples/90_split_handoff_and_final_output_shared_route_semantics`, `examples/91_handoff_routing_route_output_binding`, `examples/136_review_shared_route_binding`.
  - F7 (output shape case selector): `examples/138_output_shape_case_selector` — target shape deferred to `deep-dive` per §0.6 F7.
- H-family refs (at least 4 confirmed example dirs):
  - H1 (turn-response carrier w/ bullet fields + nested `####` failure_detail): `examples/105_...`, `examples/135_review_carrier_structured`.
  - H2 (field-level guards): `examples/39_guarded_output_sections` (both `guarded_output_sections_demo` and `nested_guarded_output_sections_demo` refs).
  - H3 (workflow route binding): `examples/87_workflow_route_output_binding`.
- Existing test assertions on F/H render bytes:
  - `tests/test_emit_docs.py:204` asserts the `| Generated Schema | ... |` row. This assertion deletes in the implement phase.
  - `tests/test_emit_docs.py:1274` asserts `"#### Payload Fields"` heading. This assertion updates — the Payload Fields heading stays (but the table contents change to 4-column `Field | Type | Null | Write`).
  - No H-specific assertions found in `test_emit_docs.py` by this grep. Other emit tests (test_emit_skill.py, test_emit_flow.py) not surveyed for F/H assertions — `implement` must recheck.
- Documentation surfaces: `docs/LANGUAGE_REFERENCE.md:931` has one passing mention of Final Output rendering. `docs/EMIT_GUIDE.md` and `docs/AGENT_IO_DESIGN_NOTES.md` have no render-shape quotes of F/H today. Impact: smaller docs churn than initially feared — mostly the plan's in-scope doc updates are adding a new section to `EMIT_GUIDE.md` about compact F/H render, not rewriting existing prose.

**Compatibility posture (separate from `fallback_policy`)**:

- **Clean cutover on F and H render surfaces.** No bridge, no flag, no compact_mode opt-in. Render surface only — the JSON schema, the `final_output.contract.json` bytes, and `schemas/*.schema.json` bytes all stay identical, so downstream harnesses that consume those artifacts are unaffected. The only consumers that see a shape change are agents reading AGENTS.md — by design, that is the whole point of the plan. Recorded in §0.3 ("Hard cutover on F and H") and §0.5 ("No new parallel render path for F or H").
- **Behavior preservation** for the underlying contracts: schema generation, field ordering, JSON payload bytes, routing semantics, `final_output.contract.json` shape. The `make verify-examples` corpus diff is the preservation signal — if any of these byte surfaces drift, the diff catches it.

**Capability-first stance**:

- Not applicable here. This is a compiler render change, not an agent-backed behavior change. No prompts, model capabilities, or native tool use are in play. The `prompt-authoring` route referenced by `shared-doctrine.md §"Capability-first rule"` does not apply. The render is deterministic emit code.

**Existing patterns to reuse**:

- `_pipe_table_lines` — already in use by F's metadata table, F's Payload Fields table, H's contract table. Both new tables (F `Field | Type | Null | Write`, H `Field | When | Write`) use it unchanged.
- Dotted-row recursion (validate/__init__.py:145-205) — already working for nested objects; need to add `&nbsp;&nbsp;` indent on the field-name cell for dotted rows only (per §0.6 J).
- `_compile_trust_surface_section` — target: repurpose as a standalone-paragraph renderer. The current function builds a `CompiledSection` with bullets; the new renderer returns a single prose paragraph (or empty) that F and H both append at section tail.

**Duplicate or drifting paths relevant to this change**:

- **F and H are parallel code paths today** that share only three helpers (`_pipe_table_lines`, `_compile_trust_surface_section`, `_compile_record_item`/`_compile_fallback_scalar`). They do not share metadata-table construction or extras emission. This is the core convergence opportunity this plan creates.
- F's metadata table (final_output.py:231-255) and H's compact metadata bullets / non-compact metadata table (outputs.py:278-296) do the same job with different code and different output shape. After this plan: same table shape (4-column for F, 3-column for H), still separate call sites unless `deep-dive` chooses a shared emitter.
- F's per-field `####` sections (from shape/output-decl extras via `_compile_output_support_items`) and H's per-field bullet list (from authored output-decl body) do the same job with different shapes. After this plan: both fold into the `Write` column of a single table per output.

**Prompt surfaces / agent contract to reuse**: N/A — compiler-side render change.

**Native model or agent capabilities to lean on**: N/A — compiler-side render change.

**Existing grounding / tool / file exposure**: N/A — compiler-side render change.

**Capability-first opportunities before new tooling**: N/A — compiler-side render change.

**Behavior-preservation signals already available**:

- `make verify-examples` — recompiles all manifest-backed examples and diffs every `ref/**` / `build_ref/**` AGENTS.md byte-for-byte. For F/H refs: diff is the proof of the new shape. For non-F/non-H refs (B, C, D, E, G, I, M surfaces): diff must be zero bytes — any drift means the render path leaked scope.
- `make verify-diagnostics` — recompiles `doctrine/_diagnostic_smoke/` fixtures. Fixtures under `doctrine/_diagnostic_smoke/fixtures_final_output.py` and `fixtures_reviews.py` define minimal F/H test cases that will regenerate.
- `tests/test_emit_docs.py` — existing unit tests that assert specific F strings (line 204 Generated Schema row, line 1274 Payload Fields heading). These update in the implement phase; they are the behavior-level unit signal.
- `uv run --locked python -m unittest tests.test_release_flow` and `make verify-package` — will stay green regardless of render shape; not proof of F/H correctness but proof that the change did not break unrelated flows.

## 3.3 Decision gaps that must be resolved before implementation

- **Gap 1 — F/H render-path convergence strategy.** Research confirmed F and H are fully parallel code paths sharing only three helpers. The plan implies convergence (§0.2 "Consolidate three parallel representations...into one render path") but does not choose: (A) new shared emitter `_compile_typed_output_table_section` that F and H both call; (B) refactor `_compile_output_decl` to handle F and delete `_compile_final_output_section`'s table code; (C) keep call sites parallel but output the same shape. Repo evidence checked: both files' structure suggests (A) is the cleanest with minimum risk of cross-surface behavior drift; (C) is cheapest but leaves future drift unaddressed. Default recommendation: (A). Answer needed: pick A, B, or C before `phase-plan` so phasing reflects the chosen structure.
- **Gap 2 — Authored field-body correlation with schema-driven rows.** In the current code the Payload Fields table is schema-driven (validate/__init__.py:133-205) while per-field `####` sections come from authored extras in the shape or output declaration. The plan's `Write` column must carry both sources per row. Repo evidence checked: `examples/83:81-103` shows real authored per-field bodies of 1-3 sentences each; `fixtures_final_output.py:71-72` shows an authored `explanation:` at the shape level. Default recommendation: at render time, the new emitter pairs schema fields with authored extras by matching the field key (e.g. `ReadableBlock` with `title == "Verdict"` maps onto the `verdict` row); any authored body that cannot be matched to a schema field falls through to a single post-table authored-notes paragraph (or is reported as a compile diagnostic). Answer needed: confirm the match-by-field-name rule is acceptable, or propose a more explicit authoring surface (e.g. `write:` scalar on the output-field declaration).
- **Gap 3 — `Write` column one-line vs. multi-line content.** Per-field authored bodies in shipped examples are mostly 1-2 sentences; some (`examples/83:86`) run to 3. Schema `note:` values are typically short. Per-enum-case guidance for F6 may be 1 line per case, multiplied by ~2-5 cases. The plan's line-count targets (§0.6 N) assume `Write` cells hold 1-2 short sentences. Repo evidence checked: survey of existing F refs shows no shipped `####` section body exceeds ~3 short sentences. Default recommendation: the `Write` column is prose of any length; markdown renderers handle long cells acceptably. If a shipped ref lands with a multi-sentence cell and still reads well, ship it; if any ref looks cramped, add a compile diagnostic or a convention that caps at ~2 sentences and requires authors to shorten. Answer needed: confirm "no hard cap, rely on shipped-ref reviewer judgment" is acceptable.
- **Gap 4 — Enum-case guidance syntax inside `Write` cell for F6.** Plan's F6 target shows: `` `next_route` | enum | — | `seek_muse` → Muse (fresh inspiration). `ready_for_critic` → Poem Critic (judgment). `` — two cases inline with periods. Repo evidence checked: `examples/120_route_field_final_output_contract` has exactly this shape today rendered as per-enum `####` subsections. Default recommendation: inline case list in one cell using `` `case` → short guidance. `` per case, period-delimited. For ≥3 cases or >1 sentence per case, switch to bullet list inside the cell (markdown permits `<br>- case A<br>- case B` but it's ugly; alternative is to break out into a small separate code-fenced block under the table). Answer needed: lock the inline-period form as the F6 target; `deep-dive` confirms per-example.
- **Gap 5 — H compact vs. non-compact render modes.** Current H has two modes: compact one-line-bullet (`_should_compact_ordinary_output_contract` at outputs.py:285) and non-compact table. Plan's H1/H2/H3 targets all use a `Field | When | Write` table. Repo evidence checked: `examples/87_workflow_route_output_binding` uses the compact mode today (H3); `examples/105_...` uses non-compact (H1). Default recommendation: the new render replaces the table mode only; the compact-single-line-bullet mode (H3) stays as today for one-field simple bindings because the proposed H3 target (§0.6) is two bullets, not a table. Answer needed: confirm compact mode is H3's target shape (two bullets + next-owner key) and the new table shape applies only when the output has ≥2 fields OR any guards.
- **Gap 6 — Field Notes section (`explanation:`) inside F.** `fixtures_final_output.py:71-72` authors `explanation:` at the shape level which currently renders as `#### Field Notes`. Plan says "standalone `#### Field Notes` section" is dropped (§0.6 F rules line "Dropped: ... Standalone `#### Field Notes` section"). Repo evidence checked: shipped refs do occasionally render Field Notes (`examples/79:44-47`). Default recommendation: per-field entries inside `explanation:` fold into their matching row's `Write` cell; any shape-wide explanation (not field-specific) becomes a trailing standalone paragraph between the Example and the Trust Surface paragraph. Answer needed: confirm this split or propose alternative.
- **Gap 7 — Dotted-row indent in payload table.** Plan's J says "parent row uses `Type: object`, then one dotted row per child field (`` `failure_detail.blocked_gate` ``). Leading cell indented via `&nbsp;&nbsp;` for the dotted row only." Repo evidence checked: current `_build_output_schema_payload_rows` (validate/__init__.py:145-205) recurses with `field_prefix` but emits no indent — the dotted name carries the hierarchy visually via the `.` separator. Default recommendation: add `&nbsp;&nbsp;` prefix at the render layer when the row's `field_prefix` depth >= 1; do not change the payload-row tuple shape. Answer needed: confirm `&nbsp;&nbsp;` is the right choice (Markdown renderers vary; pipe-cell leading whitespace may be stripped). Alternative: use a visible leading `·` or `↳` or unicode space.
- **Gap 8 — Ref scope boundary enforcement.** Plan invariant says non-F/non-H refs must show zero byte drift (§0.4, §0.5). Research shows that refs containing F or H also contain many out-of-scope surfaces (review workflow, skills, typed input) in the same AGENTS.md. The zero-drift check must therefore be surface-local, not file-local. Default recommendation: the `implement` phase uses `make verify-examples` diff as the global signal and additionally runs a targeted `diff` pass that `grep`-extracts only the `## Final Output` and `### <OutputName>` sections from each changed ref and confirms all other sections are byte-identical to pre-change. Answer needed: confirm the targeted-diff approach is the right enforcement mechanism, or name a simpler one.

No other blocking gaps from research. The implementation plan can proceed once Gaps 1, 2, 5, 6, and 8 have explicit user-approved answers (3, 4, 7 have strong defaults that `deep-dive` can lock without re-asking).
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

Render pipeline files (all under `doctrine/`):

- `doctrine/_compiler/compile/final_output.py` — F-family authoritative renderer. `_compile_final_output_section` (lines 209–401) emits the metadata table, Payload Fields table, Example, review-response notes, extras, and Trust Surface as children of one `CompiledSection`.
- `doctrine/_compiler/compile/outputs.py` — H-family authoritative renderer plus shared Trust Surface helper. `_compile_output_decl` (lines 147–405), `_should_compact_ordinary_output_contract` (line 674), `_compile_compact_ordinary_output_support_items` (lines 710–770), `_compile_ordinary_output_support_items` (lines 772–808), `_compile_trust_surface_section` (lines 407–444).
- `doctrine/_compiler/compile/records.py` — record-item fallback emitter and guarded-section emitter. `_compile_record_item` (lines 161–326) dispatches scalars through `_compile_fallback_scalar` (lines 328–364); `GuardedOutputSection` / `GuardedOutputScalar` (lines 233–286) emit `#### <Key>` + `Show this only when {condition}.`
- `doctrine/_compiler/resolve/outputs.py` — shape scalar resolution. `_split_record_items(shape_decl.items, scalar_keys={"schema", "example_file"}, ...)` at line 1692–1696 decides which record items become shape scalars vs. extras. `"kind"` is not in `scalar_keys` here, so it leaks into the extras list and renders as `- Kind: Json Object`.
- `doctrine/_compiler/validate/__init__.py` — shared markdown helpers. `_pipe_table_lines` (lines 119–131), `_build_output_schema_payload_rows_for_object` (lines 145–205) recursing on JSON schema `properties` and returning 5-tuple rows `(field_name, type_label, required_on_wire, null_allowed, meaning)`, `_json_schema_type_label` (lines 207–268).
- `doctrine/emit_docs.py:379–396` — `_serialize_final_output_contract` writes `schema_profile` and `emitted_schema_relpath` into `final_output.contract.json`. This is the canonical home for those two runtime-only facts.
- `tests/test_emit_docs.py` — byte-level assertions for F. Line 204 asserts the `| Generated Schema | … |` metadata row; line 1274 asserts the `#### Payload Fields` heading.
- `doctrine/_diagnostic_smoke/fixtures_final_output.py`, `fixtures_reviews.py` — minimal F/H fixtures for `make verify-diagnostics`.
- Shipped proofs: `examples/**/ref/**/AGENTS.md` and `examples/**/build_ref/**/AGENTS.md`. F-family refs across `examples/79`, `83`, `90`, `91`, `104`, `105`, `106`, `120`, `121`, `136`, `138`. H-family refs across `examples/39`, `87`, `105`, `135`.

## 4.2 Control paths (runtime)

Authoring → resolve → compile → emit:

1. `.prompt` source is parsed into an AST (`doctrine/model.py`).
2. Resolve pass (`doctrine/_compiler/resolve/outputs.py`) turns `OutputDecl` + shape + schema references into resolved contracts. `FinalOutputJsonShapeSummary` is built here with a schema decl, payload rows, profile, example text, and `schema_ref` paths. The `_split_record_items` call at line 1694 decides which record items on the shape are "scalars" (promoted to named fields) vs. "extras" (rendered as bullets/sections later).
3. Compile pass (`doctrine/_compiler/compile/final_output.py`, `outputs.py`) produces the `CompiledSection` tree.

F render steps today (`_compile_final_output_section`, final_output.py:209–401):

1. Build `metadata_rows` list: `Message type`, `Format`, `Shape`, `Schema`, `Profile` (when schema has profile), `Generated Schema` (when generated), `Requirement`. (final_output.py:231–243)
2. Emit `> **Final answer contract**` callout + `Contract | Value` pipe table. (final_output.py:245–255)
3. When a JSON payload exists: emit `#### Payload Fields` 5-column table via `_pipe_table_lines` + `_build_output_schema_payload_rows_for_object`. (final_output.py:257–271)
4. Emit `#### Example` code block when `example_text` is present. (final_output.py:273–286)
5. Append review-response note lines. (final_output.py:288–292)
6. Attach `structure` section if present (schema-ref `output_decl.schema_ref`).
7. Call `_compile_output_support_items` for extras → emits `#### <Label>` sections or `- <Label>: <value>` bullets for every record item that was not consumed by `scalar_keys`. This is where `- Kind: Json Object` leaks (`kind` missing from the `scalar_keys` set).
8. Per-field authored `ReadableBlock` items on the output decl render as their own `#### <Title>` sections with the authored short body. These duplicate the Payload Fields table rows.
9. `_compile_trust_surface_section` emits `#### Trust Surface` + bullet list. Separately, a `- Standalone Read: …` bullet or `#### Read on Its Own` section is emitted when the output declares one. (outputs.py:407–444 plus inline code in final_output.py)

H render steps today (`_compile_output_decl`, outputs.py:147–405):

1. Build contract rows (Target, Shape, Requirement). Branch on `_should_compact_ordinary_output_contract` (outputs.py:285) — if only one scalar field and no guards, emit two bullets; otherwise emit a `Contract | Value` pipe table.
2. Emit authored output fields. In non-compact mode, each field is either a bullet (`- **<Title>**: <body>`) or a nested `#### <Title>` subsection when the field has sub-items (e.g., `#### Failure Detail` with `##### Blocked Gate` inside). Guards emit `#### <Key>` + `Show this only when <cond>.` via `GuardedOutputSection`.
3. Attach optional schema/structure block.
4. `_compile_trust_surface_section` emits `#### Trust Surface` + bullets (same helper as F).
5. Trailing `- Standalone Read: …` bullet when declared.

## 4.3 Object model + key abstractions

- `CompiledSection(title, body, children)` — tuple-flavored tree node. `body` holds strings and nested `CompiledSection` objects; `_pipe_table_lines` returns body-string tuples.
- `FinalOutputJsonShapeSummary` — resolve-time summary carrying `schema_decl`, `payload_rows` (5-tuple, schema-driven), `example_text`, `schema_profile`, `lowered_schema`.
- `OutputDecl` and `OutputShapeDecl` — AST-level contracts. `OutputDecl.items` holds the authored record items (per-field `ReadableBlock` bodies, `trust_surface:`, `standalone_read:` scalars, nested guarded sections).
- `RecordScalar`, `RecordObject`, `ReadableBlock`, `GuardedOutputSection`, `GuardedOutputScalar` — record-item node kinds that dispatch through `_compile_record_item`.
- `_pipe_table_lines(headers, rows)` — the single markdown pipe-table helper, already used by F's metadata table, F's Payload Fields table, and H's contract table.
- `_build_output_schema_payload_rows_for_object` — recursive JSON-schema traversal that emits one row per field (including nested `failure_detail.blocked_gate`) with the 5-tuple shape `(field, type, required_on_wire, null_allowed, meaning)`.
- `_split_record_items(items, *, scalar_keys, owner_label)` — partitions record items into `(scalars_dict, sections_list, extras_list)` based on `scalar_keys`. Extras later render as fallback bullets/sections.
- `_serialize_final_output_contract` — writes `final_output.contract.json`. Already carries `schema_profile` and `emitted_schema_relpath`; these are not agent-facing and do not need to re-surface in AGENTS.md.

## 4.4 Observability + failure behavior today

- Fail-loud on schema-load failures via `final_output_compile_error` and `output_compile_error`. Existing diagnostics catalog in `doctrine/diagnostics.py` (E-code families).
- `make verify-examples` recompiles every shipped manifest case and diffs every `ref/**` AGENTS.md byte-for-byte. Any render drift is caught at CI time.
- `make verify-diagnostics` recompiles the `_diagnostic_smoke` fixtures and asserts diagnostic output.
- No agent-facing "render shape" diagnostic exists today. The authored short body on a per-field `ReadableBlock` is silently duplicated (once in the Payload Fields table row as schema `note:`, once as its own `#### Field` section).

## 4.5 UI surfaces (ASCII mockups, if UI work)

Not applicable — AGENTS.md is the rendered surface. Before/after samples live in §0.6 (target shapes per surface family) and §5.5 (pilot target).
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

Same files as today. Net diffs:

- `doctrine/_compiler/compile/outputs.py` gains one new canonical render helper, `_compile_typed_output_table_section`, that owns the `Field | Type | Null | Write` table for F and the `Field | When | Write` table for H. Both F and H call it. This is the new canonical owner path.
- `doctrine/_compiler/compile/outputs.py` gains one new helper, `_render_trust_surface_paragraph(trust_surface_fields, standalone_read_sentence) -> tuple[str, ...]`, that returns the single trailing paragraph. Old `_compile_trust_surface_section` is deleted (its `#### Trust Surface` + bullet output is retired).
- `doctrine/_compiler/compile/final_output.py` `_compile_final_output_section` is rewritten to: emit one-sentence intro + `## Final Output — <Title>`, call `_compile_typed_output_table_section`, emit Example code block, emit optional shape-wide explanation paragraph, emit trailing Trust Surface paragraph. Metadata table, per-field `####` sections, Field Notes standalone section, and Trust Surface `CompiledSection` are all deleted.
- `doctrine/_compiler/compile/outputs.py` `_compile_output_decl` table-mode branch is rewritten to call `_compile_typed_output_table_section` with `when_column=True`. Bullet-list field rendering, nested `####` subsections, and standalone Trust Surface are deleted from this branch. The compact single-bullet mode branch (`_should_compact_ordinary_output_contract`) is preserved for simple single-field route bindings (H3).
- `doctrine/_compiler/compile/outputs.py` `_compile_ordinary_output_support_items` is gutted: it no longer emits `#### <Field>` sections for schema fields. Its job shrinks to any truly shape-wide extras (e.g., per-shape `explanation:` prose) which render as one trailing paragraph handed back to the caller.
- `doctrine/_compiler/validate/__init__.py` `_build_output_schema_payload_rows_for_object` returns 5-tuple rows `(field_path, indent_depth, type_label, null_allowed, meaning)` instead of today's 5-tuple `(field, type, required_on_wire, null_allowed, meaning)`. The render layer uses `indent_depth` to prepend `&nbsp;&nbsp;` on nested-field rows. `required_on_wire` is dropped from the tuple (the JSON schema already marks every field required on wire; the column it fed is deleted).
- `doctrine/_compiler/resolve/outputs.py:1694` adds `"kind"` to the `scalar_keys` set for the shape-decl `_split_record_items` call. This consumes `kind:` as a shape scalar and stops it leaking into extras.
- `doctrine/emit_docs.py:379–396` `_serialize_final_output_contract` is unchanged; it keeps owning `schema_profile` and `emitted_schema_relpath` for `final_output.contract.json`.
- `tests/test_emit_docs.py` drops the Generated-Schema row assertion (line 204) and updates or retains the Payload Fields heading assertion (line 1274) — the `#### Payload Fields` heading is replaced by an inline table under `## Final Output — <Title>`, so the assertion retargets to the new table header (`| Field | Type | Null | Write |`) or is deleted if a broader byte-level check already covers it.
- Shipped `examples/**/ref/**/AGENTS.md` and `examples/**/build_ref/**/AGENTS.md` that render F or H surfaces are regenerated and committed in the same change. Non-F/non-H refs show zero byte drift.
- `docs/LANGUAGE_REFERENCE.md:931` updates its one passing mention of Final Output rendering to match the new shape.
- `docs/EMIT_GUIDE.md` gains a short subsection describing the compact F/H render-shape contract (one table + one example + one trailing paragraph).

## 5.2 Control paths (future)

F (new `_compile_final_output_section`):

1. Compute `requirement_word` = `Required.` or `Optional.` from `output_decl.requirement`.
2. Emit `## Final Output — <shape_title>` as the section heading (one heading, no nested `### <Title>`). `shape_title` stays authored (e.g., `Acceptance Review Response`).
3. Emit one-sentence intro body: `<requirement_word> End the turn with one JSON message matching \`<schemas/…schema.json relpath>\`.` When the output is prose/no-schema, this path is NOT taken (prose-final-output is out of scope; its current render stays).
4. Emit any review-response note lines (the existing `_compile_final_output_review_response_note_lines` output is preserved; these are routing-semantics sentences, not per-field notes).
5. Call `_compile_typed_output_table_section(schema_rows, authored_overrides, include_null_column=True, include_when_column=False)`:
   - `schema_rows` come from `_build_output_schema_payload_rows_for_object` — now a 5-tuple `(field_path, indent_depth, type_label, null_allowed, meaning)`.
   - `authored_overrides` is a dict keyed by schema field path (flat key like `verdict` or dotted key like `failure_detail.blocked_gate`) built from resolve-time authored `ReadableBlock` items on the output decl. Value is the authored short body text.
   - `Write` cell per row = authored body if the key matches; else schema `meaning` (the JSON schema `description` / `note:`); else empty cell. Authored body wins when both exist (preserves authored intent per §0.5 invariant).
   - `Null` cell: `—` when `null_allowed` is `False`; `✓` when `True`.
   - Nested rows (`indent_depth > 0`) prepend `&nbsp;&nbsp;` × `indent_depth` to the `Field` cell.
6. Emit `#### Example` code block when `example_text` is present (heading kept because Example is a distinct artifact; body unchanged).
7. If the shape has an unmatched shape-wide `explanation:` / field-notes scalar, emit it as one prose paragraph before the Trust Surface paragraph.
8. Emit `_render_trust_surface_paragraph(trust_surface_fields, standalone_read_sentence)`:
   - With both: `Trust surface: \`Field A\`, \`Field B\`. <standalone-read sentence>`
   - With trust surface only: `Trust surface: \`Field A\`.`
   - With standalone read only: `<standalone-read sentence>`
   - With neither: no paragraph.
9. `Profile`, `Generated Schema`, `Message type`, `Format`, `Shape`, `Schema` rows are NOT rendered into AGENTS.md. The intro sentence (step 3) already names the schema relpath; the rest lives in `final_output.contract.json`.

H (new `_compile_output_decl` table-mode branch):

1. Emit `### <Output Title>` heading.
2. Emit one-sentence contract body: `<requirement_word> Target \`<target>\`; shape \`<shape-title>\`.`
3. Call `_compile_typed_output_table_section(authored_rows, schema_overrides=None, include_null_column=False, include_when_column=True)`:
   - `authored_rows` come from the output-decl authored items (`ReadableBlock` per field, with title and body). Nested items (sub-`ReadableBlock` or nested record) flatten into dotted rows with `&nbsp;&nbsp;` indent, mirroring the F behavior.
   - Guard conditions (`GuardedOutputSection` / `GuardedOutputScalar`) migrate into the `When` column. Conditions normalize to `always` (no guard) / `when <human-readable cond>` / `on <enum-value>`.
   - `Write` cell = authored body text for that field.
4. Emit `_render_trust_surface_paragraph` (same helper as F).

H compact-mode branch (preserved for single-field guard-free bindings like H3):

1. Emit `### <Output Title>` heading.
2. Emit `<requirement_word> Target \`<target>\`; shape \`<shape-title>\`.`
3. Emit the compact two-bullet render exactly as today (`- **Next Owner**: Review Lead (\`ReviewLead\`)` + `- **Route Summary**: …`). No table.
4. `_should_compact_ordinary_output_contract` logic stays as today; it selects between compact-bullet and new-table branches based on field count and guard presence.

Extras / shape-wide explanation (both F and H):

- Per-field authored bodies already feed the `Write` column; they never render a separate `####` section.
- Shape-wide `explanation:` (keyed on the shape decl itself, not on an individual field) renders as one trailing prose paragraph between Example (F only; H has no Example block) and the Trust Surface paragraph.
- Any other genuinely orphan record item that is not a known scalar key and not a field body raises a compile diagnostic (`E`-coded, catalog entry added in the implement phase) so authored content cannot silently vanish.

## 5.3 Object model + abstractions (future)

- `CompiledSection` unchanged. Trees stay tuple-flavored.
- `FinalOutputJsonShapeSummary` gains one optional field: `authored_field_bodies: Mapping[str, str]` (flat or dotted key → authored short body). Populated at resolve time by walking `output_decl.items` for `ReadableBlock` children. Default empty dict.
- `_build_output_schema_payload_rows_for_object` returns 5-tuple `(field_path_str, indent_depth, type_label, null_allowed, meaning)` where `field_path_str` is `"` + `"` + `.`-joined + `` ` `` (e.g., `` `verdict` ``, `` `failure_detail.blocked_gate` ``) and `indent_depth` is the recursion depth (0 for top-level, 1 for one level nested, etc.). `required_on_wire` is dropped from the tuple because the JSON schema already marks every field required-on-wire.
- New helper `_compile_typed_output_table_section(rows, *, include_null_column, include_when_column, authored_overrides) -> tuple[str, ...]` returns the rendered pipe-table body lines. Callers splice them into the surrounding section body (no standalone heading, no `CompiledSection` wrapper).
- New helper `_render_trust_surface_paragraph(trust_surface_fields, standalone_read_sentence) -> tuple[str, ...]` returns body lines (one paragraph or empty tuple).
- `_compile_trust_surface_section` is deleted. Every F and H call site migrates to `_render_trust_surface_paragraph`.
- Old helpers that become unused after the cutover (`_compile_output_support_items`'s per-field `####` branch in `final_output.py`, the nested-`####` branch inside `_compile_output_decl` non-compact mode, and the per-field `ReadableBlock` emitter that loops over the output decl's items) are deleted in the same change. No parallel paths left behind for archaeology.

## 5.4 Invariants and boundaries

Canonical owner paths:

- F table render: `_compile_typed_output_table_section` in `doctrine/_compiler/compile/outputs.py`.
- H table render: same helper.
- Trust Surface + Standalone Read render: `_render_trust_surface_paragraph` in `doctrine/_compiler/compile/outputs.py`.
- Schema → row traversal: `_build_output_schema_payload_rows_for_object` in `doctrine/_compiler/validate/__init__.py`. Sole owner of JSON-schema-to-rows mapping.
- Authored-body → row correlation: resolve time, keyed on record-item field-name == JSON-schema property name. Dotted keys for nested objects.
- Runtime-only metadata: `doctrine/emit_docs.py:379–396` owns `final_output.contract.json`. Agent-facing AGENTS.md does not re-emit `schema_profile` or `emitted_schema_relpath`.
- `kind:` resolution: `doctrine/_compiler/resolve/outputs.py:1694` `scalar_keys` set now includes `"kind"`. No other call site needs to change; the other `_split_record_items` call sites in that file (lines 1801, 2217, 2588, 2627) already pass appropriate scalar sets for their surfaces.

Enforceable boundaries:

- Single source of truth for F field list: the JSON schema. Authored `ReadableBlock` bodies merge by field-name match; non-matching authored bodies trigger a compile diagnostic (fail-loud) so authors cannot silently lose content. Shape-wide `explanation:` scalars render as a trailing paragraph (not a per-field section).
- Single source of truth for H field list: the authored `outputs:` contract. No schema-driven rows for H — authored items are canonical.
- No parallel render path: exactly one code path per surface family, no `compact_mode:` author knob, no `render_profile:` knob, hard cutover.
- Compatibility posture: **clean cutover** on F and H render bytes. Preservation signal: `make verify-examples` diff across shipped `ref/**` AGENTS.md. Every F/H ref must change to the new shape; every non-F/non-H ref must show zero bytes changed.
- Runtime fallbacks forbidden (`fallback_policy: forbidden` at doc level). The new helpers either render correctly or raise a compile error.
- Agent-backed capability-first rule: not applicable — this is a compiler render change; no prompts, tools, or model capabilities are in play.
- Plain-language bar (AGENTS.md §"Plain Language Hard Requirement") applies to every cell of authored prose that survives into the new `Write` column. Existing authored bodies are preserved verbatim; if any of them exceed the reading-level bar, that is separate authorial follow-up outside this plan.

Deletes required to keep the boundaries honest:

- `_compile_trust_surface_section` (outputs.py:407–444) — deleted. Replaced by `_render_trust_surface_paragraph`.
- Metadata-table building code in `_compile_final_output_section` (final_output.py:231–255) — deleted. No `Contract | Value` table.
- `#### Payload Fields` heading — deleted (the table renders inline under `## Final Output — <Title>`).
- Per-field `####` subsections emitted from `_compile_output_support_items` — deleted. Their content lands in the `Write` column.
- `#### Field Notes` standalone section — deleted. Shape-wide explanation becomes a trailing paragraph; per-field notes merge into the row's `Write` cell.
- Nested `##### <SubField>` subsections under H's `#### Failure Detail` — deleted. Dotted rows inside the `Field | When | Write` table replace them.
- `- Standalone Read: …` trailing bullet — deleted. Replaced by the collapsed Trust Surface paragraph.
- `- Kind: <ShapeKind>` orphan bullet — deleted (consumed as scalar at resolve time).

## 5.5 UI surfaces (ASCII mockups, if UI work)

Target shape (pilot — Curriculum Review Response):

```markdown
## Final Output — Curriculum Review Response

End the turn with one JSON message matching `schemas/curriculum_review_response.schema.json`.

| Field | Type | Null | Write |
| --- | --- | --- | --- |
| `verdict` | enum | — | `accept` or `changes_requested` |
| `reviewed_artifact` | string | — | `home:issue.md` (producer's handoff note on the issue ledger) |
| `analysis_performed` | string | — | 2–4 plain sentences: which gates passed, which failed, what the producer cited vs what primitives returned |
| `findings_first` | string | — | Main finding, then next move. Short and plain. |
| `current_artifact` | string | ✓ | `home:issue.md` when the producer's handoff still stands; else `null` |
| `next_owner` | string | ✓ | Producer name when routing back; else `null` |
| `failure_detail` | object | ✓ | `null` on accept; object below on changes_requested |
| &nbsp;&nbsp;`.blocked_gate` | string | ✓ | Name the blocker when review could not start |
| &nbsp;&nbsp;`.failing_gates` | string[] | ✓ | Exact failing gates, authored order |

```json
{...accept example...}
```

Trust surface: `current_artifact`. This review must stand alone — a later reader should know the verdict, the current artifact when one still stands, and the next move.
```
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| resolve | `doctrine/_compiler/resolve/outputs.py:1694` | `_split_record_items(shape_decl.items, scalar_keys={"schema", "example_file"}, ...)` | `kind:` leaks into extras and renders as `- Kind: Json Object` on every shipped JSON final output ref | Add `"kind"` to `scalar_keys` (single-line change) | Consumes `kind:` as a shape scalar so the render layer never sees it as an extras record item | `scalar_keys={"schema", "example_file", "kind"}` | Every F-family ref regenerates without the `- Kind` bullet; `tests/test_emit_docs.py` F-string assertions update |
| compile (F) | `doctrine/_compiler/compile/final_output.py:209–401` | `_compile_final_output_section` | Emits `> **Final answer contract**` callout + `Contract | Value` metadata table + `#### Payload Fields` + `#### Example` + per-field `####` sections + `#### Trust Surface` + `- Standalone Read:` bullet | Rewrite to emit `## Final Output — <Title>` + one-sentence intro + inline `Field | Type | Null | Write` table via `_compile_typed_output_table_section` + optional `#### Example` + optional shape-wide explanation paragraph + trailing Trust Surface paragraph | Collapse three parallel representations (metadata table, Payload Fields, per-field sections) into one render path; drop runtime-only metadata rows | Calls new helpers in `compile/outputs.py` | `tests/test_emit_docs.py:204` (Generated Schema row assertion) deletes; `tests/test_emit_docs.py:1274` (`#### Payload Fields` heading) retargets to inline table header or is deleted |
| compile (F metadata) | `doctrine/_compiler/compile/final_output.py:231–255` | `metadata_rows` build + `_pipe_table_lines(("Contract", "Value"), ...)` | Emits 5–7 row metadata table with Message type, Format, Shape, Schema, Profile, Generated Schema, Requirement | Delete entirely. Intro sentence carries requirement + schema relpath. Profile and Generated Schema stay in `final_output.contract.json` only | Runtime-only metadata is not agent-actionable; agent-facing AGENTS.md should only carry agent-actionable signals | No new code — deletion | F-ref byte diffs |
| compile (F extras) | `doctrine/_compiler/compile/final_output.py` | `_compile_output_support_items` per-field `####` branch | Each authored `ReadableBlock` on the shape or output decl renders as its own `#### <Title>` section | Delete the per-field `####` emit. Authored bodies flow into the `Write` column via resolve-time `authored_field_bodies` mapping | Eliminates field-row duplication (table row + per-field section) while preserving authored intent | `FinalOutputJsonShapeSummary.authored_field_bodies: Mapping[str, str]` populated at resolve time | F-ref byte diffs; `tests/test_emit_docs.py` per-field string assertions update or delete |
| compile (H) | `doctrine/_compiler/compile/outputs.py:147–405` | `_compile_output_decl` non-compact branch | Emits contract table + bullet-list fields + nested `#### Failure Detail` + `##### Blocked Gate` + `#### Trust Surface` + `- Standalone Read:` | Rewrite to emit `### <Title>` + one-sentence contract body + inline `Field | When | Write` table via `_compile_typed_output_table_section` + trailing Trust Surface paragraph | Same convergence as F: one render path, one table, one trailing paragraph | Calls new helpers | H-ref byte diffs; any `test_emit_docs.py` H assertions update |
| compile (H compact) | `doctrine/_compiler/compile/outputs.py:285,674,710–770` | `_should_compact_ordinary_output_contract` + `_compile_compact_ordinary_output_support_items` | Compact two-bullet render for single-field guard-free outputs (H3) | Preserve as today. Rule unchanged: compact mode when output has one authored field and no guards | Compact two-bullet render is already tight; the plan's H3 target matches it | Unchanged | H3 refs stay green |
| compile (H non-compact extras) | `doctrine/_compiler/compile/outputs.py:772–808` | `_compile_ordinary_output_support_items` | Renders per-field sections, nested subsections, trust surface, standalone read for non-compact H | Gut. Per-field content flows into the `Write` column; nested objects flow into dotted rows; trust surface + standalone read flow into the new paragraph helper. Any shape-wide explanation becomes one trailing paragraph | Same consolidation story | N/A | H-ref byte diffs |
| compile (shared Trust Surface) | `doctrine/_compiler/compile/outputs.py:407–444` | `_compile_trust_surface_section` | Returns `CompiledSection("Trust Surface", <bullet lines>)` | Delete. Replace with `_render_trust_surface_paragraph(trust_surface_fields, standalone_read_sentence) -> tuple[str, ...]` that returns the single trailing paragraph (or empty tuple) | Trust Surface + Read on Its Own collapse into one trailing paragraph (§0.6 K) | `def _render_trust_surface_paragraph(...) -> tuple[str, ...]` | F-ref and H-ref byte diffs |
| compile (new helper) | `doctrine/_compiler/compile/outputs.py` (new function) | `_compile_typed_output_table_section` | Does not exist today | New canonical table-render helper used by F and H. Takes schema-driven or authored-driven rows, supports optional `Null` column (F) and optional `When` column (H), handles dotted-row indent via `&nbsp;&nbsp;` × `indent_depth` | Canonical owner path for `Field | Type | Null | Write` and `Field | When | Write` tables; avoids parallel table-building code in F and H | `def _compile_typed_output_table_section(rows, *, include_null_column: bool, include_when_column: bool, authored_overrides: Mapping[str, str] \| None = None) -> CompiledSection` | Exercised by every F/H ref diff |
| compile (guards) | `doctrine/_compiler/compile/records.py:233–286` | `GuardedOutputSection` / `GuardedOutputScalar` | Emits `#### <Key>` + `Show this only when {condition}.` | Keep existing emit path for out-of-scope contexts (e.g., B review workflow). For F/H table contexts, the table helper consumes the guard condition directly into the `When` column (H) or an italic `*(when <cond>)*` prefix in the `Write` cell (F) without invoking the `####`-section emitter | Guards inside F/H tables must not promote to `####` subsections | Table helper accepts optional `guard_condition: str | None` per row | F/H-ref byte diffs for guarded-output examples (e.g., `examples/39`) |
| validate (payload rows) | `doctrine/_compiler/validate/__init__.py:145–205` | `_build_output_schema_payload_rows_for_object` | Returns 5-tuple `(field_path_backticked, type_label, "Yes/No", "Yes/No", meaning)` | Change to 5-tuple `(field_path_backticked, indent_depth, type_label, null_allowed_bool, meaning)`. Drop `required_on_wire` (JSON schema already marks every field required). Add `indent_depth` so render layer can emit `&nbsp;&nbsp;` prefix for nested rows | Single source of truth for row shape moves depth metadata out of the string | Tuple shape change | Any test that asserts the 5-tuple shape updates |
| validate (pipe tables) | `doctrine/_compiler/validate/__init__.py:119–131` | `_pipe_table_lines` | Unchanged | Unchanged | Already the right primitive | Unchanged | N/A |
| validate (type labels) | `doctrine/_compiler/validate/__init__.py:207–268` | `_json_schema_type_label` | Returns `string`, `enum`, `string[]`, `int`, `bool`, or `array<X>` long-form | Drop the long-form `array<...>` return path if any remaining; keep short-form (`string[]`, `int[]`, `MyObject[]`) | Plan's J convention requires short-form arrays only | Unchanged signature; string output shortens | Any F/H ref that renders arrays |
| emit (contract JSON) | `doctrine/emit_docs.py:379–396` | `_serialize_final_output_contract` | Already writes `schema_profile` and `emitted_schema_relpath` | Unchanged | Runtime metadata stays here; agent-facing render no longer duplicates it | Unchanged | `tests/test_emit_docs.py` contract-json assertions unchanged |
| tests | `tests/test_emit_docs.py:204` | `self.assertIn("| Generated Schema | ...", rendered)` | Asserts the old metadata-table row | Delete | Row no longer renders | Deletion |  |
| tests | `tests/test_emit_docs.py:1274` | `self.assertIn("#### Payload Fields", rendered)` | Asserts the old heading | Retarget to `"| Field | Type | Null | Write |"` inline table header OR delete (the shipped-ref byte diff already covers this) | Section heading deleted; inline table replaces it | Updated/deleted assertion | — |
| tests | `tests/test_emit_docs.py` (full survey) | All F- and H-byte assertions | Assert current metadata/payload/trust-surface shapes | Survey and update every F/H assertion to the new shape; prefer behavior-level presence/field-coverage checks over byte-equality where sensible | Test must reflect new render shape | New assertions | Re-run `pytest tests/test_emit_docs.py` |
| tests | `tests/test_emit_skill.py`, `tests/test_emit_flow.py` | F/H assertions (if any) | Unknown — not surveyed yet | Survey in implement phase; update any F/H-shape assertion | Change must not leave stale assertions | — | Re-run full tests |
| refs (F) | `examples/79_final_output_output_schema/ref/**/AGENTS.md`, `examples/83_review_final_output_output_schema/ref/**/AGENTS.md`, `examples/90_split_handoff_and_final_output_shared_route_semantics/ref/**/AGENTS.md`, `examples/91_handoff_routing_route_output_binding/ref/**/AGENTS.md`, `examples/104_review_final_output_output_schema_blocked_control_ready/ref/**/AGENTS.md`, `examples/105_review_split_final_output_output_schema_control_ready/ref/**/AGENTS.md`, `examples/106_review_split_final_output_output_schema_partial/ref/**/AGENTS.md`, `examples/120_route_field_final_output_contract/ref/**/AGENTS.md`, `examples/121_nullable_route_field_final_output_contract/ref/**/AGENTS.md`, `examples/136_review_shared_route_binding/ref/**/AGENTS.md`, `examples/138_output_shape_case_selector/ref/**/AGENTS.md` | Each F `## Final Output` section | Current bloated render | Regenerate to the compact F shape | Shipped-corpus proof of the change | N/A | `make verify-examples` diff check |
| refs (H) | `examples/39_guarded_output_sections/ref/**/AGENTS.md`, `examples/87_workflow_route_output_binding/ref/**/AGENTS.md`, `examples/105_.../ref/**/AGENTS.md` (non-final `outputs:`), `examples/135_review_carrier_structured/ref/**/AGENTS.md` | Each H `## Outputs` → `### <Name>` section | Current bullet-list / nested-subsection render | Regenerate to the compact H shape (`Field | When | Write` table, trailing paragraph) | Shipped-corpus proof | N/A | `make verify-examples` diff check |
| refs (build_ref) | `examples/**/build_ref/**/AGENTS.md` | Mirrored build_ref copies | Current bloated render | Regenerate alongside `ref/**` | Keep build_ref and ref byte-identical | N/A | `make verify-examples` diff check |
| refs (non-F/non-H) | All other `examples/**/ref/**/AGENTS.md` | B / C / D / E / G / I / M surfaces | Current (acceptable) render | **Zero byte drift.** If a non-F/non-H ref diffs, the render path leaked — narrow it before merge | Scope invariant (§0.4, §0.5) | N/A | Targeted section-local diff check (see Migration notes) |
| smoke fixtures | `doctrine/_diagnostic_smoke/fixtures_final_output.py`, `fixtures_reviews.py` | Minimal F/H fixtures | Current fixtures exercise bloated render | Update any fixture-body assertions to the new shape; fixture inputs themselves stay unchanged unless they encode an F-only bullet/section that disappears | Keep `make verify-diagnostics` green | N/A | `make verify-diagnostics` |
| docs | `docs/LANGUAGE_REFERENCE.md:931` | One passing mention of Final Output render | Current shape described | Update to name the compact shape | Keep docs and shipped render honest | N/A | Manual review |
| docs | `docs/EMIT_GUIDE.md` | No render-shape section today | Add one short subsection describing the compact F/H contract (one table + optional Example + one trailing paragraph) | Docs carry shipped truth | N/A | Manual review |
| docs | `docs/AGENT_IO_DESIGN_NOTES.md` | Non-blocking survey | Skim for F/H render-shape prose; update only if it quotes old shape | Avoid unnecessary docs churn | N/A | Manual review |

## 6.2 Migration notes

- **Canonical owner path / shared code path**: `_compile_typed_output_table_section` in `doctrine/_compiler/compile/outputs.py` owns all F and H table rendering. `_render_trust_surface_paragraph` in the same file owns Trust Surface + Standalone Read collapse. `_build_output_schema_payload_rows_for_object` in `doctrine/_compiler/validate/__init__.py` remains the sole schema-to-rows traversal.
- **Deprecated APIs**: none — all changes are internal to the compiler render pipeline. No author-visible grammar, schema, or contract-JSON shapes change.
- **Delete list (superseded paths)**:
  - `_compile_trust_surface_section` (outputs.py:407–444).
  - Metadata-table construction in `_compile_final_output_section` (final_output.py:231–255).
  - Per-field `####` emit branch in `_compile_output_support_items` (`final_output.py`).
  - Bullet-list fields + nested `####` subsections + trailing `- Standalone Read:` in `_compile_output_decl` non-compact branch (outputs.py).
  - Per-shape `#### Field Notes` standalone emit (from `_compile_output_support_items`).
  - Any dead helper left over after the above deletes.
  - `- Kind:` orphan bullet — eliminated structurally by the resolve-time `scalar_keys` fix.
- **Adjacent surfaces tied to the same contract family**:
  - Included now (moved together): all F and H refs listed in 6.1; `docs/EMIT_GUIDE.md`; `docs/LANGUAGE_REFERENCE.md:931`; smoke fixtures under `_diagnostic_smoke/`; `tests/test_emit_docs.py`; any F/H assertion in `tests/test_emit_skill.py` / `tests/test_emit_flow.py`; `final_output.contract.json` emission (unchanged but confirmed as canonical home for runtime metadata).
  - Explicitly out of scope: A (agent preamble), B (review workflow blocks), C (non-review workflow blocks), D1–D4 (typed input renders), E (skills block), G (prose Final Output), I (output-to-file with structure), M (Lens / Envelope Discipline). Rationale in §0.3.
  - Explicitly deferred: F7 target shape for `examples/138_output_shape_case_selector` — deep-dive confirms the invariant (one table, no per-case `####`) but the exact grouping of selector field + case columns is refined at implement time against the rendered output. Still included in the same change, not pushed to a later plan.
- **Compatibility posture / cutover plan**: **Clean cutover** on F and H render surfaces. No flag, no bridge, no `compact_mode:` author knob. Preservation signal: `make verify-examples` byte-diff across shipped refs. Downstream consumers that read `final_output.contract.json` or `schemas/*.schema.json` see no change (those artifacts stay byte-stable). Downstream consumers that read AGENTS.md (agents in the runtime loop) see the new compact shape — this is the intended product change.
- **Capability-replacing harnesses to delete or justify**: none. This is a compiler render change, not an agent-backed behavior change. The "capability-first" rule does not apply.
- **Live docs/comments/instructions to update or delete**:
  - `docs/LANGUAGE_REFERENCE.md:931` — update the Final Output render-shape mention.
  - `docs/EMIT_GUIDE.md` — add one short subsection describing the compact F/H shape.
  - Inline code comments at the new canonical helpers (high-leverage pattern propagation): one comment at the top of `_compile_typed_output_table_section` noting the invariant (one row per field, authored body wins in `Write`, guards flow to `When` column for H or italic prefix for F) and one at `_render_trust_surface_paragraph` noting the collapse rule. Keep it to one or two short comment lines each — the plain-language bar applies.
  - `docs/AGENT_IO_DESIGN_NOTES.md` — survey only; update if it quotes old F/H shape.
- **Behavior-preservation signals for refactors**: `make verify-examples` (primary); `make verify-diagnostics`; `tests/test_emit_docs.py` updated assertions; per-ref visual review of new AGENTS.md shape for at least one case per F/H variant in §0.6 (F1–F7, H1–H3); local compile-only recompile of the flagged psflows critic agent via `doctrine` to confirm the ~20-line target shape.
- **Ref scope boundary enforcement** (resolves Gap 8): `make verify-examples` provides the global byte diff. For the zero-byte-drift invariant on non-F/non-H surfaces inside a mixed ref (many AGENTS.md files mix F or H with review/skills/typed-input sections), the implement phase runs a targeted section-local diff: `grep`-extract every section that is not `## Final Output` / `### <Output Title>` under `## Outputs` / `## Outputs`-header itself, then diff that extracted slice against the pre-change baseline. If any non-F/non-H slice shows non-empty diff, the render path leaked scope and must be narrowed before merge. This is an ad-hoc check run before commit, not a new CI harness — it is a one-line `diff` invocation inside a bash loop over the changed refs.
- **Cleanup and migration notes**: delete the old helpers in the same commit that ships the new render. Do not leave dead code for archaeology (AGENTS.md "Git is the history for retired live truth surfaces"). Do not create a `docs/archive/` entry.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| ---- | ------------- | ---------------- | --------------------- | ------------------------------------- |
| F + H table render | `_compile_typed_output_table_section` (new) | One shared helper for `Field | Type | Null | Write` (F) and `Field | When | Write` (H) | Prevents F/H from silently diverging again; eliminates today's three parallel field representations per surface | **include** (core of this plan) |
| Trust Surface + Read on Its Own | `_render_trust_surface_paragraph` (new) | One trailing paragraph with `Trust surface: …` prefix | Replaces two parallel emit sites (`#### Trust Surface` + `- Standalone Read:` bullet) with one | **include** |
| Prose Final Output (G) | `_compile_final_output_section` prose branch | Same trailing-paragraph Trust Surface collapse as F/H | The new paragraph helper could serve G too, but G's current render is already acceptable and §0.3 excludes G from this change | **defer** — if a later plan retouches G, adopt `_render_trust_surface_paragraph` for consistency |
| Typed input renders (D1–D4) | `_compile_typed_input_*` helpers in `doctrine/_compiler/compile/` | Collapse metadata bullet stack into one metadata line | §0.3 excludes D; shipped refs with typed input show ~7 lines per input, which is not egregious | **exclude** — scope boundary; new plan if ever needed |
| Review workflow blocks (B) | `doctrine/_compiler/compile/` review-block renderer | Possible trailing-paragraph treatment | §0.3 excludes B | **exclude** |
| Non-review workflow blocks (C) | `doctrine/_compiler/compile/` workflow-block renderer | Possible trailing-paragraph treatment | §0.3 excludes C | **exclude** |
| Skills block (E) | Skills-block renderer | Possible table treatment | §0.3 excludes E; current render is structured and readable | **exclude** |
| Output-to-file with structure (I) | Output-to-file renderer | Shares `_compile_typed_output_table_section` pattern conceptually | §0.3 excludes I from this change | **defer** — obvious next-plan candidate if we revisit output-to-file |
| `_compile_record_item` fallback path | `compile/records.py` | Continue owning non-F/non-H fallback emit | No consolidation pressure; it still serves authored extras outside F/H | **exclude** (no change) |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the best sequence of coherent self-contained units, optimizing for phases that are fully understood, credibly testable, compliance-complete, and safe to build on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit and is explanatory only for modern docs. `Checklist (must all be done)` is the authoritative must-do list inside the phase. `Exit criteria (all required)` names the exhaustive concrete done conditions the audit must validate. Resolve adjacent-surface dispositions and compatibility posture before writing the checklist. Before a phase is valid, run an obligation sweep and move every required promise from architecture, call-site audit, migration notes, delete lists, verification commitments, docs/comments propagation, approved bridges, and required helper follow-through into `Checklist` or `Exit criteria`. The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims — the system must work correctly or fail loudly (delete superseded paths). If a bridge is explicitly approved, timebox it and include removal work; otherwise plan either clean cutover or preservation work directly. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

## Phase 1 — `- Kind:` orphan fix (resolve-time `scalar_keys` addition)

* Goal: stop the `- Kind: Json Object` bullet from rendering on every shipped JSON final-output AGENTS.md, as a single-line resolve-time fix that is independent from the larger F/H cutover.
* Work: `"kind"` is currently missing from the `scalar_keys` set at `doctrine/_compiler/resolve/outputs.py:1694`. Because of that, the shape's `kind:` record item falls through `_split_record_items` into the extras list, and the render layer emits it as a `- Kind: Json Object` fallback bullet (via `_compile_fallback_scalar` in `compile/records.py`). Adding `"kind"` to the set consumes it as a shape scalar and eliminates the leak structurally. The other `_split_record_items` call sites in `resolve/outputs.py` (lines 1801, 2217, 2588, 2627) are for different surfaces and stay unchanged. This fix lands before the F cutover so the F cutover's ref diff does not include an unrelated bullet deletion.
* Checklist (must all be done):
  - edit `doctrine/_compiler/resolve/outputs.py:1694`: `scalar_keys={"schema", "example_file", "kind"}`.
  - survey the other 4 `_split_record_items` call sites in `resolve/outputs.py` (lines 1801, 2217, 2588, 2627) and confirm each already includes the right scalar keys for its surface; do not change any of them.
  - run `make verify-examples` and regenerate every F-family `ref/**/AGENTS.md` and `build_ref/**/AGENTS.md` that previously rendered the `- Kind: Json Object` bullet. Affected F refs named in §6.1: `examples/79`, `83`, `90`, `91`, `104`, `105`, `106`, `120`, `121`, `136`, `138` (verify by grep before regen; full list is whatever carries the bullet today).
  - commit the regenerated refs alongside the one-line resolve fix.
  - if any F ref shows non-empty byte diff outside the single `- Kind: Json Object` bullet line, stop the phase and investigate before continuing — this phase owns only the kind leak and must not drift.
  - if any non-F ref shows any byte diff, stop the phase — the scope invariant is violated and the fix leaked beyond final-output shapes.
  - update any test in `tests/test_emit_docs.py`, `tests/test_emit_skill.py`, or `tests/test_emit_flow.py` that asserts on the `- Kind: Json Object` string (delete or invert the assertion so tests go green without the bullet).
* Verification (required proof):
  - `make verify-examples` green.
  - `make verify-diagnostics` green.
  - a targeted `diff` across changed F refs that confirms the only byte change per ref is the removal of the `- Kind: Json Object` line.
  - a targeted `diff` across all other refs that confirms zero byte drift.
* Docs/comments (propagation; only if needed): none. No live docs quote the `- Kind:` bullet; no comment propagation is required at this layer.
* Exit criteria (all required):
  - `doctrine/_compiler/resolve/outputs.py:1694` `scalar_keys` contains `"kind"`.
  - every shipped F-family `ref/**/AGENTS.md` and `build_ref/**/AGENTS.md` that previously contained the `- Kind: Json Object` bullet no longer contains it.
  - every shipped non-F ref shows zero byte drift from the pre-phase baseline.
  - `make verify-examples` and `make verify-diagnostics` are both green.
  - all test suites that reference the `- Kind: Json Object` string have been updated and pass.
* Rollback: revert the single-line change at `resolve/outputs.py:1694` and the associated ref regen commit. No shared code surface or public contract changes, so rollback is clean.

## Phase 2 — Add shared render helpers (`_compile_typed_output_table_section`, `_render_trust_surface_paragraph`)

* Goal: introduce the two new canonical render primitives F and H will share, with unit-test coverage only and no production call sites yet.
* Work: §5.3 names two new helpers. `_compile_typed_output_table_section(rows, *, include_null_column, include_when_column, authored_overrides)` owns every `Field | Type | Null | Write` (F) and `Field | When | Write` (H) pipe-table in the compiler. `_render_trust_surface_paragraph(trust_surface_fields, standalone_read_sentence)` owns the single collapsed trailing paragraph that replaces today's `#### Trust Surface` bullet list plus the `- Standalone Read:` bullet / `#### Read on Its Own` section. Both live in `doctrine/_compiler/compile/outputs.py`. Adding them as pure additions in this phase (no call-site change) lets Phases 3 and 4 consume them atomically without interleaving new-helper construction with old-code deletion.
* Checklist (must all be done):
  - add `_compile_typed_output_table_section` to `doctrine/_compiler/compile/outputs.py`. Signature: `(rows: tuple[tuple[str, int, str, bool | None, str], ...], *, include_null_column: bool, include_when_column: bool, authored_overrides: Mapping[str, str] | None = None) -> tuple[str, ...]`. Returns the rendered pipe-table body lines. Handles dotted-row indent via `"&nbsp;&nbsp;" * indent_depth` on the `Field` cell when `indent_depth > 0`. `Null` column value is `"—"` when `null_allowed is False`, `"✓"` when `null_allowed is True`; omitted when `include_null_column=False`. `When` column value is the guard condition string when `include_when_column=True`; omitted otherwise. `Write` cell value is `authored_overrides.get(field_key)` when a match exists and is non-empty; else the row's default `meaning` value; else empty string.
  - add `_render_trust_surface_paragraph` to `doctrine/_compiler/compile/outputs.py`. Signature: `(trust_surface_fields: tuple[str, ...], standalone_read_sentence: str | None) -> tuple[str, ...]`. Returns one-paragraph body lines or empty tuple. Format: `Trust surface: \`Field A\`, \`Field B\`. <standalone-read sentence>` when both present; `Trust surface: \`Field A\`.` when only surface; `<standalone-read sentence>` when only standalone-read; empty tuple when neither.
  - add one short explanatory comment above each helper stating the invariant it owns (one line each, plain-language; do not write a docstring paragraph).
  - add unit tests to `tests/test_emit_docs.py` (or a new `tests/test_typed_output_render_helpers.py` if `test_emit_docs.py` is too crowded). Test cases: F-style row (null_column on, when_column off) with flat fields, F-style row with dotted nested fields, H-style row (when_column on, null_column off), authored_overrides precedence (override wins over meaning), empty trust surface paragraph, both-fields trust surface paragraph, standalone-read-only paragraph.
  - confirm no existing caller references the new helpers (grep for the two names; expect zero hits outside the new tests).
* Verification (required proof):
  - new unit tests pass.
  - `make verify-examples` green (helpers unused, no ref drift).
  - `make verify-diagnostics` green.
* Docs/comments (propagation; only if needed): the one-line comment at each new helper is required. No live doc updates yet — `docs/EMIT_GUIDE.md` updates land in Phase 5.
* Exit criteria (all required):
  - `_compile_typed_output_table_section` and `_render_trust_surface_paragraph` exist in `doctrine/_compiler/compile/outputs.py` with the signatures and semantics above.
  - the new unit tests cover: F-style row shape, H-style row shape, dotted-row indent, authored_overrides precedence, all four trust-surface-paragraph cases.
  - `make verify-examples` and `make verify-diagnostics` are both green.
  - zero byte drift on all shipped `ref/**` and `build_ref/**`.
* Rollback: delete the two helpers and their unit tests. Phase is additive and rollback is clean.

## Phase 3 — F render cutover (Final Output — JSON schema-backed)

* Goal: rewrite `_compile_final_output_section` to emit the compact `## Final Output — <Title>` shape defined in §0.6 F1–F7 and §5.2, delete every superseded F render branch, regenerate every F-family shipped ref, and update every F test assertion in the same commit.
* Work: this phase lands the full F cutover atomically. It changes the schema payload-rows tuple shape in `doctrine/_compiler/validate/__init__.py:145–205` from `(field_path, type_label, required_on_wire_str, null_allowed_str, meaning)` to `(field_path, indent_depth, type_label, null_allowed_bool, meaning)`; it adds `FinalOutputJsonShapeSummary.authored_field_bodies: Mapping[str, str]` and populates it at resolve time by walking `output_decl.items` for `ReadableBlock` children keyed on record-item field name; it adds a compile diagnostic for authored `ReadableBlock` keys that do not match any schema field (fail-loud per §5.4); it rewrites `_compile_final_output_section` (`doctrine/_compiler/compile/final_output.py:209–401`) to call the new helpers and emit the compact shape; it deletes the old metadata-table code (final_output.py:231–255), the `#### Payload Fields` heading, the per-field `####` emit branch inside `_compile_output_support_items`, the `#### Trust Surface` `CompiledSection` branch, and the trailing `- Standalone Read:` bullet; and it regenerates all 11 F-family example directories listed in §6.1 (`examples/79`, `83`, `90`, `91`, `104`, `105`, `106`, `120`, `121`, `136`, `138`). Authored `ReadableBlock.body` wins over schema `note:` in the `Write` cell when both exist. Shape-wide `explanation:` (if present, scoped to the shape decl rather than a field) renders as one trailing prose paragraph between the Example and the Trust Surface paragraph. F6 enum-case guidance lives inline in the route field's `Write` cell using `` `case` → short guidance. `` form, period-delimited. F7 (`examples/138_output_shape_case_selector`) target shape is one table with the selector field + case columns; the exact column grouping is refined against the rendered output during this phase and the exit criterion holds only when the F7 pilot reads as compact.
* Checklist (must all be done):
  - change `_build_output_schema_payload_rows_for_object` in `doctrine/_compiler/validate/__init__.py` to return 5-tuples `(field_path_backticked: str, indent_depth: int, type_label: str, null_allowed: bool, meaning: str)`. Drop `required_on_wire` from the tuple. The recursion's `field_prefix` depth becomes `indent_depth` (0 at top level, 1 for one level nested, etc.).
  - update `_json_schema_type_label` to drop any long-form `array<X>` return path and emit only short-form `string[]`, `int[]`, `MyObject[]` (§0.6 J).
  - add `authored_field_bodies: Mapping[str, str]` to `FinalOutputJsonShapeSummary`. Populate it in the resolve pass that constructs the summary (`doctrine/_compiler/resolve/outputs.py`) by walking the output decl's authored items and mapping record-item field-name → `ReadableBlock.body` (or equivalent short-body scalar). Dotted keys for nested authored items (e.g., `failure_detail.blocked_gate`).
  - add a new compile diagnostic (assign the next free E-code in `doctrine/diagnostics.py`) raised at resolve time when an authored `ReadableBlock` key does not match any JSON schema field. Message: names the authored key, names the schema title, and lists the available schema field names. Add the diagnostic to `docs/COMPILER_ERRORS.md`.
  - after wiring the diagnostic, run `make verify-examples` once against the untouched shipped corpus. If the diagnostic fires on any shipped F-family example (i.e., a shipped authored `ReadableBlock` key does not map to a JSON schema field), treat each mismatch as an authoring bug in that example: either rename the authored key to match the schema field name, or add the field to the schema, or split the authored body into a shape-wide `explanation:` paragraph. Do not relax the diagnostic, and do not skip the mismatch. Record any shipped-example authoring fix in the Phase 3 worklog entry.
  - rewrite `_compile_final_output_section` in `doctrine/_compiler/compile/final_output.py:209–401` to emit:
    1. `## Final Output — <shape_title>` heading (one heading; no nested `### <Title>`).
    2. one-sentence intro body: `<Required|Optional>. End the turn with one JSON message matching \`<schemas/....schema.json>\`.`
    3. review-response note lines via the existing `_compile_final_output_review_response_note_lines` (preserve its output unchanged).
    4. the pipe table via `_compile_typed_output_table_section(rows=..., include_null_column=True, include_when_column=False, authored_overrides=summary.authored_field_bodies)`.
    5. optional `#### Example` code block when `example_text` is present (heading preserved; body unchanged).
    6. optional shape-wide explanation paragraph when a shape-scoped `explanation:` or field-notes scalar is present but does not match a specific schema field.
    7. trailing Trust Surface paragraph via `_render_trust_surface_paragraph(...)`.
  - delete the metadata-table build in final_output.py:231–255 entirely (rows for Message type, Format, Shape, Schema, Profile, Generated Schema, Requirement). Do not keep any of those rows. The intro sentence (step 2) carries the requirement word and the schema relpath.
  - delete the `#### Payload Fields` `CompiledSection` wrapper (final_output.py:257–271). The new table renders inline under `## Final Output — <Title>`.
  - delete the per-field `####` emit branch inside `_compile_output_support_items` for schema fields. Authored bodies flow through `authored_field_bodies` into the `Write` cell instead.
  - delete the `#### Field Notes` standalone section emission path. Shape-wide explanation renders via step 6 above.
  - delete `#### Trust Surface` / `#### Read on Its Own` `CompiledSection` emits and the trailing `- Standalone Read:` bullet.
  - delete any now-dead helpers left over after the above deletions. Do not leave dead paths for archaeology.
  - run `make verify-examples` and regenerate every F-family `ref/**/AGENTS.md` and `build_ref/**/AGENTS.md` in the 11 example directories named above. For F7 (`examples/138_output_shape_case_selector`), confirm the rendered shape is one table covering selector + case fields; if the rendered output is not compact, iterate the helper or the row-building logic until it is before accepting the exit.
  - for each changed F ref, confirm the diff shows only `## Final Output` / `### <Title>` section changes. Non-F sections (review workflow, typed input, skills, etc.) within the same AGENTS.md file must show zero byte drift — scope invariant (§0.5).
  - update `tests/test_emit_docs.py:204` (delete the `Generated Schema` row assertion).
  - update `tests/test_emit_docs.py:1274` — either retarget to the new `| Field | Type | Null | Write |` inline header or delete (if shipped-ref byte diff already covers it).
  - survey every other F-related assertion in `tests/test_emit_docs.py` and update to the new shape.
  - survey `tests/test_emit_skill.py` and `tests/test_emit_flow.py` for F assertions; update any found.
  - add at least one unit test to `tests/test_emit_docs.py` (or the helper tests file) that exercises `FinalOutputJsonShapeSummary.authored_field_bodies` population and the mismatch diagnostic.
* Verification (required proof):
  - all unit tests pass: `uv run --locked python -m unittest tests.test_emit_docs` and any sibling emit-test modules touched.
  - `make verify-examples` green.
  - `make verify-diagnostics` green (the new diagnostic has test coverage via the smoke fixtures or a dedicated unit test).
  - targeted section-local `diff` loop across all changed F refs: extract every section that is not `## Final Output <...>`, confirm zero byte drift on the extracted slices.
  - targeted byte diff across all non-F refs confirms zero byte drift.
  - manual pilot review: `examples/83_review_final_output_output_schema/ref/acceptance_review_json_demo/AGENTS.md` reads as compact (one `## Final Output — <Title>` heading, one inline `Field | Type | Null | Write` table, one `#### Example` block, one trailing Trust Surface paragraph, no metadata table, no `- Kind:` bullet, no per-field `####` sections, no `#### Trust Surface`, no `- Standalone Read:` bullet).
  - manual pilot review: `examples/138_output_shape_case_selector` renders its case-selector shape as one table, not as per-case `####` subsections.
* Docs/comments (propagation; only if needed):
  - one short code comment at the top of the rewritten `_compile_final_output_section` naming the canonical render contract (one line, plain language). Live doc propagation lands in Phase 5.
  - add the new compile-diagnostic E-code entry to `docs/COMPILER_ERRORS.md` (this is a required live-doc reality-sync obligation tied to this phase, not deferred to Phase 5).
* Exit criteria (all required):
  - `_compile_final_output_section` in `doctrine/_compiler/compile/final_output.py` emits the compact F shape per §0.6 F1–F7 and §5.2, and no longer emits the metadata table, per-field `####` sections, `#### Field Notes`, `#### Trust Surface`, or trailing `- Standalone Read:` bullet.
  - `_build_output_schema_payload_rows_for_object` returns the new 5-tuple shape.
  - `FinalOutputJsonShapeSummary.authored_field_bodies` is populated at resolve time and consumed by `_compile_final_output_section` via the new helper.
  - a new fail-loud compile diagnostic exists for unmatched authored `ReadableBlock` keys, documented in `docs/COMPILER_ERRORS.md`.
  - every shipped F-family ref in `examples/79`, `83`, `90`, `91`, `104`, `105`, `106`, `120`, `121`, `136`, `138` has been regenerated to the compact shape and committed.
  - `examples/120_route_field_final_output_contract` F6 ref renders the route enum with per-case guidance inline in the route field's `Write` cell using the `` `case` → short guidance. `` form; no per-case `####` subsections remain in that ref.
  - `examples/121_nullable_route_field_final_output_contract` F5 ref renders nullable-route guidance inline in the route field's `Write` cell; no per-route `####` subsections remain in that ref.
  - `examples/138_output_shape_case_selector` F7 ref renders selector + case-specific fields as one pipe table (no per-case `####` or `#####` subsections remain in that ref).
  - no non-F section inside any regenerated F ref shows byte drift (section-local diff check passes).
  - no non-F ref shows byte drift.
  - `make verify-examples` and `make verify-diagnostics` are green.
  - all F-related assertions in `tests/test_emit_docs.py`, `tests/test_emit_skill.py`, and `tests/test_emit_flow.py` pass.
  - no dead helper code remains from the superseded F render path.
* Rollback: revert the Phase 3 commit. Because the resolve-time tuple shape change, helper-consumption change, and ref regen land atomically, a single revert restores the pre-phase state. Downstream Phases 4–6 have not shipped yet, so revert does not strand any consumer.

## Phase 4 — H render cutover (non-final structured `output` carrier)

* Goal: rewrite `_compile_output_decl`'s non-compact branch to use the shared helpers, preserve the compact single-bullet mode for H3, regenerate every H-family shipped ref, and delete every superseded H render branch.
* Work: this phase mirrors Phase 3 for the H surface. `_compile_output_decl` (outputs.py:147–405) today branches on `_should_compact_ordinary_output_contract` (outputs.py:285) between a compact two-bullet render and a non-compact render that emits a contract table, bullet-list fields, nested `#### <Field>` / `##### <SubField>` subsections, `#### Trust Surface`, and a trailing `- Standalone Read:` bullet. The compact branch stays as today (H3's target shape per §0.6 is exactly two bullets). The non-compact branch is rewritten to emit `### <Title>` + one-sentence contract body + inline `Field | When | Write` table via `_compile_typed_output_table_section(rows=..., include_null_column=False, include_when_column=True, ...)` + trailing Trust Surface paragraph via `_render_trust_surface_paragraph`. Authored `ReadableBlock` fields become rows; guards migrate into the `When` column (`always` / `when <cond>` / `on <value>`); nested objects flatten into dotted rows with `&nbsp;&nbsp;` indent. `_compile_ordinary_output_support_items` (outputs.py:772–808) is gutted: it no longer emits per-field sections or nested subsections; it keeps only the shape-wide explanation paragraph emission (mirrors Phase 3 shape-wide explanation treatment). `_compile_trust_surface_section` (outputs.py:407–444) — used by both F and H today — is deleted; every call site migrates to `_render_trust_surface_paragraph` (F already migrated in Phase 3; H migrates here).
* Checklist (must all be done):
  - rewrite the non-compact branch of `_compile_output_decl` in `doctrine/_compiler/compile/outputs.py:147–405` to emit:
    1. `### <output_title>` heading.
    2. one-sentence contract body: `<Required|Optional>. Target \`<target>\`; shape \`<shape-title>\`.`
    3. the pipe table via `_compile_typed_output_table_section(rows=authored_rows, include_null_column=False, include_when_column=True, authored_overrides=None)`. Rows come from walking the output-decl authored items (`ReadableBlock` per field). Nested items flatten into dotted rows. Guard conditions (`GuardedOutputSection` / `GuardedOutputScalar`) map to the `When` column string.
    4. trailing Trust Surface paragraph via `_render_trust_surface_paragraph(...)`.
  - preserve the compact single-bullet branch (outputs.py:285 `_should_compact_ordinary_output_contract` logic unchanged). Compact mode still applies for single-authored-field outputs with no guards (H3).
  - gut `_compile_ordinary_output_support_items` (outputs.py:772–808): remove the per-field section emit, the nested `####` / `#####` subsection emit, and the trust-surface/standalone-read handling. Keep only the shape-wide explanation paragraph path; factor it out if it is cleaner to collapse into the main renderer.
  - delete `_compile_trust_surface_section` (outputs.py:407–444) entirely. All F and H call sites now use `_render_trust_surface_paragraph`.
  - in `doctrine/_compiler/compile/records.py`, adjust the `GuardedOutputSection` / `GuardedOutputScalar` handling so that when these items are rendered inside an H table (via the new helper), the guard condition flows into the `When` column rather than emitting `#### <Key>` + `Show this only when {condition}.`. Preserve the existing `####`-section emit path for non-F/non-H contexts (e.g., review workflow B — out of scope, must not drift).
  - run `make verify-examples` and regenerate every H-family `ref/**/AGENTS.md` and `build_ref/**/AGENTS.md` in the example directories named in §6.1: `examples/39_guarded_output_sections` (both demo refs), `examples/87_workflow_route_output_binding`, `examples/105_review_split_final_output_output_schema_control_ready`, `examples/135_review_carrier_structured`.
  - for each changed H ref, confirm the diff shows only `## Outputs` / `### <Title>` section changes. Non-H sections in the same AGENTS.md file show zero byte drift.
  - confirm every F ref from Phase 3 still renders correctly (Phase 4 removes `_compile_trust_surface_section` which Phase 3 already migrated off — no regression possible, but verify with targeted diff).
  - survey `tests/test_emit_docs.py`, `tests/test_emit_skill.py`, `tests/test_emit_flow.py` for H-related assertions and update to the new shape.
  - add a unit test covering the guard → `When`-column migration (e.g., a `GuardedOutputScalar` with condition `present(next_owner)` renders as a row with `When` cell = `when present` and no standalone `#### Next Owner` section).
  - delete any dead helper code left over from the superseded H render path.
* Verification (required proof):
  - all unit tests pass.
  - `make verify-examples` green.
  - `make verify-diagnostics` green.
  - targeted section-local `diff` across every changed H ref confirms zero byte drift on non-H sections.
  - full repo-wide byte-diff across all refs (F + H + everything else) confirms the only remaining drifted sections are the F + H target sections per §0.6.
  - manual pilot review: `examples/105_.../AGENTS.md` shows the non-final `## Outputs` → `### Acceptance Review Comment` block as one inline `Field | When | Write` table plus a trailing Trust Surface paragraph, with no bullet-list fields, no `#### Failure Detail`, no `##### Blocked Gate`, no `#### Trust Surface`, and no `- Standalone Read:` bullet.
  - manual pilot review: `examples/87_workflow_route_output_binding/ref/.../AGENTS.md` still renders the compact two-bullet H3 shape for its single-field route binding (compact mode preserved).
  - manual pilot review: `examples/39_guarded_output_sections` renders guard conditions in the `When` column rather than as promoted `#### <Field>` sections.
* Docs/comments (propagation; only if needed): one short code comment at the top of the rewritten non-compact branch naming the invariant (one line). Live doc propagation lands in Phase 5.
* Exit criteria (all required):
  - the non-compact branch of `_compile_output_decl` emits `### <Title>` + one-sentence contract + inline `Field | When | Write` table + trailing Trust Surface paragraph, and no longer emits bullet-list fields, nested `####` / `#####` subsections, `#### Trust Surface`, or `- Standalone Read:` bullet.
  - the compact single-bullet branch of `_compile_output_decl` is unchanged and still applies for single-authored-field-no-guards outputs (H3).
  - `_compile_trust_surface_section` no longer exists in the codebase.
  - every shipped H-family ref (`examples/39`, `87`, `105`, `135`) has been regenerated to the compact shape and committed.
  - no non-H section inside any regenerated H ref shows byte drift.
  - no F ref drifted further from its Phase 3 state.
  - no non-F / non-H ref shows any byte drift from the Phase 3 baseline.
  - `make verify-examples` and `make verify-diagnostics` are green.
  - all H-related assertions in `tests/test_emit_docs.py`, `tests/test_emit_skill.py`, and `tests/test_emit_flow.py` pass.
  - the new guard → `When`-column unit test passes.
  - no dead helper code remains from the superseded H render path or the retired `_compile_trust_surface_section` helper.
* Rollback: revert the Phase 4 commit. Phase 3 (F cutover) remains shipped and working. A revert that restores `_compile_trust_surface_section` must restore it for H only; F already calls `_render_trust_surface_paragraph`.

## Phase 5 — Docs sync (`docs/EMIT_GUIDE.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md` survey)

* Goal: bring every live doc that quotes the old F / H render shape into alignment with the shipped compact shape, so the doc map stays honest after the cutover.
* Work: the canonical docs surface most authors and reviewers read to understand doctrine's emit contract is `docs/EMIT_GUIDE.md`. It does not yet describe the compact F/H shape (§3.2 confirmed no existing render-shape quotes for F/H). `docs/LANGUAGE_REFERENCE.md:931` has one passing mention of Final Output rendering that still describes the old shape. `docs/AGENT_IO_DESIGN_NOTES.md` was not surveyed during research; this phase surveys it and updates only if it quotes the old shape. No other docs are expected to need updates based on the research grounding (§3.2).
* Checklist (must all be done):
  - add a new short subsection to `docs/EMIT_GUIDE.md` describing the compact F/H render contract: one `## Final Output — <Title>` heading (F) or `### <Title>` heading (H), one-sentence intro/contract line, one inline pipe table (`Field | Type | Null | Write` for F; `Field | When | Write` for H), optional `#### Example` code block (F), optional shape-wide explanation paragraph, one trailing Trust Surface paragraph. Keep the subsection compact (plain-language bar).
  - update the passing F render-shape mention at `docs/LANGUAGE_REFERENCE.md:931` to match the compact shape.
  - survey `docs/AGENT_IO_DESIGN_NOTES.md` for F/H render-shape prose. If any paragraph quotes the old metadata-table shape, per-field `####` subsections, `#### Trust Surface`, or `- Standalone Read:` bullet, update it. If no quotes found, record "no update needed" in the Phase 5 worklog entry and move on.
  - grep the rest of `docs/` for any other live prose that quotes specific old-shape strings (`"Contract | Value"`, `"#### Payload Fields"`, `"#### Trust Surface"`, `"- Kind:"`, `"#### Field Notes"`). Update or delete any stale quote found. Do not add new doc surfaces for this plan.
  - do not touch `docs/VERSIONING.md` in this phase unless the release classification changes (handled in Phase 6).
  - all doc updates pass the 7th-grade plain-language bar (AGENTS.md §"Plain Language Hard Requirement").
* Verification (required proof):
  - `make verify-examples` green (docs changes should not affect emit output, but confirm).
  - manual review by the plan owner confirms the new `docs/EMIT_GUIDE.md` subsection reads plainly and matches the shipped render shape.
  - grep confirms no remaining stale-shape quotes in `docs/`.
* Docs/comments (propagation; only if needed): this entire phase IS the live-docs propagation obligation. No separate doc/comment work needed outside the phase checklist.
* Exit criteria (all required):
  - `docs/EMIT_GUIDE.md` has a new short subsection describing the compact F/H render contract.
  - `docs/LANGUAGE_REFERENCE.md:931` reflects the compact F shape.
  - `docs/AGENT_IO_DESIGN_NOTES.md` has either been updated to reflect the compact shape or confirmed to require no update (recorded in the worklog).
  - no live doc in `docs/` still quotes the old-shape strings (`"Contract | Value"`, `"#### Payload Fields"`, `"#### Trust Surface"`, `"- Kind:"`, `"#### Field Notes"`, `"- Standalone Read:"`).
  - all doc prose added or edited in this phase meets the plain-language bar.
  - `make verify-examples` and `make verify-diagnostics` remain green.
* Rollback: revert the Phase 5 commit. Docs go back to their pre-phase state. Shipped code and refs from Phases 1–4 are unaffected.

## Phase 6 — Release pass (`CHANGELOG.md`, version bump, full verify matrix, psflows spot check)

* Goal: cut the `4.1.x` patch release that ships the compact F/H render. Run the full verify matrix. Spot-check the flagged real-world agent via a local doctrine recompile so the user-visible impact is proven against the original motivating case.
* Work: §9.1 says this ships as a `4.1.x` patch — internal, language 4.1 unchanged, render surface only. AGENTS.md requires `CHANGELOG.md` and `docs/VERSIONING.md` updates when release classification or public compatibility changes. This render change IS a public compatibility change (agents reading shipped AGENTS.md see a different shape), so the changelog entry must describe it honestly. `docs/VERSIONING.md` only needs an update if the release policy or classification rules change — they do not here, so the update is a verify-and-confirm step rather than an edit. Finalization QA: full `make verify-examples`, `make verify-diagnostics`, `make verify-package`, `uv run --locked python -m unittest tests.test_release_flow`. Spot check: recompile `psflows/flows/curriculum_scope/prompts/track_scope_critic.prompt` locally via doctrine and confirm the Final Output block now renders at roughly ~20 lines — this is the motivating case from §2.2 and its success is a finalization acceptance signal, not a CI gate (psflows stays read-only from doctrine).
* Checklist (must all be done):
  - add a `CHANGELOG.md` entry describing the compact F/H render shape, the removed metadata rows (`Profile`, `Generated Schema`), the removed per-field `####` sections, the removed `- Kind:` orphan bullet, and the removed `#### Trust Surface` / `- Standalone Read:` bullets. Plain-language; keep it short.
  - confirm the release classification in `docs/VERSIONING.md` still matches this change's shape (patch-level public-compat tightening, no grammar, no schema, no breaking API). If `docs/VERSIONING.md` already covers this case, record "no update needed" in the worklog; otherwise update `docs/VERSIONING.md` to reflect the classification.
  - bump the package version to `4.1.x` per `docs/VERSIONING.md`'s patch-release policy (look up the current version and bump the patch digit).
  - run `make verify-examples`; confirm green.
  - run `make verify-diagnostics`; confirm green.
  - run `make verify-package`; confirm green.
  - run `uv run --locked python -m unittest tests.test_release_flow`; confirm green.
  - recompile `psflows/flows/curriculum_scope/prompts/track_scope_critic.prompt` via a local doctrine invocation (read-only against psflows; write output to a local scratch path). Confirm the rendered Final Output block is roughly ~20 lines and matches the F-family compact shape. Record the before/after line counts in the phase worklog.
  - recompile `examples/83_review_final_output_output_schema` and confirm the pilot AGENTS.md reads at ~40 lines (§0.1 target).
  - commit the `CHANGELOG.md` entry and any `docs/VERSIONING.md` update together with the version bump.
* Verification (required proof):
  - `make verify-examples` green.
  - `make verify-diagnostics` green.
  - `make verify-package` green.
  - `uv run --locked python -m unittest tests.test_release_flow` green.
  - psflows critic recompile shows the Final Output block at ~20 lines (motivating case from §0.1 / §2.2).
  - `examples/83` pilot reads at ~40 lines.
  - repo-wide byte diff since the pre-plan baseline: only F and H sections changed across shipped refs; zero drift on non-F/non-H surfaces.
* Docs/comments (propagation; only if needed):
  - `CHANGELOG.md` entry is required.
  - `docs/VERSIONING.md` is updated only if the release classification needs to change (expected: no edit, verify-and-confirm only).
* Exit criteria (all required):
  - `CHANGELOG.md` contains a plain-language entry describing the compact F/H render.
  - `docs/VERSIONING.md` has been verified against this change's classification (and updated if needed).
  - the package version has been bumped to `4.1.x` per patch-release policy.
  - all four verify targets (`make verify-examples`, `make verify-diagnostics`, `make verify-package`, `tests.test_release_flow`) are green.
  - the psflows `track_scope_critic` critic recompile shows a ~20-line Final Output block, recorded in the worklog alongside the pre-change ~90-line baseline.
  - the `examples/83` pilot reads at ~40 lines.
  - the repo-wide byte diff confirms the scope invariant: F and H sections changed; non-F/non-H surfaces have zero drift.
* Rollback: revert the Phase 6 commit (version bump + CHANGELOG entry) and, if needed, `docs/VERSIONING.md` update. Phases 1–5 remain shipped; the code change still works but has not been cut as a release.

<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- `tests/test_emit_docs.py` updates to the compact shape. Existing assertions stay behavior-level (section presence, field coverage), not byte-equal of old render.

## 8.2 Integration tests (flows)

- `make verify-examples` is the primary preservation signal. Every shipped manifest-backed example re-renders its `ref/**/AGENTS.md` compactly, and the ref diffs are the proof of shape change.
- `make verify-diagnostics` stays green (no diagnostic code touched).
- `make verify-package` stays green.

## 8.3 E2E / device tests (realistic)

- Local recompile of `psflows/flows/curriculum_scope/prompts/track_scope_critic.prompt` through doctrine shows the compact Final Output block. psflows stays read-only from doctrine — this is a compile-only spot check, not a cross-repo commit.

Principle line: prefer the existing `verify-examples` corpus and ref diffs over any new harness. No grep gates, no absence checks, no doc-inventory tests.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

Released as a `4.1.x` patch (internal, language 4.1 unchanged). This is surface-level render; no grammar bump, no schema bump, no workflow language bump. Every consumer that renders AGENTS.md through doctrine gets the new shape on next compile.

## 9.2 Telemetry changes

None. No runtime metrics, no new diagnostics.

## 9.3 Operational runbook

None. Standard `uv sync` + `npm ci` + `make verify-examples` flow.

# 10) Decision Log (append-only)

## 2026-04-19 - Plan bootstrapped

- **Context**: User flagged `psflows/flows/curriculum_scope/build/agents/track_scope_critic/AGENTS.md` Final Output block as ~90 lines of duplicated representations. Demonstrated a ~18-line compact shape covering the same information.
- **Options**: (a) Add an author-visible `compact:` knob per agent. (b) Hard cutover of the default render. (c) Leave it and only fix the orphan `- Kind` bullet.
- **Decision**: Hard cutover of the default render. One shape, no opt-in knob, all shipped refs regenerate in the same commit.
- **Consequences**: Every existing `examples/**/ref/**/AGENTS.md` diff must be reviewed as correct on the new render. Downstream consumers (psflows and similar) see a shape change on next recompile — this is expected and wanted.
- **Follow-ups**: Run `research` to lock the full render-path inventory before deeper planning.

## 2026-04-19 - Scope narrowed to F + H + Kind-leak; North Star confirmed

- **Context**: Initial §0.6 inventory proposed target shapes for 14 surface families (A–N). On review, most of those surfaces were already reasonable — `- Kind:` bullet leak excepted, the real bloat was concentrated in F (Final Output — JSON schema-backed) and H (structured non-final `output` carrier). Proposing changes to B / C / D / E / G / I would have been churn diffs on shipped refs nobody complained about.
- **Options**: (a) Keep the exhaustive 14-family plan and re-scope at `phase-plan`. (b) Narrow now at the North Star to F + H + Kind-leak + shared J/K/L renderers and make out-of-scope explicit in §0.3.
- **Decision**: Narrow now (option b). §0.2 lists the in-scope surfaces; §0.3 explicitly names A / B / C / D / E / G / I / M as out of scope with one-line rationale each. §0.5 adds a hard invariant: any phase proposing to touch out-of-scope surfaces must be rejected at `phase-plan`. §0.4 adds a hard check: non-F/non-H refs must show zero byte drift.
- **Consequences**: The real-world psflows critic case still lands. `examples/83` pilot still lands. Shipped-ref churn stays bounded to surfaces where the render is actually wrong. Future cosmetic tightening of B / C / D / E / G / I is a separate plan if anyone ever asks for it.
- **Follow-ups**: North Star confirmed and locked. User to run `research` next.

## 2026-04-19 - North Star status: active

- Status flipped `draft → active`. §0.6 is the authoritative target-shape spec for F, H, J, K, L. Further stages (`research`, `deep-dive`, `phase-plan`) may sharpen wording for in-scope surfaces; they may not widen scope without a new Decision Log entry reopening §0.3.

## 2026-04-19 - Deep-dive: Sections 4 / 5 / 6 locked; 8 research decision gaps resolved

- **Context**: `research` surfaced 8 decision gaps (§3.3 Gaps 1–8) before `phase-plan` could run. Deep-dive reviewed each gap against repo truth + §0.5 invariants + §0.6 target shapes and locked each resolution in Sections 4, 5, and 6 of this doc.
- **Options considered**: for each gap, either resolve from repo truth + approved intent (deep-dive authority per `shared-doctrine.md`) or ask the user. Every gap resolved from repo truth; none required a new user question, because §0.5 invariants and §0.6 targets already constrained the choice.
- **Decisions (authoritative)**:
  1. **Gap 1 — Render-path convergence strategy.** Chose **option (A)**: introduce one new canonical helper `_compile_typed_output_table_section` in `doctrine/_compiler/compile/outputs.py` that F and H both call. Keep F's primary owner in `final_output.py` and H's in `outputs.py`. Rationale: §0.5 invariant "No new parallel render path" is about render shape, not function count; (A) satisfies it while keeping F/H call-site structure familiar. (B) would pull F into `outputs.py` and make that file dual-purpose — scope creep. (C) is explicitly ruled out. Encoded in §5.1, §5.3, §6.1, §6.2.
  2. **Gap 2 — Authored field-body correlation.** Correlate by **record-item field-name == JSON schema property name** (today's authoring already uses this correspondence; no new author surface). Authored `ReadableBlock.body` wins in the `Write` cell when both an authored body and a schema `note:` exist; schema `note:` fills in when no authored body exists; empty cell when neither exists. Non-matching authored bodies (keys that don't appear in the schema) raise a compile diagnostic at resolve time so authored intent cannot silently vanish. Encoded in §5.2, §5.3, §5.4.
  3. **Gap 3 — `Write` column length cap.** **No hard cap.** A length-cap diagnostic would be repo-policing, not a real boundary (forbidden by `shared-doctrine.md` "enforceable principles"). Markdown tables render multi-sentence cells acceptably. Plain-language bar (AGENTS.md §"Plain Language Hard Requirement") already constrains shipped cell prose. Encoded in §5.4.
  4. **Gap 4 — F6 enum-case guidance syntax.** **Inline in `Write` cell** with `` `case` → short guidance. `` form, period-delimited between cases. When any single case requires more than one short sentence, that authoring is pushed back to the author before merge (plain-language bar). Encoded in §0.6 F6 and §5.2.
  5. **Gap 5 — H compact vs. non-compact modes.** Compact two-bullet mode (H3) **preserved for single authored field with no guards**; new `Field | When | Write` table mode applies when output has ≥2 authored fields OR any guards. `_should_compact_ordinary_output_contract` logic stays as today. Encoded in §5.1, §5.2, §6.1.
  6. **Gap 6 — Field Notes / shape-wide `explanation:`.** Per-field `explanation:` entries that match a schema field fold into the matching row's `Write` cell (same mechanism as authored `ReadableBlock.body`). Shape-wide `explanation:` (scoped to the shape decl, not a specific field) renders as **one trailing prose paragraph between the Example and the Trust Surface paragraph**. Encoded in §5.2.
  7. **Gap 7 — Dotted-row indent.** `&nbsp;&nbsp;` × `indent_depth` prefix on nested-field rows (standard Markdown pipe-table practice; GitHub and most static renderers preserve it). Encoded in §5.2 and §5.3 via `_build_output_schema_payload_rows_for_object` tuple change.
  8. **Gap 8 — Ref scope boundary enforcement.** Primary signal: `make verify-examples` byte diff. Ad-hoc check: targeted section-local `diff` loop that extracts non-F/non-H slices from each changed ref and confirms zero byte drift on them. Not a new CI harness; one `diff` invocation inside a bash loop run before commit in the implement phase. Encoded in §6.2.
- **Consequences**:
  - Section 3.3 gaps are resolved; the plan is one step closer to decision-complete. `phase-plan` may proceed without re-asking the user on any of Gaps 1–8.
  - Section 5 now specifies the full future architecture: one shared table helper + one trust-surface paragraph helper + 4-tuple schema payload rows with indent depth + resolve-time `authored_field_bodies` mapping + `kind:` as a shape scalar + runtime metadata confined to `final_output.contract.json`.
  - Section 6 change map is exhaustive within the F + H + shared-renderer scope. It explicitly lists the 11 F-family example refs and 4 H-family example refs that regenerate, and it restates the zero-byte-drift invariant for non-F/non-H refs.
  - Pattern Consolidation Sweep confirms the scope boundary: G (prose Final Output), D (typed inputs), B/C (review / workflow blocks), E (skills), I (output-to-file) stay **excluded or deferred**. Adopting the new helpers in those surfaces is a separate future plan.
- **Follow-ups**:
  - `phase-plan` may run next. Section 7 must sequence the work so foundational primitives land first (resolve-time `scalar_keys` fix + tuple-shape change + new helpers) and shipped-ref regeneration lands in distinct coherent phases (F first, then H, then docs updates, with an end-of-frontier `make verify-examples` + targeted-diff gate).
  - Any phase that proposes to touch out-of-scope surfaces (A / B / C / D / E / G / I / M) must be rejected at `phase-plan` — §0.5 invariant and §0.3 boundary still hold.

## 2026-04-19 - Phase plan verified; two sharpenings applied

- **Context**: `phase-plan` pass against the existing canonical Section 7. Section 7 was already decision-complete with 6 foundational-first phases (Kind fix → shared helpers → F cutover → H cutover → docs sync → release). Obligation sweep across §0.4, §0.5, §6.1, §6.2 found every required promise represented in a `Checklist` or `Exit criteria`. Two small consistency gaps surfaced.
- **Options considered**: widen the plan, split existing phases, or apply narrow sharpening edits. The existing decomposition already isolates coherent self-contained units with clean rollback per phase; splitting Phase 3 further would require a transitional tuple-shape shim (forbidden).
- **Decisions**:
  1. Fixed §5.3 return-type drift for `_compile_typed_output_table_section`. Authoritative signature is `(rows, *, include_null_column, include_when_column, authored_overrides) -> tuple[str, ...]` (not `CompiledSection`). Callers splice body lines into the surrounding section. Phase 2 checklist was already correct; §5.3 now matches.
  2. Added a Phase 3 checklist item naming the risk that the new authored-body-key diagnostic may fire on shipped F-family examples once it is wired. Resolution: treat each surfaced mismatch as a shipped-example authoring bug, fix the key or the schema or split the body, do not relax the diagnostic.
- **Consequences**: Plan is implementation-ready. No phase boundaries changed; no sequencing changed. Phase 3 is slightly larger by one checklist item. Section 7 remains the one authoritative execution checklist.
- **Follow-ups**: User may run `implement-loop` against this doc to cut the full frontier (Phases 1 → 6) in order.
