# Agent I/O Design Notes

This document now records the shipped I/O model through examples `08` to `42`.

The goal is to describe the turn-level contract the language already supports,
and the explicit non-goals that keep it from drifting into packet or
root-binding machinery too early.

For the language-level workflow-law reference, use
[WORKFLOW_LAW.md](WORKFLOW_LAW.md). This document focuses on the I/O boundary:
what outputs emit, what fields are trusted carriers, and how downstream readers
learn what is current now.

## Why This Exists

The shipped language can now say useful things about:
- agent shape
- workflow shape
- workflow law
- workflow reuse
- inheritance
- next-owner routing
- typed inputs and typed input sources
- typed outputs, output targets, output shapes, and JSON schemas
- portable currentness and invalidation carried through trusted outputs
- authored routing and stop guidance
- skill-first capability references

The core turn-contract questions the shipped subset already answers are:

- what an agent turn consumes
- what an agent turn must have before it can run
- what an agent turn may optionally consult
- what an agent turn produces
- what downstream truth is current after the turn
- what downstream truth is no longer current after the turn
- what should happen when required inputs are missing

Packets may still become important later, but they are still a convention built
on top of these lower-level primitives, not a shipped primitive themselves.

## Shipped Boundaries

Current shipped boundaries:
- `input` separates `source`, `shape`, and `requirement`
- `source` resolves to built-ins such as `Prompt`, `File`, and `EnvVar`, or to
  a declared `input source`
- input `shape` stays a symbolic label in this subset
- `output` is the one produced-contract primitive
- `output` supports either `target + shape` or `files`
- `output` may also declare typed authored child fields plus reserved
  `trust_surface`
- `output` record bodies may also declare keyed guarded sections for
  conditional readback that still belongs to the emitted output contract
- `target` resolves to built-ins such as `TurnResponse` and `File`, or to a
  declared `output target`
- `shape` resolves to a declared `output shape` first, then to a symbolic label
- `json schema` is subordinate to `output shape`, not a competing output
  primitive
- richer authored support sections such as `must_include`,
  `standalone_read`, and `notes` stay authored prose
- `trust_surface` is the explicit portable-truth contract for an output
- `trust_surface` items may be unconditional or guarded with `when`
- guarded output sections render as conditional shells in compiled `AGENTS.md`
  but stay ordinary output fields rather than portable-truth carriers
- guarded output sections may read declared inputs and enum members
- guarded output sections may not read workflow-local bindings, emitted
  output fields, or undeclared runtime names
- workflow law may bind `current artifact ... via ...` and `invalidate ... via ...`
  only through declared output fields
- trusted carrier fields must actually be emitted by the concrete turn
- path conventions such as `section_root/...` stay plain strings explained by
  surrounding guidance
- compiled `AGENTS.md` emission is a separate build layer configured outside the
  prompt language; it is not an `output target`
- there is still no packet primitive, no root-binding declaration, and no
  `runtime_tools` surface

## Portable Truth And Trust Carriers

Workflow law and output I/O now meet at one explicit handoff boundary.

Current shipped rules:
- portable currentness is declared in workflow law with `current artifact ... via ...`
- route-only turns may use `current none` instead of a current artifact
- invalidation is declared in workflow law with `invalidate ... via ...`
- the carrier side of either rule must point at an emitted output field that is
  listed in that output's `trust_surface`
- `trust_surface` is where downstream owners learn which output fields carry
  current truth, comparison-only basis, rewrite exclusions, invalidations, or
  other shipped workflow-law facts
- route-only conditional readback such as `rewrite_mode` or
  `repeated_problem` stays on the output contract unless the compiler
  explicitly promotes that field into `trust_surface`
- when a route-only branch resolves a semantic route and an emitted output
  includes a `next_owner` field, that field must structurally bind the routed
  target rather than naming it only by prose convention
- carrier semantics are compiler-owned and fail loud; they are not inferred
  from prose labels such as `current_artifact` or `invalidations`
- `standalone_read` stays human-facing companion prose; it does not act as a
  second trust carrier or override `trust_surface`
- `standalone_read` may summarize branch-level readback, but it may not
  structurally interpolate guarded output detail that could be absent when a
  guard is false

This keeps the turn contract explicit:
- `output` still says what the turn emits
- `trust_surface` says which emitted fields carry portable downstream truth
- workflow law says when those trusted fields are active and what they mean

## Current Framing

Current intuition:
- every agent turn has inputs, outputs, and failure behavior
- some inputs are delivered directly in the invocation prompt
- some inputs are external surfaces the agent must read
- some inputs are required and should fail loudly if missing
- some inputs are advisory and should guide the turn without being a hard gate
- outputs may go to different destinations and may require different formats
- input source and input type are different questions and should not be conflated

