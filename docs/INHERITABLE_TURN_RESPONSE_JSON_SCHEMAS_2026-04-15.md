---
title: "Doctrine - Inheritable Turn Response JSON Schemas - Architecture Plan"
date: 2026-04-15
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/AUTHORING_PATTERNS.md
  - examples/79_final_output_output_schema/prompts/AGENTS.prompt
  - examples/107_output_inheritance_basic/prompts/AGENTS.prompt
  - examples/110_final_output_inherited_output/prompts/AGENTS.prompt
  - ../psflows/stdlib/rally/prompts/rally/turn_results.prompt
  - https://developers.openai.com/api/docs/guides/structured-outputs
  - https://developers.openai.com/api/docs/guides/function-calling
  - https://json-schema.org/specification
  - https://python-jsonschema.readthedocs.io/en/stable/validate/
  - https://jsonschema-specifications.readthedocs.io/en/stable/api/
---

# TL;DR

## Outcome

Doctrine should ship one clean structured-output story: `output schema` owns the payload fields and the payload example, both are first-class parsed Doctrine data, the compiler lowers and validates that one source of truth, the human-facing contract renders from it, and emit produces the real lowered OpenAI-compatible JSON Schema as a canonically named generated artifact. There should be no legacy `json schema` declaration path, no stray `.example.json` support files, and no fake summary sidecar such as `AGENTS.contract.json`.

## Problem

The full approved implementation frontier now passes. Earlier audits reopened Phase 5 for public-truth leftovers and proof drift, but the fresh audit found those gaps fixed across the root instructions, shipped examples, diagnostics, package proof, editor proof, emitted schema artifact, file validator, and recorded live OpenAI proof.

## Approach

Keep the hard cutover. Treat the implementation as code-complete across the approved ordered frontier, with no weakened requirements, no hidden scope cuts, no legacy structured-output fallback, and no reopened code phases.

## Plan

1. Record the clean authoritative implementation audit in this plan.
2. Keep the implementation proof attached to the worklog.
3. Hand broader docs cleanup, plan/worklog retirement, and any evergreen-doc consolidation to `arch-docs`.

## Non-negotiables

- The most elegant user-facing authoring surface and the best rendered final-output contract are the primary success bar for this change.
- Scope discipline exists to protect that outcome, not to force a smaller but clumsier design when the elegant design is still within the approved ask.
- No second long-term authoring path for inheritable structured turn-response schemas.
- No reverse-compatibility holdovers for this feature unless the user explicitly asks for them later.
- No dead structured-output compatibility fields, labels, declarations, example files, or example names left behind on the shipped path without an explicit new approval.
- No silent drift between the Doctrine source, the lowered JSON Schema, and the rendered final-output contract.
- No syntax that fights Doctrine's current typed, keyed, inheritance-first style.
- No examples or lowering rules that are valid generic JSON Schema but invalid OpenAI strict structured outputs.
- Examples for structured final outputs are parsed first-class Doctrine citizens, not support files.
- `AGENTS.contract.json` does not survive this plan, but the real lowered schema artifact does.
- The emitted machine-readable artifact must be the exact lowered schema that passed Python validation, not a Doctrine-specific summary format.
- The generated schema artifact must have one canonical path shape so consumers can find it without heuristics.
- The plan must prove both the machine side and the human side:
  - child schemas can extend parent turn results cleanly
  - emitted Markdown stays easy to read and pleasant to scan
  - the shipped repo no longer explains this feature in legacy `json schema` terms
  - the generated schema artifact is valid Draft 2020-12, validates the authored example instance, passes the built-in Python OpenAI-subset validator, and is accepted by a real OpenAI structured-output submission path

<!-- arch_skill:block:implementation_audit:start -->
# Implementation Audit (authoritative)
Date: 2026-04-15
Verdict (code): COMPLETE
Manual QA: complete (non-blocking; worklog records live OpenAI proof on the repaired emitted schema with repo-local `.env`)

## Code blockers (why code is not done)
- None. Fresh audit found the full approved frontier code-complete across the structured-schema compiler path, emitted schema artifact, file validator, live-proof runner, public docs, examples, diagnostics, package smoke, and editor proof.
- No execution-side rewrite weakened requirements, scope, acceptance criteria, or phase obligations to hide unfinished work. The earlier Phase 5 residual gaps are fixed rather than narrowed away.

## Reopened phases (false-complete fixes)
- None.

## Missing items (code gaps; evidence-anchored; no tables)
- None. Evidence anchors:
  - Generated schema emission:
    - `doctrine/_compiler/compile/final_output.py:121`
    - `doctrine/_compiler/compile/final_output.py:152`
    - `doctrine/emit_docs.py:182`
    - `doctrine/emit_docs.py:190`
  - File validator and live OpenAI proof path:
    - `doctrine/validate_output_schema.py:18`
    - `doctrine/validate_output_schema.py:21`
    - `doctrine/prove_output_schema_openai.py:18`
    - `doctrine/prove_output_schema_openai.py:25`
  - Phase 5 public-truth fixes:
    - `AGENTS.md:59`
    - `examples/79_final_output_output_schema/prompts/INVALID_MISSING_EXAMPLE.prompt:32`
    - `examples/79_final_output_output_schema/cases.toml:118`
  - Shipped generated artifact:
    - `examples/79_final_output_output_schema/build_ref/repo_status_agent/schemas/repo_status_final_response.schema.json`
  - Worklog proof:
    - `docs/INHERITABLE_TURN_RESPONSE_JSON_SCHEMAS_2026-04-15_WORKLOG.md`
- Fresh audit commands:
  - `uv run --locked python -m doctrine.verify_corpus --manifest examples/79_final_output_output_schema/cases.toml`
  - `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_review_imported_outputs tests.test_route_output_semantics tests.test_emit_flow`
  - `make verify-examples`
  - `make verify-diagnostics`
  - `make verify-package`
  - `cd editors/vscode && make`
- Full-frontier audit result:
  - Evidence anchors:
    - `doctrine/grammars/doctrine.lark`
    - `doctrine/_parser/io.py`
    - `doctrine/_model/io.py`
    - `doctrine/_compiler/resolve/output_schemas.py`
    - `doctrine/_compiler/resolve/outputs.py`
    - `doctrine/_compiler/output_schema_validation.py`
    - `doctrine/_compiler/compile/final_output.py`
    - `doctrine/emit_docs.py`
    - `doctrine/validate_output_schema.py`
    - `doctrine/prove_output_schema_openai.py`
    - `examples/79_final_output_output_schema`
    - `editors/vscode`
  - Plan expects:
    - One Doctrine-authored `output schema` source of truth.
    - Parsed schema-owned examples validated against the lowered schema.
    - No live raw `json schema` declaration path, `.example.json` support-file path, fake `AGENTS.contract.json` artifact, stale public `_json_schema` naming, or unsupported OpenAI shape.
    - Emitted `schemas/<output-slug>.schema.json` files are the exact lowered schema object that compile validated.
    - Repo-owned file validation, package proof, diagnostics proof, editor proof, and recorded live OpenAI acceptance all stay aligned.
  - Code reality:
    - The compiler parses, resolves, lowers, validates, renders, and emits from `output schema` truth.
    - Structured examples use schema-owned `example:` blocks, and legacy `example_file` now fails loud instead of acting as a fallback.
    - The old fake sidecar artifact source is gone; no checked-in `AGENTS.contract.json` or `.example.json` support files remain.
    - Public example directories, root instructions, docs, release notes, diagnostics, and VS Code surfaces use the approved `*_output_schema` / `output schema` story.
    - The emitted schema file exists in the checked-in proof tree, the validator reads that file, and the live-proof runner submits that same file shape to the official OpenAI Responses API.
  - Fix:
    - None.

## Non-blocking follow-ups (manual QA / screenshots / human verification)
- Broader docs cleanup, evergreen consolidation, and plan/worklog retirement belong to `arch-docs` after this clean code verdict. They are not code-completeness blockers.
<!-- arch_skill:block:implementation_audit:end -->

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-15
external_research_grounding: done 2026-04-15
deep_dive_pass_2: done 2026-04-15
recommended_flow: deep dive -> external research grounding -> deep dive again -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

Doctrine can express structured `JsonObject` output schemas in Doctrine syntax, inherit and extend them across parent and child declarations, lower them to the documented OpenAI Structured Outputs strict subset, validate the result, and do it with an authoring surface and rendered final-output contract that feel elegant, first-class, and worth using.

This claim is false if any of these remain true after implementation:

- `RallyTurnResult` still depends on a raw JSON schema file as its real field source of truth
- a child turn result cannot add fields through Doctrine inheritance
- the authored surface technically works but still feels bolted on, noisy, or less elegant than the raw goal the user asked for
- the lowered JSON Schema fails OpenAI strict-subset rules, Draft 2020-12 metaschema validation, or both
- authored optional fields lower into missing keys instead of the documented required-plus-null pattern
- the final rendered Markdown contract becomes harder to read than the current shipped surface or reads like schema exhaust instead of a first-class contract
- the emitted build output still omits the actual lowered schema artifact
- the emitted artifact is any Doctrine-specific summary JSON instead of the real lowered OpenAI-compatible schema
- the emitted artifact path is heuristic or ambiguous instead of canonical
- the validator limits do not match the current official OpenAI structured-output contract
- the repo cannot validate the emitted schema file through a built-in Python validator surface
- the repo cannot show one real OpenAI acceptance proof for that emitted schema file

## 0.2 In scope

- The primary success target is the best user-facing authoring experience and the best rendered final-output contract we can deliver while still honoring the documented OpenAI schema rules and one canonical compiler path.
- A Doctrine-native declaration for structured output schemas used by `output shape` when `kind: JsonObject`.
- Inheritance and extension rules for those structured schemas.
- Lowering from Doctrine-authored structured schemas into fully formed JSON Schema objects that match the documented OpenAI Structured Outputs strict subset.
- Full documented feature coverage for that subset on current non-fine-tuned structured-output models, including:
  - `string`, `number`, `boolean`, `integer`, `object`, `array`, `enum`, and nested `anyOf`
  - `required`, `additionalProperties: false`, and root-object rules
  - nullable optionals through required-plus-null lowering
  - `$defs`, `$ref`, and recursive schemas
  - supported string, number, and array constraints
  - documented size and nesting limits
  - preserved key order from authored schema to emitted schema
- Validation of emitted schemas with a Python JSON Schema library and official metaschemas.
- Validation of parsed example instances against the lowered JSON Schema.
- Emission of the exact lowered schema as a generated JSON artifact for structured final outputs.
- One canonical emitted path shape for that artifact so downstream consumers can locate it without heuristics.
- A built-in Python validator command or module that validates emitted schema files with `jsonschema` plus Doctrine's OpenAI-subset rules.
- One real OpenAI acceptance proof path for the lowered schema, using the official OpenAI API.
- Compiler changes needed to route `final_output` JSON handling through the new Doctrine-authored schema path.
- Migration of Rally-style turn-result authoring from raw JSON schema support files to the new Doctrine source.
- Migration of final-output examples from external `.example.json` files to parsed schema-owned Doctrine source.
- Removal of the remaining legacy structured-output compatibility surfaces:
  - fake summary sidecars such as `AGENTS.contract.json`
  - stale `_json_schema` example and doc naming on this feature
- Example-rich planning and implementation proof, including:
  - base plus child turn-result schemas
  - nested object and array shapes
  - parsed schema-owned example values
  - rendered Markdown contracts that show best-case readability
  - lowered JSON Schema examples

Allowed architectural convergence scope:

- Widen internal convergence work when that is what it takes to keep the user-facing authoring surface elegant and the rendered contract excellent.
- Add new typed model, parser, resolver, validator, and compiler paths for structured-output schema declarations.
- Reuse Doctrine's existing inheritance, keyed-block, and fail-loud patterns where they fit.
- Refactor and delete the current `json schema` support path, `final_output` JSON summary path, and emitted contract baggage so there is one canonical structured-schema pipeline.
- Update examples, docs, and diagnostics so shipped truth stays aligned.
- Rename public proof and machine labels where the old names are now legacy noise.

## 0.3 Out of scope

- Ordinary markdown-only outputs that do not use `JsonObject`.
- A compatibility shim that keeps raw JSON files as equal first-class authoring truth for inheritable turn-result schemas.
- A compatibility shim that keeps `.example.json` support files or `AGENTS.contract.json` alive on the structured final-output path.
- Omitting the emitted schema contract from build output once the compiler already knows the exact lowered schema.
- Emitting any Doctrine-specific summary JSON as the canonical machine contract for this feature.
- New host runtime behavior in `psflows` outside the schema shape it consumes.
- A broad redesign of review semantics, route semantics, or ordinary output rendering.
- Unrelated legacy surfaces elsewhere in Doctrine that do not belong to the structured final-output path for this feature.
- Keywords that OpenAI explicitly marks unsupported for strict structured outputs, such as `allOf`, `not`, `dependentRequired`, `dependentSchemas`, `if`, `then`, and `else`.
- Non-strict fallback behavior.
- JSON Schema features that OpenAI docs do not clearly guarantee for the strict subset.

## 0.4 Definition of done (acceptance evidence)

