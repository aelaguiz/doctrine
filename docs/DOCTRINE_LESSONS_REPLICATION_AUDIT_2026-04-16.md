---
title: "Doctrine Lessons Replication Audit - 2026-04-16"
date: 2026-04-16
status: complete
doc_type: audit
owners: [aelaguiz]
reviewers: []
related:
  - doctrine/grammars/doctrine.lark
  - docs/LANGUAGE_REFERENCE.md
  - docs/LANGUAGE_DESIGN_NOTES.md
  - docs/EMIT_GUIDE.md
  - docs/DOCTRINE_AUTHORING_SYNTAX_SUGAR_AUDIT_2026-04-16.md
  - docs/AUTHORING_PATTERNS.md
  - examples/05_workflow_merge/prompts/AGENTS.prompt
  - examples/24_io_block_inheritance/prompts/AGENTS.prompt
  - examples/68_review_family_shared_scaffold/prompts/AGENTS.prompt
  - examples/107_output_inheritance_basic/prompts/AGENTS.prompt
  - examples/108_output_inheritance_attachments/prompts/AGENTS.prompt
  - examples/117_io_omitted_wrapper_titles/prompts/AGENTS.prompt
  - examples/120_route_field_final_output_contract/prompts/AGENTS.prompt
  - examples/121_nullable_route_field_final_output_contract/prompts/AGENTS.prompt
  - ../psflows/flows/lessons/flow.yaml
  - ../psflows/flows/lessons/prompts/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/shared/contracts.prompt
  - ../psflows/flows/lessons/prompts/shared/skills.prompt
  - ../psflows/flows/lessons/prompts/agents/project_lead/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/section_dossier_engineer/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/section_concepts_terms_curator/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/section_architect/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/lesson_architect/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/situation_synthesizer/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/playable_materializer/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/copywriter/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/metadata_copywriter/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/agents/acceptance_critic/AGENTS.prompt
  - ../psflows/flows/lessons/prompts/contracts/section_architecture.prompt
  - ../psflows/flows/lessons/prompts/contracts/section_concepts_terms.prompt
---

# TL;DR

Doctrine already has enough reuse to remove a big share of the Lessons prompt
duplication today.

The cleanest proof is inside `../psflows` itself. `section_architect` and
`section_concepts_terms_curator` already use abstract-agent inheritance, output
inheritance, grouped `inherit`, and one-line IO wrapper refs to cut a lot of
boilerplate. Most of the other Lessons agents do not yet use the same pattern.

After that cleanup, there are still real language gaps. The biggest ones are:

1. too much ceremony for routed turn-result outputs
2. no small parameter surface for owner-bound routing blocks
3. no bundle declaration for repeated artifact families
4. too much repeated review-field and output-schema wiring
5. too much `output schema` field-head ceremony

# Scope And Method

This audit used Doctrine shipped truth first:

- `doctrine/grammars/doctrine.lark`
- `docs/LANGUAGE_REFERENCE.md`
- `docs/LANGUAGE_DESIGN_NOTES.md`
- `docs/EMIT_GUIDE.md`
- manifest-backed examples under `examples/`

Then it used `../psflows` as the live stress test:

- `flows/lessons/flow.yaml`
- `flows/lessons/prompts/AGENTS.prompt`
- `flows/lessons/prompts/shared/*.prompt`
- `flows/lessons/prompts/contracts/*.prompt`
- `flows/lessons/prompts/agents/*/AGENTS.prompt`

I also used parallel agent passes plus local scripted counts. I did not run
verification because this is a docs-only audit.

# Evidence Snapshot

These counts matter because they show where the repetition really lives.

- Lessons has `11` concrete agent prompt files under
  `../psflows/flows/lessons/prompts/agents/`.
- `9` of those `11` agents repeat the same big import prelude:
  `rally.base_agent`, `rally.turn_results`, `shared.skills`,
  `shared.review`, `shared.contracts`, and the same `9` contract modules.
