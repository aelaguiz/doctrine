---
title: "Doctrine - Previous Turn Output Input Source References - Architecture Plan"
date: 2026-04-16
status: active
fallback_policy: forbidden
owners: [aelaguiz]
reviewers: []
doc_type: architectural_change
related:
  - doctrine/grammars/doctrine.lark
  - doctrine/parser.py
  - doctrine/_model/core.py
  - doctrine/_model/io.py
  - doctrine/_compiler/types.py
  - doctrine/_compiler/resolved_types.py
  - doctrine/_compiler/resolve/io_contracts.py
  - doctrine/_compiler/resolve/addressables.py
  - doctrine/_compiler/validate/addressable_children.py
  - doctrine/_compiler/compile/outputs.py
  - doctrine/emit_docs.py
  - docs/AGENT_IO_DESIGN_NOTES.md
  - docs/LANGUAGE_REFERENCE.md
  - docs/EMIT_GUIDE.md
  - docs/VERSIONING.md
  - docs/EMIT_ROUTING_CONTRACT_FOR_FINAL_OUTPUTS_AND_REVIEWS_2026-04-15.md
  - CHANGELOG.md
  - ../rally/stdlib/rally/prompts/rally/base_agent.prompt
  - ../rally/stdlib/rally/prompts/rally/turn_results.prompt
  - ../rally/src/rally/domain/flow.py
  - ../rally/src/rally/services/flow_loader.py
  - ../rally/src/rally/services/final_response_loader.py
  - ../rally/src/rally/services/runner.py
  - ../rally/docs/RALLY_COMMUNICATION_MODEL.md
  - ../rally/docs/RALLY_MASTER_DESIGN.md
  - ../psflows/flows/lessons/prompts/shared/outputs.prompt
  - ../psflows/flows/lessons/prompts/agents/project_lead/AGENTS.prompt
---

# TL;DR

## Outcome

Doctrine and Rally get one first-class way for agent `t+1` to read agent
`t`'s selected prior output. The selected previous emitted output becomes the
single source of truth for the next input contract. Durable structured outputs
stay structured. Readable-only outputs stay readable.

## Problem

Today Rally gives later agents `home:issue.md` plus the previous turn's final
JSON control path. That works for notes and routing, but it does not give
authors a clean way to feed one selected prior output into the next turn.
The current draft also drops too much structure by forcing every selected
prior output into `MarkdownDocument`.

## Approach

Add one Rally-owned `input source` declaration in the Rally stdlib named
`RallyPreviousTurnOutput`.

- With no extra config, it means "the previous turn's final output".
- With explicit `output:`, it accepts one compiler-checked selector:
  - an `OutputDecl` ref such as `shared.outputs.LessonsStateFile`
  - or one output-binding ref such as
    `project_lead.ProjectLeadOutputs:coordination_handoff`
- This source derives the input contract from the selected previous emitted
  output instead of making authors restate `shape:` or downgrade everything to
  markdown.
- Zero-config derives the exact previous final-output contract when Doctrine
  can prove one unique predecessor final contract. If it cannot, it fails loud.
  Explicit selection derives the exact selected previous emitted-output
  contract.
- Rally reopens the previous artifact in the strongest honest native form:
  - structured JSON when the selected output has a durable structured wire
  - readable text when the selected output is readable only
  - direct runtime error when Rally cannot reopen it honestly
- Extend the existing public `final_output.contract.json` with one additive
  top-level `io` block instead of creating a second runtime contract file.

## Plan

1. Make `RallyPreviousTurnOutput` a source-specific derived-contract path in
   Doctrine.
2. Extend the existing emitted `final_output.contract.json` with previous-turn
   input metadata plus previous emitted-output metadata.
3. Teach Rally to load the richer single contract file and reopen the selected
   previous artifact in native form.
4. Support typed previous-input field access only when the selected output is
   durably structured JSON.
5. Update the Lessons proof, tests, docs, and release truth so the shipped
   story matches the actual contract.

## Non-negotiables

- No quoted string selector such as `"coordination_handoff"`.
- No second authored handoff plane. `home:issue.md` stays the shared ledger.
- No new runtime sidecar such as `runtime_io.contract.json`.
- The selected previous emitted output is the single source of truth for the
  derived previous-turn input contract.
- `RallyPreviousTurnOutput` does not let authors restate `shape:` and create a
  second contract.
- Do not coerce structured JSON outputs into markdown summaries.
- Do not pretend prose or markdown outputs have deterministic field access.
- Fail loud when the selected output is missing, ambiguous, wrong-kind, or not
  durably readable.

<!-- arch_skill:block:planning_passes:start -->
<!--
arch_skill:planning_passes
deep_dive_pass_1: done 2026-04-16
recommended_flow: research -> deep dive -> phase plan -> implement
note: This block tracks stage order only. It never overrides readiness blockers caused by unresolved decisions.
-->
<!-- arch_skill:block:planning_passes:end -->

# 0) Holistic North Star

## 0.1 The claim (falsifiable)

If Doctrine and Rally ship one Rally-owned previous-turn input source that
derives its contract from the selected prior output, then authors can chain
agents through one native previous-output surface without string selectors,
shadow contracts, or a second runtime contract file.

This claim is false if any of these remain true after the change:

- authors still have to restate `shape:` for previous-turn inputs
- structured JSON previous outputs still lose typed structure at the input
  boundary
- Rally needs a second runtime contract file to make the feature work
- prose outputs are exposed as fake deterministic field trees

## 0.2 In scope

- Add one Rally-owned `input source` declaration in Rally stdlib:

  ```prompt
  input source RallyPreviousTurnOutput: "Rally Previous Turn Output"
      optional: "Optional Source Keys"
          output: "Selected prior output declaration or output binding."
  ```

- Make this source a source-specific derived-contract path:
  - authors declare `source:` and `requirement:`
  - authors do not declare `shape:` or `structure:` on this source
  - the selected previous emitted output owns the derived contract

- Zero-config authored surface:

  ```prompt
  input PreviousTurnResult: "Previous Turn Result"
      source: rally.base_agent.RallyPreviousTurnOutput
      requirement: Advisory
  ```

  Zero-config means:

  - the previous turn's actual `final_output`
  - compile-time contract = the exact previous final-output contract when the
    flow-owned predecessor set resolves to one declaration key
  - if reachable predecessors disagree on the previous final-output contract,
    fail loud and require an explicit selector or upstream contract unification

