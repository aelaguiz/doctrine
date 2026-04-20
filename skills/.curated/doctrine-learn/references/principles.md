# Principles

This file is the first thing the `doctrine-learn` skill loads. It teaches the nine principles that ground every other reference in this package. Every recommendation in later references descends from one of these rules. If a choice in Doctrine feels hard, the answer is usually in here.

The principles come from `PRINCIPLES.md` and from the durable read of "thin harness, fat skills" in `docs/THIN_HARNESS_FAT_SKILLS.md`. For the product story behind them, see `docs/WHY_DOCTRINE.md`.

## The Core Split

Doctrine sits on the authoring side of the line. The harness runs the loop, tools, files, memory, scheduling, and safety. Doctrine's job is to help that thin runtime load the right context at the right time. If a rule is really about runtime state, it belongs in the harness, not in authored doctrine.

## The Ten Principles

### 1. Context Is A Budget

Every always-on line costs prompt budget on every turn. Treat the agent home like a small header, not a dump. Put only the rules a role needs on most turns at the top, and push deeper procedure behind reusable boundaries the harness can load when the task calls for it.

In Doctrine code, this shows up as thin concrete `agent` bodies that mostly point at shared `workflow`, `review`, or skill declarations. See `examples/12_role_home_composition` for a role home that stays small by composing shared pieces.

One move to make: when you are about to paste a third paragraph into an agent home, stop and promote that prose into a named `workflow` or `document` that the agent can reference instead.

### 2. Load Depth On Demand

Start with a thin role home. Keep richer process, examples, and reference material in modules a runtime can load when it needs them. Prefer compact docs indexes over giant copied reference sections in every agent.

In Doctrine code this is the whole point of `skill`, `skill package`, `workflow`, `review`, and `document` as named declarations. The concrete agent names what it needs. The depth lives elsewhere. See `examples/11_skills_and_tools` for skills attached by reference, and `examples/95_skill_package_minimal` for a package that lives outside the agent home.

One move to make: if two agents quote the same block of prose, move that block into a named declaration and have both agents reference it.

### 3. Write For Resolvers

Give every module a sharp name, a short description, and a clear "when to load." Vague labels like `helper`, `core`, or `misc` make resolvers guess. The resolver is a reader, not a mind reader.

In Doctrine, this shows up in `skill package` metadata and in `when_to_use` / `when_not_to_use` fields. Titles on `workflow`, `review`, `document`, and `skill` declarations are the human-facing heading, not decoration. Keys are the compiler identity. See `examples/95_skill_package_minimal` for shipped metadata shape.

One move to make: read every title and description out loud. If you cannot tell when the module should load, rewrite the title.

### 4. Keep The Harness Boundary Clean

Doctrine should not own runtime state, memory, scheduling, adapter logic, tool orchestration, or session control. If a rule is really about run state or tool execution, it belongs in the harness. Doctrine should help the harness, not imitate it.

In Doctrine code this shows up as the hard stop on features that would become a "second harness." See `examples/118_output_target_delivery_skill_binding` for the right shape: delivery behavior lives on the `output target`, not in every agent home. The `route field` surface in `examples/120_route_field_final_output_contract` is another clean boundary: Doctrine owns the typed route contract, and the harness consumes `final_output.contract.json` for the actual handoff.

One move to make: when an author tries to push "when the tool returns this, do that" into a `workflow`, ask whether the rule is really a harness policy. If yes, name the harness owner and leave it out of Doctrine.

### 5. Put Deterministic Truth In Typed Surfaces

If the truth must be exact, use a typed surface. That means `input`, `output`, `output schema`, `schema`, `route field`, `review`, and `table`. Do not hide exact rules in long prose. Do not make a downstream owner infer machine-trustable facts from narrative text.

In Doctrine this is why `output schema` exists at all. See `examples/79_final_output_output_schema` for a structured JSON final answer, and `examples/116_first_class_named_tables` for a typed table contract that many documents can reuse.

One move to make: every time you write "remember to include X" in prose, ask if X is really a field on a schema. If yes, move it.

### 6. Reserve Prose For Judgment

Typed surfaces own exact truth. Prose owns reading, synthesis, comparison, and taste. Keep judgment prose readable and modular. Do not flatten rich judgment into rigid boilerplate just because it matters.

