# Language Design Notes

This document records Doctrine's durable language choices and guardrails.

For the shipped syntax and feature overview, use
[LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md). For the numbered proof corpus,
use [../examples/README.md](../examples/README.md).
For release and compatibility policy, use [VERSIONING.md](VERSIONING.md).

## Core Principles

- Runtime compatibility matters. Doctrine keeps the runtime artifact as
  Markdown because existing coding-agent tools can already consume it.
- The structured `.prompt` source is the real maintenance surface.
- The language grows example-first. A feature is not really shipped until it
  lands in `doctrine/` and in the manifest-backed corpus.
- Reuse should happen through named declarations and explicit patching, not
  through hidden merge rules.
- Compiler-owned semantics are better than prose conventions for currentness,
  routing, preservation, and review state.
- Fail loud is the default. Doctrine prefers explicit diagnostics over silent
  fallback.

## Authoring Biases

- Prefer explicit typed declarations over magic strings.
- Prefer stable keys plus authored titles over implicit heading generation.
- Prefer first-class `skill` declarations over ad hoc script prose.
- Prefer small, focused examples that introduce one new idea at a time.
- Keep public docs and examples generic rather than importing product-specific
  jargon from other repos.

## Flow Boundary Design

A flow root owns the namespace for every `.prompt` file under that directory.
Sibling files do not import each other. They use bare names because they
already compile as one merged flow. `import` is only for a real boundary:
another flow root, a runtime package, or a skill package. Cross-flow imports
can only see declarations marked `export`. If sibling files reuse the same
name, Doctrine fails loud instead of guessing which owner you meant.

## Named Table Design

First-class `table` declarations follow Doctrine's normal named-type pattern.
The declaration owns the reusable table contract. The document use site owns
the local key and local rows. This is why the syntax is
`table release_gates: ReleaseGates`, not a generic `ref:` field or a path to a
table hidden inside another document. The compiler lowers named table use back
to the ordinary document table path, so rendering and inheritance stay the
same.

## Readable Block Parity

Every readable block kind has two forms. The named form takes a CNAME key and
a heading string, like `definitions done_when: "Done When"`. The bare form
drops both, like `definitions:`. The named form gives the block an address
and a visible H3 heading with a `_kind · ..._` descriptor. The bare form
renders the body straight into the surrounding section, with no heading and
no descriptor. Authors reach for the named form when another declaration must
point at the block, when metadata like `required`, `advisory`, or `when`
needs to attach, or when the author wants the heading to stand out. They
reach for the bare form when the block is just body prose inside a section.
This parity holds for `definitions`, `callout`, `table`, `footnotes`,
`image`, `bullets`, `sequence`, `checklist`, `code`, `markdown`, and `html`,
so the language does not force an H3 heading on authors who just want the
body.

## String Literals

Single-line strings use `"..."` with standard Python escapes (`\"`, `\\`,
`\n`, `\t`, `\xHH`, `\uHHHH`). Multiline prose uses `"""..."""`. The body of
a triple-quoted string may contain up to two consecutive quotes on its own.
To embed a literal `"""` sequence, escape the first quote as `\"""`. This
keeps docstring-style teaching examples and prompt-within-prompt prose
expressible without a new delimiter. All escape semantics match Python so
authors can reuse what they already know.

## Output Inheritance Design

`output X[Parent]` reuses the same explicit-inherit, explicit-override shape
that `workflow`, `review`, `document`, and IO blocks already use. A child
names every parent entry it keeps with `inherit`, and every change it makes
with `override`. This keeps output composition loud at authoring time and
avoids implicit merge rules. Route fields, attachments, readable blocks, and
trust surfaces all take part in the same composition.

## Splitting Shared Rules From Role-Specific Turn Sequence

A role-home slot like `how_to_take_a_turn:` often mixes two kinds of prose.
One kind is always-on ledger and protocol rules that every concrete role
should keep, such as "keep the ledger current" or "end with one clear
handoff." The other kind is the role-specific turn sequence that one lane
writes differently from the next. When a concrete role overrides the slot,
the shared rules are lost.

The recommended pattern is to split the slot in two named fields on the
abstract role home:

- `shared_rules:` carries the always-on generic rules. Concrete agents
  almost always `inherit` it.
- `how_to_take_a_turn:` carries the role-specific sequence. Concrete
  agents are free to `override` it without losing the shared rules.

This keeps the generic rules in one source of truth and keeps override
cost bounded to the role-specific sequence. See
[../examples/137_role_home_shared_rules_split/](../examples/137_role_home_shared_rules_split/)
for a minimal example.

## Binding Review Outcomes Via `review.on_*.route`

When several critic agents share one output declaration for their review
carrier, each critic's own review routes `on_reject` (and often
`on_accept`) to a different producer. Doctrine's baseline structural
check for the `next_owner:` field wants a literal `{{TargetAgent}}`
interpolation that names the routed agent. On a shared carrier that
constraint forks the prose per critic, which defeats the point of one
shared output.

