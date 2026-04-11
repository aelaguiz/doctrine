# Language Design Notes

This repo exists to turn agent doctrine into structured source code instead of
hand-maintained runtime Markdown.

This document is intentionally short and easy to rewrite. Its job is to record
the language decisions we have made so far, why we made them, and how we
currently expect the parser to behave.

The shipped surface now runs through the workflow-law family in
`examples/30_*` through `examples/42_*` and the first-class review ladder in
`examples/43_*` through `examples/49_*`, plus the shared-root stdlib and
public-pack proof lane in `examples/50_*` through `examples/52_*`, not only
through `29_enums`.

## Design Approach

- We are designing the language example-first.
- Each example should prove one new idea at a time.
- We do not want speculative features in the language unless an example clearly needs them.
- The parser should grow in the same order as the examples.
- We intentionally pruned the speculative examples after inheritance so we can re-earn the next concepts instead of carrying forward placeholders we do not fully believe in.

## Core Declarations So Far

- `agent` is a language primitive.
- `abstract agent` is the current way to declare an inheritance-only agent that should not render directly.
- `workflow` is also behaving like a language primitive.
- Core declarations should not need imports.
- `import` is for user-defined or shared definitions, not built-in language words.

This means the language should feel more like Python `class` than like importing a framework symbol before every declaration.

## Agent Shape

An `agent` currently looks like a small structured declaration with named fields.

The important fields we have actually used so far are:
- `role`
- `workflow`

Current intent:
- `agent` is the top-level authored thing in the language
- one source package may define one agent or many agents
- `role` is not hidden metadata. It is output-facing text.
- `role` currently opens the rendered document directly.
- The rendered output should read naturally, not look like a debug dump of the source tree.
- compiled agent-doc emission is now a separate build concern configured outside
  the prompt language rather than part of `output`
- explicit package-local build targets in `pyproject.toml` emit concrete root agents to canonical
  `module/agent/AGENTS.md` paths
- the first shipped bootstrap supports both current `role` shapes from `01_hello_world`:
  - scalar `role: "..."` as opening prose
  - titled `role: "Title"` with indented lines as a rendered section
- the first shipped bootstrap subset accepts exactly one `role` followed by exactly one `workflow` per agent

## Workflow Shape

`workflow` is currently our main semantic unit for instructions.

Current intent:
- A simple local workflow can live directly inside an agent.
- A workflow can also be declared at the top level and reused.
- top-level named workflows are the canonical reusable and inheritable form
- A workflow is not just arbitrary text. It is a typed instruction surface.
- A workflow can contain more than one string in a row before named nested entries begin.
- the agent-level workflow block should also carry its rendered title explicitly, for example `workflow: "Instructions"`
- named workflow composition should use keyed `use` entries such as `use greeting: Greeting`

Nested content inside a workflow currently means ordered substructure.

Current intent:
- nested workflow entries should preserve order
- nested workflow entries should render as subsections
- source keys are compiler identities, not visible text
- rendered subsection titles come only from explicit authored strings

Current section-title direction:
- an agent-level workflow block looks like `workflow: "Instructions"`
- a keyed workflow entry looks like `main_point: "Main Point"`
- a reusable top-level workflow can look like `workflow Greeting: "Greeting"`
- the key is the stable compiler identity
- the field or key name is never turned into a rendered heading
- the string is the rendered section title
- new agent-level workflow blocks should provide a title string explicitly
- new keyed workflow entries should provide a title string explicitly
- new top-level reusable workflows that render as sections should provide a title string explicitly
- inherited keyed workflow entries keep their existing title unless the child overrides it
- omission of the title string is only valid when an inherited title is being reused on purpose

Current intent for adjacent workflow strings:
- sibling strings should preserve order
- sibling strings should render as consecutive lines
- the renderer should not automatically insert an extra blank line between those lines unless the source structure explicitly calls for it

