# Shipped Language Reference

Doctrine prompt files compile structured source into runtime Markdown and
skill-package trees. The authoring surface is a small set of named
declarations plus explicit composition and fail-loud compiler rules. The
shipped compiler reuses loaded prompt graphs so larger prompt families remain
practical, not just toy-sized examples.

For the motivation behind the project, start with [WHY_DOCTRINE.md](WHY_DOCTRINE.md).
For task-first guidance on which surface to choose, use
[AUTHORING_PATTERNS.md](AUTHORING_PATTERNS.md).
For versioning, releases, and upgrade rules, use
[VERSIONING.md](VERSIONING.md).
For the numbered teaching corpus, use [../examples/README.md](../examples/README.md).

## Mental Model

- A prompt file is the source of truth.
- Concrete agents are the runtime entrypoints.
- Skill packages are filesystem emit roots.
- Abstract declarations exist for reuse and inheritance, not direct emission.
- Keys are compiler identities. Authored titles and prose are the human-facing
  runtime surface.
- The compiler preserves the structure that matters and rejects ambiguous or
  inconsistent doctrine instead of guessing.

## Prompt Files And Compilation

A prompt file may contain imports and any mix of shipped declarations:

- `render_profile`, `analysis`, `decision`, `schema`, `table`, `document`
- `agent`, `abstract agent`
- `workflow`, `route_only`, `grounding`
- `review`, `review_family`, `abstract review`
- `skill package`
- `skill`, `skills`
- `input`, `inputs`, `input source`
- `output`, `outputs`, `output target`, `output shape`, `output schema`
- `enum`

The normal agent entrypoints are `AGENTS.prompt` and `SOUL.prompt`. The normal
skill-package entrypoint is `SKILL.prompt`. `emit_docs` compiles concrete
agents from the agent entrypoints into runtime Markdown artifacts whose
basename matches the entrypoint stem. It also emits imported
directory-backed runtime packages when a selected `AGENTS.prompt` uses them as
runtime homes. Structured final outputs also emit the exact lowered schema at
`schemas/<output-slug>.schema.json` beside that Markdown file. `emit_skill`
compiles one top-level `skill package` from `SKILL.prompt` into `SKILL.md`
plus bundled source-root files. Doctrine does that work through shared
compilation and indexing so module loading happens once per entrypoint and
batch emit or verification surfaces can fan out safely while preserving
deterministic output order.
For target configuration, output layout, and flow-diagram emission, use
[EMIT_GUIDE.md](EMIT_GUIDE.md). For package authoring, use
[SKILL_PACKAGE_AUTHORING.md](SKILL_PACKAGE_AUTHORING.md).

## Agents

Agents are the top-level runtime owners.

```prompt
abstract agent BaseRole:
    read_first: SharedTurn

agent Reviewer[BaseRole]: "Review Lead"
    role: "Core job: review the current brief."
    inherit read_first
```

Important rules:

- `agent` declares a concrete runtime owner.
- `abstract agent` declares an inheritance-only owner that does not render on
  its own.
- A concrete agent may declare a head title. Bare readable refs default to that
  title, while `:key` and the legacy `:name` projection keep the structural
  declaration name available.
- Every concrete agent needs a `role`.
- Reserved typed agent fields include `inputs`, `outputs`, `analysis`,
  `decision`, `skills`, `review`, and `final_output`.
- Any other keyed field is an authored workflow slot. Those slots can point at
  a named `workflow` or define an inline workflow body.
- `handoff_routing:` may also carry a route-only `law:` block. That law may
  use `active when`, `mode`, `when`, `match`, `route_from`, `stop`, and
  `route`.
- `abstract <slot_key>` marks an authored slot that concrete children must
  define directly.
- `inherit <slot_key>` keeps an inherited authored slot unchanged.
- `override <slot_key>:` replaces an inherited authored slot in place.
- A concrete agent may not define both `workflow:` and `review:`. Review turns
  use `review:` as their main semantic body.
- `workflow:` may point at a named `workflow`, `route_only`, or `grounding`
  declaration.
- `review:` may point at a concrete `review` or a case-complete
  `review_family`.
- `analysis:` attaches one reusable `analysis` declaration to an otherwise
  ordinary concrete turn.
- `decision:` attaches one reusable `decision` declaration to an otherwise
  ordinary concrete turn. A concrete agent may attach more than one
  `decision:` field when each points at a different `decision` declaration.
- `final_output:` optionally points at one emitted `output` declaration and
  marks that `TurnResponse` artifact as the turn-ending assistant message.