- Those same `9` agents also repeat the same six shell fields in the concrete
  agent body:
  `rally_contract`, `read_first`, `how_to_take_a_turn`,
  `legacy_and_old_authoring_files`, `skills`, and `final_output`.
- `11` of `11` Lessons agents repeat a `turn_result: "Turn Result"` output
  entry.
- `9` of `11` Lessons agents end with the same one-line
  `final_output: rally.turn_results.RallyTurnResult`.
- `8` contract prompt files repeat the same
  `output shape ProductionArtifactDocument: "Agent Output Document"` scaffold.
- `7` contract prompt files repeat the same larger family shape:
  `document` + `schema` + issue-artifact document + file output +
  review contract + analysis + workflow + input contract.

The Doctrine-side proof says the same thing from another angle. Across the
shipped example corpus there are at least:

- `114` `inherit` lines
- `43` `override` lines
- `153` `inputs:` lines
- `239` `outputs:` lines
- `205` `route` lines

That does not mean the language is bad. It means Doctrine is honest about
explicit accounting. The question is where that honesty turns into avoidable
ceremony.

# Part I: Replication Doctrine Already Lets Lessons Remove

This section is important. Not every repeated Lessons pattern should drive new
Doctrine syntax. A real slice of the current repetition is just uneven use of
features Doctrine already ships.

## 1. Base-agent shell reuse is underused

Doctrine already supports abstract-agent reuse.

The clean local proof is in:

- `../psflows/flows/lessons/prompts/shared/contracts.prompt`
- `../psflows/flows/lessons/prompts/agents/section_architect/AGENTS.prompt`
- `../psflows/flows/lessons/prompts/agents/section_concepts_terms_curator/AGENTS.prompt`

Those two more polished agents push shared role shell into a base agent and
then override only the parts that are truly local.

Most of the other Lessons agents do not do that. They repeat:

- the Rally context block
- `read_first`
- `how_to_take_a_turn`
- `legacy_and_old_authoring_files`
- the `skills` wrapper
- the same `final_output`

This is not a Doctrine gap first. It is a normalization gap in `psflows`.

Use this syntax today:

```prompt
abstract agent LessonsBaseAgent:
    rally_contract: "Rally Context"
        "Rally runs this flow. Use the shared rules below with this role's local rules."
    read_first: ReadFirst
    abstract how_to_take_a_turn
    abstract your_job
    legacy_and_old_authoring_files: LegacyAndOldAuthoringFiles
    abstract routing

agent SomeProducer[LessonsBaseAgent]:
    role: "..."
    your_job: SomeProducerJob
    inherit {rally_contract, read_first}
    override how_to_take_a_turn: SomeProducerWorkflow
    inputs: SomeProducerInputs
    skills: SomeProducerSkills
    outputs: SomeProducerOutputs
    final_output: SomeProducerTurnResult
    inherit legacy_and_old_authoring_files
    routing: SomeProducerRouting
```

When the child only needs to keep or replace a few inherited shell items, use
explicit `inherit` and `override` instead of rebuilding the whole agent body:

```prompt
agent SectionArchitect[LessonsBaseAgent]:
    role: "..."

    inherit {rally_contract, read_first}
    override how_to_take_a_turn: SectionArchitectWorkflow
    inputs: SectionArchitectInputs
    skills: SectionArchitectSkills
    outputs: SectionArchitectOutputs
    inherit legacy_and_old_authoring_files

    final_output: SectionArchitectTurnResult
```

## 2. Named `inputs` and `outputs` blocks are underused

Doctrine already ships top-level `inputs` and `outputs` declarations plus
block inheritance. This is the main current fix for the repeated
inputs-and-outputs boilerplate the Lessons agents keep restating.

The clean proof is:

- `examples/24_io_block_inheritance/prompts/AGENTS.prompt`
- `../psflows/flows/lessons/prompts/shared/contracts.prompt`
- `../psflows/flows/lessons/prompts/agents/section_architect/AGENTS.prompt`
- `../psflows/flows/lessons/prompts/agents/section_concepts_terms_curator/AGENTS.prompt`

