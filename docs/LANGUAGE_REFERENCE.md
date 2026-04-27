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

- A flow root owns one namespace.
- Individual prompt files inside that flow only split the authored source.
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
- `receipt`, `artifact`, `stage`, `skill_flow`, `skill_graph`
- `input`, `inputs`, `input source`
- `output`, `outputs`, `output target`, `output shape`, `output schema`
- `enum`

The normal agent entrypoints are `AGENTS.prompt` and `SOUL.prompt`. The normal
skill-package entrypoint is `SKILL.prompt`. The normal standalone graph
entrypoint is `GRAPH.prompt`. `emit_docs` compiles concrete agents from the
agent entrypoints into runtime Markdown artifacts whose basename matches the
entrypoint stem. It also emits imported directory-backed runtime packages when
a selected `AGENTS.prompt` uses them as runtime homes. Structured final
outputs also emit the exact lowered schema at
`schemas/<output-slug>.schema.json` beside that Markdown file. When a turn also
needs final-response, review, route, or resolved previous-turn IO metadata,
`emit_docs` writes `final_output.contract.json` beside that Markdown file.
`emit_skill` compiles one top-level `skill package` from `SKILL.prompt` into
`SKILL.md` plus bundled source-root files. `emit_skill_graph` compiles one
top-level `skill_graph` from a supported entrypoint such as `AGENTS.prompt`,
`SKILL.prompt`, or `GRAPH.prompt` into checked graph contracts, source
receipts, Markdown views, graph JSON, diagrams, and receipt schemas. Doctrine
does that work through shared compilation and indexing so module loading
happens once per entrypoint and batch emit or verification surfaces can fan out
safely while preserving deterministic output order.
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
- `abstract <slot_key>: <TypedEntityRef>` narrows the slot to a declared
  `document`, `schema`, `table`, `enum`, `agent`, or `workflow`. Each concrete
  descendant must bind the slot to a `name_ref` of the same family. The
  compiler rejects wrong-family bindings with `E538` and unresolvable
  annotations with `E539`. The annotation is deliberately narrower than
  skill `host_contract` family typing and output-schema field typing; the
  three shapes remain distinct.
- `inherit <slot_key>` keeps an inherited authored slot unchanged.
- `inherit {slot_a, slot_b}` is grouped parser sugar for repeated inherited
  slot accounting in the same authored order.
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
        verdict
        current_artifact: current_artifact
        next_owner
```

- On `fields:`, `override fields:`, and `review_fields:`, a bare semantic name
  like `verdict` is shorthand for the identity bind `verdict: verdict`.
  Keep `semantic: path` for non-identity binds.
- Structured final outputs may also bind one `route field` on that same output
  as the route owner:

```prompt
final_output:
    output: WriterDecision
    route: next_route
```
- Any emitted output may also read shared compiler-owned route semantics
  through `route.exists`, `route.next_owner`, `route.next_owner.key`,
  `route.next_owner.title`, `route.label`, and `route.summary` when the active
  workflow-law, `handoff_routing` law, `route_only`, `grounding`, or review
  branch resolves a real route.
- When every live routed branch on that turn comes from `route_from`, or when
  `final_output.route:` binds a `route field` on a structured final output,
  outputs may also read
  `route.choice`, `route.choice.key`, `route.choice.title`, and
  `route.choice.wire`.
- `route.next_owner.*` may stay live across several `route_from` branches. It
  means the selected route owner. `route.label` and `route.summary` still need
  one selected branch.
- If `emit_docs` writes `final_output.contract.json`, it emits this same route
  truth as a top-level `route` block. That emitted contract may also carry a
  `route.selector` object when the route comes from a bound final-output route
  field. Harnesses should use that block for runtime routing instead of copied
  owner strings in the payload.
- In authored guards, `route.exists` means a routed owner exists on that live
  branch. In emitted `final_output.contract.json`, `route.exists` means the
  final response carries route semantics at all, even when a nullable route
  field selected no handoff.
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
- `inherit {first_key, second_key}` keeps several inherited keyed items in
  the same authored position order
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
- `review contract:` may point at either a `workflow` or a `schema`. Review
  bodies reference contract gates by symbol as `contract.NAME`, and a typo in
  that reference fails loud with `E477`. See
  [REVIEW_SPEC.md](REVIEW_SPEC.md#review-contracts) and
  `examples/140_typed_gates_symbol_reference/` for proof.
- A case inside `review_family cases:` may adjust the shared contract's gate
  set through `override gates:` with `add`, `remove`, and `modify` lines.
  Removing or modifying a gate that the contract does not declare fails loud
  with `E531`; adding a gate name that already exists in the case's effective
  gate set fails loud with `E532`. See
  [REVIEW_SPEC.md](REVIEW_SPEC.md#core-review-configuration) and
  `examples/141_review_case_gate_override/` for proof.

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
- Every non-rule readable block kind has a bare form and a named form.
  The bare form drops the CNAME key and any heading string (for example,
  `definitions:`, `callout:`, `table:`, `footnotes:`, `image:`, `code:`,
  `markdown:`, `html:`). The renderer skips the H3 heading and the
  `_kind · ..._` descriptor for bare forms. Use the named form (for example,
  `definitions done_when: "Done When"`) when the block must be addressable
  from another declaration, when it needs a visible heading, or when the
  block carries `required`, `advisory`, or `when` metadata.
- `sequence`, `bullets`, and `checklist` may declare `item_schema:` for typed
  keyed descendants on the list item surface.
- `sequence`, `bullets`, and `checklist` titles are optional. Keep the key.
  With a title, the list renders as a nested headed block. Without a title,
  the list renders directly inside the parent section and is marked
  anonymous internally.
- Inline `table` blocks may declare `row_schema:` alongside `columns:` /
  `rows:` and may use structured cell bodies when a row needs nested readable
  content. Documents may also use a named top-level table with
  `table local_key: TableRef`.
- Raw `markdown`, raw `html`, `footnotes`, and `image` are explicit block
  kinds; they are not silent fallbacks from ordinary prose.
- `document` inheritance uses the same explicit accounting model as workflows:
  `inherit key` keeps a parent block, `override <kind> key` replaces it in
  place, and changing block kind fails loudly.
- `inherit {intro, appendix}` is the grouped parser-sugar form when a child
  keeps several inherited document blocks unchanged.
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

Top-level skills may also declare checked graph relations:

```prompt
skill AuthorSkill: "Author Skill"
    purpose: "Own the first draft."
    package: "author-package"
    relations:
        requires ReviewSkill:
            why: "Review uses {{skill:ReviewSkill.package}}."

skill ReviewSkill: "Review Skill"
    purpose: "Review the draft."
    package: "review-package"
