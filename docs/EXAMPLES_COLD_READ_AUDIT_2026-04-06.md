# Examples Cold Read Audit

Scope:
- Reviewed `examples/01_hello_world` through `examples/07_handoffs`
- Excluded `examples/99_not_clean_but_useful`
- Read both the source-side `prompts/*.prompt` files and the checked-in `ref` outputs
- Used a cold-read lens: "What would a first-time reader infer from the examples alone?"

## Summary

The sequence is directionally good: `01` through `06` mostly build from simple authored output to reuse, inheritance, and nested workflow composition. The main friction is not the syntax itself. The friction is that several rules about output shape, identity, and inheritance are only inferable after comparing multiple examples and their refs.

The biggest cold-read issues are:
- there is no short index explaining how to read `prompts` versus `ref`
- the rendered output shape changes in `07` without a teaching example that names the rule
- import identity and case rules are underspecified in `03`
- inheritance is explained well for workflow entries, but not for workflow preambles or agent-level named slots
- `07` looks partly exploratory rather than fully canonical

## Cross-Example Findings

### 1. There is no examples index that explains the contract

A new reader has to infer all of this:
- `prompts/*.prompt` is the authored source language
- `ref/**/*.md` is the rendered output contract
- some examples produce one output
- some produce many outputs
- error examples produce `COMPILER_ERROR.md` instead of `AGENTS.md`

That is all learnable, but it is not stated locally in `examples/`.

Why this matters:
- `01` looks like "one source file, one output file"
- `04` and later look like "one source file, many concrete rendered outputs"
- `05` adds "one source file can also produce a compiler error artifact"

Suggested fix:
- add a short `examples/README.md` that explains the source/ref contract in 6-10 lines

### 2. The output-opening rule changes without being taught explicitly

In `01` through `06`, the rendered document opens with the role text as ordinary prose. In `07`, the rendered document suddenly opens with an H1 agent name such as `# Project Lead`, and the role becomes the paragraph beneath it.

A cold reader cannot tell:
- what source pattern causes the agent name to render
- whether `07` is using a new rendering mode
- whether earlier examples omitted agent titles on purpose

Why this matters:
- this is not a minor formatting detail; it changes the visible document contract
- it also changes the mental model of what an `agent` renders into

Suggested fix:
- either add a dedicated example that introduces agent-name rendering explicitly
- or keep `07` on the same output shape as `01` through `06` until the rule is settled

### 3. Identity rules are still fuzzy across file name, declaration name, key, and rendered title

The language appears to have at least four different identities:
- file or module name, for example `greeting.prompt`
- declaration name, for example `workflow Greeting`
- internal key, for example `main_point`
- rendered title, for example `"Main Point"`

The examples imply these are intentionally different, but the reader has to reverse-engineer that.

The clearest friction point is `03_imports`:
- the import lines are lowercase: `import greeting`, `import object`
- the declarations are uppercase: `workflow Greeting`, `workflow Object`
- the references inside the agent are uppercase: `Greeting`, `Object`

Open questions a cold reader will reasonably have:
- does `import greeting` import a file, a module namespace, or a declaration named `greeting`?
- is the language case-sensitive for imported symbols?
- is `Greeting` resolved from the file name or from the declaration name?

Suggested fix:
- add one comment in `03_imports` that states the resolution model directly

### 4. Inheritance rules are clear for workflow entries, but much less clear for everything else

`05_workflow_merge` does a good job teaching explicit ordered patching for inherited workflow entries:
- `inherit key`
- `override key:`
- `override key: "New Title"`
- `key: "Title"`

What stays less clear from the examples alone:
- what happens to parent workflow preamble strings when the child provides its own preamble
- what happens to parent workflow title strings when the child provides a new workflow title
- whether explicit exhaustive accounting applies only inside `workflow` bodies or also to other named slots

`04_inheritance` already hints at this ambiguity:
- the parent workflow has a preamble string
- the child workflow changes the title and omits the parent's preamble
- the ref shows the parent preamble disappeared
- the example never names that rule

`07_handoffs` makes the ambiguity larger by introducing top-level slots such as `read_first`, `workflow_core`, and `your_job`, plus agent-level `inherit read_first`, without a focused explanation of how those slots inherit or override.

Suggested fix:
- add one compact note in `04` or `05` that scalar fields override, and workflow preambles override as a group
- if `07` keeps agent-level keyed slots, give them their own focused teaching example

### 5. `06` and `07` mix stable teaching material with visibly open design questions

Two examples explicitly signal uncertainty:
- `06_nested_workflows` says the outer composition surface may later need stable local keys
- `07_handoffs` opens with "Best-guess syntax sketch"

That may be fine in design notes. It is less fine in a canonical numbered example sequence, because a first-time reader cannot tell which parts are settled and which are still exploratory.

Suggested fix:
- label exploratory examples clearly, or move them into a separate `explorations/` area
- keep `examples/01` through `N` as the stable teaching sequence

### 6. Some example names push the wrong mental model

`05_workflow_merge` is the strongest example in the set, but its directory name is misleading. The comments inside the example explicitly say there is no implicit merge or append behavior. What the example actually demonstrates is explicit ordered patching.

Why this matters:
- "merge" invites the exact model the example is arguing against

