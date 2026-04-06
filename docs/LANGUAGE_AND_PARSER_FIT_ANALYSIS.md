# Language And Parser Fit Analysis

## Scope

This document audits:

- the current example sequence in `examples/01_hello_world` through `examples/05_workflow_merge`
- the directional pressure implied by `examples/99_not_clean_but_useful`
- the local reference libraries in `for_reference_only/`:
  - `lark`
  - `pyparsing`
  - `LibCST`
- a fourth implementation baseline that is not cloned locally but keeps coming up in the research: a small hand-written parser with an indentation preprocessor

This is both a language-design critique and a parser-fit analysis.

The main question is not just "what can parse this?" It is "what language shape should we keep or change now so implementation stays easy while the design is still fluid?"

## Executive Summary

The language is in a good place right now if the goal is to keep it small, typed, indentation-sensitive, and example-first. The current `01` through `05` sequence is still compact enough that you can change course cheaply.

The best fit depends on whether the current surface syntax is part of the product:

- If the current custom syntax is important, `Lark` is the best overall fit.
- If you want the fastest pure-Python prototype and are willing to accept a grammar expressed as Python code, `pyparsing` is viable.
- If you are willing to make the language much more Python-shaped, `LibCST` becomes attractive, but it is not a direct fit for the current syntax.
- If you keep the language tight for a while longer, a hand-written parser is still a serious option and may actually be the simplest implementation path.

The biggest risk is not indentation parsing. The biggest risk is semantic growth:

- merge semantics
- reuse semantics
- ordering rules for merged workflow entries
- future typed declarations beyond `agent` and `workflow`

The current examples are still easy to parse. The harder problem has already started in `05_workflow_merge`: the language is beginning to define ordering and inheritance behavior that is more semantic than syntactic.

## What The Language Actually Is Right Now

Based on the current examples and `docs/LANGUAGE_DESIGN_NOTES.md`, the language surface is still small:

- top-level declarations:
  - `agent Name:`
  - `workflow Name:`
  - `import module_name`
- inheritance:
  - `agent Child[Base]:`
- agent fields used so far:
  - `role: "..."` as scalar text
  - `workflow:` as an indentation-scoped body
- workflow body statement kinds used so far:
  - bare strings
  - keyed nested entries like `step_one:`
  - bare symbol references like `Greeting`

That is a very manageable grammar.

The current examples progressively add complexity:

- `01_hello_world`: one declaration, one scalar field, one workflow string
- `02_sections`: keyed nested workflow entries
- `03_imports`: top-level reusable workflow declarations plus symbol references
- `04_inheritance`: single inheritance, scalar override, keyed workflow override, inherited workflow entries, replacement of workflow string preamble
- `05_workflow_merge`: multi-level inheritance with ordering-sensitive merged workflow entries

The key point: `01` to `04` mostly grow syntax and symbol resolution. `05` starts to grow merge semantics.

## What Is Easy Versus Hard In The Current Design

### Easy Now

These parts are structurally friendly for almost any parser strategy:

- indentation-scoped blocks
- a small number of declaration types
- explicit `:` block headers
- quoted string literals as the only literal type used so far
- keyed nested workflow entries
- single inheritance syntax with one base

### Harder Now

These are the first places where design decisions will materially affect implementation difficulty:

- bare symbol references inside workflows
- exact ordering semantics for merged workflow entries
- exact replacement versus append behavior for workflow preamble strings
- import resolution model
- comment syntax and comment placement rules
- whether future reusable declarations are only `workflow` or many other top-level declaration kinds

### Why Bare Symbol References Matter

Inside a workflow, a bare line like `Greeting` is currently a reusable workflow reference.

That works, but it is the first place where the language becomes less explicit than the semantics:

- it is not syntactically obvious whether `Greeting` is a reference, a new statement kind, or a future literal form
- the parser can still handle it, but validation and error messages become less direct
- future features will compete for the same visual slot

If you keep custom syntax, an explicit keyword such as `use Greeting` or `include Greeting` would make the language easier to read, easier to validate, and easier to evolve.

### Why `05_workflow_merge` Is The Real Pressure Test

`05_workflow_merge` is where the current design stops being "just parse the tree" and starts becoming "implement a merge algorithm that users can understand."

The example commits to all of these:

- multi-level inheritance
- inherited keyed workflow entries
- replacement of inherited keyed entries
- replacement of the workflow preamble string list
- insertion of new keyed entries into a merged order
- appending of additional keyed entries

That is implementable, but it needs a crisp rule set.

Right now the example output is stronger than the written semantic contract. A human can infer the intended result, but the exact ordering algorithm is not yet obvious from syntax alone.

That means `05` is more a compiler-design problem than a parsing problem.