```

The shipped skill surface has three connected layers:

- `skill`: the reusable capability object and its typed metadata
- `skills`: a reusable block of role-specific skill relationships
- `relations:` on `skill`: checked skill-to-skill graph edges

Skill relationships are authored where they are used:

- `skill local_key: SkillRef`
- relationship metadata such as `requirement` or `reason`
- relationship bodies may reuse ordinary record-body readable blocks such as
  `definitions`, `callout`, or `code`
- inherited `skills` blocks with the same explicit patching model used
  elsewhere
- when Doctrine should own a real skill-package filesystem tree instead of an
  inline reusable capability, use `skill package` in `SKILL.prompt`
- graph-level skill relations live on the top-level `skill`, not on each
  role-local `skills` use site

Rendered Markdown keeps each inline skill compact:

- the skill title renders as the skill heading
- `requirement: Required` renders `_Required skill_` under that heading
- ordinary fields such as `purpose`, `use_when`, and `reason` render as bold
  labeled blocks instead of deeper nested headings
- readable blocks attached to the skill reference body, such as `callout`,
  still render as ordinary readable blocks

Skill relation rules:

- Relation targets must resolve to top-level `skill` declarations.
- Relation kinds are closed. The shipped kinds are `requires`,
  `delegates_to`, `wraps`, `audits`, `extends`, `supports`, `composes`,
  `teaches`, `repairs`, `baseline_for`, `blocks`, `supersedes`, `related`,
  `owns_surface`, `reads_surface`, and `writes_surface`.
- A graph with `require relation_reason` fails with `E566` when a relation
  omits `why:`.
- A graph with `warn relation_without_reason` emits `W210` for a relation that
  omits `why:` when the strict policy is off.
- Graph closure includes relation target skills for reached skills. Graph JSON
  and graph contracts carry the resolved relation facts.
- Graph skill inventories carry package ids and optional authored metadata
  such as `category`, `visibility`, `manual_only`, `default_flow_member`, and
  `aliases` when those fields are present.

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
    source:
        id: "examples.greeting-skill"
        track:
            "domain"
    emit:
        "references/query-patterns.md": QueryPatterns
    "Write short, friendly greetings that fit the current conversation."
```

Important rules:

- `SKILL.prompt` is the package entrypoint.
- A package entrypoint owns one top-level `skill package`.
- The `skill package` body uses the same record and readable-block family used
  by other readable markdown-bearing surfaces.
- `metadata:` currently accepts `name`, `description`, `version`, and
  `license`.
- `source:` is optional. It may declare `id:` and a `track:` list of extra
  source files or directories.
- `emit:` is optional. Use it when a package should emit extra `.md` files
  from prompt-authored `document` declarations.
- Each `emit:` entry is `"relative/path.md": DocumentRef`.
- `emit:` paths must stay under the package source root and end in `.md`.
- `emit:` refs must point at `document` declarations.
- If `metadata.name` is omitted, the emitted frontmatter falls back to the
  package declaration key.
- The directory that contains `SKILL.prompt` is the package source root.
- Prompt files inside that package flow already share one flat namespace.
  Use bare same-flow refs there.
- Use absolute imports from the package source root only when you cross into a
  different nested flow, such as a bundled runtime home under `agents/.../`.
- `SKILL.prompt` compiles to `SKILL.md`.
- `emit_skill` always writes `SKILL.source.json` beside `SKILL.md`.
- host-bound skill packages also emit `SKILL.contract.json` beside
  `SKILL.md`.
- `emit:` writes extra `.md` files under the package-relative paths you name.
- Any bundled file that is not a `.prompt` file emits under the same relative
  path, byte for byte, so relative Markdown links keep working after emit.
- Bundled agent prompts under `agents/**/*.prompt` compile to markdown
  companions under the same relative paths, with `.prompt` replaced by `.md`.
- Other files in the same `agents/` tree still bundle normally.
- Other descendant prompt-bearing subtrees stay compiler-owned; Doctrine does
  not copy their `.prompt` files through as ordinary bundle files.
- Package-local import collisions fail loud. Doctrine will not guess between a
  package-local module and a repo-wide prompt module with the same dotted
  path.
- Reserved-path and case-collision errors fail loudly. `SKILL.md` is
  compiler-owned output, not an authored source file. `SKILL.source.json`
  and `SKILL.contract.json` are also compiler-owned output paths.
- Use inline `skill` and `skills` when the capability only needs reusable
  semantics inside agent doctrine. Use `skill package` when Doctrine should
  author and emit the package tree itself.

### Package Source Receipts

`SKILL.source.json` is a build receipt for the emitted package tree.
It is not a runtime host contract.

The receipt records:

- the package name and title
- the Doctrine language version
- the source id, source root, and entrypoint
- hashed input files
- hashed output files, excluding the receipt itself
- one source tree hash
- one output tree hash

The source id comes from target `source_id`, then package `source.id`, then
`metadata.name`, then the package key.

`source.track:` lists extra files or directories that affect the package.
Tracked paths are relative to the receipt source root. Missing paths and
paths that leave the source root fail loud during `emit_skill`.

An emit target may also declare `source_root`, `source_id`, and `lock_file`.
Use that shape when a downstream repo emits a skill from an upstream source
tree. With `source_root`, the entrypoint may live outside the downstream
project root, but it must stay inside `source_root`. The output directory and
lock file still stay inside the downstream project root. The lock file must
stay outside the emitted skill tree.

Use this verifier in CI:

```bash
uv run --locked python -m doctrine.verify_skill_receipts --target <target-name>
```

The verifier reports `current`, `missing_receipt`, `stale_source`,
`edited_artifact`, `unexpected_artifact`, `foreign_package`,
`lock_out_of_date`, `receipt_lock_mismatch`, or
`unsupported_receipt_version`.

### Package Host Binding

Use package host binding when a reusable skill package needs typed host facts
from the consuming agent without copying that IO prose into every agent home.

Author the package contract once in `SKILL.prompt`:

```prompt
skill package SectionPipelineSkill: "Section Pipeline Skill"
    metadata:
        name: "section-pipeline-skill"
    host_contract:
        document section_map: "Section Map"
        final_output final_response: "Final Response"
    "Read {{host:section_map.title}}."
    "Emit through {{host:final_response}}."
```

Link the inline skill to that package:

```prompt
skill SectionPipeline: "Section Pipeline"
    purpose: "Run the section pipeline."
    package: "section-pipeline-skill"
```

Bind the host slots where the skill is used:

```prompt
skills SectionSkills: "Skills"
    skill section_pipeline: SectionPipeline
        bind:
            section_map: SectionMap
            final_response: final_output
```

Important rules:

- `host_contract:` is package-scoped. Declare it once on the root
  `skill package`.
- `bind:` is call-site scoped. Declare it once on the consuming skill entry.
- `package:`, `host_contract:`, and `bind:` are semantic only. They do not
  render into Markdown.
- The root `SKILL.prompt` body uses `{{host:slot_key}}` and
  `{{host:slot_key.path.to.child}}` interpolation.