- On review-driven agents, `final_output:` may either reuse the review's
  `comment_output:` or point at another emitted `TurnResponse` output.
  `comment_output:` stays the review carrier, while a separate `final_output:`
  still inherits the review semantic refs and guards.
- The short form stays legal:

```prompt
final_output: AcceptanceReviewResponse
```

- Review-driven split finals may also use the block form:

```prompt
final_output:
    output: AcceptanceControlFinalResponse
    review_fields:
        verdict: verdict
        current_artifact: current_artifact
        next_owner: next_owner
```
- Any emitted output may also read shared compiler-owned route semantics
  through `route.exists`, `route.next_owner`, `route.next_owner.key`,
  `route.next_owner.title`, `route.label`, and `route.summary` when the active
  workflow-law, `handoff_routing` law, `route_only`, `grounding`, or review
  branch resolves a real route.
- When every live routed branch on that turn comes from `route_from`, outputs
  may also read
  `route.choice`, `route.choice.key`, `route.choice.title`, and
  `route.choice.wire`.
- `route.next_owner.*` may stay live across several `route_from` branches. It
  means the selected route owner. `route.label` and `route.summary` still need
  one selected branch.
- Name each `route_from` enum member once. Use `else` at most once.
- Unguarded `route.*` reads fail loudly when some active branches may not
  route. Guard route-specific readback with `when route.exists:` when the
  route is not live on every branch.
- Guard branch-specific route detail with `when route.choice == Enum.member`
  when several routed branches stay live and every live routed branch comes
  from `route_from`.
- On `handoff_routing:`, only the slot's `law:` block makes `route.*` live.
  Prose route lines inside `handoff_routing` are still readable text only.
- When a review points `comment_output:` at an imported reusable `output`,
  bare refs inside that output still resolve locally first, then may bind the
  concrete review's local declarations when the imported module does not
  define them. Shared review comments therefore can still name local routed
  owners without moving the output declaration.

`role` has two shipped shapes:

- scalar `role: "..."` emits opening prose directly
- titled `role: "Title"` with an indented body emits a headed section

## Workflows

`workflow` is Doctrine's reusable instruction surface.

```prompt
workflow SharedTurn: "How To Take A Turn"
    sequence read_first:
        "Read `home:issue.md` first."
        "Then read this role's local rules."

    next_step: "Next Step"
        route "Return to ReviewLead when ready." -> ReviewLead
```

A workflow body may contain:

- prose lines
- local keyed sections
- non-section readable blocks such as `sequence`, `bullets`, `checklist`,
  `definitions`, `table`, `callout`, `code`, and `rule`
- `use <local_key>: WorkflowRef` composition
- readable declaration refs inside titled section bodies
- inline or referenced `skills:` blocks
- `law:` for compiler-owned workflow-law semantics

Important rules:

- Workflow titles are human-facing headings.
- Keys are the patch identities used by inheritance and addressable refs.
- Bare workflow roots are composed with `use`; they do not render as readable
  refs inside ordinary workflow section bodies.
- Workflow roots may own non-section readable blocks directly.
- Root workflow sections still use the existing `key: "Title"` form. Doctrine
  does not add a second root `section ...` syntax.
- Titled workflow section bodies may contain prose, route lines, local nested
  sections, readable declaration refs, and readable block kinds such as
  `section`, `sequence`, `bullets`, `checklist`, `definitions`, `table`,
  `callout`, `code`, and `rule`.
- `sequence`, `bullets`, and `checklist` keep the authored key, but their
  title string is optional. If the title is missing, Doctrine renders the
  list directly inside the current section instead of adding a nested heading.
- The same title-optional rule applies to `override sequence`, `override
  bullets`, and `override checklist`.
- Inherited workflow-root readable blocks use the same explicit patch model as
  other keyed workflow items. Use `inherit key` or `override <kind> key`.
- Workflow law may use `route_from` to pick one route from a typed input or
  emitted output fact.

### Workflow Inheritance

Inherited workflows use explicit ordered patching:

- `inherit key` keeps an inherited keyed item in place
- `override key:` replaces an inherited keyed item in place
- `override key: "New Title"` also replaces the rendered title
- `key: "Title"` introduces a new keyed item
- `override local_key: WorkflowRef` retargets an inherited `use` entry while
  keeping the outer key stable

Children must account for every inherited keyed item exactly once. Doctrine
does not do implicit merge by omission.

## Review Families And Control-Plane Declarations