- The shipped surface feels elegant to author and elegant to read. It should look like Doctrine, not like pasted JSON with Doctrine punctuation.
- Doctrine ships one structured-schema authoring surface that can express the Rally turn-result family without raw JSON schema files as authoring truth.
- A parent structured turn result can be extended by a child through Doctrine inheritance.
- The compiler lowers the Doctrine source to JSON Schema that passes validation against the official Draft 2020-12 metaschema and Doctrine's explicit OpenAI strict-subset checks.
- The compiler validates the parsed example instance against that same lowered schema with an external validator.
- Emit writes the exact lowered schema object to one canonical generated path: `schemas/<output-slug>.schema.json`.
- The repo has a built-in Python validator surface that can bless that emitted file directly.
- The reopened pass is not done until one real OpenAI structured-output submission accepts the generated schema.
- The lowered output covers the full documented OpenAI strict subset this plan targets, with proof for:
  - nullable optionals
  - nested `anyOf`
  - `$defs` / `$ref`
  - recursion
  - string, number, and array restrictions
  - limit checks and fail-loud diagnostics
- The final-output docs render clearly for both base and child schemas, with strong Markdown presentation for:
  - metadata
  - payload fields
  - field notes
  - examples
- The final rendered contract reads like a human-facing doctrine artifact first and a machine-schema explanation second.
- The structured final-output path no longer carries dead `schema_file` state and no longer calls structured final-output mode `json_schema`.
- The live compiler no longer parses, exports, indexes, or resolves `json schema` declarations as part of this feature path.
- Final-output examples are schema-owned parsed Doctrine data, not external support files.
- `AGENTS.contract.json` is gone.
- The shipped corpus proves at least these example classes:
  - Rally base turn result
  - Rally child turn result with added fields
  - route-aware turn result
  - review-driven structured final output
  - nested structured object output
- Shipped examples, smoke checks, docs, and release notes no longer use stale `_json_schema` naming for this feature family.
- The plan itself includes concrete syntax, lowered JSON Schema, and rendered Markdown examples for those cases.
- The repo proof shows that current OpenAI-documented limits are enforced with current values, including the documented enum-count limit.

Behavior-preservation evidence:

- Existing non-`JsonObject` outputs still compile as before.
- Existing output inheritance rules still behave the same on current output fields and attachments.
- Existing `final_output` route and review semantics stay green except where the new structured-schema source intentionally replaces raw JSON inputs.

## 0.5 Key invariants (fix immediately if violated)

- Prefer the most elegant user-facing authoring and render outcome that still preserves one source of truth, one lowering path, and the documented OpenAI contract.
- One Doctrine-authored source of truth for inheritable structured turn-response schemas.
- No silent fallback from Doctrine-authored schema source back to raw JSON files.
- No new parallel inheritance system just for structured turn results.
- No dead compatibility field, format label, declaration kind, support file, or example name left behind on the shipped structured-output path.
- No fake summary sidecar survives on this feature out of inertia.
- The real lowered schema artifact must survive and be emitted from the same validated object the compiler already trusts.
- The emitted schema artifact path must be canonical and stable.
- Fail loud when a lowered schema is invalid, incomplete, or outside the supported OpenAI JSON Schema subset.
- Fail loud when a schema-owned parsed example does not validate against the lowered schema.
- Emit explicit strict-mode-compatible schemas. Do not rely on endpoint-side normalization.
- Preserve authored field order so emitted keys follow the documented OpenAI output ordering rule.
- Keep human-facing Markdown contract quality as a first-class acceptance surface, not an afterthought.

## 0.6 Concrete target examples

These examples are the target end state. They are not filler. If the final
design cannot express these cleanly, the design is not done.

The syntax below is the chosen v1 authoring shape for this plan. Phase planning
may still split the work, but it should not reopen these choices without a new
Decision Log entry:

- one Doctrine-authored structured schema
- normal inheritance from parent to child
- one lowering path into OpenAI-compatible JSON Schema
- one readable final-output contract rendered from that same source
- one explicit keyed inheritance model:
  - `inherit <key>` keeps a parent field or reusable definition
  - `override <key>:` replaces a parent field or reusable definition

For OpenAI strict targets, authored `optional` means "nullable on the wire,"
not "key may be omitted." Lowered schemas keep the key in `required` and use a
nullable type or nested `anyOf` with `null`.

### 0.6.1 Target example A: Rally base result plus child extension

Ideal Doctrine authoring:

```prompt
output schema RallyTurnResultPayload: "Rally Turn Result Payload"
    field kind: "Kind"
        type: string
        const: "rally_turn_result"
        required
        note: "Stable machine-readable result kind."

    field status: "Status"
        type: string
        enum:
            ok
            needs_input
            blocked
        required
        note: "High-level turn state."

    field summary: "Summary"
        type: string
        required
        note: "Short user-facing summary."

    field next_step: "Next Step"
        type: string
        optional

    field citations: "Citations"
        type: array
        items: string
        optional

    example:
        kind: "rally_turn_result"
        status: ok
        summary: "Sleep routine updated."
        next_step: null
        citations:
            - "sleep_hygiene_playbook"

output shape RallyTurnResultJson: "Rally Turn Result JSON"
    kind: JsonObject
    schema: RallyTurnResultPayload

output RallyTurnResult: "Rally Turn Result"
    target: TurnResponse
    shape: RallyTurnResultJson
    requirement: Required

    standalone_read: "Standalone Read"
        "The final answer should stand on its own as one structured result."

output schema SleepCoachTurnResultPayload[RallyTurnResultPayload]: "Sleep Coach Turn Result Payload"
    inherit kind
    inherit status
    inherit summary
    inherit next_step
    inherit citations

    field sleep_window: "Sleep Window"
        type: object
        required

        field bedtime_local: "Bedtime Local"
            type: string
            required

        field wake_time_local: "Wake Time Local"
            type: string
            required

    field habits_to_try: "Habits To Try"
        type: array
        items: string
        optional

    example:
        kind: "rally_turn_result"
        status: ok
        summary: "Move bedtime 15 minutes earlier this week."
        next_step: "Start tonight and review in three days."
        citations:
            - "sleep_hygiene_playbook"
        sleep_window:
            bedtime_local: "22:30"
            wake_time_local: "06:30"
        habits_to_try:
            - "Dim lights 60 minutes before bed."
            - "Stop caffeine after 2 PM."

output shape SleepCoachTurnResultJson[RallyTurnResultJson]: "Sleep Coach Turn Result JSON"
    inherit kind
    schema: SleepCoachTurnResultPayload

output SleepCoachTurnResult[RallyTurnResult]: "Sleep Coach Turn Result"
    inherit target
    inherit requirement
    inherit standalone_read
    shape: SleepCoachTurnResultJson

    format_notes: "Expected Structure"
        "Keep `summary` short."
        "Use `habits_to_try` only for concrete next actions."
```

Ideal lowered JSON Schema:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "kind": {
      "type": "string",
      "const": "rally_turn_result",
      "description": "Stable machine-readable result kind."
    },
    "status": {
      "type": "string",
      "enum": ["ok", "needs_input", "blocked"],
      "description": "High-level turn state."
    },
    "summary": {
      "type": "string",
      "description": "Short user-facing summary."
    },
    "next_step": {
      "type": ["string", "null"]
    },
    "citations": {
      "anyOf": [
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "null"
        }
      ]
    },
    "sleep_window": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "bedtime_local": {
          "type": "string"
        },
        "wake_time_local": {
          "type": "string"
        }
      },
      "required": ["bedtime_local", "wake_time_local"]
    },
    "habits_to_try": {
      "anyOf": [
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "null"
        }
      ]
    }
  },
  "required": [
    "kind",
    "status",
    "summary",
    "next_step",
    "citations",
    "sleep_window",
    "habits_to_try"
  ]
}
```

Ideal rendered final-output contract:

````md
## Final Output

> Return one `SleepCoachTurnResult` JSON object.

### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Notes |
| --- | --- | --- | --- | --- |
| `kind` | `string` | yes | no | Always `rally_turn_result`. |
| `status` | `string` | yes | no | One of `ok`, `needs_input`, `blocked`. |
| `summary` | `string` | yes | no | Short user-facing summary. |
| `next_step` | `string` | yes | yes | Single best next step when one exists. |
| `citations` | `string[]` | yes | yes | Short source list when present. |
| `sleep_window` | `object` | yes | no | Local bedtime and wake time. |
| `habits_to_try` | `string[]` | yes | yes | Concrete habits to test when present. |

### Nested Fields

#### `sleep_window`

| Field | Type | Required On Wire | Null Allowed | Notes |
| --- | --- | --- | --- | --- |
| `bedtime_local` | `string` | yes | no | Local bedtime. |
| `wake_time_local` | `string` | yes | no | Local wake time. |

### Example JSON

```json
{
  "kind": "rally_turn_result",
  "status": "ok",
  "summary": "We found two low-risk changes to try this week.",
  "next_step": "Run the new routine for five nights and report back.",
  "sleep_window": {
    "bedtime_local": "22:30",
    "wake_time_local": "06:30"
  },
  "habits_to_try": [
    "Stop caffeine after 2 PM.",
    "Dim lights one hour before bed."
  ]
}
```
````

What this proves:

- `RallyTurnResult` can stay the reusable base output.
- A child can extend the payload through normal inheritance.
- Nested objects and arrays still lower into plain JSON Schema.
- The rendered Markdown stays easy to scan.

### 0.6.2 Target example B: route-aware child result

Ideal Doctrine authoring:

```prompt
output schema RoutedTurnResultPayload[RallyTurnResultPayload]: "Routed Turn Result Payload"
    inherit kind
    inherit status
    inherit summary
    inherit next_step
    inherit citations

    field route: "Route"
        type: object
        required

        field action: "Action"
            type: string
            enum:
                reply
                handoff
                end_turn
            required

        field owner: "Owner"
            type: string
            optional

        field reason: "Reason"
            type: string
            required

output shape RoutedTurnResultJson[RallyTurnResultJson]: "Routed Turn Result JSON"
    inherit kind
    schema: RoutedTurnResultPayload

output RoutedTurnResult[RallyTurnResult]: "Routed Turn Result"
    inherit target
    inherit requirement
    inherit standalone_read
    shape: RoutedTurnResultJson
```

Ideal lowered JSON Schema fragment:

```json
"route": {
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "action": {
      "type": "string",
      "enum": ["reply", "handoff", "end_turn"]
    },
    "owner": {
      "type": ["string", "null"]
    },
    "reason": {
      "type": "string"
    }
  },
  "required": ["action", "owner", "reason"]
}
```

Ideal rendered final-output contract:

````md
## Final Output

> Return one `RoutedTurnResult` JSON object.

### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Notes |
| --- | --- | --- | --- | --- |
| `status` | `string` | yes | no | Base Rally status. |
| `summary` | `string` | yes | no | Base Rally summary. |
| `route` | `object` | yes | no | Routing facts for the next step. |

#### `route`

| Field | Type | Required On Wire | Null Allowed | Notes |
| --- | --- | --- | --- | --- |
| `action` | `string` | yes | no | `reply`, `handoff`, or `end_turn`. |
| `owner` | `string` | yes | yes | Next owner when a handoff is needed. |
| `reason` | `string` | yes | no | Why this route was chosen. |
````

What this proves:

- Inheritance works for route-heavy turn results, not just simple summaries.
- Nested routing facts stay readable in both JSON Schema and Markdown.
- The same base result can power route-aware and non-route-aware children.

### 0.6.3 Target example C: review-driven child result

Ideal Doctrine authoring:

```prompt
output schema ReviewedTurnResultPayload[RallyTurnResultPayload]: "Reviewed Turn Result Payload"
    inherit kind
    inherit status
    inherit summary
    inherit next_step
    inherit citations

    field review: "Review"
        type: object
        required

        field verdict: "Verdict"
            type: string
            enum:
                approve
                changes_requested
                blocked
            required

        field failing_gates: "Failing Gates"
            type: array
            items: string
            optional

        field next_owner: "Next Owner"
            type: string
            required

output shape ReviewedTurnResultJson[RallyTurnResultJson]: "Reviewed Turn Result JSON"
    inherit kind
    schema: ReviewedTurnResultPayload

output ReviewedTurnResult[RallyTurnResult]: "Reviewed Turn Result"
    inherit target
    inherit requirement
    inherit standalone_read
    shape: ReviewedTurnResultJson