This means the language likely needs a real I/O contract model before it needs
a packet model.

## Core Distinction: Source Versus Shape

One of the main things we need to keep separate is:
- where an input comes from
- what kind of thing the input is once the agent has it

Those are not the same axis.

Examples:
- an input might come from the prompt and still be a Markdown document
- an input might come from a file lookup and still be a Markdown document
- an input might come from an environment variable and be a directory path
- an input might come from the prompt and be a JSON object

Current requirement:
- the language should not let source words like `file` do all the work
- the model should let us say both acquisition mode and input shape
- "go read this from a path" and "this content is already in the prompt" should
  be distinguishable even if the resulting shape is the same

## Source Should Be Typed And Extensible

`source` should not stay a loose descriptive string forever.

Current intuition:
- `source` should come from a typed built-in but extensible set of source kinds
- built-in sources can ship with the language
- users should be able to declare custom sources later without changing the
  core language

Examples we already expect as built-ins:
- `Prompt`
- `File`
- `EnvVar`

Possible future custom source:
- `FigmaDocument`

Current requirement:
- source selection should be validated as a known source kind, not accepted as
  arbitrary freeform text
- the language should support custom source declarations as first-class data
  rather than falling back to prose

## Common Input Fields Versus Source-Specific Fields

An input contract seems to need two layers:
- common fields that every input can use
- source-specific fields that only make sense for certain sources

Examples:
- common fields: source, shape, requirement
- `File`-specific field: `path`
- `EnvVar`-specific field: `env`
- `FigmaDocument`-specific field: `url`

Current requirement:
- the language should separate the stable common input contract from
  source-specific configuration
- source-specific required keys should be defined by the selected source kind
- the model should allow different sources to require different keys without
  polluting every input with every possible field

Current bias:
- common input fields should stay flat and readable
- source-specific keys should stay grouped under the chosen source instead of
  leaking everywhere

## Core Distinction: Provided Versus Lookup Input

Another useful split is:
- provided input: already present when the agent turn begins
- lookup input: the turn tells the agent where to go get it

Current requirement:
- prompt-provided input and lookup input should not be treated as the same
  runtime contract
- the language should be able to say "this is already present" versus "go fetch
  this from here"
- file-path lookup and environment-variable lookup should be representable as
  distinct acquisition modes

## Core Distinction: Shape Versus Strictness

The type or shape of an input is not the same as how fully specified it is.

Examples:
- "Markdown document" is a shape
- "directory path" is a shape
- "JSON object matching this schema" is shape plus strong structural constraint
- "loosely described plan file" is shape plus light contract strength

Current requirement:
- the model should separate what kind of thing the input is from how strict the
  contract is
- some inputs may only need a short descriptive type
- some inputs may eventually need exact structure or schema
- the language should allow light and heavy contracts without forcing every
  input into full schema detail

## High-Level Requirements

### 1. First-Class Input Concept

The language should have an explicit way to say that an agent expects input.

Current requirement:
- inputs should not be hidden only inside prose
- the author should be able to distinguish "this turn receives this input"
  from ordinary workflow guidance

### 2. Input Modalities Must Be Distinct

Not all inputs are the same kind of thing.

Current requirement:
- direct prompted input should be distinguishable from read-or-fetch input
- inputs that are handed to the agent at invocation time should not be
  conflated with files or other surfaces the agent must go inspect
- we should leave room for other modalities later without assuming them now

Examples we already expect:
- prompted input
- required read input
- advisory read input
- environment-variable lookup input

### 2a. Input Source Must Be Explicit

Current requirement:
- the author should be able to say how the agent gets the input
- the source should not be hidden only in prose
- prompt-provided content, path lookup, and env lookup should be representable
- source should resolve to a known built-in or declared custom source kind

### 2b. Input Type Must Be Explicit

Current requirement:
- the author should be able to say what kind of thing the input is
- input type should not be implied only by where it came from
- the language should leave room for both light descriptive types and more exact
  structural types later

### 3. Required Versus Advisory Input Must Be Explicit

This looks like one of the key primitive distinctions.

Current requirement:
- the language should clearly separate "must be present for this turn to run"
  from "check this if relevant"
- authors should not have to smuggle hard requirements into ordinary workflow
  prose
- advisory guidance should not accidentally become a silent hard precondition

### 3a. Requiredness Should Stay Separate From Source And Type