- Explicit structured selection surface:

  ```prompt
  input PreviousLessonsState: "Previous Lessons State"
      source: rally.base_agent.RallyPreviousTurnOutput
          output: shared.outputs.LessonsStateFile
      requirement: Advisory
  ```

  This derives the exact selected previous emitted-output contract. If that
  selected output is a durable `JsonObject`, the next agent gets a typed
  previous input and may use deterministic field paths from that selected
  contract.

- Explicit output-binding selection surface:

  ```prompt
  input PreviousRoutingHandoff: "Previous Routing Handoff"
      source: rally.base_agent.RallyPreviousTurnOutput
          output: project_lead.ProjectLeadOutputs:coordination_handoff
      requirement: Advisory
  ```

  This derives the selected bound previous emitted-output contract. If that
  selected output is readable only, the next agent gets an artifact-level
  readable input and reads it as text.

- Supported authored behavior for structured previous-turn inputs:

  ```prompt
  workflow RouteByPreviousTurn: "Route By Previous Turn"
      law:
          active when PreviousTurnResult.kind == "handoff"
  ```

  Deterministic field access is in scope only when the derived previous-turn
  input is durably structured JSON.

- Supported authored behavior for readable previous-turn inputs:

  ```prompt
  workflow ReadPreviousHandoff: "Read Previous Handoff"
      sequence steps:
          "Read `PreviousRoutingHandoff` before `Issue Ledger`."
  ```

- Extend the existing public `final_output.contract.json` with one additive
  top-level `io` block that carries:
  - current previous-turn input requests
  - previous emitted-output declaration metadata
  - previous emitted-output binding metadata

- Teach Rally to reopen the selected prior artifact in the strongest honest
  native form:
  - previous `final_output` JSON from `last_message.json`
  - ordinary `target: File` outputs from the emitted file path
  - Rally-owned note outputs from Rally-managed note identity

- Preserve native contract by readback kind:
  - `structured_json`
  - `readable_text`
  - `unsupported`

- Keep the surface additive:
  - existing prompts keep working
  - existing `final_output.contract.json` stays the one public runtime contract
    file
  - the new `io` block is additive

## 0.3 Out of scope

- Quoted-string selectors or dotted string paths.
- A second emitted runtime contract file such as `runtime_io.contract.json`.
- A second shared authored ledger beside `home:issue.md`.
- Generic `input schema:` language expansion for all inputs.
- General `OutputsDecl` promotion into a new generic addressable root unless
  repo truth later proves it is needed.
- Forcing previous-turn inputs to restate `shape:` or `structure:`.
- Coercing every prior output into `MarkdownDocument`.
- Fake deterministic field access for prose, markdown, comment, or note
  outputs that Rally only has as text.
- Parser-heavy field extraction from prose outputs.
- Arbitrary turn-history queries beyond the immediately previous turn.
- Multi-output selection, merging, or fallback ranking.

## 0.4 Definition of done (acceptance evidence)

- The zero-config authored form compiles:

  ```prompt
  input PreviousTurnResult: "Previous Turn Result"
      source: rally.base_agent.RallyPreviousTurnOutput
      requirement: Advisory
  ```

- Zero-config previous-turn inputs derive the exact previous final-output
  contract without repeating `shape:` when Doctrine can prove one unique
  predecessor final contract.
- Explicit `output:` selectors compile for both `NameRef` and `AddressableRef`
  forms.
- Previous structured JSON outputs reopen as typed previous inputs, and their
  deterministic field paths compile when the selected output is durably
  structured.
- Previous readable outputs reopen as readable artifact-level inputs without
  fake field projection.
- Invalid authored forms fail loud:
  - string selector
  - missing selector ref
  - wrong-kind selector ref
  - ambiguous binding root
  - ambiguous predecessor final-output contract on zero-config
  - zero-config previous-turn input outside flow-owned predecessor analysis
  - explicit selector that resolves to a non-emitted `TurnResponse`
  - forbidden local `shape:` or `structure:` on this source
  - structured field access attempted on a readable-only previous input
- `final_output.contract.json` stays the one public emitted runtime contract
  file and gains one additive top-level `io` block.
- Rally loads that richer single contract file, reopens the selected previous
  artifact in native form, and injects it during prompt build.
- Unsupported target kinds fail with direct runtime errors.
- Doctrine tests, Rally tests, package verification, and the real Lessons proof
  all pass.

## 0.5 Key invariants (fix immediately if violated)

- One selector surface:
  - zero-config previous `final_output`
  - or explicit `output:` typed ref
- One source of truth for derived previous-input contract:
  - the selected previous emitted output
- One public runtime contract file:
  - `final_output.contract.json`
- Structured where honest, readable where honest, fail loud otherwise.
- No lossy markdown coercion of structured JSON outputs.
- No fake field access on readable-only previous inputs.
- No string selectors.
- No second authored communication plane.

# 1) Key Design Considerations (what matters most)

## 1.1 Priorities (ranked)

1. Minimize author burden in the common case.
2. Preserve native structured contract where the previous output already has
   one.
3. Keep one public runtime contract file.
4. Stay inside Doctrine's existing strong-ref model.
5. Fail loud instead of guessing or silently degrading.

## 1.2 Constraints

- `RecordScalarValue` already supports `NameRef` and `AddressableRef` in
  `doctrine/_model/io.py`.
- Generic input compilation currently requires `source`, `shape`, and
  `requirement`, so this feature needs one narrow source-specific exception in
  `doctrine/_compiler/compile/outputs.py`.
- `AgentContract.output_bindings_by_path` already exists and should stay the
  single compiler truth for `outputs` bindings.
- Doctrine already has flow-owned runtime-root collection and target flow-graph
  extraction during emit, which gives this feature a clean place to resolve
  exact predecessor sets.
- `final_output.contract.json` is already a public emitted contract surface and
  repo policy already prefers extending it over creating a second public
  contract file.
- Rally currently loads only `final_output.contract.json`, injects only
  `AGENTS.md`, and only reopens `last_message.json`.
- Readable outputs do not have a durable deterministic field tree today.
- Rally stores exactly one durable turn-response payload today. That means
  zero-config exact previous-final resolution is honest, but non-final
  `TurnResponse` outputs are not durable previous artifacts.

## 1.3 Architectural principles (rules we will enforce)

- Reuse existing Doctrine ref shapes. Do not invent a selector mini-language.
- Keep the selected previous emitted output as the single source of truth.
- Let this source derive contract truth. Do not make authors repeat it.
- Extend the existing public contract file. Do not create a second one.
- Preserve structured JSON natively when Rally can reopen it honestly.
- Preserve readable outputs as text when that is the strongest honest form.
- Do not pretend prose is structured.
- Keep generic language expansion narrow. This is a source-specific path, not a
  new generic input-schema system.