Use this syntax today:

```prompt
inputs LessonsSectionAgentInputs: "Your Inputs"
    scoped_catalog_truth: "Scoped Catalog Truth"
        TrackCatalogMeta
        SectionCatalogMeta

    broader_curriculum_context: "Broader Curriculum Context"
        FullLessonCatalog

outputs LessonsAgentOutputs: "Your Outputs"
    coordination_handoff: "Coordination Handoff"
        shared.review.HandoffOutput
```

Then patch the shared blocks instead of rebuilding them locally:

```prompt
inputs SectionArchitectInputs[base.RallyManagedInputs]: "Inputs"
    inherit issue_ledger
    previous_section_concepts_terms_turn: PreviousSectionConceptsTermsTurn

outputs SectionArchitectOutputs[base.RallyManagedOutputs]: "Your Outputs"
    override issue_note: SectionLessonMapComment

    turn_result: "Turn Result"
        SectionArchitectTurnResult
```

The key point is simple: if several roles share the same wrapper shape, make
that wrapper a named `inputs` or `outputs` declaration and let the role patch
only the keys that differ.

## 3. One-line IO wrapper refs already exist and are not used evenly

Doctrine already proved omitted IO wrapper titles in
`examples/117_io_omitted_wrapper_titles/prompts/AGENTS.prompt`.

Lessons already uses this well in places like:

- `previous_section_dossier_turn: PreviousSectionDossierTurn`
- `previous_section_concepts_terms_turn: PreviousSectionConceptsTermsTurn`

Use this syntax today whenever the wrapper has one direct child and no local
wrapper prose:

```prompt
inputs SectionConceptsTermsInputs[base.RallyManagedInputs]: "Inputs"
    inherit issue_ledger
    previous_section_dossier_turn: PreviousSectionDossierTurn

outputs SectionDossierOutputs: "Your Outputs"
    section_handoff: SectionHandoff
```

For inherited wrappers, use the same one-line form on `override`:

```prompt
outputs SectionArchitectOutputs[base.RallyManagedOutputs]: "Your Outputs"
    override issue_note: SectionLessonMapComment
```

This is the current best answer for repeated one-child IO entries.

## 4. Grouped `inherit` already cuts repeated kept-field noise

Doctrine already ships grouped `inherit { ... }` on the surfaces that matter
here.

The Doctrine proof surfaces are:

- `examples/05_workflow_merge/prompts/AGENTS.prompt`
- `examples/24_io_block_inheritance/prompts/AGENTS.prompt`
- `examples/107_output_inheritance_basic/prompts/AGENTS.prompt`
- `examples/108_output_inheritance_attachments/prompts/AGENTS.prompt`

The local Lessons proof surfaces are:

- `../psflows/flows/lessons/prompts/agents/section_architect/AGENTS.prompt`
- `../psflows/flows/lessons/prompts/agents/section_concepts_terms_curator/AGENTS.prompt`

Use this syntax today:

```prompt
inherit {rally_contract, read_first}

output SectionLessonMapComment[outputs.LessonsSectionNote]: "Section Lesson Map Comment"
    inherit {target, shape, requirement}
    structure: SectionLessonMapDocument

output schema SectionArchitectTurnResultSchema[outputs.LessonsAgentResultSchema]: "Section Architect Turn Result Schema"
    inherit {kind, summary, reason, sleep_duration_seconds, section_edit}
```

This is the current built-in answer to "I am keeping the same fields, targets,
or wrapper items, and I do not want one `inherit` line per key."

## 5. Output inheritance already cuts real boilerplate

Doctrine already ships:

- top-level output inheritance
- attachment inheritance
- inherited final outputs

Use this syntax today for shared result carriers:

```prompt
output schema ChildTurnResultSchema[outputs.LessonsAgentResultSchema]: "Child Turn Result Schema"
    inherit {kind, summary, reason, sleep_duration_seconds, section_edit}

output shape ChildTurnResultJson[outputs.LessonsAgentResultJson]: "Child Turn Result JSON"
    inherit kind
    override schema: ChildTurnResultSchema
    inherit field_notes

output ChildTurnResult[outputs.LessonsAgentResult]: "Child Turn Result"
    inherit target
    override shape: ChildTurnResultJson
    inherit requirement
```

Then bind the final response explicitly:

```prompt
final_output: ChildTurnResult
```

Or, when the final output owns routing:

```prompt
final_output:
    output: SectionConceptsTermsTurnResult
    route: next_route
```

This does not erase the schema-shape-output chain, but it already lets Lessons
share most of the repeated result carrier instead of rebuilding every field
from scratch.

## 6. Shared routing protocol reuse exists, but only in part of the flow

Lessons already has a reusable routing protocol in
`../psflows/flows/lessons/prompts/shared/contracts.prompt`.

At least five agents use the same pattern:

- a small `ReadyForReview` workflow
- a small routing workflow that inherits `ProducerRoutingProtocol`
- a `blocked_upstream` inherit

Use this syntax today:

```prompt
workflow LessonArchitectReadyForReview: "Ready For Review"
    route_now: "Route"
        "When the lesson plan is ready for review, set final JSON `next_owner` to `11_acceptance_critic`."

workflow LessonArchitectRouting[shared.contracts.ProducerRoutingProtocol]: "Lesson Architect Routing"
    override ready_for_review: LessonArchitectReadyForReview
    inherit blocked_upstream
```

That is already better than repeating the whole routing block from scratch.
The repo just has not pushed that pattern all the way through the flow.

# Part II: Replication Doctrine Still Makes Awkward

This is the true language-pressure section. I am only counting things here
that still stay verbose after you apply the current Doctrine tools well.

## 1. Routed turn-result outputs take too many declarations

This is the strongest gap in the Lessons port.

When a role needs a typed final JSON turn result with a slightly specialized
schema, the current best pattern often needs all of this:

1. `output schema`
2. `output shape`
3. `output`
4. `outputs` wrapper entry
5. `final_output`

`section_architect` and `section_concepts_terms_curator` are the best local
proof. Even in the cleaner version, the routed result still takes a long
schema-shape-output sandwich.

This is not bad design in the compiler. The ownership split is clear:

- schema owns machine fields
- shape owns format kind
- output owns target and attachments

But the author still has to spell all three layers when the intent is really
one thing: "this role ends with the shared Lessons turn result, plus one local
route or one local carried field set."

That is the most obvious place where Doctrine is making authors do too much
work for one stable concept.

## 2. Owner-bound routing blocks still need near-copy workflows

The `ready_for_review` workflows are very similar across producer agents.
The real difference is usually one owner key.

Current Doctrine can reuse the wrapper protocol, but it cannot express a small
typed parameter like:

- ready-for-review goes to Acceptance Critic
- exact-move retry goes to Situation Synthesizer
- blocked-upstream goes to Project Lead

without defining another local workflow block.

The result is not huge per file, but it repeats across the whole flow and will
repeat again in other ports.

This is a real gap because the repeated part is semantic, not just prose.

## 3. Artifact contract families repeat the same declaration bundle

Most Lessons contract files follow a family pattern:

1. `document`
2. `schema`
3. issue-artifact `document[...]`
4. file `output`
5. review contract workflow
6. analysis
7. main workflow
8. typed input contract

You can see this clearly in:

- `section_architecture.prompt`
- `section_concepts_terms.prompt`
- `lesson_plan.prompt`
- `lesson_situations.prompt`
- `section_playable_strategy.prompt`

Doctrine today can reuse the pieces, but it cannot declare the family as one
explicit authored bundle.

That means every new artifact family has to rebuild the same skeleton even
when the repo wants the same shape every time.