The `via review.on_<section>.route` clause solves this. Inside a
`next_owner:` field body it says "this field is bound to whichever
agent the named review section resolves for its route." The clause
emits nothing at render time, so the surrounding prose can stay
layer-neutral ("Name the producer when the review routes back for
rework."). One output declaration now cleanly backs any number of
critics whose routes differ.

The shape is a three-part dotted path on purpose. Today the only
supported resolution after the section is `.route`. Future language
moves can add peers like `.current_artifact` without re-parsing the
grammar. `E317` fires when the named section does not match the
branch that resolves the route, or when two `via` clauses appear in
one override body.

See
[../examples/136_review_shared_route_binding/](../examples/136_review_shared_route_binding/)
for a two-critic shared-carrier example.

## Selector + Case Dispatch On Output Shapes

A shared output shape such as a team's JSON turn contract often needs one
body with role-specific lines: the producer reads slightly different field
notes than the critic, and the critic reads slightly different notes than
the composer. Without dispatch, authors either fall back to a
lowest-common-denominator body, or they fork the shape into N near-identical
per-role shapes that drift over time.

The `selector:` block on `output shape` together with `case EnumType.member:`
dispatch inside shape bodies lets one shared shape carry role-specific lines
in place. The shape declares one selector field and its enum, bodies include
`case EnumType.member:` blocks alongside shared prose, and each concrete
agent binds the selector with a `selectors:` field. The compiler resolves
the dispatch at compile time: each agent's emitted shape support only shows
the lines that apply to its bound member, plus the shared prose that lives
outside any case block.

Dispatch happens at compile time on purpose. The agent's selector binding
is author-time intent, not runtime state, so there is no reason for the
runtime to carry conditional branches through the emitted Markdown.
`E318` covers shape-side mistakes: a `case ...:` with no `selector:`, a
`case` placed outside an output shape body, a selector that does not
resolve to a closed enum, a case that selects a member of the wrong enum
(including a same-named enum from a different imported flow), overlapping
cases, or cases that are not exhaustive. `E319` covers agent-side
mistakes: a final_output pointing at a selector-dispatched shape without
the matching `selectors:` binding, the same selector bound twice, a
binding whose key the shape does not declare, or a binding whose enum
identity does not match the selector's resolved enum.

See
[../examples/138_output_shape_case_selector/](../examples/138_output_shape_case_selector/)
for a three-role producer / critic / composer example.

## Skill Package Host Binding Design

`host_contract:` lets a `skill package` declare the typed slots it needs
from its host. `bind:` in the calling agent fills those slots once. Emitted
documents and bundled agents inside the package read their host facts
through `host:` refs. The design keeps package bodies reusable and keeps the
typed link explicit, instead of repeating host IO prose across every inline
skill bridge. `SKILL.contract.json` makes the same link machine-readable for
harnesses that load the package.

## Shipped Boundaries

Doctrine's current shipped surface is proven across the numbered corpus listed
in [../examples/README.md](../examples/README.md).
Keep the exact example boundary there so these design notes stay durable as
the corpus grows.

That shipped surface includes:

- agent and workflow composition
- typed inputs, outputs, skills, schemas, documents, render profiles, and
  enums
- readable refs, addressable paths, and interpolation
- workflow law, `handoff_routing`, `route_only`, and `grounding`
- first-class `review`, `review_family`, and review-driven `final_output`
- structured `final_output:` contracts through `output schema`, plus generated
  schema artifacts for `JsonObject` final answers
- concrete-turn bindings and bound roots for law and review carriers
- `analysis`, `decision`, owner-aware `schema:` / `structure:`, readable
  `document` blocks, first-class named `table` declarations, first-class
  schema artifacts/groups, multiline code blocks, schema-backed review
  contracts, and shared route semantics such as `route_from`
- title-bearing concrete-agent heads plus enum-member key/title/wire identity
  projections
- authored `render_profile`, compact `properties`, explicit readable guard
  shells, profile-sensitive semantic lowering targets, typed `item_schema:` /
  `row_schema:`, and explicit late readable extensions such as raw
  `markdown`, `html`, `footnotes`, `image`, and structured nested table cells
- first-class `skill package` authoring through `SKILL.prompt`

## Current Non-Goals

The language intentionally does not ship:

- a packet primitive
- a shadow trust channel separate from `output` plus `trust_surface`
- implicit merge by omission for inherited structure
- a second capability surface parallel to `skill`
- arbitrary free-prose parsing as semantics
- a generic readable-block `ref:` system
- a second harness plane parallel to the host runtime
- vibe-based or LLM-judged lint in the compiler — see
  [WARNINGS.md](WARNINGS.md) for the scoped first-class warning plan

When a new feature earns its place, the expected path is:

1. Add the language and compiler support in `doctrine/`.
2. Prove it in a focused example with manifest-backed verification.
3. Document it in the live docs set.