Current requirement:
- whether an input is required should not be inferred from its source
- whether an input is required should not be inferred from its type
- the same source or type should be usable in both required and advisory forms

### 4. Missing Required Inputs Should Fail Loudly

If a turn depends on something mandatory, that should not be best-effort.

Current requirement:
- required missing inputs should produce a clear stop condition
- the language should be able to express "fail if this is not present"
- failure should be part of the contract, not an accidental runtime habit

### 5. First-Class Output Concept

The language should have an explicit way to say what a turn produces.

Current requirement:
- outputs should not be represented only as prose expectations
- authors should be able to distinguish "the agent says this back in the turn"
  from "the agent writes a file" or "the agent leaves a tracker comment"
- agent `outputs` should describe what the concrete turn produces, not a
  role-wide catalog of every artifact a workflow family might touch

## Output Target Should Be Typed And Extensible

Like input source, output destination should not stay a loose descriptive
string forever.

Current intuition:
- output target should come from a typed built-in but extensible set of target
  kinds
- the built-in set should stay small and standard
- custom workflow-specific targets should be declarable without changing the
  core language

Examples we already expect as built-ins:
- `TurnResponse`
- `File`

Example of a likely custom target:
- `TrackerComment`

Current requirement:
- target selection should be validated as a known built-in or declared custom
  target kind
- workflow-specific destinations should not have to become built-ins just to be
  expressible
- built-ins should cover common generic destinations, not every product or
  workflow convention

## Common Output Fields Versus Target-Specific Fields

Like inputs, outputs seem to need two layers:
- common output fields that every output can use
- target-specific fields that only make sense for certain targets

Examples:
- common fields: target, shape, requirement
- `File`-specific field: `path`
- `TrackerComment`-specific field: `issue`

Current requirement:
- the language should separate the stable common output contract from
  target-specific configuration
- target-specific required keys should be defined by the selected target kind
- the model should allow different targets to require different keys without
  polluting every output with every possible field

## Output Shape Needs A Richer Contract Surface

Outputs often need more authored structure than inputs.

Current intuition:
- an output may need not just a type label but an explanation of what it is for
- an output may need structural guidance, examples, or schema
- output shape should be reusable across different targets when the content
  contract is the same

Examples:
- a plain-text turn response may need a short purpose and expected structure
- a Markdown file may need a purpose, expected sections, and an example
- a JSON output may need schema plus explanatory notes

Current requirement:
- output shape should be able to carry richer authored contract material than a
  short type label alone
- the model should let us attach explanations, expected structure, examples, and
  schema when needed
- target and shape should remain separate so "what it looks like" is distinct
  from "where it goes"

## Rich Output Contracts Stay On Output

There should be one real produced-contract primitive: `output`.

Current intuition:
- simple outputs should stay small
- richer authored output contracts should still live on `output`, not on a
  second competing primitive
- reusable subordinate declarations should stay narrow and focused

Examples of rich output details that can live directly on `output`:
- one file versus multiple output files
- required headings or required included content
- support files that back the output without becoming the output
- what the output owns
- what a downstream role should be able to learn from it alone
- examples and notes that help the next role consume or review it

Current requirement:
- the language should not overload `shape` with every authored output rule
- the language should not need a second top-level "artifact" concept just to
  express a richer output contract
- `output target`, `output shape`, and `json schema` should remain reusable
  supporting declarations under the main `output` primitive

Current bias:
- keep `shape` narrow
- let `shape` describe form or structural type
- let `output` carry the richer authored contract when needed

## Current Output Decisions

The current output model is now narrow enough to state plainly.

Recently settled:
- `output` is the only produced-contract primitive
- `output target` is a reusable destination kind
- `output shape` is a reusable structural kind
- `json schema` is a reusable strict structural declaration that a shape can
  reference
- richer authored contract material such as required contents, support files,
  ownership notes, standalone-read notes, and examples should live directly on
  `output`
- the language does not currently need a separate top-level `artifact`
  primitive

Current consequence:
- small outputs can stay small
- large outputs can become richer `output` declarations without changing the
  primitive stack
- reusable declarations stay subordinate to `output` rather than competing with
  it

## JSON Schema Should Be First-Class

Structured JSON output looks important enough that schema should not live as an
escaped string buried inside an output shape.

Current intuition:
- JSON schema should be a named first-class declaration
- output shapes should reference a schema by name instead of embedding it inline
- the compiler should validate the schema as part of compilation
- the schema declaration should carry the profile or flavor it is meant to
  satisfy

Examples of likely schema profiles:
- generic JSON Schema
- an OpenAI structured-output profile