Current intent for emphasized prose lines:
- certain prose lines may start with one fixed emphasis label instead of embedding raw markdown
- the shipped labels are `required`, `important`, `warning`, and `note`
- those labels render as `**LABEL**: ...` in final markdown
- this is a prose-line feature, not a general inline-markup mini-language
- it currently works on workflow prose, role prose, and record prose surfaces
- emphasis lines on authored prose surfaces keep the same `{{...}}` interpolation support as ordinary prose lines on those surfaces
- role scalar values, titles, keyed scalar heads, config lines, routes, and refs do not get special emphasis syntax
- if an author needs one-off emphasis inside a scalar string surface, raw markdown is still the escape hatch

Current intent for titled workflow section body refs:
- titled workflow section bodies may mix prose strings, route lines, and named declaration refs
- those declaration refs are readable mentions, not inline expansion of the full typed contract
- declaration refs in titled workflow section bodies render as bullet lines using the declaration title, except concrete `agent` refs which render as the raw agent declaration name
- those refs currently resolve to titled declarations such as `input`, `input source`, `output`, `output target`, `output shape`, `json schema`, and `skill`, plus concrete `agent` declarations
- path-bearing refs such as `Decl:path.to.child` are the explicit widening surface for named nested contract items; bare workflow roots still stay rejected here
- path traversal follows explicitly keyed nested items only; anonymous prose lines are not addressable
- stopping on a structured nested item renders that item's title, while trying to keep walking past a scalar leaf fails loud
- workflow reuse still belongs to keyed `use` entries
- actual owner transitions still belong to `route "..." -> AgentName`
- abstract agent refs are rejected here; if an owner should be mentionable, name the concrete agent

Current intent for authored prose interpolation:
- authored prose surfaces may interpolate named declaration data inline with `{{Ref}}` and `{{Ref:field.path}}`
- the shipped authored prose surfaces are workflow preamble strings, titled workflow section strings, role prose, record prose, skill purpose, skill reference reason, and route labels
- `{{Ref}}` renders the declaration title for titled declarations and the raw declaration name for concrete `agent` refs
- `{{Ref:field.path}}` resolves explicitly keyed nested items through arbitrary depth across shipped record bodies, recursive workflow sections, and enum members
- `{{AgentRef:name}}` is the explicit agent form; broader agent field access is not currently part of this surface
- interpolation is for authored prose, not renderer-generated sentence assembly
- authors still own punctuation, filenames, conjunctions, and backticks around the placeholder
- abstract agent refs are rejected here; if a sentence should name an owner, interpolate the concrete agent
- titles, config labels, config values, keyed scalar metadata, and route targets stay literal

Current intent for enums:
- closed vocabularies may be declared once with top-level `enum`
- enum roots carry a title and flat keyed string members
- `{{EnumRef}}` renders the enum title
- `{{EnumRef:member_key}}` renders the concrete member literal
- duplicate enum member keys fail loud during compilation

## Workflow Law

Workflow law is now a shipped compiler-owned surface.

This document records the language decision, not the full reader-facing
reference. For the canonical shipped workflow-law guide, use
[WORKFLOW_LAW.md](WORKFLOW_LAW.md).

Current decision:
- `law` lives only inside `workflow`
- `trust_surface` lives only inside `output`
- `output` may use keyed guarded sections for conditional readback without
  promoting that readback into `trust_surface`
- guarded output-section expressions read declared inputs and enum members;
  they do not read workflow-local mode bindings, emitted output fields, or
  undeclared runtime names
- every active law leaf branch must resolve exactly one current-subject form:
  either `current artifact ... via ...` or `current none`
- currentness and invalidation move only through emitted output fields listed
  in the relevant output's `trust_surface`
- branch shaping is explicit through `active when`, `when`, `mode`, `match`,
  `must`, `stop`, and `route`
- inline conditional routes such as `route "..." -> Agent when expr` are part
  of the shipped workflow-law surface
- routed `next_owner` fields now use structured interpolation as the explicit
  Slice A agreement surface
- `standalone_read` may not structurally interpolate guarded output detail,
  while still remaining free prose outside those structured refs
- scope, preservation, evidence roles, invalidation, and named law subsection
  reuse are all compiler-owned surfaces now

## Nested Workflow Direction