Doctrine now ships dedicated control-plane declarations instead of forcing
every reusable review or routing shape through raw workflow or review patching.

### Review Families

`review_family` is a reusable review scaffold on the same compiler path as
`review`.

Important rules:

- `review_family` may own `comment_output`, `fields`, shared pre-outcome
  sections, `selector`, and exhaustive `cases`.
- Child `review` declarations still own `subject:`, `contract:`, and outcome
  sections unless the family is already case-complete.
- A concrete agent may attach a `review_family` directly only when the family
  already resolves to a concrete review shape, such as a case-selected family
  with exhaustive cases.
- `review_family` is additive reuse. It does not replace ordinary `review` or
  `abstract review`.

### Route-Only

`route_only` declares routing-only turns with:

- `facts:`
- `when:`
- `current none`
- `handoff_output:`
- `guarded:`
- `routes:`

Important rules:

- `route_only` lowers through the same workflow-law `current none`, route, and
  standalone-read validation path the earlier route-only ladder already used.
- The lowered route-only branches also feed the same shared output-facing
  `route.*` semantics ordinary workflow-law outputs, `handoff_routing` law,
  and review outputs use.
- The dedicated declaration does not create a second route engine.
- Guarded route-only keys must line up with guarded top-level output sections
  on the declared `handoff_output`.

### Grounding

`grounding` declares an explicit grounding protocol with:

- `source:`
- `target:`
- `policy:`

The shipped policy items are `start_from`, `forbid`, `allow`, and `if ... ->
route ...`.

Important rules:

- `grounding` lowers through ordinary workflow-style readable output, not a
  hidden receipt or packet channel.
- Grounding routes still target ordinary concrete agents.
- `grounding` owns protocol shape, not domain truth.

## Analysis, Decisions, Schemas, And Documents

Doctrine ships four additional readable declaration families for structured
reasoning, candidate-pool decisions, artifact inventories, and reusable
markdown structure.

### Analysis

`analysis` declares a reusable reasoning program that a concrete agent may
attach through `analysis:`.

```prompt
analysis ReleaseAnalysis: "Release Analysis"
    stages: "Stages"
        prove "Release plan" from {CurrentPlan}
        classify "Risk band" as RiskBand
        compare "Coverage" against {CurrentPlan}
        defend "Recommendation" using {CurrentPlan}
```

Important rules:

- `analysis` is a readable declaration with titled keyed sections.
- `analysis` may attach `render_profile:` to control how its readable
  structure renders when another shipped surface lowers it into markdown.
- A section body may contain prose plus `prove`, `derive`, `classify`,
  `compare`, and `defend`.
- Dump-era analysis shorthands such as `require ...`, `screen ... with ...`,
  top-level `basis:`, `upstream_truth`, `assign ... using ...`, and
  `export ...` are not shipped analysis syntax. Keep proof in `prove`,
  classification in `classify`, candidate obligations in `decision`, and
  higher-level contract shape in `schema`, `document`, or prose.
- `classify ... as EnumRef` uses a declared `enum`.
- `prove`, `derive`, `compare`, and `defend` read declared artifact roots or
  addressable paths.
- Analysis sections are addressable, so refs such as
  `ReleaseAnalysis:stages.title` are valid.

### Decision

`decision` declares a reusable candidate-pool and winner-selection scaffold
that a concrete agent may attach through `decision:`.

```prompt
decision PlayableStrategyChoice: "Playable Strategy Choice"
    candidates minimum 3
    rank required
    rejects required
    choose one winner
    rank_by {teaching_fit, product_reality, capstone_coherence}
```

Important rules:

- `decision` is a readable declaration that keeps candidate search, ranking,
  rejection, and winner-selection obligations typed instead of prose-only.
- `decision` may attach `render_profile:` to control how its readable body
  renders when Doctrine lowers it into markdown.
- Concrete agents may attach more than one `decision:` field, but repeating
  the same `decision` declaration on one agent is invalid.
- The shipped typed statements are `candidates minimum <n>`, `rank required`,
  `rejects required`, `candidate_pool required`, `kept required`,
  `rejected required`, `sequencing_proof required`,
  `winner_reasons required`, `choose one winner`, `winner required`, and
  `rank_by {dimension, ...}`.
- `winner required` is accepted as a normalized alias for `choose one winner`.
- Dump-era `solver_screen ...` wording is not a shipped decision keyword. Keep
  screening evidence in the generic decision scaffold or in review gating when
  the semantics are truly contract-gating.
