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

- `render_profile`, `analysis`, `schema`, `document`
- `agent`, `abstract agent`
- `workflow`, `route_only`, `grounding`
- `review`, `review_family`, `abstract review`
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
  `skills`, and `review`.
- Any other keyed field is an authored workflow slot. Those slots can point at
  a named `workflow` or define an inline workflow body.
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
- `analysis` may attach `render_profile:` to control how its readable
  structure renders when another shipped surface lowers it into markdown.
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
  `json schema`.
- Output-attached schemas must still expose at least one section.
- Schema addressability is family-namespaced by authored key:
  `BuildSurfaceSchema:sections.summary.title`,
  `BuildSurfaceSchema:artifacts.manifest_file.title`, and
  `BuildSurfaceSchema:groups.downstream_rebuild.title`.
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
  `bullets`, `checklist`, `definitions`, `properties`, `table`, `guard`,
  `callout`, `code`, `markdown`, `html`, `footnotes`, `image`, and `rule`.
- Block headers may carry `required`, `advisory`, or `optional`, plus
  descriptive `when <expr>` metadata.
- `sequence`, `bullets`, and `checklist` may declare `item_schema:` for typed
  keyed descendants on the list item surface.
- `table` may declare `row_schema:` alongside `columns:` / `rows:` and may use
  structured cell bodies when a row needs nested readable content.
- Raw `markdown`, raw `html`, `footnotes`, and `image` are explicit block
  kinds; they are not silent fallbacks from ordinary prose.
- `document` inheritance uses the same explicit accounting model as workflows:
  `inherit key` keeps a parent block, `override <kind> key` replaces it in
  place, and changing block kind fails loudly.
- `structure:` on `input` or `output` points at a named `document`.
- `structure:` requires a markdown-bearing shape such as `MarkdownDocument` or
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
- `render_profile:` may attach to a markdown-bearing `output` when exactly one
  output artifact owns the markdown contract.
- Output record bodies may reuse the same readable block family that `document`
  uses, including `definitions`, `properties`, `table`, explicit `guard`
  shells, `callout`, `code`, raw `markdown`, raw `html`, `footnotes`, and
  `image`.
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
- `ProjectLead:title`
- `ProjectLead:key`
- `ReleaseAnalysis:stages.title`
- `BuildSurfaceSchema:sections.summary.title`
- `BuildSurfaceSchema:artifacts.manifest_file.title`
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
- `LessonPlan:overview.title`
- `LessonPlan:step_arc.rows.step_1`
- `NextOwner:section_author.wire`

Paths follow authored keyed structure only. Trying to descend past a scalar
leaf fails loudly. Keyed list items, keyed definition items, table columns,
and table rows are addressable; anonymous list items are not. The first `:`
separates the root declaration from its path, and any deeper projections use
dot segments such as `NextOwner:section_author.wire`.

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