## 1.4 Known tradeoffs (explicit)

- `RallyPreviousTurnOutput` becomes one narrow exception to the usual "input
  must declare `shape:`" rule. That is deliberate. The exception is better than
  duplicating output contract truth in authored inputs.
- `final_output.contract.json` becomes a broader agent runtime contract than
  its name implies. That is still the cleaner choice because the file is
  already public and additive extension is the repo's chosen compatibility
  posture.
- Zero-config previous `final_output` now depends on flow-owned predecessor
  analysis. That is stricter, but it is the honest way to get exact prior-final
  truth without shadow contracts or base-schema fallback.
- Standalone agent compile with zero-config previous-turn input should fail
  loud when no predecessor graph is available.
- Explicit selectors may still compile locally, but flow-owned validation must
  prove that the selected output is a real previous emitted artifact. A
  non-final `TurnResponse` does not meet that bar.

# 2) Problem Statement (existing architecture + why change)

## 2.1 What exists today

- Doctrine already has typed refs for source config values.
- Doctrine already resolves concrete output declarations and `outputs` binding
  paths through `AgentContract`.
- Doctrine already publishes one public runtime contract file:
  `final_output.contract.json`.
- Rally already stores previous final JSON in `last_message.json`.
- Rally and psflows currently use `home:issue.md` plus the latest valid turn
  result as the practical previous-turn context path.

## 2.2 What's broken / missing (concrete)

- There is no first-class authored way to say "give me that previous emitted
  output as an input".
- The string workaround is weak and not rename-safe.
- The old draft fixed the selection problem but still lost too much structure
  by forcing everything to `MarkdownDocument`.
- That draft also invented a second runtime contract file even though Doctrine
  already has one public emitted runtime contract surface.
- The current runtime has no honest distinction between:
  - prior outputs Rally can reopen as structured JSON
  - prior outputs Rally can reopen as readable text
  - prior outputs Rally cannot reopen honestly at all

## 2.3 Constraints implied by the problem

- The fix must span authored source syntax, compile-time selector resolution,
  emitted contract metadata, and Rally runtime readback.
- The solution must preserve the strongest honest native contract for the
  selected output.
- The solution must not lie about prose outputs having deterministic fields.
- The zero-config path must stay tiny and exact when the flow graph can prove
  it, and fail loud when it cannot.
- The public runtime contract story must stay single-file and additive.

<!-- arch_skill:block:research_grounding:start -->
# 3) Research Grounding (external + internal "ground truth")

## 3.1 External anchors (papers, systems, prior art)

- None needed here. Repo truth is sufficient and more constraining than outside
  analogies.

## 3.2 Internal ground truth (code as spec)

- Doctrine already parses the selector shapes this feature needs:
  - `record_head` accepts `name_ref` and `path_ref` in
    [doctrine.lark](/Users/aelaguiz/workspace/doctrine/doctrine/grammars/doctrine.lark:822)
  - `path_ref` lowers to `AddressableRef` in
    [parser.py](/Users/aelaguiz/workspace/doctrine/doctrine/parser.py:100)
- Generic source config values already allow strong refs:
  - `RecordScalarValue = str | NameRef | AddressableRef` in
    [io.py](/Users/aelaguiz/workspace/doctrine/doctrine/_model/io.py:18)
- Input compilation currently requires `shape:`:
  - `_compile_input_decl()` in
    [outputs.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/compile/outputs.py:25)
- Doctrine already computes concrete output declarations and bindings:
  - `AgentContract.output_bindings_by_path` in
    [resolved_types.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolved_types.py:355)
  - `_resolve_agent_contract()` in
    [io_contracts.py](/Users/aelaguiz/workspace/doctrine/doctrine/_compiler/resolve/io_contracts.py:21)
- Doctrine already has one public emitted runtime contract file:
  - `_final_output_contract_payload()` in
    [emit_docs.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_docs.py:236)
- Repo versioning truth already says to extend that file rather than invent a
  second public contract file:
  - [VERSIONING.md](/Users/aelaguiz/workspace/doctrine/docs/VERSIONING.md:65)
  - [EMIT_ROUTING_CONTRACT_FOR_FINAL_OUTPUTS_AND_REVIEWS_2026-04-15.md](/Users/aelaguiz/workspace/doctrine/docs/EMIT_ROUTING_CONTRACT_FOR_FINAL_OUTPUTS_AND_REVIEWS_2026-04-15.md:105)
- Rally currently loads only that one contract file:
  - [flow_loader.py](/Users/aelaguiz/workspace/rally/src/rally/services/flow_loader.py:171)
- Rally currently injects only static `AGENTS.md`:
  - [_build_agent_prompt()](/Users/aelaguiz/workspace/rally/src/rally/services/runner.py:1118)
- Doctrine already has the flow-owned graph facts needed to resolve exact
  predecessor sets during emit:
  - `emit_target()` in
    [emit_docs.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_docs.py:86)
  - `extract_target_flow_graph_from_units()` in
    [emit_flow.py](/Users/aelaguiz/workspace/doctrine/doctrine/emit_flow.py:87)
- Rally already reopens previous final JSON in native form:
  - `load_turn_result_payload()` in
    [final_response_loader.py](/Users/aelaguiz/workspace/rally/src/rally/services/final_response_loader.py:58)
- Rally already has a shared base turn-result family, but that family should
  be treated as reusable schema truth, not as an always-on fallback for
  previous-turn exactness:
  - [turn_results.prompt](/Users/aelaguiz/workspace/rally/stdlib/rally/prompts/rally/turn_results.prompt:6)
- Doctrine already treats `JsonObject` inputs as first-class input roots in the
  language. Shipped examples already branch on input fields such as
  `CurrentHandoff.rewrite_regime` and
  `RouteFacts.current_specialist_output_missing` in
  [examples/35_basis_roles_and_rewrite_evidence](/Users/aelaguiz/workspace/doctrine/examples/35_basis_roles_and_rewrite_evidence/prompts/AGENTS.prompt:64)
  and
  [examples/41_route_only_reroute_handoff](/Users/aelaguiz/workspace/doctrine/examples/41_route_only_reroute_handoff/prompts/AGENTS.prompt:52).
  That means downgrading prior JSON to markdown would be a weaker model than
  Doctrine already ships for ordinary inputs.

## 3.3 Decision gaps that must be resolved before implementation

- None remain at planning time.

Resolved here:

- keep one public emitted contract file
- make `RallyPreviousTurnOutput` derive contract truth instead of repeating
  `shape:`
- preserve structured JSON natively when durable
- keep prose outputs readable only
- make zero-config previous `final_output` exact when the predecessor set makes
  it provable, and fail loud otherwise

<!-- arch_skill:block:research_grounding:end -->

<!-- arch_skill:block:current_architecture:start -->
# 4) Current Architecture (as-is)

## 4.1 On-disk structure

- Doctrine emits `AGENTS.md`.
- When an agent has `final_output` or `review`, Doctrine also emits
  `final_output.contract.json`.
- For structured final outputs, Doctrine may also emit
  `schemas/<output-slug>.schema.json`.
- Rally currently treats `AGENTS.md` plus `final_output.contract.json` as the
  required compiled package pair.

## 4.2 Control paths (runtime)

- Input compilation is static and authored:
  - `source:`
  - `shape:`
  - `requirement:`
- Final-output contract emission is owned by `emit_docs.py`.
- Rally flow loading reads the single emitted contract file into
  `CompiledAgentContract`.
- Rally prompt building injects only static `AGENTS.md`.
- Rally previous-final readback is limited to `last_message.json`.
- Ordinary outputs and ordinary input requests are not serialized into the
  runtime contract today.

## 4.3 Object model + key abstractions

- `RecordScalarValue` already supports strong refs for source config.
- `AgentContract.outputs` and `AgentContract.output_bindings_by_path` already
  know the exact output declaration and bound-output truth the feature needs.
- `CompiledAgent` today only carries `final_output`, `review`, and `route`.
- Rally `CompiledAgentContract` today only carries final-output and review
  contract truth from one metadata file.
- There is no current typed model for:
  - previous-turn input requests
  - previous emitted-output readback metadata
  - readback mode classification

## 4.4 Observability + failure behavior today

- The gap fails by absence, not by an explicit contract:
  - later agents read `home:issue.md`
  - or they infer from the latest turn result
  - or they rely on raw file knowledge
- The old draft would have closed that only halfway:
  - strong selector yes
  - typed prior JSON no
  - one-file runtime contract no
- The real Lessons `coordination_handoff` case still sits on a target Rally
  does not reopen today.

<!-- arch_skill:block:current_architecture:end -->

<!-- arch_skill:block:target_architecture:start -->
# 5) Target Architecture (to-be)

## 5.1 On-disk structure (future)

Keep the compiled package shape simple:

- `AGENTS.md`
- `final_output.contract.json`
- existing emitted schema files where already applicable

Do not add `runtime_io.contract.json`.

Extend `final_output.contract.json` with one additive top-level `io` block:

```json
{
  "contract_version": 1,
  "agent": { "...": "..." },
  "route": { "...": "..." },
  "final_output": { "...": "..." },
  "review": { "...": "..." },
  "io": {
    "previous_turn_inputs": [
      {
        "input_key": "previous_turn_result",
        "input_title": "Previous Turn Result",
        "selector_kind": "default_final_output",
        "contract_mode": "structured_json",
        "resolved_declaration_key": "lessons_writer.LessonsTurnResult",
        "shape_name": "LessonsTurnResultJson",
        "shape_title": "Lessons Turn Result JSON"
      }
    ],
    "outputs": [
      {
        "declaration_key": "shared.outputs.LessonsStateFile",
        "declaration_name": "LessonsStateFile",
        "title": "Lessons State File",
        "readback_mode": "structured_json",
        "target_kind": "File",
        "target_config": {
          "path": "artifacts/LESSONS_STATE.json"
        }
      },
      {
        "declaration_key": "project_lead.CoordinationHandoff",
        "declaration_name": "CoordinationHandoff",
        "title": "Coordination Handoff",
        "readback_mode": "readable_text",
        "target_kind": "RallyOwnedNote",
        "target_config": {
          "note_kind": "coordination_handoff"
        }
      }
    ],
    "output_bindings": [
      {
        "binding_path": "coordination_handoff",
        "declaration_key": "project_lead.CoordinationHandoff"
      }
    ]
  }
}
```

The exact wire fields may shift, but the architecture choice is fixed:

- one file
- additive top-level `io`
- enough metadata for Rally to resolve current previous-turn requests and
  previous-agent emitted-output readback truth

This sample uses a durable JSON file on purpose. A non-final `TurnResponse`
must not appear here as a reopenable `structured_json` prior artifact.
Bindings should point at declaration keys already listed in `io.outputs`
instead of duplicating target metadata.

## 5.2 Control paths (future)

### Authored source contract

`RallyPreviousTurnOutput` becomes one Rally-owned source-specific derived
contract path.

Authoring rules:

- `requirement:` remains authored locally
- `shape:` is forbidden on this source
- `structure:` is forbidden on this source
- optional `output:` accepts only:
  - `NameRef`
  - `AddressableRef`

Invalid:

```prompt
input PreviousRoutingHandoff: "Previous Routing Handoff"
    source: rally.base_agent.RallyPreviousTurnOutput
        output: "coordination_handoff"
    requirement: Advisory
```

Invalid:

```prompt
input PreviousTurnResult: "Previous Turn Result"
    source: rally.base_agent.RallyPreviousTurnOutput
    shape: MarkdownDocument
    requirement: Advisory
```

### Compile-time contract derivation

There are two derivation modes.

1. No `output:` selector:

- semantic meaning: previous turn's actual `final_output`
- flow-owned resolution rule:
  - if one reachable predecessor final-output declaration key reaches this
    agent, derive that exact contract
  - if several reachable predecessors reach this agent but all use the same
    final-output declaration key, derive that exact contract
  - otherwise fail loud and require an explicit selector or upstream contract
    unification
- deterministic field surface: the exact resolved previous final-output
  contract

2. Explicit `output:` selector:

- semantic meaning: exact selected previous emitted output
- local contract rule: exact selected output declaration or binding
- flow-owned validity rule:
  - the selector must resolve to a real previous emitted artifact on every
    reachable predecessor that can hand off here
  - `target: TurnResponse` is valid only when it is the actual previous
    `final_output`
  - durable side-artifact targets such as `File` or Rally-owned target
    families may be reopened by target family
  - non-final `TurnResponse` selections fail loud
- deterministic field surface:
  - available when the selected emitted output is durably structured JSON
  - unavailable when the selected emitted output is readable only

Compile-time and runtime responsibilities are different on purpose:

- compile-time predecessor analysis proves that every reachable predecessor can
  satisfy the selected contract
- runtime readback always reopens artifacts from the actual immediately
  previous turn