## Important Directional Pressure From `99_not_clean_but_useful`

`examples/99_not_clean_but_useful` should not be treated as a source-language contract. It is an output-pressure corpus.

That distinction matters.

Those files are useful because they show what kinds of rendered documents the language may eventually need to produce:

- large multi-section documents
- deep heading hierarchies
- stable reusable structure across many roles
- lots of lists, inline code spans, and path references
- anchor tags and other exact output details
- repeated doctrinal sections with lane-local differences

What they do **not** prove yet:

- that the source language needs raw HTML passthrough
- that the source language needs to model every Markdown detail directly
- that the source language needs all the future declaration kinds now

The right lesson from `99` is:

- the compiler must eventually support rich structured output
- the language should probably stay much simpler than the final Markdown surface

If you try to back-solve the whole source language directly from `99`, you will overbuild.

## Recommended Design Discipline From Here

The current sequence suggests a good design doctrine:

- keep the source language small
- push complexity into semantic compilation, not source notation
- add only one new concept per example
- treat `99` as a rendering target, not as a grammar blueprint

That argues for:

- a tiny number of statement kinds
- explicit reuse
- restrained inheritance
- delayed introduction of signatures, artifacts, policies, and role graphs

## Support Matrix

Support levels below mean "fit for the language you have now," not "absolute library quality."

| Capability | Lark | pyparsing | LibCST | Hand-written parser |
|---|---|---|---|---|
| Keep current custom syntax | High | High | Low | High |
| Indentation-sensitive parsing | High | High | Low unless syntax becomes Pythonic | Medium-High |
| Bare string workflow lines | High | High | Medium via Python docstrings/desugaring | High |
| Keyed nested workflow entries | High | High | Low unless syntax becomes Pythonic | High |
| Single inheritance syntax like `Child[Base]` | High | High | Low unless preprocessed | High |
| Import and symbol-resolution hooks | High | Medium | Medium if you accept Python-shaped imports | High |
| Source-preserving refactors | Medium | Low | High | Low |
| Error recovery and editor tooling | Medium | Low-Medium | High for Python syntax only | Low |
| Long-term grammar readability | High | Medium | High only if Python-shaped | Medium |
| Fastest path to first working compiler | High | High | Low-Medium | High |
| Best fit if language grows while staying custom | High | Medium | Low | Medium |

## Library Analysis

## Lark

### What will work well

Lark is a strong fit for the language as it exists today.

Why:

- it is built for custom grammars, not just Python syntax
- it uses explicit grammar files, which is good for a language that is still being designed
- it has a documented indentation strategy through `Indenter`
- it builds parse trees automatically and gives you a clear transform stage
- it supports both forgiving and fast parsing modes

The relevant fit points from the reference clone:

- `README.md` presents Lark as a general-purpose grammar toolkit with automatic tree construction and stand-alone parser generation
- `lark/indenter.py` shows the exact post-lex indentation hook you would use
- `examples/indented_tree.py` shows the intended pattern for indentation-sensitive grammars
- `docs/parsers.md` makes the Earley versus LALR tradeoff explicit

This matches your current language shape very well:

- custom declaration headers
- indentation-scoped bodies
- ordered nested structures
- future semantic transforms into Markdown

### What will be difficult

Lark does not remove design complexity. It mostly removes parser-construction complexity.

The hard parts will still be:

- getting newline and comment handling exactly right
- avoiding avoidable ambiguities if the language gains too many bare statement forms
- designing a clean AST instead of leaking grammar details into semantics
- implementing merge semantics above the parse tree

The sharp edge to watch is indentation tokenization:

- the newline token must include the trailing spaces that determine indentation
- if comments are legal in indentation-sensitive positions, the newline token must account for them correctly

That is manageable, but it is a real implementation detail, not magic.

### Design changes that help Lark

- make workflow references explicit, such as `use Greeting`
- decide comment syntax early
- keep the number of statement kinds low
- keep merge semantics simple and documented separately from parsing
- avoid introducing context-sensitive shortcuts that depend on later semantic knowledge

### Bottom line

If the current custom syntax is important, `Lark` is the best overall implementation target.

## pyparsing

### What will work well

pyparsing is also a real option for the current language.

Why:

- it handles grammars directly in Python code
- it has `IndentedBlock`
- it is ergonomic for fast prototyping
- it gives you parse actions immediately, which can be convenient while the language is small

The relevant fit points from the reference clone:

- `README.rst` frames pyparsing as direct grammar construction in Python
- `docs/HowToUsePyparsing.rst` documents `IndentedBlock`
- `docs/whats_new_in_3_3.rst` notes that modern `IndentedBlock` supports nested indentation levels without the older external indent-stack ceremony