- Decision declarations stay generic. What counts as a candidate or which
  dimensions matter remains author-owned, not compiler-owned.

### Schemas

`schema` declares a reusable artifact inventory and optional gate catalog.

```prompt
schema BuildSurfaceSchema: "Build Surface Schema"
    sections:
        summary: "Summary"
            "Include a short summary."

    artifacts:
        manifest_file: "Manifest File"
            ref: ManifestFile

    groups:
        downstream_rebuild: "Downstream Rebuild"
            manifest_file

    gates:
        evidence_grounded: "Evidence Grounded"
            "Confirm the evidence is cited."
```

Important rules:

- `schema` owns reusable `sections:`, optional named `gates:`, first-class
  `artifacts:`, and reusable `groups:`.
- `schema` may attach `render_profile:` to control how its readable sections
  render when lowered into markdown.
- A schema must declare at least one `sections:` or `artifacts:` block.
- On `output`, `schema:` points at a Doctrine `schema` declaration.
- On `output shape`, `schema:` remains the owner-aware attachment point for
  `output schema` when the shape kind is `JsonObject`.
- Output-attached schemas must still expose at least one section.
- A markdown-bearing `output` may not attach both `schema:` and `structure:`.
  Pick exactly one artifact owner on that surface.
- Schema addressability is family-namespaced by authored key:
  `BuildSurfaceSchema:sections.summary.title`,
  `BuildSurfaceSchema:artifacts.manifest_file.title`, and
  `BuildSurfaceSchema:groups.downstream_rebuild.title`.
- `review contract:` may point at either a `workflow` or a `schema`.

### Tables

`table` declares a reusable table contract once. Documents can place that
contract under a local document key.

```prompt
table ReleaseGates: "Release Gates"
    columns:
        gate: "Gate"
            "What must pass before shipment."

        evidence: "Evidence"
            "What proves the gate passed."


document ReleaseGuide: "Release Guide"
    table release_gates: ReleaseGates required
        rows:
            release_notes:
                gate: "Release notes"
                evidence: "Linked to the shipped proof."
```

Important rules:

- A top-level `table` declaration owns the table title, `columns:`, optional
  `row_schema:`, and optional default `notes:`.
- A document use site owns the local key, `required` / `advisory` /
  `optional`, `when <expr>`, local `rows:`, and local `notes:`.
- A named document use site uses `table local_key: TableRef`. It does not use
  a generic `ref:` field.
- A named use site may be empty. It still renders the normal no-row contract
  table.
- A named use site lowers to the same document table shape as an inline table.
  Rendered Markdown does not change.
- A child document may still use `override table local_key: TableRef` because
  named tables keep the existing `table` block kind.
- Table declarations are addressable roots, such as
  `ReleaseGates:columns.evidence.title`.
- Document-local table paths stay addressable under the local key, such as
  `ReleaseGuide:release_gates.columns.evidence.title` and
  `ReleaseGuide:release_gates.rows.release_notes`.

### Documents

`document` declares a reusable markdown structure for markdown-bearing inputs
and outputs.

```prompt
document LessonPlan: "Lesson Plan"
    section read_first: "Read First"
        sequence steps:
            "Read the learner goal."
            "Read the current lesson plan."

    bullets evidence: "Evidence"
        "Name the latest status source."
        "Name the latest review note."
```

Important rules:

- `document` supports readable block kinds such as `section`, `sequence`,
  `bullets`, `checklist`, `definitions`, `properties`, `table`, `guard`,
  `callout`, `code`, `markdown`, `html`, `footnotes`, `image`, and `rule`.
- Block headers may carry `required`, `advisory`, or `optional`, plus
  descriptive `when <expr>` metadata.
- `sequence`, `bullets`, and `checklist` may declare `item_schema:` for typed
  keyed descendants on the list item surface.
- `sequence`, `bullets`, and `checklist` titles are optional. Keep the key.
  With a title, the list renders as a nested headed block. Without a title,
  the list renders directly inside the parent section.
- Inline `table` blocks may declare `row_schema:` alongside `columns:` /
  `rows:` and may use structured cell bodies when a row needs nested readable
  content. Documents may also use a named top-level table with
  `table local_key: TableRef`.
- Raw `markdown`, raw `html`, `footnotes`, and `image` are explicit block
  kinds; they are not silent fallbacks from ordinary prose.
- `document` inheritance uses the same explicit accounting model as workflows:
  `inherit key` keeps a parent block, `override <kind> key` replaces it in
  place, and changing block kind fails loudly.