```

Ideal lowered JSON Schema fragment:

```json
"review": {
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "verdict": {
      "type": "string",
      "enum": ["approve", "changes_requested", "blocked"]
    },
    "failing_gates": {
      "anyOf": [
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "null"
        }
      ]
    },
    "next_owner": {
      "type": "string"
    }
  },
  "required": ["verdict", "failing_gates", "next_owner"]
}
```

Ideal rendered final-output contract:

````md
## Final Output

> Return one `ReviewedTurnResult` JSON object.

### Payload Fields

| Field | Type | Required On Wire | Null Allowed | Notes |
| --- | --- | --- | --- | --- |
| `summary` | `string` | yes | no | Short user-facing readback. |
| `review` | `object` | yes | no | Review verdict and next owner. |

#### `review`

| Field | Type | Required On Wire | Null Allowed | Notes |
| --- | --- | --- | --- | --- |
| `verdict` | `string` | yes | no | `approve`, `changes_requested`, or `blocked`. |
| `failing_gates` | `string[]` | yes | yes | Exact failing gates when review fails. |
| `next_owner` | `string` | yes | no | Who acts next. |
````

What this proves:

- The same inheritance model can express review-driven machine output.
- Arrays of simple values lower cleanly without raw JSON files.
- Final rendered docs can stay crisp even when the machine shape grows.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Achieve the most elegant user-facing authoring surface and the best rendered final-output contract for the user.
2. Remove the remaining structured-output legacy baggage instead of normalizing around it.
3. Keep one canonical lowering path from Doctrine source to emitted JSON Schema.
4. Cover the full documented OpenAI Structured Outputs strict subset we plan to target.
5. Keep the syntax and machine labels unmistakably aligned with current Doctrine truth.
6. Validate emitted schemas with an established Python library instead of ad hoc checks.

## 1.2 Constraints

- Current Doctrine already uses `output`, `output shape`, `final_output`, and top-level inheritance rules as shipped truth.
- The structured-output feature already ships on top of `output schema`, inherited `output shape`, lowering, and validation. The remaining work is cleanup and convergence, not another first implementation pass.
- Doctrine already has a typed `schema` declaration family, but that family currently models sections, gates, artifacts, and groups, not JSON payload fields.
- The new surface must stay plain, keyed, and explicit. It should not feel like a pasted JSON file with Doctrine punctuation.
- Removing `schema_file`, deleting `AGENTS.contract.json`, deleting external `.example.json` support files, renaming machine labels, and deleting the old declaration family is public compatibility work. Docs, versioning notes, and checked-in refs must move with it.
- OpenAI strict structured outputs require:
  - a root object, not a root `anyOf`
  - `additionalProperties: false` on every object
  - every property present in `required`
  - optional semantics expressed through `null`, not omitted keys
- OpenAI also documents hard limits on property count, nesting depth, enum count, and total string size. Current docs say the total enum-value cap is `1000`, which is higher than the repo's current hard-coded `500`.
- OpenAI says outputs follow schema key order, so field order is part of the visible contract.
- Initial external validator candidate is Python's `jsonschema` library, with `jsonschema-specifications` for packaged official metaschemas.
- The current `uv` environment already has `jsonschema`, but does not have the official `openai` Python SDK and does not expose `OPENAI_API_KEY`, so live OpenAI proof is still missing today.

## 1.3 Architectural principles (rules we will enforce)

- Structured-output schema authoring stays inside Doctrine.
- Structured-output examples stay inside Doctrine too.
- Lowering to JSON Schema is deterministic and compiler-owned.
- Validation uses official metaschemas and a maintained Python implementation.
- Example-instance validation uses that same maintained Python implementation against the lowered schema.
- Inheritance happens through the same Doctrine rules users already know.
- Markdown render quality is part of the contract, not separate polish work.
- Delete dead compatibility surfaces instead of keeping null placeholders or stale labels around them.
- If a machine-facing name still matters, rename it to current truth. If it does not, delete it.

## 1.4 Known tradeoffs (explicit)

- A new typed declaration is cleaner than raw JSON files, but it adds language surface and compiler work.
- Reusing the name `schema` would blur current meaning, so a dedicated structured-schema surface is likely cleaner even if it adds one more declaration kind.
- Strict validation may reject shapes that users can hand-write today. That pain is acceptable if the new source is clearer and safer.
- Best-case Markdown rendering will likely make final-output docs longer, but that is worth it if readers can scan them faster.
- Moving examples into parsed Doctrine syntax and deleting `AGENTS.contract.json` creates churn, but keeping sidecar JSON support files and fake machine artifacts is worse because it leaves the shipped feature looking half-migrated and under-validated.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

Doctrine now has the core feature we wanted:

- `output schema` is a real top-level declaration.
- `output shape` can inherit.
- child structured payloads can add fields through Doctrine inheritance.
- the compiler lowers the authored schema to JSON Schema and validates it.
- `final_output` renders from compiler-owned schema truth instead of raw `.schema.json` files.

What still exists beside that clean path is old structured-output baggage:

- `emit_docs` now writes only `AGENTS.md`, so the actual lowered schema never becomes a machine-readable build artifact.
- the only machine-readable schema truth is the transient in-memory `lowered_schema` object during compile.
- there is no built-in Python validator entry point that reads the emitted artifact path, because no artifact path exists yet.
- there is still no live OpenAI acceptance proof against an emitted schema file.

## 2.2 What’s broken / missing (concrete)

- The shipped structured-output story is still incomplete at the machine boundary.
- A downstream consumer has no canonical emitted JSON Schema file to read.
- The repo cannot point to one stable path and say "this is the contract that was validated and that OpenAI accepted."
- The Python validator only proves compiler internals today, not the emitted artifact that consumers would actually load.
- The live OpenAI proof is incomplete because there is no emitted file for it to consume.

## 2.3 Constraints implied by the problem

- The cleanup must not break the shipped inheritance, lowering, validation, review, or route behavior we already landed.
- The fix must keep one Doctrine-authored source of truth and must not reintroduce authored raw JSON files.
- The fix must emit the real validated schema, not a second summary format.
- The fix must give that emitted schema one canonical path shape that scales cleanly if an agent ever emits more than one machine schema.
- The fix must keep the current final-output ergonomics users rely on, including payload field tables and example JSON.
- The fix must update checked-in proof, release guidance, and compatibility notes in the same change because the emitted machine contract changes again.

# 3) Research Grounding (external + internal “ground truth”)

<!-- arch_skill:block:research_grounding:start -->
## 3.1 External anchors (papers, systems, prior art)

- OpenAI Structured Outputs guide — adopt as the hard external contract for the supported schema subset, documented limits, root-object rules, and strict-mode-friendly examples — this is the primary standards anchor for what Doctrine must emit.
  - `https://developers.openai.com/api/docs/guides/structured-outputs`
- OpenAI function calling guide — adopt for strict-mode behavior and endpoint caveats, especially the rule that non-strict tool schemas can be normalized by Responses but should not define our authored contract — this keeps the plan honest about wire behavior.
  - `https://developers.openai.com/api/docs/guides/function-calling`
- JSON Schema specification — adopt as the Draft 2020-12 baseline and metaschema reference, but reject it as the whole target contract because OpenAI supports only a documented subset.
  - `https://json-schema.org/specification`
- Python `jsonschema` validation docs — adopt as the leading maintained validator candidate for Draft 2020-12 schema validation, `SchemaError`, `ValidationError`, and versioned validator entry points.
  - `https://python-jsonschema.readthedocs.io/en/stable/validate/`
- `jsonschema-specifications` API docs — adopt as the clean path to official metaschemas and vocabularies through a registry instead of copying spec files into the repo.
  - `https://jsonschema-specifications.readthedocs.io/en/stable/api/`

## 3.2 Internal ground truth (code as spec)

- Authoritative behavior anchors (do not reinvent):
  - [doctrine/_compiler/resolve/output_schemas.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/output_schemas.py) — canonical owner of structured output-schema inheritance and lowering.
  - [doctrine/_compiler/resolve/outputs.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/outputs.py) — current owner of inherited output-shape accounting and final-output schema summaries.
  - [doctrine/_compiler/compile/final_output.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/compile/final_output.py) — current owner of rendered final-output contract metadata and payload preview rendering.
  - [doctrine/_compiler/validate/__init__.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/validate/__init__.py) — current owner of Draft 2020-12 validation and OpenAI strict-subset checks.
  - [doctrine/emit_docs.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_docs.py) — current emit surface; today it writes only Markdown and is the place that must grow the real schema artifact.
- Canonical path / owner to reuse:
  - [doctrine/_compiler/resolve/output_schemas.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/output_schemas.py), [doctrine/_compiler/resolve/outputs.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/outputs.py), and [doctrine/_compiler/compile/final_output.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/compile/final_output.py) together are the real owner path for structured final-output semantics. The cleanup must finish on that same path instead of adding or preserving a sidecar compatibility layer.
- Existing patterns to reuse:
  - [doctrine/_compiler/resolve/schemas.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/schemas.py) — explicit inherit / override / fail-loud block accounting for typed schema bodies.
  - [doctrine/_compiler/resolve/outputs.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/outputs.py) — inherited attachment accounting and missing-parent-item failures that already fit Doctrine's style.
  - [doctrine/_compiler/validate/__init__.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/validate/__init__.py) — validator reuse point for a file-based emitted-schema validator surface.
- Prompt surfaces / agent contract to reuse:
  - [examples/79_final_output_output_schema/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/79_final_output_output_schema/prompts/AGENTS.prompt) — minimal schema-backed `final_output:` proof.
  - [examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/104_review_final_output_output_schema_blocked_control_ready/prompts/AGENTS.prompt) — review-driven JSON final-output proof.
  - [examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/105_review_split_final_output_output_schema_control_ready/prompts/AGENTS.prompt) — split review/final-output JSON proof.
  - [examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/106_review_split_final_output_output_schema_partial/prompts/AGENTS.prompt) — route-aware partial JSON final-output proof.
  - [examples/110_final_output_inherited_output/prompts/AGENTS.prompt](/Users/aelaguiz/workspace/doctrine/examples/110_final_output_inherited_output/prompts/AGENTS.prompt) — inherited final-output proof on the ordinary output side.
  - [/Users/aelaguiz/workspace/psflows/stdlib/rally/prompts/rally/turn_results.prompt](/Users/aelaguiz/workspace/psflows/stdlib/rally/prompts/rally/turn_results.prompt) — real downstream consumer anchor for the exact Rally inheritance goal.
- Native model or agent capabilities to lean on:
  - not agent-backed runtime behavior — this is compiler authoring, lowering, and render work, so no custom harness is justified on model-capability grounds.
- Existing grounding / tool / file exposure:
  - emitted `AGENTS.md` output — the visible human surface this plan must keep aligned with the emitted schema contract
  - manifest-backed example cases — the repo's end-to-end proof surface for emitted doctrine
  - current `uv` environment check — `jsonschema` is installed, but the official `openai` SDK is missing and `OPENAI_API_KEY` is absent
- Duplicate or drifting paths relevant to this change:
  - [doctrine/emit_docs.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_docs.py) — emits only Markdown even though the compiler already has the machine contract object in hand
  - [doctrine/_compiler/resolve/outputs.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/outputs.py) `lowered_schema` — trusted internal object that never becomes a consumer-facing artifact
  - [doctrine/_compiler/compile/final_output.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/compile/final_output.py) — renders schema metadata but not the generated schema artifact path
  - [docs/EMIT_GUIDE.md](/Users/aelaguiz/workspace/doctrine/docs/EMIT_GUIDE.md) — now needs to describe the real emitted schema contract instead of a markdown-only story
- Capability-first opportunities before new tooling:
  - compiler-owned typed lowering plus current fail-loud inheritance/accounting patterns — solves the problem without wrappers, sidecar schema-merging scripts, or new runtime tooling
- Behavior-preservation signals already available:
  - [tests/test_output_inheritance.py](/Users/aelaguiz/workspace/doctrine/tests/test_output_inheritance.py) — inherited output behavior proof
  - [tests/test_final_output.py](/Users/aelaguiz/workspace/doctrine/tests/test_final_output.py) — current prose, JSON, review-driven, split, and route-aware final-output proof
  - [tests/test_emit_docs.py](/Users/aelaguiz/workspace/doctrine/tests/test_emit_docs.py) — emitted machine-contract proof
  - [tests/test_review_imported_outputs.py](/Users/aelaguiz/workspace/doctrine/tests/test_review_imported_outputs.py) — imported review-output proof
  - [tests/test_route_output_semantics.py](/Users/aelaguiz/workspace/doctrine/tests/test_route_output_semantics.py) — route/output coupling proof
  - `make verify-examples` — manifest-backed emitted-surface proof across the shipped corpus

## 3.3 Decisions locked by this pass

- Final-output examples stay in `output schema` as parsed Doctrine-owned data.
  - Current repo truth:
    - Examples now live on `output schema`, and `resolve/outputs.py` validates the parsed example instance against the lowered schema.
  - Locked decision:
    - keep that example ownership model and do not reintroduce external example support files
  - Why:
    - this keeps example truth beside schema truth and preserves real instance validation
- `AGENTS.contract.json` stays deleted.
  - Current repo truth:
    - The fake summary artifact is already gone.
  - Locked decision:
    - keep it gone and do not replace it with another Doctrine-specific summary format
  - Why:
    - the machine contract should now be the real lowered schema artifact, not a summary wrapper
- OpenAI compatibility proof becomes two-layer and mandatory.
  - Current repo truth:
    - The compiler already validates lowered schemas and parsed examples in Python, but there is no file-level validator surface and no emitted schema artifact to prove.
  - Locked decision:
    - keep the Python validator as the primary repo-owned proof surface, expose it as a validator for emitted schema files, and keep one live OpenAI API acceptance run as the final external truth check
  - Why:
    - Codex acceptance is not a validator, and a third-party wrapper should not become the repo's authority when the repo already owns the exact OpenAI subset rules it emits
- The emitted machine contract becomes the real lowered schema artifact.
  - Current repo truth:
    - `emit_docs` writes only `AGENTS.md`, so the actual lowered schema never reaches downstream consumers as a file.
  - Locked decision:
    - emit `schemas/<output-slug>.schema.json` beside `AGENTS.md`, where `<output-slug>` is the slugged final-output declaration name, and make both the Python validator and the live OpenAI proof read that emitted file
  - Why:
    - this keeps one real machine contract, avoids heuristic artifact discovery, and gives downstream consumers the exact file the repo validated
<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:external_research:start -->
# External Research (best-in-class references; plan-adjacent)

> Goal: ground this plan in the current OpenAI Structured Outputs contract and a real Python validation path, then fold that into the Doctrine design without drift.

## Topics researched (and why)

- OpenAI Structured Outputs schema subset — this plan exists to emit those schemas.
- OpenAI strict-mode behavior — this changes what "optional" can mean on the wire.
- Python Draft 2020-12 validation tools — Doctrine needs local validation and fail-loud checks.