- Emitted docs and bundled agent prompts use the same `host:` root anywhere
  that artifact kind already supports normal addressable refs.
- The shipped host-slot families are:
  - `input`
  - `output`
  - `document`
  - `analysis`
  - `schema`
  - `table`
  - `final_output`
  - `receipt`
- Bind targets may point at:
  - `inputs:key`
  - `outputs:key`
  - `analysis`
  - `final_output`
  - ordinary declaration refs such as `SectionMap`
  - addressable child paths on those same roots
- Every declared host slot must be bound exactly once, except `receipt`
  slots — the package owns the receipt contract itself, so receipt slots
  are not bound at the call site.
- Unknown slots, missing binds, extra binds, wrong families, and bad child
  paths fail loud.

#### Receipt Host Slots

Receipt slots let a skill package declare the typed receipt envelope it
emits on every run. The typed fields are the contract — downstream critics
can reference them by symbol without restating the prose.

```prompt
skill package ProducerPackage: "Producer Package"
    metadata:
        name: "producer-package"
    host_contract:
        receipt process_receipt: "Process Receipt"
            confidence: ConfidenceLevel
            evidence: list[EvidenceRow]
    "Every run emits the process receipt."
```

Rules:

- A `receipt` slot body must declare at least one typed field. Empty
  receipts fail with `E535`.
- Each field types its value with a declared `enum`, `table`, `schema`,
  or `document`. Using an undeclared name fails with `E537`.
- `list[Row]` marks a repeating field.
- Critics and other consumers address receipt fields through the skill
  binding: `skill_binding_key.receipt.field_key`. References that do not
  resolve fail with `E536`.
- `SKILL.contract.json` records each receipt slot with its typed
  `fields` map so runtime hosts can validate the emitted envelope.
- When a package has host-binding truth, `SKILL.contract.json` records the
  package host contract and the host paths used by each emitted prompt-authored
  artifact.
- Two `host_contract:` slots may not share the same key. Duplicate slot
  keys fail with `E535`.

#### Top-Level Receipt Declarations

Receipts can also live at the top level so many packages or graph stages
can share the same typed handoff fact. Top-level receipts use the same
explicit `[Parent]` inheritance model as `output`, `workflow`, and
`document`.

```prompt
enum StageStatus: "Stage Status"
    not_started: "Not Started"
    approved: "Approved"

receipt StageReceipt: "Stage Receipt"
    stage: string
    status: StageStatus

receipt LessonPlanReceipt[StageReceipt]: "Lesson Plan Receipt"
    inherit {stage, status}
    fit_grid_written: boolean
```

Rules:

- All fields are required. Model an absent value with an enum member or
  point at a nullable schema instead.
- Field types are closed: builtin scalars (`string`, `integer`, `number`,
  `boolean`), declared `enum`, `table`, `schema`, or another declared
  `receipt`. `list[Type]` marks a repeating field.
- Inherited fields must be accounted for with `inherit <key>` or
  `override <key>: <Type>`. Redeclaring an inherited field without one of
  those keywords, missing accounting for an inherited field, overriding
  an undefined parent field, or repeating a field key fails with `E544`.
- Receipt inheritance cycles and receipt-of-receipt field cycles fail
  with `E544`.

A skill package can point a host contract slot at a top-level receipt by
reference. The slot keeps its package-local key while the receipt fields
come from the shared declaration.

```prompt
skill package ControllerPackage: "Controller Package"
    metadata:
        name: "controller-package"
    host_contract:
        receipt flow_receipt: StageReceipt
        receipt plan_receipt: LessonPlanReceipt
```

Rules:

- The receipt name after the colon must resolve to a top-level `receipt`
  declaration in scope. Unresolved refs fail with `E545`.
- The slot title and field map come from the resolved receipt; do not
  restate them inside the package.
- The inline `receipt key: "Title"` form with a body still works, side by
  side with by-reference slots.
- `SKILL.contract.json` records each by-reference slot with the slot key,
  the canonical receipt name under `receipt`, the lowered `fields` map,
  and a `json_schema` object so consumers do not need to re-resolve the
  source declaration. Each field carries its `kind` (`builtin`, `enum`,
  `table`, `schema`, or `receipt`). When the resolved receipt also
  declares route fields, the slot adds a `routes` map keyed by route name,
  and the route keys also appear in `json_schema` as required string enum
  properties over the authored choice keys.

#### Top-Level Artifact Declarations

An `artifact` declaration names one durable graph target. It is a symbol that
stages can write or read. Doctrine checks ownership and typed use, but it does
not inspect live files.

```prompt
document PacketPathFamily: "Packet Path Family"
    "Section packet paths."

artifact SectionPacket: "Section Packet"
    owner: ProducePacket
    path_family: PacketPathFamily
    section: "Template"
    anchor: "Section Packet"
    intent: "Carry checked section facts."
```

Rules:

- `owner:` is required and must resolve to a top-level `stage`.
- `path_family:` is optional. When present, it must resolve to a supported
  top-level type such as `document`, `schema`, `table`, `enum`, `receipt`,
  `input`, `output`, or `output target`.
- An artifact must declare at least one location hint: `path:`, `section:`, or
  `anchor:`.
- Only the owner stage may list that artifact under `artifacts:`.
- Later stages may read the artifact by listing it in `inputs:`.
- Reached artifact anchors must be unique inside one graph. Duplicate anchors
  fail with `E562`.

#### Top-Level Stage Declarations

A `stage` declaration names one graph node and binds an owner skill to
typed inputs, optional durable artifacts, an optional emitted receipt, an
advance condition, and a durable checkpoint rule. Stages compose with
`skill_flow` and `skill_graph` declarations in the shipped graph surface.

```prompt
enum StageLane: "Stage Lane"
    pipeline: "Pipeline Stage"
    primitive: "Primitive"

skill StudioLessonPlan: "Studio Lesson Plan"
    purpose: "Plan one lesson."
    package: "studio-lesson-plan"

skill CatalogOps: "Catalog Ops"
    purpose: "Write exact catalog facts."
    package: "catalog-ops"

receipt FlowReceipt: "Flow Receipt"
    current_stage: string

receipt LessonPlanReceipt: "Lesson Plan Receipt"
    plan_status: string

artifact LessonPlanPacket: "Lesson Plan Packet"
    owner: LessonPlan
    section: "Brief"
    intent: "Carry the checked lesson plan packet."

skill_flow F1AuthorLesson: "F1 - Author One Lesson"
    intent: "Author one lesson end-to-end."

stage LessonPlan: "Lesson Plan"
    id: "lesson_plan"
    owner: StudioLessonPlan
    lane: StageLane.pipeline
    supports:
        CatalogOps
    applies_to:
        F1AuthorLesson
    inputs:
        flow_receipt: FlowReceipt
    artifacts:
        LessonPlanPacket
    emits: LessonPlanReceipt
    intent: "Turn the section strategy into a lesson plan."
    entry: "Start after the graph inputs are current."
    durable_target: "Lesson plan brief."
    durable_evidence: "Plan write receipt."
    advance_condition: "Author approval plus write receipt."
    risk_guarded: "Reps chosen before pool exists."
    repair_routes: "Route stale input back to preparation."
    waiver_policy: "Only a human owner can waive stale input."
    forbidden_outputs:
        "rep selection"
        "correct action columns"
```