- `structure:` on `input` or `output` points at a named `document` and
  requires a markdown-bearing shape such as `MarkdownDocument` or
  `AgentOutputDocument`.
- `document` may attach `render_profile:` so downstream markdown-bearing
  surfaces can render the same structure with a different presentation policy.
- Document blocks are addressable by authored key, and keyed descendants stay
  addressable where the block shape defines them:
  `LessonPlan:overview.title`, `LessonPlan:read_order.first`,
  `LessonPlan:read_order.item_schema.step_label.title`,
  `LessonPlan:step_arc.columns.coaching_level.title`,
  `LessonPlan:step_arc.row_schema.topic.title`, and
  `LessonPlan:step_arc.rows.step_1`.

### Render Profiles

`render_profile` declares reusable markdown presentation policy for shipped
readable surfaces.

```prompt
render_profile CompactComment:
    properties -> sentence
    guarded_sections -> concise_explanatory_shell
    identity.owner -> title_and_key
    identity.enum_wire -> wire_only
```

Important rules:

- Built-in shipped profile families are `ContractMarkdown`,
  `ArtifactMarkdown`, and `CommentMarkdown`.
- Authored `render_profile` declarations may override supported readable
  targets such as `properties`, `guarded_sections`, the identity-aware
  display family, and the shipped semantic lowering targets
  `analysis.stages`, `review.contract_checks`, and `control.invalidations`.
- `analysis.stages` supports `titled_section` and `natural_ordered_prose`.
- `review.contract_checks` supports `titled_section` and `sentence`.
- `control.invalidations` supports `expanded_sequence` and `sentence`.
- Workflow-law sentences such as `current artifact`, `own only`, and
  `preserve exact` stay compiler-owned sentence lowering. They are not shipped
  `render_profile` targets.
- `render_profile:` may attach to `analysis`, `schema`, `document`, and
  markdown-bearing `output`.
- `Comment` and `CommentText` outputs default to `CommentMarkdown`.
- Other markdown-bearing outputs default to `ArtifactMarkdown`.
- Unprojected identity refs stay human-facing by default; authored profiles may
  request title-plus-key debug readback or wire-only enum display without
  changing addressability.
- A `document render_profile:` survives `output structure:` lowering unless the
  markdown-bearing output attaches its own `render_profile:`.
- Directly rendered readable declarations continue to use the contract-style
  `ContractMarkdown` baseline unless a downstream lowering surface overrides it.

## Skills

Doctrine treats reusable capability as named `skill` declarations, not as
ad hoc script prose.

```prompt
skill RepoSearch: "repo-search"
    purpose: "Find the right repo surface for the current job."
```

The shipped skill surface has two layers:

- `skill`: the reusable capability object and its typed metadata
- `skills`: a reusable block of role-specific skill relationships

Skill relationships are authored where they are used:

- `skill local_key: SkillRef`
- relationship metadata such as `requirement` or `reason`
- relationship bodies may reuse ordinary record-body readable blocks such as
  `definitions`, `callout`, or `code`
- inherited `skills` blocks with the same explicit patching model used
  elsewhere
- when Doctrine should own a real skill-package filesystem tree instead of an
  inline reusable capability, use `skill package` in `SKILL.prompt`

Rendered Markdown keeps each inline skill compact:

- the skill title renders as the skill heading
- `requirement: Required` renders `_Required skill_` under that heading
- ordinary fields such as `purpose`, `use_when`, and `reason` render as bold
  labeled blocks instead of deeper nested headings
- readable blocks attached to the skill reference body, such as `callout`,
  still render as ordinary readable blocks

When a field is really a list, author a titleless `bullets` or `checklist`
block inside that field so the emitted Markdown stays easy to scan.

```prompt
skill RepoSearch: "repo-search"
    purpose: "Find the right repo surface for the current job."

    use_when: "Use When"
        bullets cases:
            "Use this when the job still needs the right repo entrypoint."
            "Narrow the task before you search if the request is still broad."
```

Typical emitted shape inside a `skills` block:

```md
#### repo-search
_Required skill_

**Purpose**
Find the right repo surface for the current job.

**Use When**
- Use this when the job still needs the right repo entrypoint.
- Narrow the task before you search if the request is still broad.
```

## Skill Packages

Doctrine also ships a first-class package surface for real skill bundles.

```prompt
skill package GreetingSkill: "Greeting Skill"
    metadata:
        name: "greeting-skill"
        description: "Write short, friendly greetings that sound human."
        version: "1.0.0"
        license: "MIT"
    "Write short, friendly greetings that fit the current conversation."
```

