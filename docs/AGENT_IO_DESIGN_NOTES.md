# Agent I/O Design Notes

This document is a working note for the next foundational language layer after
workflow composition and next-owner routing.

The goal is to describe the turn-level contract of an agent before we jump to
higher-level conventions like packets.

## Why This Exists

Right now the language can say useful things about:
- agent shape
- workflow shape
- workflow reuse
- inheritance
- next-owner routing

But it still does not have a clear model for the more primitive question:

- what an agent turn consumes
- what an agent turn must have before it can run
- what an agent turn may optionally consult
- what an agent turn produces
- what should happen when required inputs are missing

Packets may still become important later, but they look more like a convention
built on top of these lower-level primitives than like the next primitive
itself.

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
- file artifact
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

## Concrete Capability Areas To Define

The next questions to answer are probably:

1. What are the minimum input source modes we need to name explicitly?
2. What are the minimum input shapes or types we need to name explicitly?
3. How should required versus advisory inputs be represented?
4. How should fail-if-missing semantics be represented?
5. How much contract strength do we need before full schema becomes necessary?
6. What are the minimum output modalities we need to name explicitly?
7. Should outputs be single or multiple per turn?
8. What are the minimum built-in output targets we actually want to ship?
9. How should custom output targets be declared?
10. How should output shape differ from output destination?
11. How much richer than input shape should the output contract surface be?
12. How much of this belongs on the agent declaration versus inside a reusable
   named declaration?

## What This Document Is Not Deciding Yet

This document is not yet deciding:
- packet syntax
- packet review syntax
- tool boundary syntax
- evidence syntax
- validation command syntax

Those may attach to this model later, but they should not blur the more
primitive question of agent turn inputs and outputs.

## Current Bias

Right now the best bias seems to be:
- define a small explicit agent I/O contract surface
- keep required versus advisory semantics explicit
- keep input modality and output modality distinct
- let packets, proof, and validation build on top of that later