For a small grammar, this can move very fast.

### What will be difficult

pyparsing becomes less attractive as the language wants to become a real language specification instead of just a parser implementation.

The main risks are:

- the grammar lives in Python code instead of a compact grammar file
- parse actions can encourage mixing parsing and semantics too early
- parse results are flexible, but less naturally spec-like than a dedicated grammar plus tree transform
- performance and debugging tradeoffs become more noticeable as the grammar grows
- parser features like packrat, recursion support, and parse actions need more care

This matters for your trajectory because the language is already moving from "parse a tree" toward "compile a small structured language with inheritance and merge behavior."

pyparsing can absolutely do that, but it may become harder to keep the grammar itself as a clean reference artifact.

### Design changes that help pyparsing

- make every statement kind visually explicit
- avoid multiple bare forms that look similar
- keep inheritance semantics shallow
- keep source notation close to a small set of composable parser elements
- do not rely on implicit contextual meaning when an explicit keyword would do

### Bottom line

If you want the fastest pure-Python prototype, `pyparsing` can work. If you want a durable language definition that will remain easy to reason about as the language grows, it is a weaker long-term fit than `Lark`.

## LibCST

### What will work well

LibCST is excellent at parsing, analyzing, and rewriting Python code while preserving formatting.

The relevant fit points from the reference clone:

- `README.rst` makes its purpose explicit: it parses Python code as a lossless CST
- `docs/source/parser.rst` exposes `parse_module`, `parse_statement`, and `parse_expression`
- `docs/source/motivation.rst` and `docs/source/why_libcst.rst` make clear that exact representation and rewritability are the core value

If you were building a Python-shaped DSL, or if you decided that your authoring format should simply be valid Python with a tiny amount of convention, LibCST would be a strong tool.

It would also be excellent for:

- canonicalization
- codemods
- source-preserving auto-fixes
- rich editor-aware workflows

### What will be difficult

LibCST is not a good direct parser for the custom syntax you currently have.

Your current examples are not Python:

- `agent Name:`
- `workflow:`
- `role: "..."` as field syntax inside custom declarations
- bare symbol references inside workflow bodies

To use LibCST, you would need one of these:

- change the language surface to become Python-shaped
- add a preprocessor that rewrites your DSL into Python before parsing

That is possible, but it changes the design question.

If you go down that path, you are no longer mainly choosing a parser. You are choosing to bend the language toward Python.

That trade can be good, but it is a language-design decision, not just an implementation trick.

### What the language would need to change

A LibCST-friendly direction would look more like:

- `agent HelloWorld:` becomes `class HelloWorld:`
- `role: "..."` becomes `role = "..."`
- `workflow:` becomes a nested class or a structured assignment
- bare workflow strings become Python docstrings or list elements
- inheritance becomes normal Python class inheritance

That would make parsing easier, but it would materially change the feel of the language.

### Bottom line

`LibCST` is a strong fit only if you are willing to make the language substantially more Python-shaped. It is not the right direct parser if the current custom syntax is part of the product.

## Fourth Baseline: Hand-Written Parser

This is not in `for_reference_only/`, but it deserves a place in the analysis because the current language is still small.

### What will work well

For the language as it exists today, a hand-written parser is not crazy at all.

Current grammar burden:

- a few top-level declarations
- indentation-scoped blocks
- quoted strings
- keyed nested entries
- simple imports
- single inheritance header syntax

That is still small enough that a hand-written tokenizer plus indentation preprocessor could be clearer than integrating a larger toolkit.

The advantages:

- exact control over diagnostics
- exact control over AST shape
- no dependency model to absorb
- easy to keep semantics and parsing visibly separate if you are disciplined

### What will be difficult

The risk is not the current grammar. The risk is the next ten features.

A hand-written parser becomes less appealing if you add:

- multiple new declaration types
- signatures and type annotations
- richer import resolution
- more statement kinds
- policies, artifacts, and packet contracts
- editor tooling and source-preserving rewrites

The more grammar you earn, the more valuable a real grammar system becomes.

### Bottom line

If you keep the language disciplined through a few more examples, a hand-written parser remains a legitimate baseline. If you expect the language to broaden soon, `Lark` is safer.

## What The Parser Does Not Solve

It is important to separate parser complexity from compiler complexity.

The parser solves:

- declaration headers
- indentation
- strings
- nested blocks
- references as syntax

The compiler or semantic layer solves:

- import resolution
- symbol lookup
- merge semantics
- inheritance behavior
- source-name to rendered-name humanization
- Markdown rendering rules

Right now your hardest problems are already shifting into the semantic layer.

That is another reason to keep the source language small.

## Language Design Critique

## What is strong