The `06_nested_workflows` examples forced a clearer boundary between "small local workflow" and "real nested workflow structure."

Current constraints:
- we do not want one workflow inheritance model at depth 1 and a different ad hoc model below it
- if nested workflow structure is real semantic structure, it must follow the same explicit inheritance rules as other workflows
- we do not want deep anonymous workflow trees inside inheriting agents to become a second hidden composition system

Current requirements:
- simple local flat workflows should still be easy to author inline inside an agent
- nested, reusable, or inherited workflow structure should have stable names and stable identities
- agents should stay readable and should not become giant deep patch surfaces just to express shared structure

Current choices:
- inline agent workflows are still allowed for simple local cases
- inline agent workflows are convenience authoring, not a separate semantic model
- nested, reusable, or inherited structure should be promoted to named top-level `workflow` declarations
- agents should compose named workflows through keyed `use` entries when the structure is deeper than a simple local workflow
- workflow inheritance should use the same explicit ordered patching model we already use for inherited agent workflows

## Imports

Imports exist to compose user-defined pieces.

Current intent:
- imported definitions should be typed declarations
- importing a module should bring in real named language objects, not raw text snippets
- the current `03_imports` direction is Python-like module resolution:
  - `import package.module` resolves from the example or package root
  - `import .sibling.module` resolves from the current package
  - `import ..shared.module` walks to the parent package first
  - any number of leading dots is allowed and walks up one package level fewer than the dot count before following the remaining module path
- an imported workflow should be composed through a keyed `use` entry such as `use greeting: simple.greeting.Greeting`
- imported declaration refs also work in inheritance headers such as `agent Child[simple.roles.BaseRole]:`
- imported symbol identity should not depend on case guesswork or fallback lookup
- the first negative `03` contracts should cover missing modules, unresolved qualified symbols, and duplicate declaration names within one imported module

This is why the imported examples are typed as `workflow Greeting: "Greeting"` and composed through explicit keyed `use` entries instead of as untyped text labels.

## Composition

We currently want composition to stay explicit and understandable.

Current intent:
- when one workflow composes another named workflow, the final rendered output should read like one coherent document
- composition should feel like assembling semantic pieces, not pasting arbitrary text
- simple inline workflows and composed named workflows should not behave like two different languages
- composition should use keyed `use local_key: WorkflowName` entries so outer structure has a stable patch identity

We are deliberately avoiding looser reuse features until the examples prove that we need them.

## Inheritance

Inheritance has earned a place conceptually, and the current direction is now clearly "explicit ordered patching" rather than any kind of implicit merge.

Current syntax direction:
- `agent Child[Base]:` means the child extends a local base agent
- `agent Child[shared.roles.Base]:` means the child extends an imported base agent through a normal dotted declaration ref
- `abstract agent Base:` means the base exists for inheritance and should not render by itself
- `workflow Child[Base]: "Title"` means the child extends a local named base workflow and keeps the same explicit patching model
- `workflow Child[shared.flows.Base]: "Title"` means the child extends an imported named base workflow through the same dotted ref model

Current intent:
- inheritance should produce one merged final document
- the child should be able to specialize inherited behavior without rewriting everything
- inherited output should feel natural, not expose internal implementation details unless we want that explicitly
- scalar fields like `role` should override
- workflow preamble strings should override as a group when the child provides them
- shared doctrine should be modeled through inheritance rather than through a separate doctrine primitive
- only concrete leaf agents should render as final outputs

Current workflow inheritance direction:
- inherited workflow order is always explicit
- there is no implicit merge mode for inherited workflow entries
- a child must account for every inherited workflow entry exactly once
- inherited workflow structure should never survive by omission or move by guesswork
- deletion of inherited workflow entries is not supported right now
- the same explicit workflow inheritance rules should apply whether the workflow is attached directly to an agent or declared as a named top-level workflow
- moving to nested workflow structure should not introduce a second inheritance model