## Findings + how we apply them

### OpenAI Structured Outputs schema subset

- Best practices (synthesized):
  - Target the documented subset, not generic JSON Schema in the abstract.
  - Treat root-object shape, `required`, and `additionalProperties: false` as hard contract rules, not style.
  - Treat nullable optionals as required keys with `null` allowed.
  - Preserve authored key order because OpenAI says output order follows schema order.
  - Keep schema truth close to the authored type surface. OpenAI explicitly warns against schema and type divergence and recommends native typed ownership over separate JSON schema files.
  - Separate supported subset coverage from unsupported-keyword rejection.
- Adopt for this plan:
  - Doctrine will target the documented OpenAI strict subset as the compiler contract.
  - The plan will cover primitives, objects, arrays, enums, nested `anyOf`, `$defs`, `$ref`, recursion, and documented string / number / array constraints.
  - Doctrine will fail loud on unsupported keywords instead of trying to "mostly work."
  - Doctrine will validate documented limit rules before ship.
  - Doctrine will align its hard-coded limits to the current docs, including the current total enum-value cap.
- Reject for this plan:
  - Do not treat generic JSON Schema support as the target.
  - Do not allow root `anyOf`.
  - Do not allow omitted-key optionals in lowered OpenAI schemas.
  - Do not quietly pass through unsupported composition keywords.
- Pitfalls / footguns:
  - A schema can be valid Draft 2020-12 JSON Schema and still be invalid for OpenAI strict structured outputs.
  - Fine-tuned models have extra keyword limits, so the base-model subset and fine-tuned subset are not identical.
  - `patternProperties` is not safe to treat as part of the base target from current docs, so this plan should reject it until there is direct official support.
  - A stale local copy of a documented limit is still a correctness bug, even if the validator shape is otherwise right.
- Sources:
  - OpenAI Structured Outputs guide — https://developers.openai.com/api/docs/guides/structured-outputs — primary source for supported subset, limits, and examples.
  - JSON Schema specification — https://json-schema.org/specification — primary source for Draft 2020-12 dialect and metaschema framing.

#### Exhaustive support target for this plan

| Feature family | Grounding | Plan action | Example usage |
| --- | --- | --- | --- |
| Root object | OpenAI says the root must be an object and must not use root `anyOf`. | Support and validate. Reject invalid roots. | Base turn result object. |
| Primitive types | OpenAI lists `string`, `number`, `boolean`, `integer`. | Support. | `status`, `score`, `is_blocked`. |
| Object fields | OpenAI supports objects, with `additionalProperties: false` required. | Support on every object. Auto-emit and validate `additionalProperties: false`. | `sleep_window`, `review`, `route`. |
| Arrays | OpenAI supports arrays. | Support `items`, `minItems`, `maxItems` where allowed. | `citations`, `habits_to_try`. |
| Enum | OpenAI supports enums and documents enum-size limits. Current docs say up to `1000` enum values across all enum properties. | Support and validate limits with the current documented values. | `status`, `verdict`, `route.action`. |
| Const | OpenAI documents size accounting for const values. Inference: const is part of the accepted subset. | Support, but add focused proof because the docs imply support rather than showing a direct example. | Stable `kind`. |
| Nullable optionals | OpenAI says all fields must be required and optionals should use `null`. | Support as the OpenAI wire rule. | `next_step`, `route.owner`, `failing_gates`. |
| Nested `anyOf` | OpenAI supports `anyOf` when each branch is itself valid for the subset. | Support nested unions. Reject invalid branches. | array-or-null, object-or-null, discriminated child shapes below root. |
| `$defs` / `$ref` | OpenAI says definitions are supported. | Support. | shared step shapes, reused child objects. |
| Recursion | OpenAI says recursive schemas are supported. | Support. | tree or linked-list style nested nodes. |
| String constraints | OpenAI examples show `pattern` and `format`. | Support for the base target. Note fine-tuned limits separately. | usernames, emails. |
| Number constraints | OpenAI examples show `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`. | Support for the base target. Note fine-tuned limits separately. | bounded scores or temperatures. |
| Array constraints | OpenAI examples show `minItems` and `maxItems`. | Support for the base target. Note fine-tuned limits separately. | bounded citations or steps. |
| Size limits | OpenAI documents limits on property count, nesting, enum count, and total string size. | Enforce with fail-loud validation. | very large result families. |
| Key order | OpenAI says outputs follow schema key order. | Preserve authored order through lowering and render. | stable user-facing docs and machine output. |
| Unsupported composition | OpenAI says `allOf`, `not`, `dependentRequired`, `dependentSchemas`, `if`, `then`, and `else` are not supported. | Reject in the compiler with clear diagnostics. | n/a |
| `patternProperties` | OpenAI docs only call out non-support on fine-tuned models, and do not clearly bless it for the base subset. | Reject in v1 until OpenAI docs give direct support. | n/a |

#### Grounded usage examples that matter for Doctrine

Optional-via-null:

```json
{
  "type": "object",
  "properties": {
    "next_step": {
      "type": ["string", "null"]
    }
  },
  "required": ["next_step"],
  "additionalProperties": false
}
```

Nested `anyOf` that stays inside the supported subset:

```json
{
  "type": "object",
  "properties": {
    "item": {
      "anyOf": [
        {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "age": { "type": "number" }
          },
          "required": ["name", "age"],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "number": { "type": "string" },
            "street": { "type": "string" },
            "city": { "type": "string" }
          },
          "required": ["number", "street", "city"],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": ["item"],
  "additionalProperties": false
}
```

Definitions and references:

```json
{
  "type": "object",
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/step"
      }
    },
    "final_answer": {
      "type": "string"
    }
  },
  "$defs": {
    "step": {
      "type": "object",
      "properties": {
        "explanation": { "type": "string" },
        "output": { "type": "string" }
      },
      "required": ["explanation", "output"],
      "additionalProperties": false
    }
  },
  "required": ["steps", "final_answer"],
  "additionalProperties": false
}
```

### OpenAI strict mode and endpoint behavior

- Best practices (synthesized):
  - Always emit explicit strict-mode-compatible schemas.
  - Do not rely on endpoint-side normalization to repair a weak schema.
  - Treat omitted-key optionals as a schema bug for this plan.
- Adopt for this plan:
  - Emit explicit strict-ready schemas and validate them before runtime.
  - Keep OpenAI wire semantics explicit in rendered docs, especially for nullable optionals.
  - Treat Responses auto-normalization as a warning, not as the product contract.
  - Require one real OpenAI acceptance run against a current Structured Outputs-capable model before calling this reopened pass complete.
- Reject for this plan:
  - Non-strict fallback mode.
  - "Best effort" JSON that later repair code tries to coerce.
- Pitfalls / footguns:
  - Responses can normalize a non-strict tool schema into strict mode, which can silently change optionality if the authoring surface is weak.
  - Chat Completions remains non-strict by default unless strict mode is explicit.
- Sources:
  - OpenAI function calling guide — https://developers.openai.com/api/docs/guides/function-calling — primary source for strict-mode behavior and endpoint default differences.

### Python Draft 2020-12 validation stack

- Best practices (synthesized):
  - Use a maintained Draft 2020-12 validator instead of hand-written schema checks.
  - Keep OpenAI-subset checks as a second layer on top of metaschema validation, because Draft 2020-12 alone is not enough.
  - Keep official metaschemas available from a library registry instead of copying them into the repo.
- Adopt for this plan:
  - Use `jsonschema` for Draft 2020-12 validation.
  - Keep `jsonschema-specifications` available for official metaschema and vocabulary registry access.
  - Add Doctrine-owned OpenAI-subset validation after Draft 2020-12 schema validation.
  - Validate schema-owned parsed example instances with `Draft202012Validator(lowered_schema).validate(example_instance)`.
- Reject for this plan:
  - Ad hoc custom metaschema logic as the first validator.
- Pitfalls / footguns:
  - Passing Draft 2020-12 validation does not prove OpenAI acceptance.
  - `$ref`-heavy schemas are easier to validate correctly when the metaschema registry is explicit.
  - Treating JSON examples as opaque text throws away the validator's ability to prove that authored examples match the authored schema.
- Sources:
  - `jsonschema` validation docs — https://python-jsonschema.readthedocs.io/en/stable/validate/ — maintained Python validator with `SchemaError`, `ValidationError`, and versioned validators such as `Draft202012Validator`.
  - `jsonschema-specifications` API docs — https://jsonschema-specifications.readthedocs.io/en/stable/api/ — official metaschemas and vocabularies exposed as a registry.

### Proof doctrine for this plan

- Best practices (synthesized):
  - Use offline validator proof for standards correctness and example-instance correctness.
  - Use one live OpenAI submission to prove that the generated schema is accepted by the real target platform.
  - Treat either layer missing as incomplete proof.
- Adopt for this plan:
  - Offline proof must include:
    - `Draft202012Validator.check_schema(lowered_schema)`
    - `Draft202012Validator(lowered_schema).validate(example_instance)` for schema-owned examples
  - Live proof must include one successful schema acceptance run through the official OpenAI API.
  - The live proof harness may require adding the official `openai` SDK to the repo or test environment because the current `uv` environment does not have it.
- Reject for this plan:
  - Calling the work complete with only local subset checks.
  - Treating rendered Markdown or emitted sidecar JSON as proof of OpenAI acceptance.
- Sources:
  - OpenAI Structured Outputs guide — https://developers.openai.com/api/docs/guides/structured-outputs
  - OpenAI function calling guide — https://developers.openai.com/api/docs/guides/function-calling
  - `jsonschema` validation docs — https://python-jsonschema.readthedocs.io/en/stable/validate/

## Adopt / Reject summary

- Adopt:
  - Target the documented OpenAI strict subset, not loose generic JSON Schema.
  - Emit explicit strict-mode-compatible schemas.
  - Preserve authored field order.
  - Lower author-facing optionals into required nullable wire fields.
  - Validate both Draft 2020-12 and OpenAI-specific subset rules.
  - Validate schema-owned parsed example instances.
  - Require one real OpenAI acceptance run before calling the reopened pass complete.
- Reject:
  - Non-strict fallback.
  - Unsupported composition keywords.
  - Silent omission-based optionals.
  - `patternProperties` in v1.

## Decision gaps that must be resolved before implementation

- None. External research left no blocker after deep-dive pass 2 locked the v1 authoring surface, nullability rule, explicit reusable-definition story, and hard-cutover migration stance.
<!-- arch_skill:block:external_research:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- `doctrine/grammars/doctrine.lark`, `doctrine/_parser/io.py`, and `doctrine/_model/io.py` now expose the real `output schema` language surface and its typed field or `def` nodes.
- `doctrine/_compiler/resolve/output_schemas.py` owns structured-schema inheritance and lowering.
- `doctrine/_compiler/resolve/outputs.py` and `doctrine/_compiler/compile/final_output.py` now own the live structured final-output summary and render path.
- `doctrine/emit_docs.py` is now the only emit surface for this feature, and it currently writes only `AGENTS.md`.
- The shipped proof surfaces for this path live in:
  - `tests/test_final_output.py`
  - `tests/test_emit_docs.py`
  - `tests/test_review_imported_outputs.py`
  - `tests/test_route_output_semantics.py`
  - `doctrine/_diagnostic_smoke/fixtures_final_output.py`
  - `doctrine/_diagnostic_smoke/compile_checks.py`
  - `doctrine/_diagnostic_smoke/review_checks.py`
  - `examples/09_outputs`
  - `examples/55_owner_aware_schema_attachments`
  - `examples/79_final_output_output_schema`
  - `examples/83_review_final_output_output_schema`
  - `examples/85_review_split_final_output_output_schema`
  - `examples/90_split_handoff_and_final_output_shared_route_semantics`
  - `examples/91_handoff_routing_route_output_binding`
  - `examples/104_review_final_output_output_schema_blocked_control_ready`
  - `examples/105_review_split_final_output_output_schema_control_ready`
  - `examples/106_review_split_final_output_output_schema_partial`
- Rally keeps the real downstream pressure case in `../psflows/stdlib/rally/prompts/rally/turn_results.prompt`.

## 4.2 Control paths (runtime)

Today the real structured-schema pipeline is already compiler-owned:

1. `agent.final_output` resolves to one emitted `output`.
2. That `output` points at an `output shape`.
3. For `kind: JsonObject`, `_resolve_final_output_json_shape_summary(...)` resolves `output shape.schema` to an `output schema` declaration.
4. `doctrine/_compiler/resolve/output_schemas.py` applies inheritance, lowers the typed Doctrine schema to JSON Schema, and returns compiler-owned payload truth.
5. `doctrine/_compiler/validate/__init__.py` validates that lowered schema against Draft 2020-12 and Doctrine's OpenAI strict-subset rules.
6. The summary path also materializes the parsed schema-owned example and validates it as an instance against that lowered schema.
7. `CompileFinalOutputMixin` renders the metadata table, payload-fields table, example block, and any extra authored final-output sections from that lowered summary.
8. `emit_docs.py` writes Markdown from the compiled contract and stops there.

The remaining drift is no longer in authoring, inheritance, or local validation.
It is the missing emitted machine artifact:

- the compiler already has the validated lowered schema object, but emit never writes it
- `AGENTS.md` previews the contract, but downstream tools have no canonical JSON Schema file to load
- the repo has no built-in Python validator command that validates emitted schema files
- the repo has no live OpenAI acceptance proof path on an emitted schema file