Rules:

- `owner:` is required and must resolve to a top-level `skill`. Unresolved
  refs fail with `E546`.
- `intent:` and `advance_condition:` are required. Missing required fields
  fail with `E559`.
- `id:` is optional; it gives the public stage id used in rendered docs.
- `lane:` is optional. When present it must resolve to an enum member
  (`EnumName.member`); unknown enums or members fail with `E559`.
- `supports:` lists top-level skill refs. Each ref must resolve
  (`E547`). Duplicates and entries that repeat the owner fail with
  `E559`.
- `applies_to:` is optional. Each ref must resolve to a top-level
  `skill_flow`. Duplicate resolved flows fail with `E559`. On the graph path,
  a reached stage that declares `applies_to:` must list every reaching flow, or
  graph compile fails with `E562`.
- `inputs:` map keys must be unique (`E559`). Each value must resolve to
  a top-level `receipt`, `artifact`, `document`, `schema`, or `table` (`E548`).
- `artifacts:` is optional. Each value must resolve to a top-level `artifact`
  declaration owned by this stage. Other stages read artifacts through
  `inputs:`.
- `emits:` must resolve to a top-level `receipt` (`E549`).
- `entry:`, `repair_routes:`, and `waiver_policy:` are optional text fields
  used by graph contracts and stage-contract views.
- `forbidden_outputs:` is an optional list of strings.
- `checkpoint:` is optional. The closed value set is `durable`,
  `review_only`, `diagnostic`, and `none`; the default is `durable`.
  Other values fail with `E559`.
- A stage with `checkpoint: durable` must declare `durable_target:` and
  `durable_evidence:` (`E559`).

#### Top-Level `skill_flow` Declarations

A `skill_flow` is a typed DAG of stages and nested flows. The body owns
`intent:`, `start:`, `approve:`, `edge` blocks, `repeat` blocks,
`variation`, `unsafe`, and `changed_workflow:`. Graph closure across
flows, graph policies, and graph emit are now owned by top-level
`skill_graph`.

```prompt
enum ExactMoveProofNeeded: "Exact Move Proof Needed"
    yes: "Yes"
    no: "No"

skill_flow F18PublishHandoff: "F18 - Publish Handoff"
    intent: "Publish the lesson when authoring is done."
    start: Publish

skill_flow F1AuthorLesson: "F1 - Author One Lesson"
    intent: "Turn one stable lesson slot into a complete review-ready lesson."
    start: LessonPlan
    edge LessonPlan -> AuthorRender:
        route: LessonPlanReceipt.next_route.approve
        kind: review
        why: "The author reviews the plan before downstream work depends on it."
    edge AuthorRender -> SituationSynthesis:
        why: "Concrete situations must be built from approved plan truth."
    edge SituationSynthesis -> ExactMoveProof:
        when: ExactMoveProofNeeded.yes
        why: "Exact action claims need solver proof before build."
    edge SituationSynthesis -> PlayableMaterialization:
        when: ExactMoveProofNeeded.no
        why: "No exact-action proof is needed for this lesson contract."
    edge ExactMoveProof -> PlayableMaterialization:
        why: "The proof must land before the manifest relies on it."
    variation skip_exact_move_proof: "Skip exact-move proof for family recognition lessons."
        safe_when: ExactMoveProofNeeded.no
    unsafe concrete_hands_in_plan: "Pick concrete hands during planning."
    changed_workflow:
        allow provisional_flow
        require nearest_flow
        require difference
        require safety_rationale
    approve: F18PublishHandoff
```

Rules:

- `intent:` is optional. When present it captures one short statement of
  flow purpose.
- `start:` is optional. When present it must resolve to a top-level
  `stage`, top-level `skill_flow`, or a local `repeat` name. Unresolved
  refs fail with `E561`.
- `approve:` is optional and must resolve to a top-level `skill_flow`
  declaration. Unresolved refs fail with `E561`.
- Each `edge Source -> Target:` block requires a `why:` reason and resolves
  the source and target against top-level `stage`, top-level `skill_flow`,
  or local repeat names. Direct self-edges (same source and target) and
  edges that close a local cycle fail with `E561`.
- Edge `kind:` is optional. The closed v1 set is `normal`, `review`,
  `repair`, `recovery`, `approval`, and `handoff`. The default is
  `normal`. Other values fail with `E561`.
- Edge `route:` accepts the form `<ReceiptRef>.<route_field>.<choice>`.
  The receipt must resolve to a top-level `receipt`, the route field must
  exist on that receipt, the choice must exist on that route field, and
  the choice target must match the edge target. Otherwise `E561`.
- Strict default: if a source stage emits a routed receipt and a route
  choice on that receipt targets the edge target, the edge must bind that
  exact route choice with `route:`. A missing required binding fails with
  `E561` on ordinary flow compile. On the graph compile path, `allow
  unbound_edges` may relax this case; if `warn edge_route_binding_missing` is
  also present, Doctrine emits `W209`.
- Edge `when:` accepts declared enum members in the form
  `EnumName.member`. Unresolved enums or members fail with `E561`.
- Branch coverage: if any outgoing edge from one source uses `when:`,
  every outgoing edge from that source must use `when:` on the same enum
  family and must cover each member exactly once. Mixed enum families,
  duplicate member branches, or missing members all fail with `E561`.
  On the graph compile path, `warn branch_coverage_incomplete` may let missing
  enum members compile as `W205` when `require branch_coverage` is not also
  present. Mixed enum families and duplicate member branches still fail.
- `repeat <Name>: <FlowRef>` requires `over:`, `order:`, and `why:`. The
  target flow ref must resolve to a top-level `skill_flow`. The `over:`
  ref must resolve to a top-level `enum`, `table`, or `schema` on ordinary
  flow compile. On the graph compile path it may also resolve to a graph
  `sets:` name or a dotted graph input or field path. The `order:` value is one
  of the closed set `serial`, `parallel`, or `unspecified`. The repeat name is
  local to one flow. It may not shadow a top-level `stage`, top-level
  `skill_flow`, or another repeat in the same flow. Local repeat names take
  precedence over top-level stage and flow refs when resolving edge endpoints.
  Missing or duplicate parser-owned body lines such as `over:`, `order:`, or
  `why:` still fail during parse with `E199`. Repeat resolution and shadowing
  failures use `E561`.