Current explicit-order syntax direction:
- `inherit key` means "place the inherited workflow entry here unchanged"
- `override key:` means "replace the inherited workflow entry and place the replacement here"
- `override key: "New Title"` means "replace the inherited workflow entry and also replace its rendered title"
- `key: "Title"` means "create a new workflow entry here"
- `use local_key: WorkflowName` means "compose this named workflow here with `local_key` as the outer patch identity"
- `override local_key: WorkflowName` is also valid for an inherited keyed `use` entry and means "keep the outer key, but retarget that composed piece to a different named workflow here"

Current inheritance pattern:
- use `abstract agent` for any inheritance-only or non-leaf agent
- use plain `agent` for concrete leaf agents
- only concrete leaf agents emit rendered output
- shared doctrine should live in abstract bases and be specialized by concrete children

Why this direction currently looks better than implicit merge:
- it makes placement explicit in the source
- it removes merge guesswork entirely
- it gives the parser cleaner semantics
- it makes compiler errors easier to explain

Current compiler validation direction:
- `override key:` should fail if the parent does not define that key
- `inherit key` should fail if the parent does not define that key
- an inherited workflow should fail if any inherited entry is omitted
- an inherited workflow should fail if any inherited entry is accounted for more than once
- an inherited workflow should fail if the author attempts to remove an inherited entry
- an agent-level workflow block should fail if it omits its explicit title string
- a new rendered section should fail if it omits its explicit title string
- if the intent is to add something new, the author should define a new key directly instead of using `override`

The current examples are intentionally pushing on these rules so we can validate that explicit exhaustive inheritance is actually the right simplification.

## Recently Settled

- `agent` is the top-level authored thing in the language.
- one source package may contain one agent or many agents.
- shared doctrine should be modeled through inheritance.
- non-leaf agents should be marked `abstract`.
- concrete agents are written as plain `agent` declarations.
- only concrete leaf agents should render.
- `04_inheritance` should follow the same inheritance model as `05_workflow_merge`.
- `06_nested_workflows` should show both allowed authoring modes: simple inline local workflows and named workflows for nested or reusable structure.
- The inheritance model we are carrying forward is explicit ordered patching, not implicit key-merge magic.
- Inherited workflows are now explicit-only. There is no second implicit merge mode.
- A child that inherits a workflow must account for every inherited workflow entry exactly once.
- Dropping inherited workflow entries is not supported right now.
- `inherit key` is the clearest syntax we have found so far for "keep this inherited workflow entry and place it here."
- `override key:` is the clearest syntax we have found so far for "replace this inherited workflow entry and place the replacement here."
- `abstract key` is the clearest syntax we have found so far for "this authored slot must be defined by a concrete descendant without placeholder content."
- `key: "Title"` inside an inherited child means "this is a new workflow entry and it belongs exactly here."
- simple local workflows may still live inline inside an agent.
- named top-level workflows are the canonical home for nested, reusable, or inherited workflow structure.
- inline agent workflows are convenience authoring, not a second semantic model.
- workflow inheritance should work the same way for named workflows as it does for inherited agent workflows.
- Rendered section titles are explicit authored data. Keys are never used as visible headings.
- Adjacent workflow strings should stay adjacent in the rendered output. The renderer should not invent an extra blank line between them.
- Invalid overrides should be real compiler errors, not silent fallbacks.
- We now have a canonical numbered compiler error reference in [COMPILER_ERRORS.md](COMPILER_ERRORS.md).
- `09_outputs` now treats `output` as the only produced-contract primitive.
- `output target`, `output shape`, and `json schema` are reusable supporting
  declarations under `output`, not competing output primitives.
- richer output contract material should live directly on `output`; we do not
  currently need a separate top-level `artifact` concept.
- `18_rich_io_buckets` widens `inputs` and `outputs` from bare ref lists to
  authored buckets that may mix prose, titled groups, and typed declaration
  refs.
- those bucket refs stay kind-specific: `inputs` refs must resolve to `input`
  declarations and `outputs` refs must resolve to `output` declarations.
- `11_skills_and_tools` is intentionally skill-first.
- reusable capabilities should be modeled as `skill` declarations.
- `30_law_route_only_turns` through `42_route_only_handoff_capstone` are
  active shipped workflow-law proof, not planned-only examples.