## 4. Review field wiring duplicates itself across review and final output

Doctrine already improved this area a lot with first-class review surfaces and
identity shorthand, but split-review finals still make authors restate similar
semantic maps in two places:

1. `review.fields`
2. `final_output.review_fields`

That duplication is still visible in the example corpus and in design pressure
around critic-style or control-ready outputs.

This is a good target because the repeated meaning is narrow and typed already.

## 5. `output schema` field heads still carry a lot of local ceremony

This shows up more in Doctrine examples than in current Lessons agent files,
but it matters because Lessons result carriers and control JSON surfaces will
keep growing.

The pattern is verbose:

- field head
- title
- type
- nullable
- note
- values or route members

Doctrine is right to keep schema ownership explicit. Still, the field-head
surface is carrying more spelling than meaning in the common case.

# Part III: What Is Product-Specific And Should Stay Repeated

Some repetition is good. It is not a language problem.

## 1. Lane-specific quality bars

The critic lane rules differ because the real review bars differ.

The same is true for:

- section dossier work
- concepts and terms work
- section architecture
- playable strategy
- copy
- metadata wording

This is product truth. It should not be flattened into language sugar.

## 2. Grounding and gameplay detail

A lot of the long wording in Lessons is domain detail:

- poker meaning
- exact-move proof
- playable-layout constraints
- metadata mode rules

That is real authored content, not syntax duplication.

## 3. Local readable teaching comments

Some comments in the cleaner agent files explain why a shorter pattern is safe.
Those are useful while the repo is still converging on a cleaner Doctrine
style. They may disappear later, but they are not themselves the problem.

# Audit Verdict

The honest split looks like this:

## 1. Lessons has real cleanup left before Doctrine needs new syntax

That cleanup includes:

- moving more agents to the abstract-base pattern already used by the two
  cleaner roles
- moving repeated `inputs` and `outputs` wrappers into named top-level blocks
- patching those blocks with inherited `inputs[...]` and `outputs[...]`
  instead of rebuilding them
- pushing one-line IO wrapper refs further
- using grouped `inherit { ... }` wherever a child is only keeping shared
  wrapper items or shared result-carrier fields
- using shared routed result carriers more consistently
- normalizing routing protocol reuse

Doctrine already pays for those wins.

## 2. After that cleanup, five language gaps still stand out

In priority order:

1. routed turn-result specialization
2. small typed owner-bound workflow parameters
3. artifact-family bundle declarations
4. lighter shared review-to-final-output field wiring
5. lighter `output schema` field heads

Those are the places where the language still makes authors repeat the same
meaning more than once.

# Natural Doctrine Enhancements

This section starts only after the audit on purpose. These are not "make the
language magic" ideas. These are the small, explicit extensions that fit
Doctrine's current style.

## 1. Add inline output-shape and output-schema specialization inside `output`

### Why this is natural

Doctrine already treats `output`, `output shape`, and `output schema` as one
ownership chain. The author pain comes from having to split one local result
carrier across three declarations even when only one small thing changed.

### What it should aim for

Let an inherited `output` specialize its shape or schema inline instead of
forcing three separate top-level declarations for every local turn result.

The idea is not to collapse the model. The idea is to let one authored surface
own a small local patch to that chain.

### What it would replace

The repeated pattern in files like:

- `section_architect/AGENTS.prompt`
- `section_concepts_terms_curator/AGENTS.prompt`

### Guardrails

- do not blur schema ownership
- do not infer target or final-output behavior
- lower to the same resolved `output`, `shape`, and `schema` model Doctrine
  already uses

## 2. Add small typed parameters for reusable routing workflows

### Why this is natural

Lessons is repeating tiny routing workflows whose meaning is:

- same rule
- different owner

That is a good fit for a small typed parameter, not a macro system.

### What it should aim for

Allow a workflow or route-only declaration to bind one or two typed values,
such as:

- next owner
- blocked owner
- accepted owner

The body stays explicit. Only the small typed variable changes.