Important rules:

- `SKILL.prompt` is the package entrypoint.
- A package entrypoint owns one top-level `skill package`.
- The `skill package` body uses the same record and readable-block family used
  by other readable markdown-bearing surfaces.
- `metadata:` currently accepts `name`, `description`, `version`, and
  `license`.
- If `metadata.name` is omitted, the emitted frontmatter falls back to the
  package declaration key.
- The directory that contains `SKILL.prompt` is the package source root.
- `SKILL.prompt` compiles to `SKILL.md`.
- Any bundled file that is not a `.prompt` file emits under the same relative
  path, byte for byte, so relative Markdown links keep working after emit.
- Bundled agent prompts under `agents/**/*.prompt` compile to markdown
  companions under the same relative paths, with `.prompt` replaced by `.md`.
- Other files in the same `agents/` tree still bundle normally.
- Other descendant prompt-bearing subtrees stay compiler-owned; Doctrine does
  not copy their `.prompt` files through as ordinary bundle files.
- Reserved-path and case-collision errors fail loudly. `SKILL.md` is
  compiler-owned output, not an authored source file.
- Use inline `skill` and `skills` when the capability only needs reusable
  semantics inside agent doctrine. Use `skill package` when Doctrine should
  author and emit the package tree itself.

## Inputs And Outputs

Doctrine makes turn contracts explicit.

### Inputs

An `input` declares what a turn may read:

```prompt
input DraftSpec: "Draft Spec"
    source: File
        path: "unit_root/DRAFT_SPEC.md"
    shape: MarkdownDocument
    requirement: Required
```

Important rules:

- `source`, `shape`, and `requirement` are separate questions.
- Built-in sources used in the shipped corpus include `Prompt`, `File`, and
  `EnvVar`.
- Custom sources can be declared with `input source`.
- `structure:` may attach a named `document` to a markdown-bearing input.
- Ordinary record bodies may also reuse readable block kinds such as
  `definitions`, `table`, `callout`, and `code`.
- `inputs` blocks group and bind inputs with local keys for a concrete turn.

### Omitted Wrapper Titles

`inputs` and `outputs` wrapper sections have three separate title rules:

- `key: "Title"` is the normal long form.
- In inherited `inputs` or `outputs`, `override key:` keeps the parent title
  when you omit the override title.
- In base `inputs` or `outputs`, `key:` may omit the title only when the body
  resolves to exactly one direct declaration. Doctrine lowers the wrapper into
  that declaration's heading, so the output has one visible heading.
- If an omitted wrapper title would need a guess, such as multiple direct refs
  or keyed child sections, Doctrine fails loud.
- Titleless `sequence`, `bullets`, and `checklist` also lower into their
  parent. Inherited `override key:` forms are different because they keep an
  inherited title.

Example:

```prompt
input LessonsIssueLedger: "Lessons Issue Ledger"
    source: File
        path: "catalog/lessons_issue_ledger.json"
    shape: "JSON Document"
    requirement: Required

output SectionHandoff: "Section Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

inputs SectionDossierInputs: "Your Inputs"
    issue_ledger:
        LessonsIssueLedger

outputs SectionDossierOutputs: "Your Outputs"
    section_handoff:
        SectionHandoff
```

The omitted wrappers render one visible heading each: `Lessons Issue Ledger`
and `Section Handoff`. The direct declaration bodies render under those
headings without a second nested heading.

Concrete shipped proof:

- `examples/117_io_omitted_wrapper_titles`

### Outputs

An `output` declares what a turn emits:

```prompt
output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required
```

Important rules:

- An output uses either `target` plus `shape`, or a titled `files:` section.
- Built-in targets used in the shipped corpus include `TurnResponse` and
  `File`.
- Custom targets can be declared with `output target`.
- Output shapes can be named with `output shape`.
- `schema:` on `output` attaches a Doctrine `schema` declaration.
- `schema:` on `output shape` remains the owner-aware attachment point for
  `output schema` when the shape kind is `JsonObject`.
- `output schema` owns the machine-readable payload fields for structured
  `JsonObject` outputs.
- `output schema` may also declare an optional `example:` block. When present,
  Doctrine validates it and renders an `Example` section on structured final
  outputs.
- `structure:` on `output` attaches a named `document` when the output shape is
  markdown-bearing.
- `render_profile:` may attach to a markdown-bearing `output` when exactly one
  output artifact owns the markdown contract.