Suggested fix:
- rename `05_workflow_merge` to something closer to `05_explicit_workflow_patch` or `05_inherited_workflow_order`

### 7. Error coverage feels thinner than the surrounding language notes imply

The checked-in examples currently show a concrete example for `E001` only. The repo docs also describe at least:
- `E002` missing rendered section title
- `E003` missing inherited workflow entry

From a cold-read perspective, that leaves a gap:
- the language claims these validation rules matter
- the examples do not yet teach what those failures look like in practice

Suggested fix:
- add one minimal error example for either `E002` or `E003`

## Example-By-Example Notes

### 01 Hello World

What is unclear:
- the prompt file defines two agents, `HelloWorld` and `HelloWorld2`
- the checked-in ref only shows one rendered `AGENTS.md`
- the example never says which agent the ref corresponds to or why the second one has no sibling ref

There is also a wording issue in the first comment:
- "When there is no body beneath the key: heading it renders as plain text"

That sentence is hard to parse on first read. The idea seems to be important, but the phrasing makes the reader stop too early.

Suggested fix:
- either split this into two separate examples or add refs for both agents
- rewrite the comment in plain language, for example: "A scalar `role` string renders as opening prose; a nested `role` block renders as a titled section."

### 02 Sections

This example is mostly clear. The only missing piece is that it would be a good place to reinforce a core rule:
- the visible headings come from authored strings like `"Steps"` and `"Step One"`
- keys like `step_one` are internal identities, not rendered text

Right now that rule is inferable, but not stated here.

### 03 Imports

This is the first example where the reader needs a symbol-resolution model, but the example does not provide one.

Main friction:
- lowercase import target
- uppercase declaration names
- uppercase references inside the agent

The example works as a concept demo, but a cold reader does not know whether the important identity is the file name, the declaration name, or both.

Suggested fix:
- add one comment that explicitly says what `import greeting` means and how `Greeting` is resolved

### 04 Inheritance

This is the first real inheritance example, and it largely works. The main missing explanation is about workflow-level preambles and titles.

What the reader sees:
- `BaseGreeter` has workflow title `"Shared Instructions"` and a preamble string
- `HelloWorldGreeter` defines a new workflow title `"Hello World Instructions"`
- the rendered ref contains only the child's title and none of the base preamble text

That is a real semantic rule, but the example leaves the reader to infer it from output comparison.

Suggested fix:
- add one comment that says child workflow preamble/title override the parent workflow preamble/title, while inherited keyed entries must still be accounted for explicitly

### 05 Workflow Merge

This is the clearest example in the set. The comments do the most teaching work here, and the error ref is useful.

The two remaining issues are:
- the word "merge" in the directory name conflicts with the actual semantics
- the sequence still does not show what an omission error looks like, only an invalid override error

Suggested fix:
- keep the content, but consider renaming the example and eventually add an omission-based failure sibling

### 06 Nested Workflows

This example teaches an important distinction:
- small local inline workflows are still allowed
- nested, reusable, or inherited structure should move into named top-level workflows

What is still dense on a cold read:
- bare workflow references such as `Preparation` and `Delivery` are doing a lot of semantic work
- the example relies heavily on comments to distinguish local composition from inheritance
- the comments also hint that the outer composition surface may need a different long-term treatment

The underlying idea seems right, but the reader has to process a lot of explanation to understand why this is not just another inheritance example.

Suggested fix:
- add one short plain statement near `Preparation` and `Delivery`: "Referencing a named workflow inside another workflow nests its rendered section here."

### 07 Handoffs

This is the largest conceptual jump in the sequence. It introduces all of the following at once:
- a new `route "..." -> AgentName` syntax
- top-level named slots on agents, not just `role` plus `workflow`
- agent-level `inherit read_first`
- direct reassignment of inherited slots such as `read_first: ProjectLeadReadFirst`
- a new rendered output shape with agent name as H1
- multi-agent package structure as the normal presentation

Any one of those could carry an example by itself. Introducing all of them together makes the example feel more like a design sketch than a teaching example.

Two especially unclear points:
- why top-level slot override is direct assignment here, while workflow entry override uses explicit `override`
- why `ProjectLeadReadFirst` is duplicated rather than shown as a small inherited variation of `ReadFirst`

Suggested fix:
- split `07` into at least two examples:
  - one for agent-level named sections and their inheritance/override rules
  - one for `route` syntax and handoff rendering

## Suggested Cleanup Order

1. Add `examples/README.md` explaining source files, refs, multi-output examples, and compiler-error refs.
2. Fix `01` so the source/ref relationship is unambiguous.
3. Tighten `03` with one explicit note about import resolution and symbol identity.
4. Add one sentence in `04` or `05` that explains workflow preamble/title override behavior.
5. Rename or reframe `05_workflow_merge` so the name matches the semantics.
6. Either split `07` or label it explicitly as exploratory.
7. Add one minimal example for `E002` or `E003`.

## Bottom Line

The examples are already strong enough to communicate the broad direction of the language. The main cold-read weakness is that the reader has to infer too many renderer and inheritance rules indirectly from file layout and output comparison. A small amount of framing and one or two narrower examples would make the sequence much easier to trust.