## 4.3 Object model + key abstractions

- `OutputDecl` owns the emitted output contract: target, shape, requirement, trust surface, and extra authored record items.
- `OutputShapeDecl` is now inheritable and still owns `kind`, `schema`, and shape-owned helper sections.
- `OutputSchemaDecl` is the real structured payload declaration.
- `FinalOutputJsonShapeSummary` is the bridge object today. It holds:
  - the resolved shape declaration
  - the resolved `output schema` declaration
  - the lowered JSON Schema object
  - payload rows derived from that lowered compiler truth
  - example text derived from parsed schema-owned data
  - extra authored shape items
- `CompiledFinalOutputSpec` now uses `format_mode="json_object"` for structured final outputs.
- The missing abstraction is not a legacy field anymore. It is the generated-schema path that emit and render still need to expose truthfully.

## 4.4 Observability + failure behavior today

- Doctrine fails loud on invalid structured schema authoring, invalid lowered JSON Schema, unsupported OpenAI keywords, and documented limit errors.
- Doctrine fails loud when a structured final output still tries to use legacy `example_file` (`E215`).
- The shipped review and route tests prove the structured-output behavior still works through the new compiler-owned path.
- The remaining gap is easiest to see through emitted output inspection: the validated machine contract exists in memory but not on disk.

## 4.5 UI surfaces (ASCII mockups, if UI work)

No UI screen is in scope. The shipped human and machine surfaces here are:

- prompt authoring syntax in `.prompt` files
- rendered `AGENTS.md` final-output contract Markdown
- the missing emitted schema artifact that machine consumers still need
- example directories, smoke refs, and public docs that need to point at the new emitted schema story
<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

