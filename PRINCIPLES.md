# Principles

This file distills the "thin harness, fat skills" lesson as it applies to
Doctrine.
For the longer evergreen guide, see
[docs/THIN_HARNESS_FAT_SKILLS.md](docs/THIN_HARNESS_FAT_SKILLS.md).

Doctrine helps people author agent systems that stay small, loadable, and
clear. Doctrine is not the harness. Its job is to help authors give a thin
runtime the right context at the right time without filling every turn with
noise.

## Doctrine's Job

- Help authors keep always-on context small.
- Help authors split summary from depth.
- Help authors make shared doctrine easy to reuse and patch.
- Help authors keep exact truth in typed surfaces.
- Help authors keep harness concerns out of authored doctrine.

## Core Principles

### Context Is A Budget

- Treat every always-on line as expensive.
- Put only the rules a role needs on most turns in the agent home.
- Move deep reference material behind reusable boundaries and point to it.

### Load Depth On Demand

- Start with a thin role home.
- Keep richer process, examples, and reference material in modules a runtime
  can load when the task calls for them.
- Prefer compact docs indexes over giant copied reference sections.

### Write For Resolvers

- Name modules clearly.
- Write short descriptions that say what a module is for, when it should load,
  and what problem it helps solve.
- Avoid vague labels such as `helper`, `core`, or `misc`.

### Keep The Harness Boundary Clean

- Doctrine should not own runtime state, memory, scheduling, adapter logic,
  tool orchestration, or session control.
- If a rule is really about run state or tool execution, it belongs in the
  harness, not in emitted doctrine.
- Doctrine should help the harness, not imitate it.

### Put Deterministic Truth In Typed Surfaces

- Use typed inputs, outputs, schemas, routes, reviews, and contracts when the
  truth must be exact.
- Do not hide exact rules in long prose.
- Do not make downstream owners infer machine-trustable facts from narrative
  text.

### Reserve Prose For Judgment

- Use prose for the parts that need reading, synthesis, comparison, and taste.
- Keep that prose readable and modular.
- Do not flatten rich judgment into rigid boilerplate just because it matters.

### Reuse Beats Repetition

- If the same doctrine appears in more than one place, give it one shared
  home.
- Favor inheritance, composition, and reusable packages over copy-paste.
- One fix should land once.

### Repeated Work Should Become Reusable Doctrine

- If authors keep solving the same instruction problem, Doctrine should make
  the reusable shape easier to express.
- The goal is not one-off prompt craft. The goal is durable authoring leverage.

### Make Bloat Visible

- Doctrine should move toward warnings, docs, and patterns that expose
  oversized agent homes, copied prose, weak descriptions, and bad boundaries.
- Silent prompt sprawl is drift.

## What This Means For Doctrine

- Favor features that shrink always-on context.
- Favor features that create clean load boundaries.
- Favor metadata and descriptions that make resolver-style loading easier.
- Favor typed surfaces for exact truth.
- Favor reusable declarations over copied prose.
- Reject features that turn Doctrine into a second harness.

## Do

- Keep agent homes thin.
- Use docs indexes to point at deeper truth.
- Write sharp names and descriptions.
- Separate exact contracts from judgment prose.
- Share doctrine once and patch it in place.

## Do Not

- Dump whole systems into root context.
- Copy large reference blocks into many agents.
- Put harness behavior into authored doctrine.
- Use prose where typed truth is needed.
- Grow features that make Doctrine act like the runtime.