- `43_review_basic_verdict_and_route_coupling` through
  `49_review_capstone` are active shipped review proof, not draft proposal
  examples.
- `50_stdlib_coordination` through `52_public_code_review_pack` are active
  shipped proof that shared-root stdlib and public-pack modules compile,
  render, and emit through the existing corpus harness without widening Layer 1.
- workflow law is now the shipped way to express route-only turns, portable
  currentness, trust carriers, scope/preservation law, basis roles,
  invalidation, and named law reuse.
- `review` and `abstract review` are now shipped declaration families for
  shared review contracts, exact failing gates, carried mode and trigger
  state, blocked review turns, review inheritance, and portable review-owned
  current truth.
- `law` on workflows and `trust_surface` on outputs are reserved typed
  surfaces, not generic prose or generic record fallbacks.
- `12_role_home_composition` has already earned the basic role-home shell by
  composing shared `workflow` sections into named agent fields.
- that means the open question is what belongs inside those composed sections,
  not whether role homes need a new primitive.
- telling an agent to run a raw script or Python file path is currently treated
  as a workaround, not as a supported parallel authoring pattern.
- we are not currently supporting a separate `runtime_tools` language surface.
- `12_role_home_composition` and `13_critic_protocol` should stay aligned with
  that no-`runtime_tools` rule.
- packets are not a current language primitive direction.
- the same authoring pressure should be handled through inputs, outputs,
  authored routing and stop guidance, ownership, and readable file contracts
  instead.
- do not cargo-cult legacy draft output patterns such as redundant `owns` sections when
  the output contract already makes ownership obvious.
- `14_handoff_truth` shows the basic "tell the next owner what to use now"
  pattern without adding a new primitive.
- do not treat that handoff-truth pattern as an open language gap unless we
  later decide we need machine-readable freshness semantics.
- `15_workflow_body_refs` earns a narrow readable-mention path for named typed
  declarations inside titled workflow sections without creating a second
  contract surface.
- `16_workflow_string_interpolation` earns the complementary inline-prose path
  for workflow strings that need one authored sentence instead of a block list.
- `17_agent_mentions` extends those two mention surfaces to concrete agents so
  workflow prose can name owners without pretending that a mention is a route.
- `21_first_class_skills_blocks` promotes `skills` from an agent-only typed
  field into a first-class block that can be declared at the top level and
  embedded inside workflows.
- `22_skills_block_inheritance` gives named `skills` blocks the same explicit
  patching model already used by workflows.
- `23_first_class_io_blocks` promotes `inputs` and `outputs` from agent-only
  typed fields into first-class blocks that can be declared at the top level
  and referenced directly from agents.
- `24_io_block_inheritance` gives named `inputs` and `outputs` blocks the same
  explicit patching model already used by workflows and `skills`.
- `25_abstract_agent_io_override` shows the intended abstract-parent pattern:
  parent agents point at named IO blocks, and child agents either reuse or
  patch those named blocks directly.
- `26_abstract_authored_slots` shows the authored-slot requirement pattern:
  abstract parents can require concrete descendants to define named authored
  slots directly with `abstract <slot_key>` and no placeholder prose.
- `27_addressable_record_paths` earns addressable nested record items instead
  of forcing reusable headings and scalar leaves into bare strings.
- `28_addressable_workflow_paths` extends that path surface to recursive local
  workflow sections without widening bare workflow mentions.
- `29_enums` earns a first-class closed-vocabulary surface for repeated
  literals that should stop drifting as copied prose.
- large schemas and large example payloads should prefer file-backed references
  instead of inline JSON blocks.
- paths like `section_root/...` and `lesson_root/...` are currently explained
  path conventions, not separate root-binding declarations.
- the indentation-sensitive bootstrap grammar supports standalone `#` comment
  lines through the newline token rather than as separately ignored trivia

## Shipped Through 52

The shipped language subset now covers examples `01` through `52`, including
workflow law on existing `workflow` and `output` owners, first-class `review`
on its own shipped declaration family, and shared-root stdlib/public-pack
proof under the repo-level `prompts/` root.