- Keep `output schema` as the only structured payload declaration family for this feature.
- Add one parsed example surface to `output schema` so payload examples live with payload truth.
- Delete the old `json schema` declaration family from the live structured-output path:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/_parser/io.py`
  - `doctrine/_model/io.py`
  - `doctrine/_model/declarations.py`
  - `doctrine/model.py`
- Keep inheritable `output shape` and compiler-owned lowering as the only structured-output pipeline.
- Delete the old registry, readable, and ref surfaces that still advertise `json schema`:
  - `doctrine/_compiler/indexing.py`
  - `doctrine/_compiler/constants.py`
  - `doctrine/_compiler/resolve/refs.py`
  - `doctrine/_compiler/validate/__init__.py`
- Remove dead schema-file and example-file state from compiler types and final-output summaries:
  - `doctrine/_compiler/types.py`
  - `doctrine/_compiler/resolved_types.py`
- Keep fake sidecar contract surfaces deleted:
  - `doctrine/emit_contract.py`
  - the old `AGENTS.contract.json` emit path
- Add one real generated schema artifact surface:
  - `doctrine/emit_docs.py` emitted schema write path
  - per-agent generated schema directory `schemas/`
- Rename shipped example directories and their references from `*_json_schema` to `*_output_schema`.
- Delete structured final-output `.example.json` files. The examples become parsed Doctrine source instead of support artifacts.

## 5.2 Control paths (future)

The chosen future path is:

1. The parser produces one typed `output schema` declaration from Doctrine source, and no parallel `json schema` declaration family remains for this feature.
2. `output schema` uses the normal `[Parent]` inheritance clause already used by other typed declarations.
3. Child `output schema` declarations account for parent fields and reusable definitions through Doctrine's existing keyed model:
   - `inherit <key>` keeps a parent field or named reusable definition
   - `override <key>:` replaces one
   - missing inherited keys still fail loud
4. An `output shape` with `kind: JsonObject` points at that Doctrine-authored `output schema`, and output shapes themselves may also inherit where that keeps the rendered contract surface clean.
5. The lowerer emits one Draft 2020-12 JSON Schema object from that typed Doctrine source.
6. Author-facing `optional` is the normal way to say "may be absent in meaning" and it lowers to a required wire key that allows `null`.
7. `output schema` also owns one parsed example block. That example is parsed into structured Doctrine data, inherited or overridden deliberately, and validated as an instance against the lowered schema.
8. Reusable shapes and recursion are direct author-owned data:
  - named `def` entries are declared in Doctrine source
  - fields or array items reference them explicitly with `ref`
  - recursive shapes use an explicit self-reference, not compiler-synthesized hidden definitions
9. Validation runs in three layers:
  - Draft 2020-12 schema correctness
  - parsed example-instance validation against the lowered schema
  - OpenAI strict-subset rules and current documented limit checks
10. `doctrine/_compiler/resolve/outputs.py` returns a structured summary from the lowered compiler-owned schema and parsed example data, not from a support-file scan.
11. `doctrine/_compiler/compile/final_output.py` renders metadata, payload rows, examples, and the relative generated-schema path from that same lowered summary.
12. `emit_docs.py` writes `AGENTS.md` plus one generated schema file at `schemas/<output-slug>.schema.json` for each structured final output.
13. The built-in Python validator validates that emitted schema file with `Draft202012Validator` plus Doctrine's OpenAI subset checks.
14. The live OpenAI proof harness reads that same emitted file and submits it through the official API.

Canonical owner path:

- `output schema` inheritance, lowering, and parsed example ownership own the payload truth
- `resolve/outputs.py` adapts that truth into final-output summaries
- `compile/final_output.py` consumes the summary
- `emit_docs.py` emits the summary's lowered schema to the canonical file path

Explicit convergence rule:

- do not keep a second raw-file authoring path for `JsonObject` output shapes after migration
- do not keep top-level authored `json schema` declarations beside `output schema` for the same public surface
- do not keep `example_file` or checked-in `.example.json` support files on the structured final-output path
- do not keep `AGENTS.contract.json`
- do not omit the real lowered schema artifact from emitted output
- do not emit any Doctrine-specific summary JSON as the machine contract for this feature
- do not keep `_json_schema` naming in shipped examples or public docs for this feature family

## 5.3 Object model + abstractions (future)

- `OutputSchemaDecl` stays as the typed declaration that owns structured payload truth.
- `OutputSchemaDecl` also owns parsed example truth for structured final outputs.
- That declaration keeps two keyed authored item families:
  - `field <key>: "Title"` for object properties
  - `def <key>: "Title"` for reusable named definitions and recursion anchors
- Reuse Doctrine's existing keyed inheritance rules instead of inventing a second patch language:
  - child schemas keep parent entries with `inherit <key>`
  - child schemas replace parent entries with `override <key>:`
  - missing inherited entries still fail loud
- Add a typed schema AST rich enough to express the supported OpenAI strict subset:
  - scalars
  - objects
  - arrays
  - enums
  - const
  - nullable optionals
  - nested `anyOf`
  - definitions and references
  - recursion
  - supported string, number, and array constraints
- Add a typed example AST rich enough to express the JSON instance values that the lowered schema can accept:
  - objects
  - arrays
  - strings
  - numbers
  - booleans
  - null
- Child schemas extend parent schemas through compiler-owned typed nodes, not through raw JSON merge tricks.
- Keep `output shape` thin and inheritable. It should still own:
  - `kind`
  - the structured-schema reference
  - extra authored presentation sections such as field notes or route-aware helper sections
- `FinalOutputJsonShapeSummary` may stay as the final-output read model, but it must be populated from compiler-owned lowered schema data and must carry the generated schema relpath needed by render and emit.
- `CompiledFinalOutputSpec.format_mode` becomes `json_object`, which matches `kind: JsonObject` instead of the old declaration family name.
- Delete `emit_contract.py` and the emitted `AGENTS.contract.json` surface instead of trying to rescue them with renamed fields.
- Add one emitted machine-contract field with current truth, such as `emitted_schema_relpath`, rather than reviving `schema_file`.
- Reuse the existing inheritance discipline from `doctrine/_compiler/resolve/schemas.py` and `doctrine/_compiler/resolve/outputs.py` instead of inventing a second schema-specific override system.

## 5.4 Invariants and boundaries

- One source of truth for structured turn-response payload fields: Doctrine-authored structured schema declarations.
- One source of truth for structured turn-response payload examples: schema-owned parsed Doctrine example data.
- One lowering path from that source to JSON Schema.
- One validation path: Draft 2020-12, parsed example-instance validation, and Doctrine-owned OpenAI strict-subset checks.
- One emitted machine contract: the exact lowered schema at `schemas/<output-slug>.schema.json`.
- No raw-schema fallback, merge shim, or dual authoring mode for `JsonObject` output shapes.
- `output shape.schema` remains the shape-owned attachment key, but for `kind: JsonObject` it points at `output schema`, not `json schema`.
- `output.schema` keeps its current meaning as the ordinary Doctrine `schema` attachment.
- No `example_file` field or structured-output `.example.json` support file on the shipped final-output path.
- No `AGENTS.contract.json`.
- No consumer should have to scrape `AGENTS.md` to recover the machine contract.
- Review semantics, route semantics, and non-`JsonObject` output behavior stay on their current paths.
- Fail loud on unsupported keywords, invalid roots, bad limit cases, and missing required wire truth.
- Keep validator constants aligned with the current official OpenAI docs, not stale local guesses.
- Preserve authored key order through lowering and render.
- Keep generated lowered JSON artifacts clearly marked as generated proof.
- Emit exactly one always-emitted lowered-schema artifact for each structured final output, and do not add any second summary format beside it.
- Keep shipped example, smoke, and doc naming aligned with current `output schema` truth.

## 5.5 UI surfaces (ASCII mockups, if UI work)

No UI screen is in scope. The acceptance pack for this feature is the user-facing authoring and render story:

- one Doctrine-authored parent schema example
- one Doctrine-authored child schema example
- one lowered JSON Schema example for each
- one rendered final-output contract example for each

That acceptance pack must cover at least:

- Rally base turn result
- Rally child turn result with added sleep fields
- review-driven structured final output
- route-aware structured final output
- nested object and array structured output

The shipped docs, examples, and emitted refs must all tell the same story: Doctrine authors the payload shape, the compiler lowers it, and the rendered final-output contract reads from that same source.
<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonical emitted schema artifact | `doctrine/emit_docs.py`, `doctrine/emit_common.py`, `doctrine/_compiler/resolve/outputs.py` | emit target write loop, output-name helpers, `FinalOutputJsonShapeSummary.lowered_schema` | The compiler already has the validated lowered schema in memory, but `emit_docs.py` only writes `AGENTS.md`. | Emit one generated schema file at `schemas/<output-slug>.schema.json` beside `AGENTS.md`, using the final-output declaration name as the stable slug source. | Downstream consumers need the real schema contract as a file, not a markdown preview. | Structured final outputs emit the exact lowered schema object to one canonical path. | `tests/test_emit_docs.py`, `tests/test_emit_flow.py`, `make verify-examples`, `make verify-package` |
| Final-output read model and render | `doctrine/_compiler/types.py`, `doctrine/_compiler/resolved_types.py`, `doctrine/_compiler/compile/final_output.py` | `CompiledFinalOutputSpec`, `FinalOutputJsonShapeSummary`, metadata rows | The rendered contract shows schema metadata and examples, but it does not expose the generated schema artifact path. | Add emitted-schema path data to the compiled final-output model and render a truthful metadata row such as `Generated Schema`. | Humans should be able to see where the machine contract lives without scraping the build tree. | Final-output render names the emitted schema artifact path without reviving authored `schema_file`. | `tests/test_final_output.py`, `tests/test_review_imported_outputs.py`, `tests/test_route_output_semantics.py` |
| Python validator surface | `doctrine/_compiler/validate/__init__.py`, new validator entry point module to be chosen in implementation, `tests/test_output_schema_validation.py` | OpenAI subset validator, Draft 2020-12 validator, new file-based validator command | The validator logic exists inside compiler code, but there is no built-in file-based validator that validates emitted schema artifacts directly. | Expose a Python validator surface that reads emitted schema files and runs `Draft202012Validator.check_schema`, the existing OpenAI subset checks, and example-instance validation when an example is provided. | Repo proof should validate the exact artifact consumers load. | One repo-owned Python validator for emitted schema files. | `tests/test_output_schema_validation.py`, focused validator CLI/module tests |
| Live OpenAI proof harness | new live-proof runner location to be chosen in implementation, `pyproject.toml` or `uv` invocation docs, emitted schema refs in examples | emitted schema file input, official SDK call, env contract | There is no live acceptance harness, and no official SDK dependency or `uv` command path is documented yet. | Add one narrow harness that reads the emitted schema file and submits it through the official OpenAI Python SDK via the Responses API `text.format` / `json_schema` path. | Server acceptance is the only external truth that the emitted schema really works. | One repeatable live proof command that operates on the emitted file, not an in-memory object. | live proof command, `make verify-examples` note, docs update |
| Public docs and release notes | `docs/EMIT_GUIDE.md`, `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`, `examples/README.md`, `docs/VERSIONING.md`, `CHANGELOG.md` | emit contract docs, upgrade guidance, example refs | Docs currently teach a markdown-only emit story for this feature after deleting `AGENTS.contract.json`. | Update docs to teach the real story: `AGENTS.md` for humans plus `schemas/<output-slug>.schema.json` for machines. | The public repo should explain the exact contract consumers are expected to load. | One truthful human-plus-machine emit story. | doc review, release docs review |

## 6.2 Migration notes

* Canonical owner path / shared code path: compiler-owned `output schema` declarations resolve, lower, and validate first; inherited output shapes adapt that schema truth into final-output summaries; `compile/final_output.py` consumes the summary; `emit_docs.py` writes the same lowered schema object to `schemas/<output-slug>.schema.json`. Reuse the shipped inheritance discipline from `resolve/schemas.py` and `resolve/outputs.py` rather than inventing a new merge model.
* Deprecated APIs (if any): top-level authored `json schema` declarations and raw `.schema.json` authoring truth for `JsonObject` output shapes. This is a hard cutover, not a long deprecation window with two authoring paths.
* Delete list (what must be removed; include superseded shims/parallel paths if any):
  - raw `.schema.json` files that are the authored truth for migrated `JsonObject` output shapes
  - the shipped prompt-language `json schema` authoring path for `JsonObject` outputs
  - raw-schema-file loading as the structured final-output source-of-truth path in `resolve/outputs.py` and `validate/__init__.py`
  - `output shape.example_file` and checked-in `.example.json` support files for structured final outputs
  - `AGENTS.contract.json`, `doctrine/emit_contract.py`, and sidecar contract build refs
  - live comments and docs that say `output shape.schema` still means raw `json schema` for `JsonObject` shapes, especially in `examples/09_outputs` and `examples/55_owner_aware_schema_attachments`
  - stale raw-schema-specific diagnostic wording once the raw-schema authoring path is gone
* Capability-replacing harnesses to delete or justify: none. This is compiler authoring, lowering, validation, and render work. No extra harness or wrapper is warranted.
* Live docs/comments/instructions to update or delete:
  - `docs/AGENT_IO_DESIGN_NOTES.md`
  - `docs/LANGUAGE_REFERENCE.md`
  - `docs/AUTHORING_PATTERNS.md`
  - `docs/EMIT_GUIDE.md`
  - `docs/COMPILER_ERRORS.md`
  - `examples/README.md`
  - `docs/VERSIONING.md`
  - `CHANGELOG.md`
  - shipped explanatory comments in `examples/09_outputs` and `examples/55_owner_aware_schema_attachments`
* Behavior-preservation signals for refactors:
  - `tests/test_final_output.py`
  - `tests/test_emit_docs.py`
  - `tests/test_review_imported_outputs.py`
  - `tests/test_route_output_semantics.py`
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics or smoke fixtures change
* Cleanup and migration notes:
  - migrate shipped `JsonObject` examples and their checked-in refs in the same change set
  - keep generated lowered JSON Schema, if stored in refs or docs, clearly generated and never hand-edited
  - the one allowed emitted schema artifact is the real generated contract at `schemas/<output-slug>.schema.json`; do not add a second summary format beside it
  - treat the live OpenAI acceptance run as part of the migration proof, not an optional follow-up

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope (include/defer/exclude/blocker question) |
| --- | --- | --- | --- | --- |
| Shipped `JsonObject` examples | `examples/09_outputs`, `examples/79_final_output_output_schema`, `examples/83_review_final_output_output_schema`, `examples/85_review_split_final_output_output_schema`, `examples/90_split_handoff_and_final_output_shared_route_semantics`, `examples/91_handoff_routing_route_output_binding`, `examples/104_review_final_output_output_schema_blocked_control_ready`, `examples/105_review_split_final_output_output_schema_control_ready`, `examples/106_review_split_final_output_output_schema_partial` | Move every shipped structured payload example to the new structured-schema source | Prevents a mixed public language where old and new schema stories both look live | include |
| Owner-aware wording | `examples/55_owner_aware_schema_attachments`, `docs/LANGUAGE_REFERENCE.md`, `docs/AGENT_IO_DESIGN_NOTES.md` | Keep the owner-sensitive `schema` split explicit after the change: `output shape.schema` points at `output schema`, `output.schema` points at Doctrine `schema` | Prevents docs drift around `output shape.schema` versus `output.schema` | include |
| Diagnostic fixtures | `doctrine/_diagnostic_smoke/fixtures_final_output.py`, `doctrine/_diagnostic_smoke/compile_checks.py`, `doctrine/_diagnostic_smoke/review_checks.py`, `doctrine/_diagnostic_smoke/emit_checks.py` | Use the new structured-schema authoring surface in smoke sources | Prevents local smoke proof from teaching the legacy raw-schema path | include |
| Inherited output shapes | `output shape` declarations that back child structured outputs | Let child shapes inherit `kind` and helper sections from parents, and handle example ownership according to Section 3.3 | Prevents every child structured output from re-spelling the same shape shell | include |
| Emitted schema contract | `doctrine/emit_docs.py`, `tests/test_emit_docs.py`, `tests/test_emit_flow.py` | Emit the real lowered schema at `schemas/<output-slug>.schema.json` and make render point at it | Prevents a silent split between rendered Markdown, emitted machine JSON, and the schema that was actually validated | include |
| Review and route shells | `tests/test_review_imported_outputs.py`, `tests/test_route_output_semantics.py` | Keep review and route semantics unchanged while the schema source changes underneath | Prevents the structured-schema refactor from breaking higher-level semantics | include |
| Always-emitted lowered-schema files | emit target and emitted contract surfaces | Emit exactly one real lowered-schema file per structured final output | Machine consumers need the contract, but they only need the real schema, not a second summary format | include |
| Non-`JsonObject` output shapes | prose and markdown output shapes across the repo | Leave them on their current path | The approved change is for structured payload schemas, not every output shape | exclude |
| Input-side `JsonObject` uses | input shapes and input-source guidance | Reuse the new structured-schema family for inputs too | Could be a useful follow-on, but it is not required by the current ask | exclude |
<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

> Rule: systematic build, foundational first; split Section 7 into the smallest reasonable sequence of coherent self-contained units that can be completed, verified, and built on later. If two decompositions are both valid, bias toward more phases than fewer. `Work` explains the unit; `Checklist (must all be done)` is the authoritative must-do list inside the phase; `Exit criteria (all required)` names the concrete done conditions. Refactors, consolidations, and shared-path extractions must preserve existing behavior with credible evidence proportional to the risk. For agent-backed systems, prefer prompt, grounding, and native-capability changes before new harnesses or scripts. No fallbacks/runtime shims - the system must work correctly or fail loudly (delete superseded paths). The authoritative checklist must name the actual chosen work, not unresolved branches or "if needed" placeholders. Prefer programmatic checks per phase; defer manual/UI verification to finalization. Avoid negative-value tests and heuristic gates (deletion checks, visual constants, doc-driven gates, keyword or absence gates, repo-shape policing). Also: document new patterns/gotchas in code comments at the canonical boundary (high leverage, not comment spam).

Current state:

- Phases 1 through 9 landed the core structured-output feature, the parsed-example migration, the `AGENTS.contract.json` delete, the legacy cleanup, and the local Python validator alignment.
- Phase 10 and Phase 11 remain complete:
  - Phase 10: emit the canonical lowered schema artifact
  - Phase 11: expose the Python validator for emitted schema files
- Phase 2, Phase 4, Phase 5, and Phase 12 are complete after the fresh 2026-04-15 audit.
- No reopened code phases remain.
- The next frontier is `arch-docs` for broader docs cleanup, evergreen consolidation, and plan/worklog retirement.

## Phase 1 — Add the new language surface and declaration plumbing

* Goal:
  Make `output schema` and inherited `output shape` real compiler declarations so every later phase can build on one canonical owner path.
* Work:
  Add the new prompt-language surface, typed model nodes, registry entries, and owner-sensitive display behavior before any lowering or render work starts.
* Checklist (must all be done):
  - Add top-level `output schema` grammar to `doctrine/grammars/doctrine.lark`.
  - Add typed model nodes in the parser and model for:
    - `OutputSchemaDecl`
    - `field`
    - `def`
    - the keyed authored item forms needed for `inherit <key>` and `override <key>:`
  - Extend `output shape` so it can inherit in the same style as `output`.
  - Register and resolve `output schema` declarations through `doctrine/_compiler/indexing.py` and `doctrine/_compiler/resolve/refs.py`.
  - Update owner-sensitive display and addressability so `output shape.schema` points at `output schema` for `JsonObject` shapes while `output.schema` keeps its current Doctrine `schema` meaning.
  - Add focused parse, resolution, and display coverage for the new declaration surface and inherited output shapes.
* Verification (required proof):
  - Focused parser and resolution tests for `output schema` and inherited `output shape`
  - Existing output and display tests still pass where the new declarations are not involved
* Docs/comments (propagation; only if needed):
  - Add one short code comment at the owner-sensitive `schema` boundary if the split between `output shape.schema` and `output.schema` would otherwise be easy to regress.
* Exit criteria (all required):
  - The compiler can parse and resolve `output schema` declarations and inherited output shapes.
  - Addressable and display surfaces can talk about `output shape.schema` truthfully after the new declaration kind exists.
  - No parser, registry, ref, display, or addressability code touched in this phase still needs to guess whether `JsonObject` shapes use `json schema` or `output schema`.
* Rollback:
  - Revert the new declaration and inherited-shape plumbing if the compiler cannot preserve existing non-`JsonObject` parse and display behavior.

## Phase 2 — Implement output-schema inheritance and lowering

Status: COMPLETE (fresh audit verified)

Reopened reason fixed:
- Optional fields with `enum` or `const` did not really accept `null`.

Completed work:
- Optional enum fields now add `null` to the enum values as well as the nullable type.
- Optional const fields now lower through `anyOf` so the const branch and the null branch are both valid.
- Focused tests cover optional enum and optional const null examples.

Proof:
- `uv run --locked python -m unittest tests.test_output_schema_lowering tests.test_final_output`
- `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_review_imported_outputs tests.test_route_output_semantics tests.test_emit_flow`

* Goal:
  Turn `output schema` declarations into one typed, inherited, compiler-owned payload model that lowers to Draft 2020-12 JSON Schema.
* Work:
  Build the schema AST resolution and lowering path before validation or final-output consumers switch over.
* Checklist (must all be done):
  - Resolve parent and child `output schema` declarations with keyed `inherit <key>` and `override <key>:` accounting.
  - Support explicit author-owned reusable definitions and recursion through typed `def` and `ref` nodes.
  - Lower structured schemas to JSON Schema while preserving authored key order.
  - Cover the supported feature set in the lowerer:
    - primitives
    - objects
    - arrays and items
    - enums and const
    - authored `optional` lowered to required nullable wire fields
    - nested `anyOf`
    - explicit definitions and references
    - recursion
    - supported string, number, and array constraints
  - Keep the lowered schema compiler-internal by default. Do not add a new always-emitted runtime artifact.
  - Add focused lowerer coverage for parent/child inheritance, nullability, nested objects, arrays, `anyOf`, defs/refs, and recursion.
* Verification (required proof):
  - Focused lowerer tests for parent and child payloads
  - Existing non-structured output tests still pass
* Docs/comments (propagation; only if needed):
  - Add one short code comment at the canonical lowering boundary if the split between typed schema truth and lowered JSON would otherwise be easy to misuse later.
* Exit criteria (all required):
  - A parent and child `output schema` can resolve and lower cleanly.
  - Lowered JSON Schema is fully derived from compiler-owned typed data, not from raw file mining.
  - The lowerer supports every authored schema feature family this plan assigns to lowering:
    - primitives
    - objects
    - arrays and items
    - enums and const
    - authored `optional` lowered to required nullable wire fields
    - nested `anyOf`
    - explicit definitions and references
    - recursion
    - supported string, number, and array constraints
* Rollback:
  - Revert the typed schema resolver and lowerer if inheritance accounting or key-order preservation is not trustworthy.

## Phase 3 — Add the validator stack and replace the raw summary path

* Goal:
  Make validation and summary generation read from the new lowered schema path instead of raw `.schema.json` support files.
* Work:
  Replace the shallow raw-file checks with the layered standards-plus-OpenAI validator and use the lowered schema as the one summary input.
* Checklist (must all be done):
  - Add Draft 2020-12 validation through `jsonschema` and official metaschema registry usage.
  - Add Doctrine-owned OpenAI strict-subset validation and documented limit checks.
  - Reject unsupported OpenAI keywords and invalid root shapes with clear diagnostics.
  - Replace `_load_json_schema_payload_rows(...)`-style raw file mining with payload-row derivation from the lowered schema object.
  - Update `resolve/outputs.py` and related summary types so final-output summaries carry lowered-schema truth instead of raw schema file truth.
  - Do not let `.example.json` support files influence payload-schema truth. Example ownership is handled later in the reopened canonical phases.
  - Add focused validator tests for:
    - root `anyOf`
    - missing `additionalProperties: false`
    - unsupported keywords
    - nullable optionals
    - recursion
    - documented size and nesting limits
* Verification (required proof):
  - Focused validator tests for Draft 2020-12 and OpenAI-subset failures
  - Focused summary tests that prove payload rows now come from lowered compiler truth
* Docs/comments (propagation; only if needed):
  - No public doc update in this phase.
* Exit criteria (all required):
  - Structured-schema validation is layered and fail-loud.
  - Final-output summary data no longer depends on raw `.schema.json` parsing.
  - Example ownership is isolated from schema truth and can be hard-cut later without reopening the lowering path.
* Rollback:
  - Revert the summary-path replacement if the compiler cannot yet derive stable payload rows from lowered schema truth.

## Phase 4 — Switch final-output render, emitted contract truth, and diagnostics

Status: COMPLETE (fresh audit verified)

Reopened reason fixed:
- Rendered payload rows only covered root fields.

Completed work:
- Payload rows now recurse into nested object properties and render dotted field paths such as `route.action`, `route.owner`, and `route.reason`.
- Nested rows use the same lowered schema truth as the emitted schema artifact.
- `$ref` expansion is guarded so recursive schemas do not make the human contract loop forever.
- Enum meanings now omit the synthetic nullable `null` enum value because null allowance is already shown in its own column.
- Focused render tests cover nested object payload rows.

Proof:
- `uv run --locked python -m unittest tests.test_final_output`
- `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_review_imported_outputs tests.test_route_output_semantics tests.test_emit_flow`

* Goal:
  Move every compiler-owned consumer of structured final-output schema truth onto the new lowered path without widening public machine artifacts at that stage.
* Work:
  Rewire rendering, then-current emitted contract metadata, and compiler diagnostics to the new source of truth while keeping review and route semantics stable. This phase is already landed; the new emitted schema artifact comes later in Phase 10.
* Checklist (must all be done):
  - Update `doctrine/_compiler/compile/final_output.py` to render metadata rows, payload rows, examples, and helper sections from the lowered summary.
  - Render strict-wire truth clearly, including required-on-wire nullable fields.
  - Update the then-current emitted contract surface so it reads from the lowered summary without adding a new always-emitted lowered-schema file field.
  - Retire or rewrite raw-schema-specific diagnostics and sync `docs/COMPILER_ERRORS.md` to current truth.
  - Keep review-driven and route-aware final-output behavior unchanged except for the structured-schema source swap.
  - Add or update proof in:
    - `tests/test_final_output.py`
    - `tests/test_emit_docs.py`
    - `tests/test_review_imported_outputs.py`
    - `tests/test_route_output_semantics.py`
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_final_output`
  - `uv run --locked python -m unittest tests.test_emit_docs`
  - `uv run --locked python -m unittest tests.test_review_imported_outputs`
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
* Docs/comments (propagation; only if needed):
  - Update `docs/COMPILER_ERRORS.md` if diagnostic wording changes.