- runtime never guesses across several prior turns

### Runtime readback modes

Every selected prior output resolves to one of three runtime readback modes.

1. `structured_json`

- previous final-output JSON in `last_message.json`
- `target: File` outputs whose declared shape is `JsonObject` and whose file
  content is valid JSON
- future Rally-owned structured targets if Rally stores them durably

Runtime behavior:

- Rally reopens the raw JSON object
- Rally injects that raw JSON into the prompt
- Doctrine treats the previous input as a typed structured input

2. `readable_text`

- previous prose final outputs if Rally-managed flows ever expose them
- `target: File` outputs with readable shapes
- Rally-owned note outputs
- Rally-owned readable targets such as note-backed comment, markdown, and
  plain-text artifacts

Runtime behavior:

- Rally reopens the raw readable artifact
- Rally injects readable text into the prompt
- Doctrine treats the previous input as an artifact-level readable input, not a
  field-addressable structure

3. `unsupported`

- selected targets with no Rally readback adapter
- selected outputs whose durable state is not present
- selected outputs whose stored value contradicts the declared readback mode
- selected `TurnResponse` declarations that are not the actual previous
  `final_output`

Runtime behavior:

- fail loud with a direct runtime error

### Prompt injection

All prompt input is still text at the adapter boundary, but the packet should
preserve native wire form instead of paraphrasing it.

Structured example:

```md
## Previous Turn Result

```json
{
  "kind": "handoff",
  "next_owner": "developer",
  "summary": null,
  "reason": null,
  "sleep_duration_seconds": null
}
```
```

Readable example:

```md
## Previous Routing Handoff

<raw prior handoff text>
```

This is not a markdown summary of a JSON contract. It is the native previous
artifact rendered into the prompt.

## 5.3 Object model + abstractions (future)

### Doctrine compile model

Add one narrow source-specific previous-turn input model:

- selector kind:
  - `default_final_output`
  - `output_decl`
  - `output_binding`
- derived contract mode:
  - `structured_json`
  - `readable_text`
- resolved output declaration key when explicit

This model belongs under the compiled agent and emitted contract serializer. It
does not require a new generic input-schema system.

### Derived input surface rules

`RallyPreviousTurnOutput` derives from output truth like this:

- input title: authored locally
- input requirement: authored locally
- source title and selector: authored locally
- artifact contract: derived from selected output
- target and delivery details: not copied into the input contract

For structured JSON selected outputs:

- preserve native `JsonObject` contract
- preserve schema-backed payload truth from the selected output family
- expose deterministic field addressing on the previous input root

For readable selected outputs:

- preserve artifact-level readable shape
- do not synthesize a field tree from comment headings, prose sections, or note
  prose

### Rally runtime model

Extend Rally's loaded compiled contract model with the new `io` block from the
same metadata file. Do not create a second loader path.

Rally runtime needs:

- current agent previous-turn input requests
- previous agent emitted-output metadata
- previous agent output-binding metadata

Rally uses those two layers differently:

- current-agent metadata tells Rally what shape the current prompt expects
- previous-turn artifacts come from the actual immediately previous turn home
- predecessor-set analysis never changes which turn Rally reads; it only proves
  compile-time contract compatibility

### Zero-config previous final-output contract

Zero-config previous final-output derivation is special:

- compile-time contract = exact previous final-output contract when the
  predecessor set proves one declaration key
- runtime data = actual previous `last_message.json`
- deterministic fields = the exact resolved prior-final contract
- ambiguous predecessor final-output sets fail loud
- no-graph standalone compile fails loud

This keeps zero-config tiny and honest.

## 5.4 Invariants and boundaries

- `RallyPreviousTurnOutput` is the one source-specific exception to the normal
  input `shape:` rule.
- Explicit selector = exact previous emitted-output truth.
- Zero-config = exact previous final-output truth when the flow graph proves
  it, and direct error otherwise.
- Structured JSON survives the input boundary as structured JSON when Rally can
  reopen it honestly.
- Readable outputs survive the input boundary as readable artifacts.
- Readable outputs do not gain fake field-level addressing.
- `final_output.contract.json` stays the one public emitted runtime contract
  file.
- No second authored communication plane.
- No parser-heavy prose extraction in the first cut.

<!-- arch_skill:block:target_architecture:end -->

<!-- arch_skill:block:call_site_audit:start -->
# 6) Call-Site Audit (exhaustive change inventory)

## 6.1 Change map (table)