Current shipped declaration kinds:
- `import`
- `workflow`
- `review`
- `abstract review`
- `skills`
- `inputs`
- `outputs`
- `agent`
- `abstract agent`
- `input`
- `input source`
- `output`
- `output target`
- `output shape`
- `json schema`
- `skill`
- `enum`

Workflow law does not add a new top-level declaration family.
It adds reserved child surfaces on existing owners:
- `law` on `workflow`
- `trust_surface` on `output`

Current shipped agent field families:
- `role`
- authored workflow slots such as `workflow`, `your_job`, `read_first`,
  `workflow_core`, `how_to_take_a_turn`, `standards_and_support`, and
  `when_to_use_this_role`
- authored-slot `abstract <slot_key>` requirements, which only concrete
  descendants must satisfy
- `inputs` as either a rich inline bucket, a direct ref to a named inputs
  block, or an explicit patch of a named inputs block
- `outputs` as either a rich inline bucket, a direct ref to a named outputs
  block, or an explicit patch of a named outputs block
- `skills`

Current shipped boundaries:
- the renderer stays role-first; there is no H1 agent-name mode in the shipped
  subset
- `skills` is now a first-class block surface:
  - it can be declared at the top level
  - it can be referenced directly from an agent `skills:` field
  - it can appear inline or by reference inside a workflow body
  - named `skills` blocks patch through explicit `inherit` and `override`
- `inputs` and `outputs` are now first-class block surfaces:
  - they can be declared at the top level
  - they can be referenced directly from an agent `inputs:` or `outputs:` field
  - named IO blocks patch through explicit `inherit` and `override`
  - abstract parent agents can centralize named IO blocks and child agents can
    reuse or patch those named blocks directly
  - anonymous parent-agent `inputs` and `outputs` fields are not themselves
    inherited patch surfaces
- `workflow` now owns the reserved `law` block for typed currentness,
  invalidation, mode/match branching, scope, preservation, basis-role, stop,
  and reroute semantics
- `output` now owns the reserved `trust_surface` block for downstream-readable
  carrier fields and guarded trust items
- portable currentness and invalidation move only through emitted output fields
  listed in the relevant `trust_surface`; there is no packet or shadow carrier
  model
- `route "..." -> AgentName` is a narrow typed line item inside workflow and
  authored-slot sections, not a standalone role-graph DSL
- output paths such as `section_root/...` stay plain path strings explained by
  surrounding guidance
- the language is skill-first; it does not ship a parallel `runtime_tools`
  surface
- `14_handoff_truth` is satisfied through imports plus existing primitives, not
  through a new freshness or packet primitive
- package build emission is configured separately from turn-level `output`
  contracts and currently emits only compiled `AGENTS.md` trees for explicit
  entrypoints
- emit config is discovered from the nearest `pyproject.toml` or an explicit
  CLI path; it does not live in prompt syntax

## Top-Level Buckets From Older Draft Role Docs

The older draft role docs suggest that the next language questions should not be tiny workflow details.

They suggest a handful of bigger buckets that will shape the workflow language anyway.

### 1. Role Home Composition

They are large role homes built from repeated sections such as:
- `Read First`
- `Workflow Core`
- `How To Take A Turn`
- `Skills And Tools`
- `Your Job`
- `Files For This Role`
- `When To Use This Role`
- `Standards And Support`

`12_role_home_composition` already earned the basic shell for this.

That means the remaining question is not whether role homes need a new
primitive.

The remaining question is what guidance belongs inside those composed sections
without turning them back into copied doctrine blobs.

### 2. Role Graph And Handoff Model

Those older draft outputs clearly encode a multi-role system, not isolated agents.

They repeatedly specify:
- normal owner order
- critic lanes
- next owner
- handoff comment rules
- stop and escalate behavior

This pressure is real, but the current shipped answer is intentionally narrow:
- `route "..." -> AgentName` inside workflow or authored-slot sections
- same-issue ownership truth carried by authored guidance plus typed
  `inputs`, `outputs`, and ordinary authored routing / stop slots
- no standalone role-graph or packet primitive yet