### Guardrails

- keep parameters typed
- keep call sites explicit
- no free-form templating
- no hidden string interpolation as semantics

## 3. Add a first-class artifact-family bundle declaration

### Why this is natural

The same authored family keeps repeating:

- human-readable artifact document
- schema and gates
- issue artifact variant
- file output
- review contract
- analysis
- main workflow

That is already a stable Doctrine shape in Lessons.

### What it should aim for

Introduce one explicit declaration for an authored artifact family that lowers
into the same individual owned declarations Doctrine already understands.

This would pay off in every large port, not just Lessons.

### Guardrails

- keep the lowered declarations addressable
- do not hide review gates or schema ownership
- do not turn this into a catch-all macro surface

## 4. Add review-field carry-over sugar for split finals

### Why this is natural

Doctrine already knows the review semantic field set. Split finals often need
only a subset of that same set.

### What it should aim for

Let `final_output.review_fields` explicitly inherit or copy a subset from the
review field map instead of rebuilding it entry by entry.

This should stay narrow. It is not a new binding system. It is a shorter way
to reuse the same one.

### Guardrails

- keep explicit subset selection
- keep normal `semantic: path` entries legal
- keep fail-loud behavior when a requested semantic field does not exist

## 5. Add compact common-case `output schema` field heads

### Why this is natural

This is already a high-friction surface in the Doctrine examples. It will keep
hurting as more flows end in structured final outputs.

### What it should aim for

Shorten the common case where the author is only saying:

- field name
- title
- type
- optional nullable
- maybe one short note

### Guardrails

- keep the current explicit long form
- lower both forms to the same schema model
- do not create a second schema ownership path

# Recommended Order

If the goal is fastest real payoff with lowest language risk, the order should
be:

1. normalize Lessons onto the Doctrine features it already ships
2. add inline result-carrier specialization for inherited outputs
3. add narrow review-field carry-over for split finals
4. decide whether owner-bound routing parameters are worth the added language
   weight
5. consider an artifact-family bundle only after one or two more real ports
   confirm the same family shape

# Immediate Cleanup Work In `psflows` Without Changing Doctrine

This is not the language roadmap. This is the free win list.

## 1. Move the remaining producer agents onto the shared base-agent pattern

Best local examples:

- `section_architect`
- `section_concepts_terms_curator`

## 2. Collapse the repeated turn-result and handoff wrappers first

The repeated wins are in `inputs`, `outputs`, shared result carriers, and
agent shells first. Imports are cleanup, not the main language win.

Standardize on:

- one shared `LessonsAgentOutputs`
- one shared base result carrier
- child `outputs[...]` blocks that only patch `issue_note` and bind the local
  turn result
- explicit `final_output` on the inherited result carrier

## 3. Move repeated IO wrappers into named blocks and patch those blocks

Standardize on:

- top-level `inputs` / `outputs`
- inherited `inputs[...]` / `outputs[...]`
- one-line child refs where the wrapper owns no extra prose
- `override issue_note: SomeComment` where a child only swaps the carrier

## 4. Standardize routed turn-result carriers

Even before new language work, the flow should settle on one shared result
shape and one consistent specialization style.

## 5. Normalize routing workflow reuse

The repo already has a routing protocol. It should use it the same way across
all producer lanes.

## 6. Pick one local Doctrine style and teach it

Right now Lessons has at least two visible authoring styles:

- older long-form role files
- newer compressed role files

That makes it harder to tell which repetition is truly required.

# Final Verdict

Doctrine is not the main source of the current Lessons repetition, but it is
also not blameless.

The short honest answer is:

- a large first cut is available right now with current Doctrine features
- the remaining high-value syntax work is real, focused, and worth doing
- the cleanest next Doctrine work is not more hidden behavior
- the cleanest next Doctrine work is a small set of explicit shorthand surfaces
  for routed result carriers, split-final review wiring, artifact bundles, and
  maybe typed workflow parameters