* Exit criteria (all required):
  - Rendered final-output contracts and the then-current sidecar contract path read from the lowered schema path.
  - Review and route semantics stay green.
  - Public machine artifacts do not grow a new lowered-schema file surface.
* Rollback:
  - Revert the consumer switch if render truth and emitted contract truth diverge or if review and route semantics start to move with it.

## Phase 5 — Hard-cut shipped examples, docs, diagnostics, and release guidance

Status: COMPLETE (fresh audit verified)

Reopened reason fixed:
- The shipped manifest-backed examples did not yet prove a child structured final output whose child `output schema` extends a parent and emits the generated schema artifact.
- Stale raw `.schema.json` support files remained in shipped example directories and could still look like authored schema truth.
- `AGENTS.md` still named the old `examples/106_review_split_final_output_json_schema_partial` corpus endpoint even though the approved cutover and actual examples use `_output_schema`.
- `examples/79_final_output_output_schema/prompts/INVALID_MISSING_EXAMPLE.prompt` and its manifest still used `InvalidMissingExampleFileAgent`; the case now proves a missing schema-owned `example:`, not a missing external example file.

Completed work:
- `examples/79_final_output_output_schema` now uses a base `output schema`, a child `output schema` with added fields, a base `output shape`, and a child `output shape`.
- The child example uses explicit keyed replacement syntax with `override example:` and `override schema:`.
- Stale raw schema support files were deleted from shipped example `schemas/` directories. The only remaining `.schema.json` files under examples are generated build or build_ref artifacts.
- Public example directories and references were restored to the approved `*_output_schema` naming.
- `editors/vscode` syntax, resolver, unit fixtures, integration fixtures, and snapshots now use `output schema` and schema-owned `example:` for this surface.
- VS Code grammar alignment covers the new output-schema keywords instead of a legacy `json schema` grammar branch.
- Root `AGENTS.md` now names the current `examples/106_review_split_final_output_output_schema_partial` corpus endpoint.
- The missing schema-owned example case now uses `InvalidMissingExampleAgent` in the prompt and manifest.

Proof:
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/79_final_output_output_schema/cases.toml`
- `cd editors/vscode && make`
- `uv run --locked python -m unittest tests.test_output_schema_surface tests.test_output_schema_lowering tests.test_output_schema_validation tests.test_final_output tests.test_emit_docs tests.test_validate_output_schema tests.test_prove_output_schema_openai tests.test_review_imported_outputs tests.test_route_output_semantics tests.test_emit_flow`
- `make verify-examples`
- `make verify-diagnostics`
- `make verify-package`

* Goal:
  Make the new surface the only shipped public truth for structured `JsonObject` outputs.
* Work:
  Move every shipped example, smoke fixture, and public doc to the new `output schema` story and remove stale raw-schema truth surfaces.
* Checklist (must all be done):
  - Migrate shipped `JsonObject` examples from raw `json schema` authoring truth to `output schema`.
  - Update invalid prompts, checked-in refs, and generated proof artifacts in the same change set.
  - Remove redundant raw authored `.schema.json` files that no longer serve as proof artifacts.
  - Migrate diagnostic smoke fixtures and smoke expectations to the new authoring surface.
  - Rewrite public docs and examples that still teach the old path:
    - `docs/AGENT_IO_DESIGN_NOTES.md`
    - `docs/LANGUAGE_REFERENCE.md`
    - `docs/AUTHORING_PATTERNS.md`
    - `docs/EMIT_GUIDE.md`
    - `examples/README.md`
    - shipped explanatory comments in example prompt files
  - Update `docs/VERSIONING.md` and `CHANGELOG.md` for the public breaking-language change and the hard cutover guidance.
  - Keep generated lowered JSON shown only where human proof needs it.
* Verification (required proof):
  - `make verify-examples`
  - `make verify-diagnostics` when diagnostics or smoke fixtures changed
  - Focused unit and integration tests from earlier phases still pass
* Docs/comments (propagation; only if needed):
  - This phase owns the public doc and release-note sync work.
* Exit criteria (all required):
  - Shipped examples, smoke fixtures, emitted refs, docs, and release notes all tell one `output schema` story.
  - No shipped prompt, doc, or live comment still teaches raw `json schema` authoring truth for `JsonObject` outputs.
  - Public upgrade guidance exists in `docs/VERSIONING.md` and `CHANGELOG.md`.
* Rollback:
  - Revert example, smoke, and public-doc migration together with the compiler cutover if the repo cannot ship one consistent public story.

## Phase 10 — Emit the canonical lowered schema artifact

* Goal:
  Put the real machine contract on disk in a canonical place.
* Work:
  Extend emit so every structured final output writes the exact lowered schema to `schemas/<output-slug>.schema.json`, where `<output-slug>` is derived from the final-output declaration name.
* Checklist (must all be done):
  - Add emitted-schema relpath data to the final-output summary or compiled model without reviving authored `schema_file`.
  - Update `doctrine/emit_docs.py` to write `AGENTS.md` and the generated schema file for structured final outputs.
  - Ensure the written JSON is the exact lowered schema object that already passed local validation.
  - Render the generated schema path in the final-output metadata so humans can find the machine contract.
  - Update emit-flow tests, corpus refs, and docs that currently assume markdown-only output.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_emit_docs`
  - `uv run --locked python -m unittest tests.test_emit_flow`
  - `uv run --locked python -m unittest tests.test_final_output`
  - `make verify-examples`
  - `make verify-package`
* Docs/comments (propagation; only if needed):
  - Update `docs/EMIT_GUIDE.md` to teach the new schema artifact path and naming rule.
* Exit criteria (all required):
  - Structured final outputs emit `schemas/<output-slug>.schema.json`.
  - That file matches the validated lowered schema object exactly.
  - `AGENTS.md` names the generated schema path.
* Rollback:
  - Revert the emitted artifact as one unit if emit or package flows cannot carry the real schema file truthfully.

## Phase 11 — Expose the Python validator for emitted schema files

* Goal:
  Make the Python validator a first-class repo-owned proof surface for the emitted artifact.
* Work:
  Expose the current validator stack behind a file-based Python entry point that validates emitted schema files with `jsonschema` plus Doctrine's OpenAI strict-subset checks.
* Checklist (must all be done):
  - Factor or wrap the existing lowered-schema validator so it can validate a schema file directly.
  - Keep `Draft202012Validator.check_schema` and the current OpenAI subset checks on the same path the compiler uses.
  - Add focused proof that validates emitted schema files, not just in-memory schema dicts.
  - Keep parsed example-instance validation on the same validator surface when example data is available.
  - Document the validator command in the plan, worklog, and public docs if it is part of the shipped proof story.
* Verification (required proof):
  - `uv run --locked python -m unittest tests.test_output_schema_validation`
  - the new emitted-schema validator command against at least one shipped emitted schema file
* Docs/comments (propagation; only if needed):
  - Document the validator command in `docs/EMIT_GUIDE.md` or the most appropriate proof-facing doc.
* Exit criteria (all required):
  - The repo can validate an emitted schema file with one Python command.
  - That validator command reuses the same Draft 2020-12 and OpenAI subset rules the compiler trusts.
  - Repo proof now targets the emitted artifact, not just compiler internals.
* Rollback:
  - Revert the public validator entry point if it forks away from compiler truth instead of reusing it.

## Phase 12 — Add live OpenAI acceptance on the emitted artifact and finish public truth

Status: COMPLETE (fresh audit verified)

Reopened reason fixed:
- The live OpenAI proof had to be rerun after the nullable lowering and nested contract fixes landed.

Completed work:
- Reran the official OpenAI proof command from the repo-local `.env`.
- Used the emitted schema artifact at `examples/79_final_output_output_schema/build_ref/repo_status_agent/schemas/repo_status_final_response.schema.json`.
- Recorded the accepted schema path, model, and response id in the worklog.

Proof:
- `set -a; source .env >/dev/null 2>&1; set +a; uv run --with openai python -m doctrine.prove_output_schema_openai --schema examples/79_final_output_output_schema/build_ref/repo_status_agent/schemas/repo_status_final_response.schema.json --model gpt-4.1`
- OpenAI response id: `resp_0723b655002b8d630069dfb4e894bc81938c36a8893c43b934`

* Goal:
  Close the last external-proof gap on the actual emitted schema file.
* Work:
  Add one narrow live-proof harness that reads the emitted schema artifact, submits it through the official OpenAI Python SDK, and records the exact proof command and result.
* Checklist (must all be done):
  - Add a live-proof runner that accepts an emitted schema path and uses the official OpenAI Python SDK.
  - Use the official structured-output API path with `json_schema`, not a Codex-only acceptance trick.
  - Keep the SDK dependency narrow; prefer `uv run --with openai` or an equivalent proof-only install path over widening core runtime dependencies unless there is a strong reason.
  - Run one real acceptance proof against an emitted schema file and record the exact command and outcome in the worklog.
  - Update public docs and release notes so the repo now teaches the human contract plus the emitted machine contract together.
* Verification (required proof):
  - the new live OpenAI acceptance command added by this phase
  - `make verify-examples`
  - `make verify-package`
* Docs/comments (propagation; only if needed):
  - Document the live proof prerequisites, including `OPENAI_API_KEY`.
* Exit criteria (all required):
  - The repo has one recorded live OpenAI acceptance proof for an emitted schema file.
  - Public docs tell one truthful human-plus-machine contract story.
  - The feature is no longer missing the machine-consumer boundary it set out to own.
* Rollback:
  - Revert the live-proof harness if it cannot be made narrow, truthful, and maintainable, then reopen the plan instead of pretending proof exists.
<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Unit tests (contracts)

- Parser and resolution tests for `output schema` and inherited `output shape`.
- Inheritance tests for parent/child structured schemas.
- Lowering tests that compare Doctrine input to emitted JSON Schema objects.
- Validator tests that fail loud on invalid lowered schemas.
- Parsed-example tests that prove the authored example is parsed as data, not text.
- Example-instance validation tests that prove the authored example validates against the lowered schema.
- Validator tests for OpenAI-only failures:
  - root `anyOf`
  - missing `additionalProperties: false`
  - unsupported keywords
  - documented size-limit violations
  - recursion and reusable-definition errors
  - required nullable wire lowering for authored `optional`
  - current documented enum-count limits

## 8.2 Integration tests (flows)

- Final-output tests for base and child turn-result outputs.
- Review-driven structured final-output tests.
- Route-aware structured final-output tests.
- Emit-flow tests that prove `schemas/<output-slug>.schema.json` is emitted and matches the lowered schema.
- Run the focused existing suites that own those flows:
  - `uv run --locked python -m unittest tests.test_final_output`
  - `uv run --locked python -m unittest tests.test_emit_docs`
  - `uv run --locked python -m unittest tests.test_review_imported_outputs`
  - `uv run --locked python -m unittest tests.test_route_output_semantics`
  - `uv run --locked python -m unittest tests.test_output_schema_surface`
  - `uv run --locked python -m unittest tests.test_output_schema_validation`
- Run `make verify-diagnostics` when the schema-backed fixture or diagnostic surface changes.
- Feature-coverage tests for:
  - nullable optionals
  - nested `anyOf`
  - `$defs` / `$ref`
  - recursion
  - string, number, and array restrictions
- Run `make verify-examples` after migrated examples and refs land.
- Run `make verify-package` when the emit or package surface changes.
- Run the emitted-schema validator command from Phase 11 and record the exact command and result.
- Run one live OpenAI acceptance command from the Phase 12 harness and record the exact command and result.

## 8.3 E2E / device tests (realistic)

- No UI device testing is needed.
- Final manual check should read the rendered Markdown examples and the emitted schema file side by side to confirm they match and are easy to understand.
- Final manual check should also confirm the schema-owned parsed example reads naturally in Doctrine source.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout plan