### 3. I/O, File Ownership, And Review Truth

Those older draft outputs spend a lot of energy defining what a role reads, what it
produces, which files are in scope now, what the next owner should trust, and
what should happen when review truth is missing.

That pressure is real, but it should not become a packet primitive.

We should handle it through:
- inputs
- outputs
- authored routing and stop guidance
- file ownership and readability rules
- next owner if accepted
- stop rule
- review truth that can be named explicitly without creating a packet surface

### 4. Shared Doctrine, Standards, And Support

The repeated support sections in those older draft docs are not just ordinary workflow steps.

They include things like:
- quality bars
- proof rules
- grounding standards
- escalation rules
- local read order

This suggests we need to decide how shared doctrine is represented and reused across many roles.

### 5. Skills And Tool Boundaries

Those older draft docs distinguish skills from named tools and helper surfaces.

Current design decision:
- the language intentionally supports `skill` first
- repeated reusable capability should be modeled as a skill
- a raw script path or ad hoc tool call is not a second supported authoring
  pattern
- tool-boundary and proof-boundary guidance may still appear in prose
  sections while the language stays skill-first

What is still real pressure from those older drafts:
- what a capability may support
- what it may not prove
- proof-route selection

What is not a current language goal:
- a separate `runtime_tools` declaration surface
- a language feature whose main job is to tell the agent where a script lives
- examples should not drift into a `runtime_tools` field when the design
  decision above already rejects that surface

### 6. Scope Roots And Path Variables

Those older draft outputs rely heavily on named roots and path conventions such as:
- `track_root`
- `section_root`
- `lesson_root`
- `<owner_root>`

Current read:
- those examples clearly show a pressure area
- but we have not yet earned prompt-level syntax for root binding
- for now, paths like `section_root/...` may remain explained conventions on
  file objects instead of separate declarations

That means this bucket is still real, but it is not yet earned as a formal
language primitive.

### 7. Evidence, Validation, And Review Runs

Those older draft outputs repeatedly talk about:
- current review files
- receipt-backed proof
- validation commands
- output contracts
- attached checkout truth

This suggests that "proof and validation surfaces" are a top-level design bucket, not just later detail.

### 8. Attached Checkouts And External Truth Sources

Several older draft outputs distinguish repo workflow truth from product truth in an attached checkout.

That means the language may need a richer way to talk about attached repos,
external artifacts, env files, and commands later without collapsing them into
ordinary workflow text.

## Current Priorities

Before we spend much more effort on workflow micro-rules, the bigger buckets to
resolve are:

1. clean up what belongs inside already-earned role-home shells
2. role graph and handoff model
3. I/O, ownership, and review truth without adding packets
4. skills and proof boundaries
5. attached checkouts and evidence surfaces
6. keep later examples aligned with the no-`runtime_tools` rule

Those buckets appear to be the real structure underneath those older draft role docs.

## Current Pressure Areas

Now that `01` through `16` are shipped, the next real design pressure is not
whether these primitives exist. The pressure is where to stop widening them.

Current live questions:
- what belongs in shared doctrine sections versus typed field families
- whether route semantics ever need to grow past the current narrow line-item
  form
- whether attached checkout and evidence surfaces need first-class declarations
- whether path-root conventions ever need more than explained string guidance
- how much extra validation or normalization the compiler should enforce on the
  richer contract surfaces without making authoring brittle

## Current Bias

Right now the language is biased toward:
- explicit typed declarations
- small readable examples
- semantic composition
- minimal magic

Right now the language is not trying to be:
- a generic macro system
- a free-form templating language
- a giant schema up front

That bias is intentional. We want to earn complexity instead of assuming it.

## Future Roadmap

These are not current commitments. They are future directions we may support
after the current skill-first surface is stable.

- MCP-backed capabilities are a likely future extension point.
- If we add MCP support, it should be explicit and first-class, not smuggled in
  as raw command or script-path guidance.
- We are not designing MCP syntax yet.
- The current design stance is still: model reusable capability as a skill
  today, and defer broader capability-surface expansion until the examples
  force it cleanly.