| Area | File | Symbol / Call site | Current behavior | Required change | Why | New API / contract | Tests impacted |
| ---- | ---- | ------------------ | ---------------- | --------------- | --- | ------------------ | -------------- |
| Grammar reuse | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py` | `record_head`, `path_ref` | Already parses `name_ref` and `path_ref` in record scalars. | Keep unchanged. | Reuse shipped strong-ref syntax. | No new grammar. | Parser coverage only if diagnostics text changes. |
| Input compile | `doctrine/_compiler/compile/outputs.py` | `_compile_input_decl()` | Always requires `shape:` on inputs. | Add one narrow source-specific exception for `RallyPreviousTurnOutput`; reject local `shape:` and `structure:` there; render derived contract summary instead. | Avoid duplicate contract truth. | Source-derived previous-turn input contract. | New Doctrine unit tests for valid and invalid authored forms. |
| Selector resolution | `doctrine/_compiler/resolve/outputs.py`, `doctrine/_compiler/resolve/io_contracts.py`, `doctrine/_compiler/flow.py`, `doctrine/emit_docs.py` | input-source resolution, `AgentContract.output_bindings_by_path`, target flow graph | Input sources resolve generic config only; ordinary output bindings stay compiler-internal; zero-config has no predecessor-aware resolution. | Add narrow previous-turn selector resolver using `AgentContract.outputs`, `output_bindings_by_path`, and flow-owned predecessor analysis. | Strong refs without a new selector language, plus exact-or-error zero-config. | `output:` accepts `NameRef` or `AddressableRef`; zero-config resolves from predecessor final-output declaration keys. | Focused compile, emit, and diagnostics tests. |
| Structured input addressability | `doctrine/_compiler/resolve/addressables.py`, `doctrine/_compiler/validate/addressable_children.py`, related field-node helpers | addressable input paths | No previous-turn derived structured input model exists. | Add source-specific addressability for derived structured previous inputs only. | Preserve typed JSON where honest. | Previous structured inputs expose field paths; readable ones do not. | Law/review/path tests for structured previous inputs and fail-loud readable misuse. |
| Compiled agent model | `doctrine/_compiler/types.py`, `doctrine/_compiler/compile/agent.py` | `CompiledAgent` | Carries `final_output`, `review`, and `route` only. | Add compiled previous-turn input specs and previous emitted-output readback specs needed by emit. | One canonical compile model for serializer and renderer. | Additive compiled `io` contract model. | `tests/test_emit_docs.py` and targeted compile tests. |
| Emit contract | `doctrine/emit_docs.py` | `_final_output_contract_payload()` | Emits one public runtime contract file with `agent`, `route`, `final_output`, and optional `review`. | Extend that file with additive top-level `io`; do not create `runtime_io.contract.json`. | Keep one public runtime contract file. | `final_output.contract.json.io`. | `tests/test_emit_docs.py`, `make verify-package`, corpus proof if touched. |
| Doctrine public docs | `docs/AGENT_IO_DESIGN_NOTES.md`, `docs/LANGUAGE_REFERENCE.md`, `docs/EMIT_GUIDE.md`, `docs/VERSIONING.md`, `CHANGELOG.md` | live docs and release truth | Docs teach current input/output model and current single contract file. | Update docs to teach the new source-specific derived-input contract and additive `io` block on the existing file. | Keep docs aligned with shipped truth. | Updated public contract story. | `make verify-package` if release truth changes. |
| Rally stdlib | `../rally/stdlib/rally/prompts/rally/base_agent.prompt` | shared inputs and sources | No previous-turn source exists. | Add `input source RallyPreviousTurnOutput` with source-specific prose and examples; keep it opt-in. | Rally should own Rally-specific source behavior. | New stdlib source declaration. | Rally stdlib prompt tests and build/load proof. |
| Rally contract model | `../rally/src/rally/domain/flow.py` | `CompiledAgentContract` | Carries final-output and review metadata only. | Add typed `io` contract model on the same loaded metadata file. | Runner needs previous-turn input requests plus previous emitted-output metadata. | Additive `CompiledAgentContract.io`. | Rally domain and loader tests. |
| Rally loader | `../rally/src/rally/services/flow_loader.py` | compiled agent load | Requires `AGENTS.md` plus `final_output.contract.json`. | Keep the same required pair, but parse the richer contract payload and validate the new `io` block when present. | One file, no sidecar. | Same file, richer payload. | Loader tests. |
| Rally previous-output readback | `../rally/src/rally/services/final_response_loader.py` or new sibling service, `../rally/src/rally/services/runner.py` | previous final-output load and prompt injection | Only opens `last_message.json`; prompt build injects only static `AGENTS.md`. | Add previous-output renderer that reopens selected prior artifacts in native form and appends them during prompt build. | Make prior outputs real runtime inputs. | Structured JSON or readable-text prompt packets. | Runner and readback tests. |
| Rally note identity | `../rally/src/rally/services/issue_ledger.py` | note lookup | Stores notes, but not by output identity. | Add Rally-owned note identity fields and lookup helpers for readback-capable note targets. | Read note-backed outputs by declaration or binding, not by "latest note". | Rally-owned note readback identity. | Issue-ledger tests and runtime tests. |
| Lessons proof | `../psflows/flows/lessons/**` | `coordination_handoff` path | Real motivating path uses a target Rally does not reopen yet. | Migrate the proof path onto a Rally-owned readback-capable target or keep it explicitly unsupported until migrated. | Real end-to-end proof matters. | Concrete Lessons proof chain. | Cross-repo proof and build artifact updates as needed. |

## 6.2 Migration notes

- Compatibility posture stays additive.
- Keep `final_output.contract.json` on version `1` if the additive `io` block
  can preserve wire compatibility, the same way the top-level `route` block
  stayed additive.
- Do not create or ship `runtime_io.contract.json`.
- Zero-config previous final-output access should be exact-or-error, not
  base-schema fallback.
- Direct compile without flow-owned predecessor facts should reject
  zero-config previous-turn input.
- Explicit richer prior-final behavior must resolve to a real previous emitted
  artifact, not just a declaration that exists on paper.
- Readable prior outputs stay artifact-level only. That is not a missing
  feature. It is the honest boundary.

## Pattern Consolidation Sweep (anti-blinders; scoped by plan)

| Area | File / Symbol | Pattern to adopt | Why (drift prevented) | Proposed scope |
| ---- | ------------- | ---------------- | ---------------------- | -------------- |
| Selector syntax | `doctrine/grammars/doctrine.lark`, `doctrine/parser.py` | Reuse `name_ref` and `path_ref` | Prevent a second selector language | include |
| Contract ownership | selected `OutputDecl` | Derived-contract input source | Prevent duplicated `shape:` truth on previous-turn inputs | include |
| Public runtime contract | `doctrine/emit_docs.py` | Extend `final_output.contract.json` | Prevent contract-file sprawl | include |
| Structured preservation | structured previous outputs | Preserve native JSON | Prevent lossy markdown downgrade | include |
| Readable preservation | readable previous outputs | Preserve readable artifact only | Prevent fake field access | include |
| Generic input-schema expansion | Doctrine core input syntax | Avoid new generic `input schema:` | Keep language growth narrow | exclude |
| Generic `OutputsDecl` addressability | generic addressable root model | Avoid widening unless forced later | Prevent language-scope jump | exclude |

<!-- arch_skill:block:call_site_audit:end -->

<!-- arch_skill:block:phase_plan:start -->
# 7) Depth-First Phased Implementation Plan (authoritative)

## Phase 1 — Doctrine derived-source contract

* Goal:
  - Make `RallyPreviousTurnOutput` a real source-specific derived-contract path
    in Doctrine.
* Work:
  - This phase closes the authoring gap without widening grammar. It teaches
    Doctrine how to derive previous-turn input truth from selected outputs and
    how to make zero-config previous final-output exact when the predecessor
    graph proves one unique prior-final contract.
* Checklist (must all be done):
  - Add a narrow previous-turn source resolver for
    `source: rally.base_agent.RallyPreviousTurnOutput`.
  - Support zero-config selection of previous `final_output`.
  - Support explicit `NameRef` and `AddressableRef` selectors.
  - Use runtime emit roots plus target flow-graph extraction to compute the
    reachable predecessor set for each concrete agent that uses zero-config
    previous-turn input.
  - Make this source reject local `shape:` and `structure:` so the selected
    output stays the only contract owner.
  - Keep `requirement:` authored locally.
  - Define the compile-time derivation rule:
    - zero-config derives the exact previous final-output contract when the
      predecessor set proves one declaration key
    - ambiguous predecessor final-output sets fail loud
    - no-graph standalone compile fails loud for zero-config
    - explicit selector derives the exact selected previous emitted-output
      contract
    - explicit `TurnResponse` selector is valid only when it resolves to the
      actual previous `final_output`
  - Keep authored contract derivation separate from flow-owned emitted-artifact
    eligibility validation:
    - local compile may derive an explicit selector contract from the selected
      declaration or binding
    - flow-owned emit validation must prove that the selector resolves to a
      real previous emitted artifact on every reachable predecessor
  - Add a source-specific derived-contract model on the compiled agent surface.
  - Add source-specific structured-input addressability only when the derived
    contract is durably structured JSON.
  - Fail loud on:
    - string selector values
    - missing refs
    - wrong-kind refs
    - ambiguous binding roots
    - ambiguous predecessor final-output sets
    - zero-config previous-turn input without predecessor graph facts
    - explicit selector that resolves to a non-emitted `TurnResponse`
    - local `shape:` or `structure:` on this source
    - structured field access attempted on a readable-only previous input
  - Add concise code comments only at the source-specific exception boundary if
    needed.
* Verification (required proof):
  - Focused Doctrine unit tests for:
    - zero-config previous final-output source compile
    - zero-config exact predecessor-final contract resolution
    - zero-config ambiguous predecessor-final compile failure
    - zero-config standalone-compile failure without flow graph
    - explicit output-declaration selector compile
    - explicit output-binding selector compile
    - flow-owned failure for explicit non-final `TurnResponse` selector
    - flow-owned success for explicit durable file selector
    - invalid string selector
    - invalid missing or wrong-kind selector
    - forbidden local `shape:` and `structure:`
    - structured field access on derived structured previous inputs
    - fail-loud readable-only field access
* Exit criteria (all required):
  - Doctrine can compile previous-turn inputs without authored `shape:`.
  - Zero-config previous final-output is exact when the predecessor set proves
    it and fails loud otherwise.
  - Explicit selectors derive the exact selected previous emitted-output
    contract.
  - The compiler keeps structured and readable derived previous inputs
    distinct.
  - Invalid authored forms fail loud with direct errors.

## Phase 2 — Extend the existing public contract file

* Goal:
  - Serialize previous-turn input requests and previous emitted-output
    readback truth into the existing `final_output.contract.json`.
* Work:
  - This phase keeps the runtime contract story single-file and additive. It
    adds the metadata Rally needs for current previous-turn input requests and
    previous-agent emitted outputs without inventing a second public file.
* Checklist (must all be done):
  - Add a compiled `io` contract model under `CompiledAgent`.
  - Serialize an additive top-level `io` block from `emit_docs.py`.
  - Keep `final_output`, `review`, and `route` shapes unchanged.
  - Keep the file name `final_output.contract.json`.
  - Reuse `AgentContract.outputs` and `output_bindings_by_path` as the only
    compiler truth for output declarations and bound outputs.
  - Serialize enough metadata for Rally to reopen prior outputs honestly:
    - previous-turn input selector kind
    - derived contract mode
    - resolved zero-config predecessor-final declaration key when present
    - resolved zero-config shape identity when present
    - previous emitted-output declaration metadata
    - previous emitted-output binding metadata
    - binding-to-declaration linkage through declaration keys already present in
      the outputs table
    - emitted-vs-non-emitted eligibility for prior-output readback
    - readback-relevant target config
  - Decide and document whether `contract_version` stays `1`; if it changes,
    update the versioning story everywhere.
* Verification (required proof):
  - Focused emit tests for the new top-level `io` block.
  - Focused emit tests for binding metadata referential integrity.
  - `make verify-examples`
  - `make verify-package`
  - `make verify-diagnostics` if new diagnostics are added
* Exit criteria (all required):
  - `final_output.contract.json` remains the one public emitted runtime
    contract file.
  - The file now carries additive `io` metadata for this feature.
  - No `runtime_io.contract.json` exists.
  - Public contract verification passes.

## Phase 3 — Rally load path and exact zero-config previous final-output runtime

* Goal:
  - Make the zero-config previous-final-output path work end to end through the
    richer single contract file.
* Work:
  - This phase uses Rally's strongest existing durable path:
    `last_message.json`. It proves the single-file contract load, the new
    source declaration, and the native structured JSON readback path for the
    common case with exact prior-final contract truth.
* Checklist (must all be done):
  - Add `input source RallyPreviousTurnOutput` to Rally stdlib.
  - Keep it opt-in. Do not add it to `RallyManagedInputs`.
  - Extend Rally `CompiledAgentContract` with typed `io` data from the same
    contract file.
  - Update Rally loader validation to parse the richer
    `final_output.contract.json`.
  - Build the zero-config previous-final-output packet renderer.
  - Reopen raw previous final JSON from `last_message.json`.
  - Inject raw JSON into prompt build, not a prose summary.
  - Validate that the previous final JSON matches the exact resolved
    predecessor-final contract.
  - Use the actual immediately previous turn directory for zero-config readback.
* Verification (required proof):
  - Focused Rally unit tests for:
    - contract load
    - zero-config previous-final-output request load
    - exact predecessor-final contract load
    - raw JSON prompt packet injection
    - ambiguous predecessor-final failure
    - missing `last_message.json` failure for zero-config readback
* Exit criteria (all required):
  - Rally still loads one runtime contract file.
  - A current agent can request zero-config previous final-output input.
  - The prior final JSON is reopened in native form and injected into the
    prompt.
  - Zero-config previous final-output is exact-or-error.
  - The default previous-turn path works without authored `shape:`.

## Phase 4 — Explicit selectors and honest emitted-output readback modes

* Goal:
  - Make explicit prior-output selection work for supported target kinds with
    the correct structured-vs-readable boundary.
* Work:
  - This phase extends the runtime from the common zero-config path to explicit
    output declarations and bound outputs. It keeps the contract honest by
    separating `structured_json`, `readable_text`, and `unsupported`, and by
    refusing to treat non-emitted `TurnResponse` declarations as reopenable
    prior artifacts.
* Checklist (must all be done):
  - Resolve explicit previous-output requests against the previous agent's
    serialized emitted outputs and bindings.
  - Resolve binding metadata through the referenced output declaration key
    instead of duplicating target config on the binding itself.
  - Use the actual immediately previous turn directory for explicit readback.
  - Support `structured_json` readback for:
    - previous final-output JSON
    - `target: File` outputs whose declared shape is `JsonObject` and whose
      file content is valid JSON
  - Support `readable_text` readback for:
    - readable file outputs
    - Rally-owned note outputs
    - Rally-owned readable targets such as note-backed comment, markdown, and
      plain-text artifacts
  - Add Rally-owned note identity fields and note lookup helpers for
    readback-capable note targets.
  - Resolve file-backed prior outputs from the previous turn home using the
    emitted target path and fail loud when the file is missing or escapes the
    turn-owned artifact root.
  - Fail loud when an explicit selector points at a `TurnResponse` declaration
    that is not the actual previous `final_output`.
  - Fail loud when a selected output resolves to `unsupported`.
  - Keep readable previous outputs artifact-level only.
  - Do not add parser-heavy extraction from prose outputs.
* Verification (required proof):
  - Focused Rally unit tests for:
    - explicit output-declaration selector runtime resolution
    - explicit output-binding selector runtime resolution
    - non-final `TurnResponse` selector failure
    - structured JSON file-output readback
    - missing-file failure for file-backed prior output
    - out-of-root file-path rejection for file-backed prior output
    - readable file-output readback
    - Rally-owned note-output readback
    - unsupported-target runtime errors
* Exit criteria (all required):
  - Explicit selectors work through the richer single contract file.
  - Structured outputs stay structured.
  - Readable outputs stay readable.
  - Unsupported outputs fail loud.
  - Non-final `TurnResponse` declarations are rejected as prior-output
    selectors instead of being treated as phantom emitted artifacts.
  - Output bindings resolve through declaration metadata without duplicated
    target truth.
  - Rally note readback is keyed by output identity, not "latest note".

## Phase 5 — Lessons proof, docs, and release truth

* Goal:
  - Prove the real motivating chain and align the shipped docs and release
    story.
* Work:
  - This phase closes the loop on the real `coordination_handoff` use case and
    updates Doctrine and Rally docs so they teach the actual contract: derived
    previous-turn inputs, one public contract file, structured where honest,
    readable where honest.
* Checklist (must all be done):
  - Migrate the Lessons proof path onto a Rally-owned readback-capable target
    if `coordination_handoff` still uses an unsupported target family.
  - Add one real proof path where agent `t+1` reads agent `t`'s selected prior
    output through `RallyPreviousTurnOutput`.
  - Update Doctrine docs:
    - `AGENT_IO_DESIGN_NOTES.md`
    - `LANGUAGE_REFERENCE.md`
    - `EMIT_GUIDE.md`
    - `VERSIONING.md`
    - `CHANGELOG.md`
  - Update Rally docs to teach:
    - the new source
    - zero-config default
    - explicit selector syntax
    - single-file `final_output.contract.json` plus top-level `io`
    - exact-or-error zero-config predecessor-final resolution
    - structured vs readable readback boundary
  - Keep Doctrine public examples generic. Use Rally plus psflows as the
    concrete feature proof.
* Verification (required proof):
  - Doctrine:
    - targeted unit tests
    - `make verify-examples`
    - `make verify-package`
    - `make verify-diagnostics` if diagnostics changed
  - Rally:
    - targeted loader, runner, note, and readback tests
  - Real Lessons proof remains passing
* Exit criteria (all required):
  - The real motivating chain works end to end.
  - No in-scope live doc teaches the old markdown-only previous-output model.
  - No in-scope live doc teaches a second runtime sidecar.
  - Public release truth matches the single-file additive contract.

<!-- arch_skill:block:phase_plan:end -->

# 8) Verification Strategy (common-sense; non-blocking)

## 8.1 Doctrine proof

- unit tests for:
  - previous-turn source compile
  - exact predecessor-set resolution for zero-config
  - ambiguous predecessor failure
  - derived structured previous inputs
  - readable-only fail-loud field access
  - single-file contract serialization
  - binding metadata referential integrity
- `make verify-examples`
- `make verify-package`
- `make verify-diagnostics` if new diagnostics appear

## 8.2 Rally proof

- unit tests for:
  - richer `final_output.contract.json` loading
  - zero-config previous final-output runtime path
  - explicit selector runtime resolution
  - structured JSON readback
  - readable text readback
  - missing previous-artifact failures
  - file-path safety for file-backed prior outputs
  - unsupported-target errors
  - Rally-owned note identity and lookup

## 8.3 Real-flow proof

One real Lessons chain should show agent `t+1` reading agent `t`'s selected
prior output without the author restating that content in `home:issue.md`.

# 9) Rollout / Ops / Telemetry

## 9.1 Rollout

- additive feature
- existing prompts keep working
- authors opt in by using `RallyPreviousTurnOutput`
- compiled packages keep the same public metadata filename
- rebuilt packages gain additive top-level `io` metadata inside that file

## 9.2 Ops stance

- no runtime fallback to string selectors
- no runtime fallback to markdown summaries of structured JSON
- no runtime fallback to fake prose parsing
- no runtime fallback across several prior turns
- no runtime fallback from non-final `TurnResponse` to phantom prior artifact
- unsupported selected outputs fail loud

## 9.3 Telemetry

- no new telemetry requirement in the first cut
- rely on test proof plus direct runtime error messages

# 10) Decision Log (append-only)

- 2026-04-16: North Star confirmed. Doc status moved from `draft` to `active`
  with no scope change.
- 2026-04-16: First planning pass chose a Rally-owned
  `RallyPreviousTurnOutput` source declaration with zero-config previous
  `final_output` as the common case.
- 2026-04-16: First planning pass chose strong refs for explicit selection:
  `NameRef` for output declarations and one binding-path ref surface for
  `outputs` members.
- 2026-04-16: First planning pass originally chose readable prior-output text
  and a new `runtime_io.contract.json` sidecar.
- 2026-04-16: Review against shipped Doctrine and Rally truth rejected that
  earlier design because it still lost typed JSON structure and created a
  second public runtime contract file.
- 2026-04-16: The canonical plan now uses a source-specific derived-contract
  model:
  - zero-config previous `final_output` is exact when the predecessor set
    proves one contract and fails loud otherwise
  - explicit selection derives the exact selected previous emitted-output
    contract
- 2026-04-16: The canonical plan now preserves the strongest honest native
  readback form:
  - `structured_json`
  - `readable_text`
  - `unsupported`
- 2026-04-16: The canonical plan now extends the existing public
  `final_output.contract.json` with one additive top-level `io` block instead
  of creating `runtime_io.contract.json`.
- 2026-04-16: The canonical plan now forbids local `shape:` or `structure:` on
  `RallyPreviousTurnOutput` so the selected previous emitted output stays the
  only contract owner.
