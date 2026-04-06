# Language Design Notes

This document is intentionally short and easy to rewrite.

The goal is to capture the language decisions we have made so far, why we made them, and how we currently expect the parser to behave.

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
- output file-name mapping for rendered agents is a future concern, not a locked rule yet
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
- agents should compose named workflows when the structure is deeper than a simple local workflow
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
- an imported workflow should be referenceable through an explicit qualified symbol path such as `simple.greeting.Greeting`
- imported symbol identity should not depend on case guesswork or fallback lookup

This is why the imported examples are typed as `workflow Greeting: "Greeting"` and referenced as explicit module-qualified symbols instead of as untyped text labels.

## Composition

We currently want composition to stay explicit and understandable.

Current intent:
- when one workflow references another named workflow, the final rendered output should read like one coherent document
- composition should feel like assembling semantic pieces, not pasting arbitrary text
- simple inline workflows and composed named workflows should not behave like two different languages

We are deliberately avoiding looser reuse features until the examples prove that we need them.

## Inheritance

Inheritance has earned a place conceptually, and the current direction is now clearly "explicit ordered patching" rather than any kind of implicit merge.

Current syntax direction:
- `agent Child[Base]:` means the child extends the base agent
- `abstract agent Base:` means the base exists for inheritance and should not render by itself
- `workflow Child[Base]: "Title"` means the child extends a named base workflow and keeps the same explicit patching model

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
- `key: "Title"` inside an inherited child means "this is a new workflow entry and it belongs exactly here."
- simple local workflows may still live inline inside an agent.
- named top-level workflows are the canonical home for nested, reusable, or inherited workflow structure.
- inline agent workflows are convenience authoring, not a second semantic model.
- workflow inheritance should work the same way for named workflows as it does for inherited agent workflows.
- Rendered section titles are explicit authored data. Keys are never used as visible headings.
- Adjacent workflow strings should stay adjacent in the rendered output. The renderer should not invent an extra blank line between them.
- Invalid overrides should be real compiler errors, not silent fallbacks.
- We now have a canonical numbered compiler error reference in [COMPILER_ERRORS.md](/Users/aelaguiz/workspace/pyprompt/docs/COMPILER_ERRORS.md).
- `09_outputs` now treats `output` as the only produced-contract primitive.
- `output target`, `output shape`, and `json schema` are reusable supporting
  declarations under `output`, not competing output primitives.
- richer output contract material should live directly on `output`; we do not
  currently need a separate top-level `artifact` concept.
- `11_skills_and_tools` is intentionally skill-first.
- reusable capabilities should be modeled as `skill` declarations.
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
  outcomes, ownership, and readable file contracts instead.
- do not cargo-cult `99` output patterns such as redundant `owns` sections when
  the output contract already makes ownership obvious.
- `14_handoff_truth` shows the basic "tell the next owner what to use now"
  pattern without adding a new primitive.
- do not treat that handoff-truth pattern as an open language gap unless we
  later decide we need machine-readable freshness semantics.
- large schemas and large example payloads should prefer file-backed references
  instead of inline JSON blocks.
- paths like `section_root/...` and `lesson_root/...` are currently explained
  path conventions, not separate root-binding declarations.
- the indentation-sensitive bootstrap grammar supports standalone `#` comment
  lines through the newline token rather than as separately ignored trivia

## Pending Decisions

- How should rendered output file names map from concrete agent names when one source package emits many concrete agents?
- Should workflow children always be keyed, or do we also want anonymous ordered items beyond strings?
- When a child overrides a workflow, should the string preamble always replace the parent preamble, or do we eventually want append behavior too?
- Do we want top-level reusable declarations besides `workflow`, or should we keep reuse narrow for as long as possible?
- should named workflow composition stay as a bare reference line, or do we want a more explicit `use`-style syntax later?

## Pending Concepts

These are concepts we expect to revisit, but they are not locked into the example sequence yet.

- richer ordered workflow semantics
- multi-agent output from one source package
- agent input and output signatures
- skills
- more explicit workflow declarations and reuse patterns
- formal runtime-root declarations and path interpolation
- file ownership and review-readability conventions built on inputs and outputs
- policies and tool boundaries
- role graphs and handoff structure

## Top-Level Buckets From 99

The `99_not_clean_but_useful` examples suggest that the next language questions should not be tiny workflow details.

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

The `99` outputs clearly encode a multi-role system, not isolated agents.

They repeatedly specify:
- normal owner order
- critic lanes
- next owner
- handoff comment rules
- stop and escalate behavior

This suggests the language needs a first-class way to express role-to-role routing and ownership flow.

### 3. I/O, File Ownership, And Review Truth

The `99` outputs spend a lot of energy defining what a role reads, what it
produces, which files are in scope now, what the next owner should trust, and
what should happen when review truth is missing.

That pressure is real, but it should not become a packet primitive.

We should handle it through:
- inputs
- outputs
- outcomes
- file ownership and readability rules
- next owner if accepted
- stop rule
- review truth that can be named explicitly without creating a packet surface

### 4. Shared Doctrine, Standards, And Support

The repeated support sections in `99` are not just ordinary workflow steps.

They include things like:
- quality bars
- proof rules
- grounding standards
- escalation rules
- local read order

This suggests we need to decide how shared doctrine is represented and reused across many roles.

### 5. Skills And Tool Boundaries

The `99` examples distinguish skills from named tools and helper surfaces.

Current design decision:
- the language intentionally supports `skill` first
- repeated reusable capability should be modeled as a skill
- a raw script path or ad hoc tool call is not a second supported authoring
  pattern
- tool-boundary and proof-boundary guidance may still appear in prose
  sections while the language stays skill-first

What is still real pressure from `99`:
- what a capability may support
- what it may not prove
- proof-route selection

What is not a current language goal:
- a separate `runtime_tools` declaration surface
- a language feature whose main job is to tell the agent where a script lives
- examples should not drift into a `runtime_tools` field when the design
  decision above already rejects that surface

### 6. Scope Roots And Path Variables

The `99` outputs rely heavily on named roots and path conventions such as:
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

The `99` outputs repeatedly talk about:
- current review files
- receipt-backed proof
- validation commands
- output contracts
- attached checkout truth

This suggests that "proof and validation surfaces" are a top-level design bucket, not just later detail.

### 8. Attached Checkouts And External Truth Sources

Several `99` outputs distinguish repo workflow truth from product truth in an attached checkout.

That means the language may need a way to talk about attached repos, external artifacts, env files, and commands without collapsing them into ordinary workflow text.

## Current Priorities

Before we spend much more effort on workflow micro-rules, the bigger buckets to
resolve are:

1. clean up what belongs inside already-earned role-home shells
2. role graph and handoff model
3. I/O, ownership, and review truth without adding packets
4. skills and proof boundaries
5. attached checkouts and evidence surfaces
6. keep later examples aligned with the no-`runtime_tools` rule

Those buckets appear to be the real structure underneath the `99` examples.

## Top Candidates For Next Work

- Decide what should live in shared doctrine sections versus role-local fields
  now that the basic role-home shell is already earned.
- Decide how to represent role graphs, handoff order, critic lanes, and next-owner rules.
- Decide how to express ownership and review truth through inputs, outputs,
  outcomes, and file contracts without introducing packets.
- Decide how skills and proof boundaries should be represented while keeping the
  language skill-first.
- Decide how attached checkouts and review/evidence files should be modeled.
- Keep `12_role_home_composition` and `13_critic_protocol` consistent with the
  no-`runtime_tools` rule.

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