- The examples are genuinely example-first.
- The progression from `01` to `05` is coherent.
- The language still has a visible core instead of a giant speculative surface.
- The design notes correctly resist overcommitting to future concepts.
- Output focus is good: the language is designed around what the compiled documents should feel like.

## What is risky

### Bare workflow references are too implicit

`Greeting` as a workflow body line is compact, but it is a soft spot for future ambiguity.

Recommendation:

- prefer an explicit form such as `use Greeting`

### `05_workflow_merge` is ahead of the written rulebook

The example is useful, but it commits to merge-order behavior that is more complex than the rest of the language surface.

Recommendation:

- either write the exact ordering rule now
- or simplify the merge model before more examples depend on it

### `99_not_clean_but_useful` can overpressure the source language

Those files are useful as output targets, but they are dangerous as direct source-language inspiration.

Recommendation:

- keep using them as rendering pressure, not as immediate grammar commitments

### The next feature set could explode the grammar

Artifacts, signatures, skills, policies, and role graphs all push the language toward a much richer declaration system.

Recommendation:

- do not add several of those at once
- add one of them only after the core parser exists and the AST feels stable

## Design Changes Worth Making Now

These changes would materially improve implementation ease without harming the spirit of the language.

### 1. Make reuse explicit

Change:

- from bare references like `Greeting`
- to something like `use Greeting`

Why:

- easier grammar
- easier error messages
- easier AST
- easier future language growth

### 2. Keep workflow bodies to exactly three statement kinds for now

Recommended set:

- string line
- keyed nested block
- explicit reuse statement

That keeps the core language legible.

### 3. Keep inheritance shallow

Current inheritance is still fine, but it should remain:

- single inheritance only
- scalar override
- keyed nested replacement by key
- explicitly documented workflow preamble rule

Avoid adding more inheritance modes until the current one is implemented and feels good.

### 4. Simplify merge ordering if possible

This is the most important semantic design question.

The easiest implementation model is something like:

- child scalar fields override
- child workflow preamble replaces parent preamble
- keyed workflow entries merge by key
- inherited omitted keys keep parent order
- child replacements happen in place
- truly new child keys append

That model is easy to explain and easy to implement.

Your current `05_workflow_merge` example asks for something a bit richer than that.

If you keep the richer behavior, add syntax or explicit rules for it. Do not leave it as implicit inference from one example.

### 5. Decide comments now

Comment syntax is not glamorous, but indentation-sensitive grammars care about it.

Pick one comment form early and keep it stable.

### 6. Reserve keywords early

At minimum, reserve:

- `agent`
- `workflow`
- `import`
- any explicit reuse keyword you choose

That will reduce future ambiguity and improve error messages.

### 7. Delay the typed declaration explosion

Do not add `artifact`, signatures, policies, and role graphs all at once.

The implementation cost is not just more grammar. It is:

- more AST types
- more validation rules
- more merge semantics
- more documentation burden

### 8. Treat rich Markdown as output, not input

Keep the source language semantic and structured.

Do not try to expose:

- raw anchors
- raw HTML passthrough
- low-level Markdown formatting controls

unless real examples prove you need them.

## Recommended Paths

## Path A: Keep Current Syntax, Choose Lark

Choose this if:

- the current custom syntax matters
- you want a real grammar artifact
- you expect the language to grow beyond five tiny examples

This is the best default path.

## Path B: Keep Current Syntax, Prototype In Pyparsing

Choose this if:

- you want a first prototype extremely quickly
- you are comfortable expressing the grammar directly in Python
- you accept that you may later migrate to a grammar-file-based implementation

This is a fast prototype path, not my preferred durable path.

## Path C: Make The Language Python-Shaped, Use LibCST

Choose this if:

- parser and tooling maturity matter more than current surface syntax
- you are open to the language becoming more Python-like
- source-preserving transforms and codemods are a first-class requirement

This is a language redesign path, not just a parser choice.

## Path D: Stay Small Longer, Build A Hand-Written Parser

Choose this if:

- you want maximal control
- you expect to add only a few more tightly-scoped examples before freezing the core
- you are disciplined about keeping the language tiny

This is viable only if you stay disciplined.

## Final Recommendation

If the current custom syntax is part of the product, the recommendation is:

1. choose `Lark`
2. make workflow reuse explicit
3. simplify or explicitly define merge ordering semantics before adding more features
4. keep future declaration kinds out of the grammar until the current five-example core is implemented

If you are willing to change the language surface materially, reevaluate around a Python-shaped design and `LibCST`.

Until that decision changes, the best near-term design principle is:

- keep the language smaller than the output
- keep the parser smaller than the compiler
- keep the semantics smaller than the ambitions implied by `99_not_clean_but_useful`