- `variation <name>: "<Title>"` is optional. The optional `safe_when:`
  body line uses the same `EnumName.member` form as `when:` and reports
  unresolved enums or members with `E561`. Duplicate variation names
  fail with `E561`.
- `unsafe <name>: "<Title>"` lists unsafe variations as compiler-owned
  facts. Duplicate names fail with `E561`.
- `changed_workflow:` is optional. The closed body keys are
  `allow provisional_flow` and `require <name>`, where `<name>` is one of
  `nearest_flow`, `difference`, or `safety_rationale`. Unknown keys fail
  with `E561`.
- Parser-level `skill_flow` syntax or block-shape failures still use
  fallback parse `E199`. That includes missing required body lines,
  duplicate parser-owned body keys, and malformed dotted `route:` or
  enum-member refs. Compile-time flow validation uses `E561`. Receipt
  route target resolution still uses `E560` so that diagnostic surface
  stays stable.

#### Top-Level `skill_graph` Declarations

A `skill_graph` closes one authored graph over root stages and flows. The
graph owns graph-local sets, recovery refs, policy facts, and emitted graph
views.

```prompt
enum StageStatus: "Stage Status"
    ready: "Ready"
    blocked: "Blocked"

enum DurableArtifactStatus: "Durable Artifact Status"
    current: "Current"
    stale: "Stale"

skill_graph AuthoringGraph: "Authoring Graph"
    purpose: "Close the authoring graph over roots sets and recovery refs."
    roots:
        flow F2AuthorSection
    sets:
        LessonSlots: "The slots in the section plan."
    recovery:
        flow_receipt: FlowReceipt
        stage_status: StageStatus
        durable_artifact_status: DurableArtifactStatus
    policy:
        dag acyclic
        require edge_reason
        require relation_reason
        require durable_checkpoint
        require route_targets_resolve
        require checked_skill_mentions
        allow unbound_edges
        warn edge_route_binding_missing
        warn receipt_without_consumer
    views:
        graph_markdown: "references/controller-graph.md"
        artifact_inventory: "references/artifact-inventory.md"
        receipt_schema_dir: "references/receipt-schemas"
        diagram_mermaid: "references/controller-graph.mmd"
```

Rules:

- `purpose:` is required. Missing `purpose:` fails with `E562`.
- `roots:` is required. Each root line is either `flow <Ref>` or
  `stage <Ref>`. Missing or wrong roots fail with `E562`.
- `sets:` is optional. It declares graph-local names for repeat late
  binding. A graph compile may late-bind `repeat over:` to a graph set
  or dotted graph input or field path only on the graph path. Agent and
  skill-package compile still keep the strict `enum` / `table` / `schema`
  flow check.
- `recovery:` is optional. `flow_receipt:` must resolve to a top-level
  `receipt`. `stage_status:` and `durable_artifact_status:` must resolve to
  top-level `enum` declarations. Wrong-kind or missing refs fail with
  `E562`.
- `policy:` is optional. The shipped DAG keys are `dag acyclic` and
  `dag allow_cycle "Reason"`. The shipped allow key is
  `allow unbound_edges`. The shipped strict keys are `require edge_reason`,
  `require durable_checkpoint`, `require route_targets_resolve`,
  `require branch_coverage`, `require stage_lane`,
  `require relation_reason`, and `require checked_skill_mentions`.
  Unsupported keys fail with `E562`.
- `views:` is optional. The shipped keys are `graph_contract`,
  `graph_source`, `graph_json`, `graph_markdown`, `skill_inventory`,
  `artifact_inventory`, `flow_registry`, `stage_contracts`,
  `recovery_audit`, `stepwise_manifest`, `receipt_schema_dir`,
  `diagram_d2`, `diagram_svg`, and `diagram_mermaid`. Invalid keys or
  output paths that escape the target output dir fail with `E564`.
- Graph compile closes roots over nested flows, repeat targets, reached
  stages, owner and support skills, skill relations, checked skill mentions,
  receipts, durable artifacts, route bindings, package ids, and recovery refs.
- A reached stage that declares `applies_to:` must list every reaching
  flow. Otherwise graph compile fails with `E562`.
- The graph compile path checks the expanded stage DAG. A cross-flow stage
  cycle fails with `E562` unless the graph declares
  `dag allow_cycle "Reason"`.
- `emit_skill_graph` writes `SKILL_GRAPH.contract.json`,
  `SKILL_GRAPH.source.json`, `references/skill-graph.json`, the requested
  Markdown views, diagrams, and receipt schema files under
  `receipt_schema_dir`.
- `verify_skill_graph` checks the graph outputs, graph source receipt, emitted
  receipt schemas, and linked package receipts when those package receipts are
  present.

Graph warning policy keys are live. They only emit warnings when the graph
opts in with the matching `warn <key>` policy line.

| Code | Policy key | Meaning |
| --- | --- | --- |
| `W201` | `orphan_stage` | A visible stage is not reached from this graph's roots. |
| `W202` | `orphan_skill` | A visible skill is not reached from a stage, relation, or checked skill mention. |
| `W203` | `stage_owner_shared` | One skill owns more than one reached stage. |
| `W204` | `checked_skill_mention_unknown` | A checked skill mention does not resolve, and strict checked mentions are off. |
| `W205` | `branch_coverage_incomplete` | A graph allowed an enum branch source that does not cover every enum member. |
| `W206` | `receipt_without_consumer` | A reached receipt is not read by a reached stage input or recovery ref. |
| `W207` | `flow_without_approve` | A reached flow has no `approve:` flow. |
| `W208` | `stage_without_risk_guard` | A reached stage has no `risk_guarded:` field. |
| `W209` | `edge_route_binding_missing` | `allow unbound_edges` let a routed edge compile without `route:`. |
| `W210` | `relation_without_reason` | A skill relation has no `why:` and `require relation_reason` is off. |
| `W211` | `manual_only_default_flow_conflict` | A reached skill is marked both manual-only and a default flow member. |

#### Checked Skill Mentions

Checked skill mentions let graph-owned prose name skills without stale
hand-written package names.

```prompt
"Use {{skill:CatalogOps}} for exact catalog writes."
"The owner package is {{skill:StudioLessonPlan.package}}."
"The purpose is {{skill:StudioLessonPlan.purpose}}."
```

Rules:

- `{{skill:Name}}` must resolve to a top-level `skill`.
- The default projection renders the skill title.
- `{{skill:Name.package}}` renders the package id.
- `{{skill:Name.purpose}}` renders the purpose text.
- Checked mentions are resolved in graph-owned text such as graph purpose,
  stage text, flow text, edge reasons, repeat reasons, and relation reasons.
- Unknown skill mentions fail with `E562` when the graph declares
  `require checked_skill_mentions`.
- Unknown skill mentions emit `W204` when the graph declares
  `warn checked_skill_mention_unknown` and the strict policy is off.