- Output record bodies may reuse the same readable block family that `document`
  uses, including `definitions`, `properties`, `table`, explicit `guard`
  shells, `callout`, `code`, raw `markdown`, raw `html`, `footnotes`, and
  `image`.
- `output schema` is subordinate to `output shape`, not a competing output
  primitive.
- `outputs` blocks group and bind outputs with local keys for a concrete turn.
- `final_output:` on an agent designates one emitted `TurnResponse` output as
  the final assistant message.
- When that designated output's `output shape` carries an `output schema`, the
  final assistant message is structured JSON. Otherwise it stays ordinary
  prose or markdown according to the output contract.
- If that `output schema` omits `example:`, the structured final-output render
  still succeeds and skips the `Example` section.
- On review-driven agents, the designated final output may be either the
  review's `comment_output:` or a second emitted `TurnResponse`.
  `comment_output:` still remains the review carrier for routing and
  currentness semantics.
- When that second output uses `review_fields:`, the compiler binds those
  paths to review semantics and emits whether the split final response is
  `control_ready`.
- The designated final output renders under a dedicated `Final Output`
  section and is omitted from ordinary `Outputs` rendering for that agent.

Shipped Markdown render shape:

- This is emitted output shape only. It does not change the input language.
- A single-artifact ordinary output renders one grouped `Contract | Value`
  table first.
- A `files:` output renders that same contract table, then an `Artifacts`
  table for the named files.
- `current_truth`, titled `properties`, parseable `notes`, and
  `support_files` render as tables when their authored shape is tabular.
- `trust_surface` keeps its own section, and ordinary output labels render as
  inline code.
- `structure:` renders as one `Artifact Structure` section with a summary
  table and any needed detail blocks.

Example emitted shape:

```md
### Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |
```

### Output Inheritance

Inherited outputs use the same explicit patching style Doctrine already uses
elsewhere:

- `output Child[Parent]: "Title"` inherits from another `output`
- `inherit key` keeps one inherited top-level output entry
- `override key:` replaces one inherited top-level output entry
- top-level attachment keys such as `target`, `shape`, `requirement`,
  `schema`, `structure`, `render_profile`, `trust_surface`, and
  `standalone_read` follow that same explicit `inherit` or `override` model
- children must account for every inherited top-level key exactly once
- inherited parent outputs must use stable keyed top-level items only
- `outputs[...]` block inheritance is separate from `output[...]` declaration
  inheritance
- v1 output inheritance is top-level only; if you need to change
  `current_truth.invalidations`, override `current_truth` and rewrite that
  whole top-level section

Output bodies may also contain:

- authored fields and sections
- readable declaration refs
- `standalone_read`
- guarded output items such as
  `next_owner: route.next_owner when route.exists`
- keyed guarded sections such as
  `failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:`
- `trust_surface`

For the full I/O model, see [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md).

## Imports

Imports compose typed declarations across prompt modules.

```prompt
import shared.contracts
import .local.sibling
import ..common.roles
```

Important rules:

- Each prompt file still owns its nearest local `prompts/` tree.
- Inside one `prompts/` root, an import may resolve to either
  `<module>.prompt` or `<module>/AGENTS.prompt`.
- If both shapes exist for the same dotted path, Doctrine fails loudly
  instead of guessing which one owns the module.
- Absolute imports may also search explicitly configured shared authored roots
  from `[tool.doctrine.compile].additional_prompt_roots` in the nearest
  `pyproject.toml`.
- Each `additional_prompt_roots` entry resolves relative to that
  `pyproject.toml` and must point at an existing directory literally named
  `prompts`.
- A file-backed `<module>.prompt` import is a compile-time module only.
- A directory-backed `<module>/AGENTS.prompt` import is a runtime package
  root for `emit_docs` and the shared runtime frontier that `emit_flow`
  uses.
- A sibling `SOUL.prompt` beside a runtime package `AGENTS.prompt` is optional
  runtime emit input. It is not a second import target.
- Absolute and relative imports both keep typed declaration identity.
- Relative imports stay rooted in the importing module's own `prompts/` tree.
  They do not hop across configured roots.
- `SKILL.prompt` uses the same import rules, including bundled package modules
  such as `agents.cold_reviewer`.
- Imported symbols are still used through normal declaration refs such as
  `shared.contracts.ReviewContract`.
- Duplicate dotted modules across configured roots fail loudly instead of using
  root precedence heuristics.
- Missing modules, missing declarations, duplicate declarations, and module
  cycles still fail loudly.

