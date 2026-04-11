# Shipped Language Reference

Doctrine prompt files compile structured source into runtime Markdown. The
authoring surface is a small set of named declarations plus explicit
composition and fail-loud compiler rules. The shipped compiler reuses loaded
prompt graphs so larger prompt families remain practical, not just toy-sized
examples.

For the motivation behind the project, start with [WHY_DOCTRINE.md](WHY_DOCTRINE.md).
For the numbered teaching corpus, use [../examples/README.md](../examples/README.md).

## Mental Model

- A prompt file is the source of truth.
- Concrete agents are the runtime entrypoints.
- Abstract declarations exist for reuse and inheritance, not direct emission.
- Keys are compiler identities. Authored titles and prose are the human-facing
  runtime surface.
- The compiler preserves the structure that matters and rejects ambiguous or
  inconsistent doctrine instead of guessing.

## Prompt Files And Compilation

A prompt file may contain imports and any mix of shipped declarations:

- `analysis`, `schema`, `document`
- `agent`, `abstract agent`
- `workflow`
- `review`, `abstract review`
- `skill`, `skills`
- `input`, `inputs`, `input source`
- `output`, `outputs`, `output target`, `output shape`, `json schema`
- `enum`

The normal authoring entrypoints are `AGENTS.prompt` and `SOUL.prompt`. The
emit pipeline compiles each concrete agent in the entrypoint into a Markdown
runtime artifact whose basename matches the entrypoint stem.
Doctrine does that work through a shared compilation session, so module loading
and indexing happen once per entrypoint and batch emit or verification surfaces
can fan out safely while preserving deterministic output order.
For target configuration, output layout, and flow-diagram emission, use
[EMIT_GUIDE.md](EMIT_GUIDE.md).

## Agents

Agents are the top-level runtime owners.

```prompt
abstract agent BaseRole:
    read_first: SharedTurn

agent Reviewer[BaseRole]:
    role: "Core job: review the current brief."
    inherit read_first
```

Important rules:

- `agent` declares a concrete runtime owner.
- `abstract agent` declares an inheritance-only owner that does not render on
  its own.
- Every concrete agent needs a `role`.
- Reserved typed agent fields include `inputs`, `outputs`, `analysis`,
  `skills`, and `review`.
- Any other keyed field is an authored workflow slot. Those slots can point at
  a named `workflow` or define an inline workflow body.
- `abstract <slot_key>` marks an authored slot that concrete children must
  define directly.
- `inherit <slot_key>` keeps an inherited authored slot unchanged.
- `override <slot_key>:` replaces an inherited authored slot in place.
- A concrete agent may not define both `workflow:` and `review:`. Review turns
  use `review:` as their main semantic body.
- `analysis:` attaches one reusable `analysis` declaration to an otherwise
  ordinary concrete turn.

`role` has two shipped shapes:

- scalar `role: "..."` emits opening prose directly
- titled `role: "Title"` with an indented body emits a headed section

## Workflows

`workflow` is Doctrine's reusable instruction surface.

```prompt
workflow SharedTurn: "How To Take A Turn"
    "Read the current brief before you act."

    next_step: "Next Step"
        route "Return to ReviewLead when ready." -> ReviewLead
```

A workflow body may contain:

- prose lines
- local keyed sections
- `use <local_key>: WorkflowRef` composition
- readable declaration refs inside titled section bodies
- inline or referenced `skills:` blocks
- `law:` for compiler-owned workflow-law semantics

Important rules:

- Workflow titles are human-facing headings.
- Keys are the patch identities used by inheritance and addressable refs.
- Bare workflow roots are composed with `use`; they do not render as readable
  refs inside ordinary workflow section bodies.
- Titled workflow section bodies may contain prose, route lines, local nested
  sections, readable declaration refs, and readable block kinds such as
  `section`, `sequence`, `bullets`, `checklist`, `definitions`, `table`,
  `callout`, `code`, and `rule`.

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

## Analysis, Schemas, And Documents

Doctrine ships three additional readable declaration families for structured
reasoning, artifact inventories, and reusable markdown structure.

### Analysis

`analysis` declares a reusable reasoning program that a concrete agent may
attach through `analysis:`.

```prompt
analysis ReleaseAnalysis: "Release Analysis"
    stages: "Stages"
        derive "Release plan" from {CurrentPlan}
        classify "Risk band" as RiskBand
        compare "Coverage" against {CurrentPlan}
        defend "Recommendation" using {CurrentPlan}
```

Important rules:

- `analysis` is a readable declaration with titled keyed sections.
- A section body may contain prose plus `derive`, `classify`, `compare`, and
  `defend`.
- `classify ... as EnumRef` uses a declared `enum`.
- `derive`, `compare`, and `defend` read declared artifact roots or addressable
  paths.