The manifest-backed graph examples prove the shipped graph ladder through
`164_skill_graph_artifacts`. Examples `160` through `164` cover
`GRAPH.prompt`, skill relations, checked mentions, warning policies, receipt
schema views, graph policy relaxers, authoring metadata, and durable artifacts.

#### Receipt Route Fields

Top-level receipts may declare route fields that name typed handoff
choices. Each choice points at one of `stage <Name>`, `flow <Name>`, or
the closed sentinel set `human`, `external`, or `terminal`.

```prompt
receipt LessonPlanReceipt: "Lesson Plan Receipt"
    plan_status: string
    route next_route: "Next Route"
        approve: "Show review." -> stage AuthorRender
        revise: "Re-plan." -> stage LessonPlan
        flow: "Jump to flow." -> flow F1AuthorLesson
        human: "Hand to human." -> human
        external: "External system." -> external
        done: "Done." -> terminal
```

Rules:

- `stage StageRef` must resolve to a top-level `stage` (`E560`).
- `flow SkillFlowRef` must resolve to a top-level `skill_flow` (`E560`).
- The sentinel set is closed to `human`, `external`, and `terminal`. The
  parser rejects any other bare keyword.
- Route field keys must be unique within one receipt; duplicate route
  fields or duplicate choice keys fail with `E544`.
- When a skill package's `host_contract:` slot points at a receipt with
  routes, `SKILL.contract.json` adds a deterministic `routes` map under
  the slot. Each entry carries `title`, then `choices` keyed by choice
  name. Each choice entry carries `title`, `target_kind` (one of `stage`,
  `flow`, or `sentinel`), and `target` (the canonical declaration name or
  the sentinel keyword). The same slot also adds `json_schema`, where each
  route key lowers to a required string enum property over the authored
  choice keys.

#### Skill Binding Mode

A skill entry may tag itself with a `mode` statement. This is the canonical
`mode CNAME = expr as name_ref` production shared with review cases, law
matchers, and output-shape selectors. The mode keeps producer and audit uses
of the same skill compile-time distinguishable.

```prompt
enum SkillMode: "Skill Mode"
    producer: "Producer"
    audit: "Audit"


skill SharedSkill: "Shared Skill"
    purpose: "Run the shared producer/audit package."
    package: "shared-skill-package"


agent ProducerAgent:
    role: "Run the shared skill in producer mode."
    skills: "Skills"
        skill shared: SharedSkill
            mode producer = SkillMode.producer as SkillMode


agent AuditorAgent:
    role: "Run the shared skill in audit mode."
    skills: "Skills"
        skill shared: SharedSkill
            mode audit = SkillMode.audit as SkillMode
```

Rules:

- The `CNAME` after `mode` must be one of the declared enum's members.
  Unknown names fail with `E542`.
- The `name_ref` after `as` must resolve to a declared enum. Unresolved
  targets fail with `E540`.
- A skill entry tagged with `mode audit = ...` must not `bind:` to an
  `output` or `final_output` host slot. Audit-mode bindings stay read-only
  and fail with `E541` if they try to emit.

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
- When a previous-turn input source resolves one concrete upstream output,
  `emit_docs` records that derived contract under
  `final_output.contract.json.io.previous_turn_inputs`.
- `structure:` may attach a named `document` to a markdown-bearing input.
- Ordinary record bodies may also reuse readable block kinds such as
  `definitions`, `table`, `callout`, and `code`.
- `inputs` blocks group and bind inputs with local keys for a concrete turn.

### Omitted Wrapper Titles

`inputs` and `outputs` wrapper sections have three separate title rules:

- `key: "Title"` is the normal long form when you need a local title or local
  prose.
- In base `inputs` or `outputs`, `key: SharedDecl` is the short form for one
  direct declaration ref. Doctrine lowers it through the same omitted-title
  wrapper rule, so the child declaration still owns the visible heading.
- In inherited `inputs` or `outputs`, `override key: SharedDecl` is the short
  form when the child only swaps one direct declaration and keeps the parent
  title.
- In inherited `inputs` or `outputs`, `inherit {left_key, right_key}` keeps
  several wrapper sections with the same explicit accounting model.
- The multiline title-omitted form still works too. Use it when you need one
  direct declaration plus local prose around it.
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
    issue_ledger: LessonsIssueLedger

outputs SectionDossierOutputs: "Your Outputs"
    section_handoff: SectionHandoff
```

The omitted wrappers render one visible heading each: `Lessons Issue Ledger`
and `Section Handoff`. The direct declaration bodies render under those
headings without a second nested heading. If you need local prose before or
after the declaration, keep the multiline wrapper form.

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
- A custom `output target` may bind one reusable delivery skill with
  `delivery_skill:`. Put delivery behavior on the target, not on each output.
- A custom `output target` may also declare `typed_as:` pointing at a
  `document`, `schema`, or `table`. That makes the target carry the handoff
  note's family identity. `typed_as:` referencing any other entity kind fails
  loud with `E533`. If a downstream `output` that uses the target also sets
  `structure:` or `schema:`, the family must match the target's `typed_as:`
  family or the compiler raises `E534`. See
  `examples/143_typed_handoff_note_identity/` for the canonical form.
- Output shapes can be named with `output shape`.
- An `output shape` may declare a `selector:` block. Each selector statement
  uses the canonical expr-based `mode CNAME = expr as EnumType` production,
  the same one shared with review cases, law matchers, and skill-binding
  modes. `expr` is usually the selector field access, e.g.
  `mode role = selectors.role as WriterRole`. The enum-only shorthand
  `mode CNAME as EnumType` is soft-deprecated and fails with `E543`; it
  will be removed at the next minor bump. Each `as` target must resolve to
  a closed enum.
- Inside a shape with a `selector:`, body items may use `case EnumType.member:`
  blocks for per-case content. Cases must cover every enum member exactly once
  and must not overlap. `case` outside a shape body, or without a `selector:`,
  is fail-loud (`E318`).
- An agent that points `final_output` at a shape with a `selector:` must bind
  every selector key under a `selectors:` block. Duplicates, unknown keys, and
  bindings to a same-named enum from a different flow are fail-loud (`E319`).
- `schema:` on `output` attaches a Doctrine `schema` declaration.
- `schema:` on `output shape` remains the owner-aware attachment point for
  `output schema` when the shape kind is `JsonObject`.
- `output schema` owns the machine-readable payload fields for structured
  `JsonObject` outputs.
- `output schema` may also declare an optional `example:` block. When present,
  Doctrine validates it and renders an `Example` section on structured final
  outputs.
- On the current structured-output profile, object properties stay present on
  the wire. That includes normal fields, route fields, and route-field
  overrides.
- Use `nullable` when an `output schema` field or route field may be `null`.
- `required` and `optional` are retired on this surface. Doctrine still
  parses them there only so it can raise targeted upgrade errors.
- Doctrine does not ship `?` shorthand for `output schema` fields.
- For a closed vocabulary on any field-shaped surface — output-schema
  fields, `row_schema` / `item_schema` entries, table columns, and record
  scalars — declare `enum X: "..."` once and type the field with `type: X`.
  The renderer emits a `Valid values: <k1>, <k2>, ...` line in declared
  order under the typed field; the JSON-schema lowering path emits the
  same members as `enum`. Typing against an unknown name fails loud with
  `E320`. See `examples/139_enum_typed_field_bodies/` for the canonical
  form on a `row_schema` entry.
- A structured final output may declare a first-class routed owner with
  `route field`.
- A `route field` owns the route choice keys, labels, and named target agents
  in one place.
- `route field` still lowers to an ordinary string enum on the wire.
- Use `nullable` on a `route field` when `null` means "no handoff on this
  turn." Use the same `nullable` flag on ordinary schema fields.
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
- `final_output.route:` may bind one `route field` on that structured final
  output. That gives the turn one authored route owner without a second
  `route_from` table.
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
- `review_fields:` also accepts bare identity binds like `next_owner` when the
  final-output field key matches the review semantic name.
- The emitted `final_output.contract.json` companion also carries the
  top-level `route` block for ordinary finals, `route_only`,
  `handoff_routing`, `route_from`, routed reviews, and bound final-output
  route fields.
- When a route comes from `final_output.route:`, the emitted route contract
  also carries `route.selector` with the bound field path and null behavior.
- The same companion file also carries a top-level `io` block.
  `io.previous_turn_inputs` records resolved previous-turn input contracts.
  `io.outputs` and `io.output_bindings` record emitted output contracts and
  readback binding paths.
- The designated final output renders under a dedicated `Final Output`
  section and is omitted from ordinary `Outputs` rendering for that agent.

Canonical form for a closed field vocabulary:

```prompt
enum Status: "Status"
    ok: "OK"
    action_required: "Action Required"

