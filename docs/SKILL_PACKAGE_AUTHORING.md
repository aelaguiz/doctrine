# Skill Package Authoring

Doctrine ships two related skill surfaces:

- inline `skill` and `skills` for reusable capability semantics inside agent
  doctrine
- `skill package` in `SKILL.prompt` when Doctrine should author and emit a real
  package tree

This guide covers the second surface.
If you first need to decide between inline `skill` / `skills` and a real
`skill package`, use [AUTHORING_PATTERNS.md](AUTHORING_PATTERNS.md).

Doctrine also ships runtime packages under `AGENTS.prompt`. They are a
different public surface. Runtime packages emit `AGENTS.md`, optional
same-name `SOUL.md`, and peer files for real runtime homes. Skill packages
emit `SKILL.md` plus bundled package files for reusable capabilities. Do not
use `SKILL.prompt` to model a runtime home, and do not use runtime packages as
a substitute for `SKILL.md`.

## When To Use Which

- Use inline `skill` and `skills` when the capability only needs to exist
  inside `AGENTS.prompt` or `SOUL.prompt` as reusable runtime doctrine.
- Use a runtime package under `AGENTS.prompt` when you need an emitted runtime
  home, not a `SKILL.md` bundle.
- Use `skill package` when Doctrine should emit `SKILL.md` plus bundled
  references, scripts, runtime metadata, plugin metadata, or bundled agent
  companions.
- Keep the two surfaces additive. First-class package authoring does not
  replace the shipped inline `skill` and `skills` model.

## Quick Start

Start with `SKILL.prompt`:

```prompt
skill package GreetingSkill: "Greeting Skill"
    metadata:
        name: "greeting-skill"
        description: "Write short, friendly greetings that sound human."
        version: "1.0.0"
        license: "MIT"
    "Write short, friendly greetings that fit the current conversation."
    when_to_use: "When to use"
        "You need a quick greeting or sign-off."
        "Match the user's tone before drafting."
    workflow: "Workflow"
        "Read the latest message first."
        "Draft one greeting and one sign-off."
        "Keep both short and natural."
```

Register a normal emit target in `pyproject.toml`:

```toml
[[tool.doctrine.emit.targets]]
name = "example_95_skill_package_minimal"
entrypoint = "examples/95_skill_package_minimal/prompts/SKILL.prompt"
output_dir = "examples/95_skill_package_minimal/build"
```

Emit the package:

```bash
uv run --locked python -m doctrine.emit_skill --target example_95_skill_package_minimal
```

The emitted tree is:

```text
build/
`-- SKILL.md
```

`SKILL.md` starts with YAML frontmatter from `metadata:` and then renders the
package body as ordinary Doctrine-authored Markdown.

## Source-Root Model

The package source root is the directory that contains `SKILL.prompt`.

Doctrine treats that directory as the package tree it owns:

- `SKILL.prompt` compiles to `SKILL.md`.
- Any bundled file that is not a `.prompt` file copies through under the same
  relative paths, byte for byte.
- Relative Markdown links should therefore be authored against the source tree
  you keep beside `SKILL.prompt`.
- `build_ref/` is not part of this model. It is verifier-owned checked-in proof
  only.

Example source tree:

```text
prompts/
|-- SKILL.prompt
|-- references/
|   `-- checklist.md
`-- scripts/
    `-- greet.py
```

Emitted tree:

```text
build/
|-- SKILL.md
|-- references/
|   `-- checklist.md
`-- scripts/
    `-- greet.py
```

This is why examples such as
`96_skill_package_references`,
`97_skill_package_scripts`, and
`102_skill_package_path_case_preservation`
are authored as ordinary source-root bundles instead of compiler-owned special
file-family declarations.

## Metadata

`metadata:` currently accepts these scalar fields:

- `name`
- `description`
- `version`
- `license`

Important rules:

- `metadata:` may appear at most once.
- Unknown metadata fields fail loudly.
- Duplicate metadata fields fail loudly.
- If `name` is omitted, emitted frontmatter falls back to the package
  declaration key.

## Bundled Files

Doctrine currently owns two bundled-file behaviors.

### Ordinary bundled files

Any bundled file under the package source root that is not a `.prompt` file
copies through under the same relative path, byte for byte.

Examples:

- `references/checklist.md`
- `reference/REFERENCE.md`
- `scripts/greet.py`
- `scripts/greet.ts`
- `assets/icon.png`
- `agents/openai.yaml`
- `.codex-plugin/plugin.json`
- `.app.json`

This is the public authoring surface. Doctrine does not require privileged
compiler declarations for `references/`, `scripts/`, `assets/`, runtime
metadata roots, or plugin metadata roots.

### Bundled agent prompts

Prompt modules under `agents/**/*.prompt` compile to markdown companions rather
than copying through as raw `.prompt` files.

Example:

```prompt
import agents.cold_reviewer
import agents.escalation_router