In Doctrine this is the right use of `analysis`, `decision`, `review` outcome sections, and `document` bodies. See `examples/54_analysis_attachment` for an analysis that guides reasoning without pretending to be a schema.

One move to make: if a field is really "describe the trade-off," keep it as prose. If it is really "pick one of three values," make it an enum. Do not split the difference.

### 7. Reuse Beats Repetition

If the same doctrine appears in more than one place, give it one shared home. Favor inheritance, composition, and reusable packages over copy-paste. One fix should land once.

In Doctrine this is what `abstract agent`, `inherit`, `override`, and shared `workflow`, `review`, `document`, and `skill package` declarations are for. See `examples/04_inheritance` for the basic shape and `examples/37_law_reuse_and_patching` for a deeper patching pattern.

One move to make: when you are about to duplicate a section across two agents, stop and either pull it into a shared declaration or inherit from a common `abstract agent`.

### 8. Repeated Work Should Become Reusable Doctrine

If authors keep solving the same instruction problem by hand, the language should make the reusable shape easier to express. The goal is not one-off prompt craft. The goal is durable authoring leverage.

In Doctrine this shows up as first-class declarations for patterns that used to live in ad hoc prose. `review_family` in `examples/68_review_family_shared_scaffold` is a good example: shared review scaffolds became a typed surface instead of a copied template. `skill package` in `examples/95_skill_package_minimal` did the same for reusable capability.

One move to make: when you notice the third copy of the same hand-rolled pattern, file it as a reuse signal even if you do not add the feature today. Do not keep pasting.

### 9. Make Bloat Visible

Silent prompt sprawl is drift. Doctrine should move toward warnings, docs, and patterns that expose oversized agent homes, copied prose, weak descriptions, and bad boundaries.

In Doctrine this is why the compiler fails loud, why the shipped `agent-linter` skill exists alongside `doctrine-learn`, and why examples stay small. See `examples/112_output_inheritance_fail_loud` for fail-loud output inheritance.

One move to make: when an agent home grows past a page, treat that as a bug and open a review, not a refactor ticket for "later."

### 10. Plain Human Speech

Shipped agent prose and shipped skill prose must read like plain speech at about a 7th grade level. Short sentences. Direct verbs. Common words. Keep the Doctrine terms that carry exact meaning and simplify everything around them.

This is a hard rule, not a style note. Role bodies that read like state-transition code burn prompt budget on every turn and hide the real instruction from the runtime. Machine-language prose is a readability failure and a fail-loud target for `agent-linter` finding `AL740`.

Five concrete triggers to avoid in role prose:
- Sentences longer than about 40 words.
- Nested parentheticals (a clause inside a clause inside a clause).
- Inline `(a)`/`(b)`/`(c)` enumerations embedded in a sentence instead of a bullet list.
- Dense jargon-per-sentence that forces the reader to decode every clause.
- Code-like phrasing that reads as state-transition code rather than human instruction.

Bad: `The LensWarden, when invoked (typically after the section planner (which itself runs after the track planner)), must install each rule (a) by calling lens CLI rules add, (b) verifying the sha256, then (c) emitting the review verdict.`

Good: `LensWarden installs each rule through the lens skill. The skill owns the CLI call and the sha256 check. Emit the review verdict once the install finishes.`

One move to make: read every new sentence out loud. If you cannot say it in one breath at a normal pace, split it.

## Do / Do Not Cheat Sheet

Do:

- Keep agent homes thin. Put depth behind named declarations.
- Use typed surfaces (`output schema`, `route field`, `schema`, `table`) for exact truth.
- Write titles and descriptions that say when to load the module.
- Share one doctrine home and patch it in place with `inherit` and `override`.
- Ship each new feature with a small focused example.
- Fail loud when the source is inconsistent.
- Write role and skill prose at a 7th grade reading level in plain human speech.

Do not:

- Dump whole systems into root context.
- Copy large reference blocks into many agents.
- Put harness behavior (memory, scheduling, tool control) into authored doctrine.
- Use prose when typed truth is needed.
- Grow features that make Doctrine act like the runtime.
- Invent unshipped constructs. If it is not in `doctrine/grammars/doctrine.lark`, it does not exist yet.
- Write role prose as state-transition code, nested parentheticals, or inline `(a)`/`(b)`/`(c)` enumerations.

**Load when:** the author starts any new Doctrine task, is unsure which construct fits, or is about to push runtime behavior into authored doctrine.