- Analysis sections are addressable, so refs such as
  `ReleaseAnalysis:stages.title` are valid.

### Schemas

`schema` declares a reusable artifact inventory and optional gate catalog.

```prompt
schema DeliveryInventory: "Delivery Inventory"
    sections:
        summary: "Summary"
            "Include a short summary."

    gates:
        evidence_grounded: "Evidence Grounded"
            "Confirm the evidence is cited."
```

Important rules:

- `schema` owns artifact inventory sections and optional named `gates:`.
- On `output`, `schema:` points at a Doctrine `schema` declaration.
- On `output shape`, `schema:` remains the owner-aware attachment point for
  `json schema`.
- Schema sections and gates are addressable by authored key.
- `review contract:` may point at either a `workflow` or a `schema`.

### Documents

`document` declares a reusable markdown structure for markdown-bearing inputs
and outputs.

```prompt
document LessonPlan: "Lesson Plan"
    section overview: "Overview"
        "Start with the plan overview."

    sequence steps: "Sequence"
        "List the lesson steps in order."
```

Important rules:

- `document` supports readable block kinds such as `section`, `sequence`,
  `bullets`, `checklist`, `definitions`, `table`, `callout`, `code`, and
  `rule`.
- Block headers may carry `required`, `advisory`, or `optional`, plus
  descriptive `when <expr>` metadata.
- `document` inheritance uses the same explicit accounting model as workflows:
  `inherit key` keeps a parent block, `override <kind> key` replaces it in
  place, and changing block kind fails loudly.
- `structure:` on `input` or `output` points at a named `document`.
- `structure:` requires a markdown-bearing shape such as `MarkdownDocument` or
  `AgentOutputDocument`.
- Document blocks are addressable by authored key, and keyed descendants stay
  addressable where the block shape defines them:
  `LessonPlan:overview.title`, `LessonPlan:read_order.first`,
  `LessonPlan:step_arc.columns.coaching_level.title`, and
  `LessonPlan:step_arc.rows.step_1`.

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
  `json schema`.
- `structure:` on `output` attaches a named `document` when the output shape is
  markdown-bearing.
- Output record bodies may reuse the same readable block family that `document`
  uses, including `definitions`, `table`, `callout`, and `code`.
- `json schema` is subordinate to `output shape`, not a competing output
  primitive.
- `outputs` blocks group and bind outputs with local keys for a concrete turn.

Output bodies may also contain:

- authored fields and sections
- readable declaration refs
- `standalone_read`
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

- Import resolution is rooted in the nearest `prompts/` tree.
- Absolute and relative imports both keep typed declaration identity.
- Imported symbols are still used through normal declaration refs such as
  `shared.contracts.ReviewContract`.
- Missing modules, missing declarations, duplicate declarations, and module
  cycles fail loudly.

## Readable Refs, Addressable Paths, And Interpolation

Doctrine has two related reference surfaces.

### Readable refs

Inside workflow sections and record bodies, a declaration ref renders as a
readable mention of that declaration rather than expanding the whole contract.

Examples:

- `DraftSpec`
- `ReviewComment`
- `MetadataContract:files.summary`
- `ReleaseAnalysis:stages.title`
- `LessonPlan:read_order.first`
- `LessonPlan:step_arc.columns.coaching_level.title`

### Addressable paths

Nested keyed items can be addressed explicitly:

- `Decl:path.to.child`
- `Output:detail_panel.rewrite_detail`
- `Workflow:section.title`
- `LessonPlan:overview.title`
- `LessonPlan:step_arc.rows.step_1`

Paths follow authored keyed structure only. Trying to descend past a scalar
leaf fails loudly. Keyed list items, keyed definition items, table columns,
and table rows are addressable; anonymous list items are not.

### Authored interpolation

Authored prose surfaces may interpolate declaration data inline:

- `{{Ref}}`
- `{{Ref:path.to.child}}`
- `{{AgentRef:name}}`

Interpolation is still authored prose. Authors keep control of punctuation,
wording, and emphasis.

Review-bound outputs add semantic interpolation roots such as `contract.*` and
`fields.*`; those are documented in [REVIEW_SPEC.md](REVIEW_SPEC.md).

## Enums And Expressions

`enum` declares a closed vocabulary once and gives later law or review a stable
set of values to branch on.

```prompt
enum ReviewMode: "Review Mode"
    draft_rewrite: "draft-rewrite"
    metadata_refresh: "metadata-refresh"
```

The shipped expression surface supports:

- dotted refs
- string, number, and boolean literals
- set literals
- helper-style calls used by the corpus, such as `present(...)` and
  `unclear(...)`
- boolean operators and comparison operators

Those expressions are used in `when`, `match`, guarded output sections,
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