field status: "Status"
    type: Status
```

The same `type: <EnumName>` form types a `row_schema` or `item_schema`
entry, a readable table column, or a record scalar. Every typed field
renders the same `Valid values: ok, action_required.` line in declared
order. Typing against an unknown name fails loud with `E320`.

Nullable field example:

```prompt
field next_step: "Next Step"
    type: string
    nullable
```

First-class routed final-output form:

```prompt
output schema WriterDecisionSchema: "Writer Decision Schema"
    route field next_route: "Next Route"
        seek_muse: "Send to Muse." -> Muse
        ready_for_critic: "Send to Critic." -> Critic
        nullable

    field summary: "Summary"
        type: string

agent Writer:
    final_output:
        output: WriterDecision
        route: next_route
```

Shipped Markdown render shape:

- This is emitted output shape only. It does not change the input language.
- A simple `TurnResponse` ordinary output with only `Target`, `Shape`, and
  `Requirement` renders as a short bullet contract.
- Richer single-artifact ordinary outputs still start with one grouped
  `Contract | Value` table.
- A `files:` output renders that same contract table, then an `Artifacts`
  table for the named files.
- `current_truth`, titled `properties`, parseable `notes`, and
  `support_files` render as tables when their authored shape is tabular.
- `trust_surface` keeps its own section, and ordinary output labels render as
  inline code.
- If `structure:` only needs titled section summaries, Doctrine renders a
  compact `Required Structure:` list.
- `structure:` still renders one `Artifact Structure` section with a summary
  table and any needed detail blocks when the shape is richer.
- Compiler-owned `* Binding` wrappers may collapse when they only repeat one
  direct child section and add no keyed content of their own.
- If the target declares `delivery_skill:`, the contract table renders one
  `Delivered Via` row after `Target` and before target config rows.

Example emitted shape:

```md
### Review Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required
```

Target-owned delivery example:

```prompt
skill LedgerNoteDelivery: "ledger-note-delivery"
    purpose: "Append markdown notes to the shared ledger."

output target LedgerNoteAppend: "Ledger Note Append"
    delivery_skill: LedgerNoteDelivery
    required: "Required"
        ledger_id: "Ledger ID"

output LedgerNote: "Ledger Note"
    target: LedgerNoteAppend
        ledger_id: "current-ledger"
    shape: MarkdownDocument
    requirement: Advisory
```

The emitted output contract starts like this:

```md
| Contract | Value |
| --- | --- |
| Target | Ledger Note Append |
| Delivered Via | `ledger-note-delivery` |
| Ledger ID | `current-ledger` |
| Shape | Markdown Document |
| Requirement | Advisory |
```

Typed handoff-note target example:

```prompt
document ReleaseNoteDocument: "Release Note"
    section summary: "Summary"
        "Say what shipped."

output target ReleaseNoteHandoff: "Release Note Handoff"
    typed_as: ReleaseNoteDocument

output ReleaseNote: "Release Note"
    target: ReleaseNoteHandoff
    shape: MarkdownDocument
    requirement: Advisory
    structure: ReleaseNoteDocument
