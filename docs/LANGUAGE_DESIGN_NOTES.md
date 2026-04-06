# Language Design Notes

This document is intentionally short and easy to rewrite.

The goal is to capture the language decisions we have made so far, why we made them, and how we currently expect the parser to behave.

## Design Approach

- We are designing the language example-first.
- Each example should prove one new idea at a time.
- We do not want speculative features in the language unless an example clearly needs them.
- The parser should grow in the same order as the examples.

## Core Declarations So Far

- `agent` is a language primitive.
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
- `role` is not hidden metadata. It is output-facing text.
- `role` currently opens the rendered document directly.
- The rendered output should read naturally, not look like a debug dump of the source tree.

## Workflow Shape

`workflow` is currently our main semantic unit for instructions.

Current intent:
- A workflow can live directly inside an agent.
- A workflow can also be declared at the top level and reused.
- A workflow is not just arbitrary text. It is a typed instruction surface.
- A workflow can contain more than one string in a row before named nested entries begin.

Nested content inside a workflow currently means ordered substructure.

Current intent:
- nested workflow entries should preserve order
- nested workflow entries should render as subsections
- source names can be machine-friendly
- rendered names can be humanized

For example, a source key like `step_one` is intended to render more like `Step One`.

Current intent for adjacent workflow strings:
- sibling strings should preserve order
- sibling strings should render as consecutive lines
- the renderer should not automatically insert an extra blank line between those lines unless the source structure explicitly calls for it

## Imports

Imports exist to compose user-defined pieces.

Current intent:
- imported definitions should be typed declarations
- importing a file should bring in real named language objects, not raw text snippets
- a workflow declared in another file should be referenceable by name inside an agent workflow

This is why the imported examples are typed as `workflow Greeting:` and `workflow Object:` instead of just using untyped labels.

## Composition

We currently want composition to stay explicit and understandable.

Current intent:
- when one workflow references another named workflow, the final rendered output should read like one coherent document
- composition should feel like assembling semantic pieces, not pasting arbitrary text

We are deliberately avoiding looser reuse features until the examples prove that we need them.

## Inheritance

Inheritance has earned a place conceptually, and we now have a first concrete shape for it.

Current syntax direction:
- `agent Child[Base]:` means the child extends the base agent

Current intent:
- inheritance should produce one merged final document
- the child should be able to specialize inherited behavior without rewriting everything
- inherited output should feel natural, not expose internal implementation details unless we want that explicitly
- scalar fields like `role` should override
- nested workflow entries should merge by key
- omitted child workflow entries should be inherited
- child workflow entries with the same key should replace the parent version
- the child workflow string list should replace the parent workflow string list

Current example intent:
- in the inheritance example, `greeting` is inherited because the child does not redefine it
- `object` is overridden because the child defines it
- the child also overrides the workflow intro strings by providing its own two-line preamble

We still do not want to over-design merge semantics beyond what the current examples force.

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