skill package BundledAgentsPackage: "Bundled Agents Package"
    metadata:
        name: "bundled-agents-package"
        description: "Ship bundled agent prompts beside the main skill package."
        version: "1.0.0"
        license: "MIT"
    "Delegate cold review work to bundled markdown agents and runtime metadata under `agents/`."
```

With source files:

```text
prompts/
|-- SKILL.prompt
`-- agents/
    |-- cold_reviewer.prompt
    |-- openai.yaml
    `-- escalation_router.prompt
```

Doctrine emits:

```text
build/
|-- SKILL.md
`-- agents/
    |-- cold_reviewer.md
    |-- openai.yaml
    `-- escalation_router.md
```

Important rules:

- bundled agent prompts must live under `agents/`
- each bundled agent prompt must define exactly one concrete agent
- other files in the same `agents/` tree still bundle normally
- other descendant prompt-bearing subtrees stay compiler-owned, and their
  `.prompt` files are not copied through as ordinary files

## Fail-Loud Boundaries

The package emitter rejects ambiguous or dangerous filesystem states instead of
guessing.

Important fail-loud cases:

- authored bundled files may not collide with emitted `SKILL.md`
- authored bundled files may not collide with compiled bundled agent markdown
  paths such as `agents/reviewer.md`
- path case-collisions fail loudly
- bundled paths must stay relative to the package source root
- bundled paths must use `/` separators
- bundled files preserve their bytes exactly

Example `102_skill_package_path_case_preservation` proves the exact-path and
case-preservation boundary, including a negative collision case.

## Example Gallery

The canonical package authoring ladder is `95` through `103`.

- `95_skill_package_minimal`: smallest `SKILL.prompt` plus `skill package`
  surface
- `96_skill_package_references`: ordinary bundled reference documents beside
  `SKILL.prompt`
- `97_skill_package_scripts`: ordinary bundled script files beside
  `SKILL.prompt`
- `98_skill_package_runtime_metadata`: runtime metadata roots such as
  `agents/openai.yaml`
- `99_skill_package_plugin_metadata`: plugin-style split metadata roots such as
  `.codex-plugin/plugin.json`, `.app.json`, and `agents/openai.yaml`
- `100_skill_package_bundled_agents`: bundled `agents/**/*.prompt` modules that
  emit markdown companions while normal files in the same tree still bundle
- `101_skill_package_compendium`: larger source-root compendium and reference
  tree preservation
- `102_skill_package_path_case_preservation`: exact path and case preservation
  plus negative collision proof
- `103_skill_package_binary_assets`: bundled binary assets such as `assets/*.png`
  preserved byte for byte

This gallery is generic on purpose, but it is shaped to match the real skill
families Doctrine needs to author in practice: markdown-only skills,
reference-heavy skills, script-backed helpers, runtime metadata packages,
plugin bundles, delegating companion-agent packages, larger compendia, and
path-sensitive bundles, including binary assets.

## First-Party Reference Package

Doctrine also ships one real first-party skill package under
`skills/agent-linter/`.
It is a good reference when you need a larger package that still stays lean.
Use a source checkout for this reference package. The published Python package
does not ship the repo-owned prompt tree or named emit target.

It shows this package shape:

- `SKILL.prompt` owns the trigger contract and core workflow
- `references/` own the deeper doctrine
- `schemas/` own the machine-readable report contract
- `agents/openai.yaml` owns runtime metadata

It is also intentionally script-free.
The bundle keeps judgment in the skill and uses scripts only where
deterministic value is clearly earned.

Emit it with:

```bash
uv run --locked python -m doctrine.emit_skill --target doctrine_agent_linter_skill
```

## Verification

For one package example:

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/95_skill_package_minimal/cases.toml
```

For the full shipped corpus:

```bash
make verify-examples
```

If you changed emit diagnostics:

```bash
make verify-diagnostics
```

`build_ref/` remains the checked-in expected emitted tree for corpus
verification. It is not an authoring requirement and should not shape package
layout decisions.

## Relationship To Inline Skills

Inline `skill` and `skills` still cover reusable capability semantics inside
agent doctrine.

Use inline skills when:

- the capability is only consumed inside `AGENTS.prompt` or `SOUL.prompt`
- no standalone skill-package tree needs to be emitted

Use `skill package` when:

- the package itself is the product Doctrine should author
- the emitted tree must preserve bundled companion files and paths
- you want one Doctrine source of truth for `SKILL.md` and its companions

The two surfaces compose, but they solve different ownership problems.