```

The emitted contract carries a `Typed As` row so downstream readers see the
bound family directly:

```md
| Contract | Value |
| --- | --- |
| Target | Release Note Handoff |
| Typed As | Release Note |
| Shape | Markdown Document |
| Requirement | Advisory |
| Structure | Release Note |
```

### Output Inheritance

Inherited outputs use the same explicit patching style Doctrine already uses
elsewhere:

- `output Child[Parent]: "Title"` inherits from another `output`
- `inherit key` keeps one inherited top-level output entry
- `inherit {target, shape, requirement}` keeps several inherited top-level
  output entries with the same explicit accounting model
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

Imports compose typed declarations across real flow boundaries.

```prompt
import shared.contracts as shared_contracts
from shared.review import DraftReviewComment
from shared.review import DraftReviewComment as ImportedComment
```

Important rules:

- `AGENTS.prompt`, `SOUL.prompt`, and `SKILL.prompt` are the flow entrypoints.
- One flow entrypoint plus its sibling `.prompt` files owns one flat
  namespace.
- Same-flow imports are retired. Sibling files already share that namespace
  and fail loud with `E315` if they try to import each other.
- A cross-flow import may resolve to either `<module>.prompt` or
  `<module>/AGENTS.prompt`.
- If both shapes exist for the same dotted path, Doctrine fails loudly
  instead of guessing which one owns the module.
- Absolute imports search the active roots for the compile. Active roots
  include the entrypoint-local root, configured shared authored roots from
  `[tool.doctrine.compile].additional_prompt_roots`, and provider roots passed
  by an embedding runtime.
- Each `additional_prompt_roots` entry resolves relative to that
  `pyproject.toml` and must point at an existing directory literally named
  `prompts`.
- Each provider root must also point at an existing directory literally named
  `prompts`. Provider roots come from the Python API, not from host TOML.
- Cross-flow imports only see declarations marked `export`. Non-exported
  declarations stay private to their home flow and fail loud with `E314`.
- The `export` keyword is a leading modifier on a declaration line, for
  example `export workflow Foo: "Foo"` or `export agent Bar:`. A declaration
  without `export` is private to its home flow regardless of its visibility
  name.
- Sibling `.prompt` files inside one flow share one namespace and reach each
  other by bare name. Using `from <same-flow> import Name` is fail-loud
  (`E315`). Two sibling declarations with the same name collide fail-loud
  (`E316`).
- A file-backed `<module>.prompt` import is a compile-time boundary with one
  prompt file as its full flow surface.
- A directory-backed `<module>/AGENTS.prompt` import is a runtime package
  root for `emit_docs` and the shared runtime frontier that `emit_flow`
  uses.
- A sibling `SOUL.prompt` beside a runtime package `AGENTS.prompt` is optional
  runtime emit input. It is not a second import target.
- `SKILL.prompt` uses the same boundary rules. Same-flow package files use
  bare refs. Cross-flow package imports stay absolute.
- `import module as alias` keeps the imported module explicit through normal
  declaration refs such as `shared_contracts.ReviewContract`.
- `from module import Name` binds the imported declaration on its bare visible
  name everywhere Doctrine already accepts that declaration kind.
- `from module import Name as Alias` binds the imported declaration on the
  renamed visible name.
- Bare imported symbols follow the same name-resolution path as local refs.
  That means workflows, review outputs, route targets, output attachments,
  inheritance parents, addressable roots, and law paths all read the same
  import scope.
- `from ... import ...` does not create a visible module path. Keep a normal
  `import module` line when you also want `module.Name`.
- Duplicate visible module names, duplicate imported symbol names, and
  local-versus-imported bare-name conflicts all fail loudly instead of picking
  one owner by precedence.
- Duplicate dotted modules across active roots fail loudly instead of using
  root precedence heuristics.
- Missing modules, missing declarations, missing exports, sibling declaration
  collisions, and true cross-flow cycles still fail loudly.

## Readable Refs, Addressable Paths, And Interpolation

Doctrine has two related reference surfaces.

### Readable refs

Inside workflow sections and record bodies, a declaration ref renders as a
readable mention of that declaration rather than expanding the whole contract.

Examples:

- `DraftSpec`
- `ReviewComment`
- `MetadataContract:files.summary`
- `self:detail_panel.rewrite_detail`
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
- `self:path.to.child`
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

Inside a declaration-root addressable context, `self:path` is short for the
current declaration root. Doctrine ships that on named workflow, analysis,
schema, document, skills, input, and output bodies. If the current surface
does not carry that root, `self:` fails loud with `E312`. Use an explicit
`Root:path` ref there.

### Authored interpolation

Authored prose surfaces may interpolate declaration data inline:

- `{{Ref}}`
- `{{Ref:path.to.child}}`
- `{{self:path.to.child}}`
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

### Typed Field Bodies

When a field's value comes from a small fixed vocabulary, declare the enum
once and type the field with that name. The language ships exactly one
canonical form:

```prompt
enum StepRole: "Step Role"
    introduce: "Introduce"
    practice: "Practice"
    test: "Test"
    capstone: "Capstone"
```

Every field-shaped surface then carries `type: <EnumName>` in the field
body:

```prompt
# output-schema field
output schema ReviewSchema: "Review Schema"
    field status: "Status"
        type: StepRole

# row_schema entry on a readable table
table step_arc: "Step Arc" required
    row_schema:
        step_role: "Step Role"
            type: StepRole
            "Name the step's role in the arc."

# item_schema entry on a readable list
sequence read_order: "Read Order"
    item_schema:
        step_role: "Step Role"
            type: StepRole

# readable table column
columns:
    step_role: "Step Role"
        type: StepRole
        "Coach guidance level for the step."

# record scalar on a structured comment output
output StepNote: "Step Note"
    target: TurnResponse
    shape: Comment
    message as step_role: "Step Role"
        type: StepRole
```

The renderer emits the same `Valid values: introduce, practice, test, capstone.`
line in declared order under each typed field. The JSON-schema lowering
path emits the same member keys as `enum`. Typing against an unknown
name fails loud with `E320`.

Glossary and label nodes (`properties` and `definitions` items) stay
prose-only by design.

See `examples/139_enum_typed_field_bodies/` for the canonical form on a
`row_schema` entry, backed by `render_contract` and `compile_fail` cases.

The shipped expression surface supports:

- dotted refs
- string, number, and boolean literals
- set literals
- helper-style calls used by the corpus, such as `present(...)` and
  `unclear(...)`
- boolean operators and comparison operators

Those expressions are used in `when`, `match`, guarded output items,
workflow law, and review semantics.

## Project Rules

Doctrine ships a declarative `rule` primitive that a project uses to lint its
own agent graph. A `rule` lives at the top of a prompt file and runs during
compile. If the rule matches a concrete agent and the agent violates an
assertion, the compiler raises a `RULE###` diagnostic (see
[`COMPILER_ERRORS.md`](./COMPILER_ERRORS.md)).

The shape is:

```doctrine
rule <RuleName>: "Human-readable rule headline"
    scope:
        <scope predicate>
    assertions:
        <assertion predicate>
    message: "Plain-English explanation shown when the rule fires."
```

The shipped predicate set is closed. Scope predicates select which concrete
agents the rule evaluates against:

- `agent_tag: <CNAME>` — the agent whose name equals `<CNAME>` exactly
- `flow: <NameRef>` — every agent whose ancestor chain transitively includes
  the named flow or ancestor
- `role_class: <CNAME>` — every agent whose name ends with the `<CNAME>`
  suffix
- `file_tree: <STRING>` — every agent whose prompt file path matches the
  glob (evaluated with `fnmatch.fnmatch`) relative to the prompt root

Multiple scope predicates combine with OR semantics: an agent matches the
rule when at least one predicate matches.

Assertions say what scoped agents must or must not do:

- `requires inherit <NameRef>` — the scoped agent must transitively inherit
  from `<NameRef>`. If the target agent is not declared, the compiler raises
  `RULE002`. If a scoped agent fails the check, it raises `RULE003`.
- `forbids bind <NameRef>` — the scoped agent must not transitively inherit
  from `<NameRef>`. Unknown target raises `RULE002`. Violations raise
  `RULE004`.
- `requires declare <CNAME>` — the scoped agent (or one of its declared
  ancestors) must declare a slot named `<CNAME>`. Violations raise `RULE005`.

The `flow: <NameRef>` scope predicate also requires its target to resolve. If
it does not, the compiler raises `RULE001`.

The `message:` body is surfaced back to the author when the rule fires. Use it
to explain the invariant in plain English so a downstream author can read the
diagnostic alone and know what to fix.

See [`../examples/146_declarative_project_lint_rule`](../examples/146_declarative_project_lint_rule)
for the manifest-backed teaching example that covers all five shipped
`RULE###` codes.

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