- Ship as one compiler change with updated examples and docs.
- Do not hide the new surface behind a runtime fallback.
- Migrate the repo's own structured final-output examples as part of the same rollout.
- Remove the shipped raw `json schema` authoring story for `JsonObject` outputs in that same public release. Do not ship a mixed public story.
- Keep `AGENTS.contract.json` deleted and keep structured-output `.example.json` support files deleted in that same public release.
- Add the generated schema artifact in that same public release so the delete does not leave machine consumers with nothing.
- Do not call the reopened elegance pass done until the live OpenAI proof run lands.
- Publish upgrade guidance and changelog notes in the same release because this is a public language cutover.

## 9.2 Telemetry changes

- No product telemetry is expected.
- Compiler diagnostics remain the main observability surface.

## 9.3 Operational runbook

- If the lowering path or metaschema validation rejects an authored schema, fail loud during compile.
- If a migration leaves old `.example.json` files, old `AGENTS.contract.json` refs, or old `_json_schema` names behind, fix the source of truth and regenerate proof artifacts before merge.
- If an emitted structured final-output schema is missing from `schemas/<output-slug>.schema.json`, do not claim the feature is done.
- If the live OpenAI proof cannot run in the current environment, do not claim completion. Fix the environment or reopen the plan.

<!-- arch_skill:block:consistency_pass:start -->
## Consistency Pass
- Reviewers: self-integrator
- Scope checked:
  - `# TL;DR`, `# 0)`, `# 3)` through `# 9)`, and helper-block alignment
  - canonical owner path, hard-cut migration scope, phase order, verification burden, and rollout obligations
- Findings summary:
  - The rewritten plan now tells one canonical post-cutover story end to end.
  - The earlier over-correction is fixed: fake summary JSON stays deleted, but the real lowered schema must be emitted as the machine contract.
  - The architecture is now locked around schema-owned parsed examples, one canonical emitted schema artifact, a repo-owned Python validator for that artifact, no reverse compatibility, and mandatory live OpenAI proof.
- Integrated repairs:
  - reopened the North Star around the missing emitted schema contract
  - locked Section 3.3 around the canonical emitted artifact and the Python validator preference
  - tightened the proof doctrine so Python validation is primary and live acceptance is final external proof
  - reopened Section 6 and Section 7 around the new emitted-schema frontier
  - tightened Section 8 and Section 9 so the reopened pass does not claim readiness before the emitted artifact and live proof land
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

## 2026-04-15 - Treat inheritable structured turn results as the main outcome

### Context

The user asked for a child result to inherit from `RallyTurnResult`, add fields through inheritance, and stop depending on raw JSON schema files as the real source of truth.

### Options

- Keep raw JSON schema files and add a custom merge layer on top.
- Add a Doctrine-native structured-schema surface and lower it to JSON Schema.

### Decision

Draft the plan around a Doctrine-native structured-schema surface and a compiler-owned lowering path.

### Consequences

- The work is larger than a small render tweak.
- The reward is cleaner inheritance and one source of truth.

### Follow-ups

- Confirm the exact declaration surface during research.

## 2026-04-15 - No fallback authoring path for inheritable turn-result schemas

### Context

The ask is about elegant inheritance and one Doctrine-native source of truth.

### Options

- Keep raw JSON schema files as an equal long-term source.
- Treat Doctrine-authored structured schema as the only long-term authoring truth for this surface.

### Decision

Draft this plan with `fallback_policy: forbidden`.

### Consequences

- Migration must be explicit.
- Compiler failures must be clear and helpful.

### Follow-ups

- Confirm whether any generated JSON Schema artifacts should remain for proof or tooling.

## 2026-04-15 - Initial validator candidate is Python jsonschema

### Context

The plan needs an online Python validator choice for lowered JSON Schema output.

### Options

- Build custom validation logic in Doctrine.
- Use a maintained Python JSON Schema implementation with official metaschema support.

### Decision

Use `jsonschema` as the initial lead candidate, with `jsonschema-specifications` as the first library to inspect for official metaschema access.

### Consequences

- External research must confirm Draft 2020-12 support, metaschema flow, and clean repo integration.
- We avoid starting with ad hoc validation logic.

### Follow-ups

- Validate the exact library API and version story in the external-research pass.

## 2026-04-15 - Target the documented OpenAI strict subset, not loose generic JSON Schema

### Context

The external-research pass confirmed that OpenAI Structured Outputs supports a documented subset of JSON Schema with extra rules around root shape, `required`, `additionalProperties`, limits, and unsupported keywords.

### Options

- Treat generic Draft 2020-12 JSON Schema as the target and hope runtime compatibility falls out later.
- Treat the documented OpenAI strict subset as the compiler contract and validate it directly.

### Decision

Treat the documented OpenAI Structured Outputs strict subset as the target contract for this plan.

### Consequences

- Draft 2020-12 validation is necessary but not sufficient.
- The compiler must own OpenAI-only checks and fail loud on unsupported shapes.
- The example pack must prove OpenAI-valid lowering, not just JSON-shaped output.

### Follow-ups

- Lock the exact authoring surface for the subset in phase 1.

## 2026-04-15 - OpenAI wire optionals are required nullable fields

### Context

OpenAI docs say strict structured outputs require every field in `required`, and recommend `null` unions to emulate optional values.

### Options

- Lower author-facing optionals to missing keys.
- Lower author-facing optionals to required wire keys that allow `null`.

### Decision

Draft the plan around required nullable wire fields for OpenAI-targeted optionals.

### Consequences

- Rendered docs must show both "required on wire" and "null allowed" when that distinction matters.
- The lowering contract becomes stricter and more honest than the current raw-file examples.

### Follow-ups

- Phase 1 must lock whether Doctrine spells that as authored `optional`, explicit nullability, or both.

## 2026-04-15 - Keep Draft 2020-12 validation and OpenAI-subset validation as separate layers

### Context

The Python validator docs and `jsonschema-specifications` docs support a clean Draft 2020-12 validation path, but OpenAI adds subset rules beyond the generic metaschema.

### Options

- Write one custom validator for everything.
- Use `jsonschema` for Draft 2020-12 validation and add Doctrine-owned OpenAI-subset checks on top.

### Decision

Keep the validation stack layered: `jsonschema` plus official metaschema support first, Doctrine OpenAI-subset checks second.

### Consequences

- We get a real standards validator without giving up OpenAI-specific correctness.
- Unsupported OpenAI shapes must still produce Doctrine-owned diagnostics.

### Follow-ups

- Phase 1 must lock the exact library entry points and registry usage.

## 2026-04-15 - Lock the v1 structured-schema authoring and migration shape

### Context

Research and deep-dive pass 1 narrowed the architecture, but the plan still had
open choices about the exact declaration surface, child-accounting model,
nullable optionals, reusable definitions, generated artifacts, and migration
policy.

### Options

- Leave those choices open for implementation to settle later.
- Lock one v1 authoring and migration shape before phase planning.

### Decision

Lock the v1 design to this shape:

- top-level `output schema` declarations own structured payload truth
- child schemas use Doctrine's keyed inheritance style with `inherit <key>` and
  `override <key>:`
- authored `optional` lowers to required nullable wire fields
- reusable definitions and recursion are explicit author-owned `def` and `ref`
  constructs
- lowered JSON Schema stays compiler-internal by default and is shown only as
  generated proof where docs, refs, or tests need it
- shipped `JsonObject` examples hard cut over from raw `json schema` authoring
  truth in the same public change

### Consequences

- The next step can be a real phase plan instead of another design placeholder.
- The compiler work now clearly includes removing the raw-schema authoring path
  for shipped `JsonObject` outputs.
- This is a breaking public language migration, so `docs/VERSIONING.md` and
  `CHANGELOG.md` must move with the code.

### Follow-ups

- Phase planning must treat `json schema` retirement, shipped example
  migration, and emitted-contract non-expansion as first-class work.

## 2026-04-15 - Implement in five code-bearing phases after planning

### Context

The earlier draft Section 7 still started with a design-lock phase even though
deep-dive pass 2 had already locked the architecture. That was no longer an
honest implementation plan.

### Options

- Keep a broad four-phase plan that still starts with design work.
- Split implementation into smaller code-bearing phases that start with the
  language surface and end with shipped-truth migration.

### Decision

Use five implementation phases:

- language surface and declaration plumbing
- schema inheritance and lowering
- validator stack and raw-summary replacement
- final-output render, emitted-contract truth, and diagnostics
- shipped examples, docs, and release guidance

### Consequences

- The plan is smaller-step and easier to audit for completeness.
- Public migration work is now explicit instead of buried at the end.
- `phase-plan` now hands implementation one authoritative checklist instead of
  another design placeholder.

### Follow-ups

- The next controller-owned step is `consistency-pass`.

## 2026-04-15 - Reopen the finish line around elegance, not just core behavior

### Context

The first implementation pass landed the core `output schema` feature, but a
deeper audit showed that the repo still carries stale compatibility surfaces
and under-justified sidecar artifacts. The validator is real, but the emitted
machine artifact and final-output example story are not clean enough yet.

### Options

- Treat the shipped code as done because the core inheritance and validation
  path works.
- Reopen the plan around a stricter finish line with no legacy structured-output
  baggage and no sidecar artifact left alive by inertia.

### Decision

Reopen the plan. The new bar is:

- delete the remaining `json schema` declaration baggage
- delete dead `schema_file` state and stale `json_schema` labels
- rename shipped proof to current `output schema` truth
- force an explicit decision on final-output example ownership
- force an explicit decision on whether `AGENTS.contract.json` survives and, if
  so, what truthful machine role it owns

### Consequences

- The plan is no longer decision-complete.
- Phase 6 is implementation-ready cleanup work, but the artifact and example
  questions in Section 3.3 must be locked before the elegance pass can honestly
  finish.
- A later release may need a stronger public contract-change note than the
  earlier plan expected.

### Follow-ups

- Resolve Section 3.3 before calling the reopened pass complete.

## 2026-04-15 - Structured final-output examples become schema-owned parsed data

### Context

The deeper audit showed that the last inelegant split was example truth. The
repo still kept structured final-output examples in external `.example.json`
files through `example_file`, which meant examples were outside Doctrine source
and never validated as instances against the lowered schema.

### Options

- Keep `.example.json` files as external proof artifacts.
- Move examples into `output schema` as parsed Doctrine-owned data.

### Decision

Move structured final-output examples into `output schema` as parsed data and
validate them against the lowered schema.

### Consequences

- `output shape.example_file` and structured-output `.example.json` support
  files should disappear.
- The parser and model need a typed example AST.
- The compiler can now validate authored examples as real instances instead of
  treating them as text.

### Follow-ups

- Add the parsed example surface in Phase 6.
- Update shipped prompts and diagnostics in the same change set.

## 2026-04-15 - Delete `AGENTS.contract.json`

### Context

The repo still emits `AGENTS.contract.json`, but it does not contain the actual
lowered OpenAI schema and repo search found no in-tree consumer beyond docs,
tests, smoke, and emitted refs.

### Options

- Keep the artifact and try to justify or rename it.
- Delete the artifact.

### Decision

Delete `AGENTS.contract.json` and its emitter.

### Consequences

- `doctrine/emit_contract.py` and the sidecar emit path in `emit_docs.py`
  should disappear.
- Emit and package proof must be updated together.
- This is a breaking public surface change and belongs in versioning and
  changelog docs.

### Follow-ups

- Remove the sidecar artifact in Phase 7.

## 2026-04-15 - OpenAI compatibility proof must include one live acceptance run

### Context

The repo already uses `jsonschema` for Draft 2020-12 validation, but that only
proves metaschema correctness. The user explicitly asked for proof of actual
OpenAI compatibility, and current repo state has no live acceptance run.

### Options

- Stop at local validation and Doctrine-owned subset checks.
- Keep local validation, add parsed example-instance validation, and require one
  real OpenAI acceptance run.

### Decision

Require both local external-validator proof and one live OpenAI acceptance run
before this reopened pass can be called complete.

### Consequences

- Validator constants must match the current OpenAI docs.
- The repo needs a narrow live-proof harness that reads the emitted schema file
  through the official OpenAI SDK.
- The worklog must record the exact live proof command and result.

### Follow-ups

- Add the live-proof harness in Phase 12.

## 2026-04-15 - Emit the real lowered schema artifact and validate that file

### Context

The branch deleted the fake `AGENTS.contract.json` summary, but that left
machine consumers with no canonical emitted schema file at all. The compiler
already has the exact lowered schema object in memory and already validates it,
so omitting the file is an over-correction.

### Options

- Keep markdown as the only emitted surface and let consumers recover schema
  truth some other way.
- Emit a Doctrine-specific summary JSON again.
- Emit the exact lowered schema as the canonical generated artifact and make the
  validator and live proof consume that file.

### Decision

Emit `schemas/<output-slug>.schema.json` as the canonical generated machine
contract for structured final outputs. Make the Python validator the primary
repo-owned proof surface for that file, and keep one live OpenAI acceptance run
as the final external proof.

### Consequences

- `emit_docs.py` must emit the real schema artifact, not just `AGENTS.md`.
- The final-output read model needs a truthful generated-schema path field.
- Public docs must teach the human contract and the machine contract together.
- The validator proof now targets the emitted artifact, not only compiler
  internals.

### Follow-ups

- Add emitted schema output in Phase 10.
- Add the emitted-file Python validator surface in Phase 11.
- Add live OpenAI acceptance proof on that emitted file in Phase 12.