## Readable Refs, Addressable Paths, And Interpolation

Doctrine has two related reference surfaces.

### Readable refs

Inside workflow sections and record bodies, a declaration ref renders as a
readable mention of that declaration rather than expanding the whole contract.

Examples:

- `DraftSpec`
- `ReviewComment`
- `MetadataContract:files.summary`
- `ProjectLead:title`
- `ProjectLead:key`
- `ReleaseAnalysis:stages.title`
- `BuildSurfaceSchema:sections.summary.title`
- `BuildSurfaceSchema:artifacts.manifest_file.title`
- `ReleaseGates:columns.evidence.title`
- `LessonPlan:read_order.first`
- `LessonPlan:step_arc.columns.coaching_level.title`
- `NextOwner:section_author.wire`

### Addressable paths

Nested keyed items can be addressed explicitly:

- `Decl:path.to.child`
- `ProjectLead:key`
- `Output:detail_panel.rewrite_detail`
- `Workflow:section.title`
- `BuildSurfaceSchema:groups.downstream_rebuild.title`
- `ReleaseGates:columns.evidence.title`
- `LessonPlan:overview.title`
- `LessonPlan:step_arc.rows.step_1`
- `NextOwner:section_author.wire`

Paths follow authored keyed structure only. Trying to descend past a scalar
leaf fails loudly. Keyed list items, keyed definition items, table declaration
columns, document table columns, and document table rows are addressable;
anonymous list items are not. The first `:` separates the root declaration
from its path, and any deeper projections use dot segments such as
`NextOwner:section_author.wire`.

### Authored interpolation

Authored prose surfaces may interpolate declaration data inline:

- `{{Ref}}`
- `{{Ref:path.to.child}}`
- `{{ProjectLead:key}}`
- `{{AgentRef:name}}`
- `{{NextOwner:section_author.wire}}`

Interpolation is still authored prose. Authors keep control of punctuation,
wording, and emphasis.

Concrete-agent roots expose title-bearing identity projections:

- bare `{{AgentRef}}` defaults to the human-facing title when one exists
- `{{AgentRef:title}}` resolves the visible title explicitly
- `{{AgentRef:key}}` and legacy `{{AgentRef:name}}` resolve the structural
  declaration name

Enum members expose the same title-versus-key split plus optional wire values:

- bare `{{EnumRef:member_key}}` defaults to the member title
- `{{EnumRef:member_key.key}}` resolves the structural member key
- `{{EnumRef:member_key.wire}}` resolves the serialized or host-facing wire
  value

Review-bound outputs add semantic interpolation roots such as `contract.*` and
`fields.*`; those are documented in [REVIEW_SPEC.md](REVIEW_SPEC.md).

## Enums And Expressions

`enum` declares a closed vocabulary once and gives later law or review a stable
set of values to branch on.

```prompt
enum ReviewMode: "Review Mode"
    draft_rewrite: "Draft Rewrite"
        wire: "draft-rewrite"

    metadata_refresh: "Metadata Refresh"
        wire: "metadata-refresh"
```

Important rules:

- Enum member keys stay structural; authored titles are the readable runtime
  surface.
- `wire:` is optional and remains the host-facing or serialized value.
- The one-line member form remains legal shorthand for `title == wire`.

The shipped expression surface supports:

- dotted refs
- string, number, and boolean literals
- set literals
- helper-style calls used by the corpus, such as `present(...)` and
  `unclear(...)`
- boolean operators and comparison operators

Those expressions are used in `when`, `match`, guarded output items,
workflow law, and review semantics.

## Markdown Emission

Doctrine compiles human-facing Markdown, not a debug dump of the source tree.

Emission rules to remember:

- scalar `role` text opens the document directly
- titled fields render as Markdown headings
- nested titled sections render at deeper heading levels
- adjacent prose lines preserve order
- emphasized lines render as `**REQUIRED**:`, `**IMPORTANT**:`,
  `**WARNING**:`, and `**NOTE**:`
- compiler keys stay structural unless the author makes them visible through a
  title or prose

## Where To Go Next

- Use [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md) for turn contracts,
  bindings, and trusted carriers.
- Use [WORKFLOW_LAW.md](WORKFLOW_LAW.md) for currentness, scope,
  preservation, invalidation, and route-only turns.
- Use [REVIEW_SPEC.md](REVIEW_SPEC.md) for first-class reviewer turns.
- Use [../examples/README.md](../examples/README.md) for the full numbered
  teaching ladder.