Current requirement:
- schema should not be reduced to a multi-line prose string
- authors should be able to reuse one schema across multiple output shapes or
  targets
- profile-specific validation should be attached to the schema declaration, not
  hidden in workflow prose
- explanatory notes and examples should still live on the output shape, while
  the schema declaration remains the source of structural truth

Current bias:
- use a first-class `json schema` primitive rather than inventing a second
  schema language inside the prompt language
- let the schema declaration own validation and profile selection
- let the output shape own purpose, usage notes, and examples

Current simplifying assumption:
- schema declarations should load their schema body from a file rather than
  embedding raw JSON directly in `.prompt` files
- this keeps prompt files readable while still letting the compiler validate
  the schema during compilation
- rendered output can still show the resolved schema if that is useful, but
  authored prompt source should stay file-backed for now
- example payloads should also prefer file-backed references when they are
  large enough to be noisy inline

## Path Conventions Stay As Guidance For Now

Some file paths in the examples use prefixes like `section_root/...` or
`lesson_root/...`.

Current decision:
- those prefixes are not currently separate language primitives
- those paths remain plain path strings
- the surrounding turn guidance may explain how to interpret those prefixes
- the language does not currently need separate runtime-root declarations just
  to make those paths usable

Current implication:
- typed acquisition modes such as `EnvVar` still matter because they are
  genuinely different runtime channels
- context-bound path prefixes do not yet need the same level of formality
- we should not promote path conventions into a new binding system until a real
  prompt example requires more than explained guidance

### 6. Output Modalities Must Be Distinct

Like inputs, outputs are not one thing.

Current requirement:
- the language should distinguish human-facing response output from external
  side-effect outputs
- file outputs should not be conflated with comment outputs
- structured outputs such as JSON should be representable without pretending
  they are the same as ordinary prose replies

Examples we already expect:
- normal turn response
- project tracker comment
- file output
- structured JSON output

### 7. Output Shape And Output Destination Should Be Separately Thinkable

One important distinction is:
- what shape the output has
- where the output goes

Current requirement:
- we should not force every output mode to bundle shape and destination into one
  inseparable concept
- "JSON" and "write this to a file" are different kinds of constraints
- "comment on the tracker" and "say this in the turn" are different
  destinations even if the content is both text

### 8. The Turn Contract Should Be More Primitive Than Packets

Packets may still matter, but they should not be the base layer if they are
really just bundled I/O expectations.

Current requirement:
- the language should be able to describe turn-level I/O without requiring a
  packet abstraction first
- if packets are introduced later, they should sit on top of the I/O model
  rather than replacing it

### 9. The Model Should Support Hard Preconditions Without Becoming Workflow Soup

Today a lot of these ideas would get hidden under sections like:
- Read First
- Your Job
- Stop Rule

Current requirement:
- the contract layer should keep hard execution requirements out of freeform
  workflow prose when possible
- workflow guidance and execution preconditions should be distinguishable

### 10. The Model Should Stay Small And Non-Magical

This next layer still needs to follow the same language bias we already have.

Current requirement:
- typed explicit declarations or fields should beat inferred magic
- required behavior should be explicit
- advisory behavior should be explicit
- the language should not collapse into a giant schema too early

## Post-14 Pressure Areas

The shipped subset now answers the minimum questions needed for `08` through
`14`. The remaining pressure is not whether the current primitives exist. The
pressure is where to stop widening them.

The next honest questions are:

1. How much validation should input `shape` labels get before they stop being
   lightweight symbolic names?
2. How much normalization should `files` output mode get before authoring
   becomes brittle?
3. Which additional built-in `input source` or `output target` kinds, if any,
   would earn their way into the language beyond `Prompt`, `File`, `EnvVar`,
   `TurnResponse`, and `File`?
4. How should richer schema validation or profile-specific validation attach to
   `json schema` and `output shape` without turning the language into a giant
   schema surface too early?
5. When do explained path conventions stop being enough and force a more
   formal binding model?
6. If packet-like bundles matter later, what sits cleanly on top of the
   shipped I/O layer instead of replacing it?

## Explicit Non-Goals For This Subset

This shipped subset still does not define:
- packet syntax
- packet review syntax
- tool boundary syntax
- evidence syntax
- validation command syntax
- formal runtime-root declarations or path interpolation primitives

Those may become future layers, but they should not blur the more primitive
question of agent turn inputs and outputs that is now already shipped.

## Current Bias

Right now the best bias seems to be:
- define a small explicit agent I/O contract surface
- keep required versus advisory semantics explicit
- keep input modality and output modality distinct
- let packets, proof, and validation build on top of that later
