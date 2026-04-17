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
- Use `skill package` when Doctrine should emit `SKILL.md`, explicit `emit:`
  document companions, bundled references, scripts, runtime metadata, plugin
  metadata, or bundled agent companions.
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
- Prompt files inside the package may import each other from that package root
  with absolute imports such as `from refs.query_patterns import
  QueryPatterns`, or with relative imports.
- Package-local import collisions fail loud. Doctrine will not guess between a
  package-local module and a repo-wide prompt module with the same dotted
  path.
- Any bundled file that is not a `.prompt` file copies through under the same
  relative paths, byte for byte.
- Prompt files outside `agents/**/*.prompt` do not copy through as raw files.
  Use `emit:` when those prompt files should turn into bundled `.md` docs.
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

## Emitted Documents

Use `emit:` when the package should emit companion Markdown files from
prompt-authored `document` declarations instead of copying raw `.md` files.

Example:

```prompt
from refs.query_patterns import QueryPatterns
from refs.receipts_template import ReceiptsTemplate

skill package ResearchReviewKit: "Research Review Kit"
    metadata:
        name: "research-review-kit"
        description: "Keep the root short and emit deeper docs from prompt files."
    emit:
        "references/query-patterns.md": QueryPatterns
        "references/receipts-template.md": ReceiptsTemplate
    "Use this skill when you need a short root and deeper reusable docs."
```

With prompt-authored docs:

```text
prompts/
|-- SKILL.prompt
`-- refs/
    |-- query_patterns.prompt
    `-- receipts_template.prompt
```

Doctrine emits:

```text
build/
|-- SKILL.md
`-- references/
    |-- query-patterns.md
    `-- receipts-template.md
```

Important rules:

- `emit:` is optional.
- `emit:` may appear at most once.
- Each `emit:` entry is `"relative/path.md": DocumentRef`.
- Each `emit:` path must stay under the package source root and end in `.md`.
- Each `emit:` ref must point at a `document` declaration.
- `emit:` refs may be local or imported from prompt files anywhere under the
  package source root.
- `emit:` paths may not collide with `SKILL.md`, raw bundled files, or
  compiled bundled-agent markdown.

The two first-party skills in this repo use this pattern end to end as
working exemplars. `skills/agent-linter/prompts/SKILL.prompt` and
`skills/doctrine-learn/prompts/SKILL.prompt` each import many `.prompt`
modules under `prompts/refs/` and emit the whole reference bundle through
one `emit:` block. The checked-in install trees under
`skills/.curated/<name>/references/` are verifier-owned proof; the authored
truth lives in `prompts/refs/*.prompt`.

## Bundled Files

Doctrine currently owns three package output behaviors:

- explicit emitted docs from `emit:`
- ordinary bundled files
- bundled agent prompts
- one package contract sidecar at `SKILL.contract.json` when the package has
  host-binding truth

## Host Binding

Use package host binding when one fat skill package needs typed host facts from
its consuming agent.

The authoring model stays small:

1. Declare `host_contract:` once on the root `skill package`.
2. Point the inline skill at that package with `package:`.
3. Bind those slots once at the consuming skill entry with `bind:`.
4. Use `host:` inside the prompt-authored emitted package tree.

Example package:

```prompt
from refs.query_patterns import QueryPatterns

skill package SectionPipelineSkill: "Section Pipeline Skill"
    metadata:
        name: "section-pipeline-skill"
    emit:
        "references/query-patterns.md": QueryPatterns
    host_contract:
        document section_map: "Section Map"
        final_output final_response: "Final Response"
    "Read {{host:section_map.title}}."
    "Emit through {{host:final_response}}."
```

Example inline bridge and bind:

```prompt
skill SectionPipeline: "Section Pipeline"
    purpose: "Run the section pipeline."
    package: "section-pipeline-skill"

agent SectionArchitect:
    role: "Use the shared package."
    outputs: "Outputs"
        FinalResponse
    final_output: FinalResponse
    skills: "Skills"
        skill section_pipeline: SectionPipeline
            bind:
                section_map: SectionMap
                final_response: final_output
```

Important rules:

- `host_contract:` is optional, but once a package declares slots, every slot
  must be bound exactly once by each consuming skill entry.
- The root `SKILL.prompt` body uses `{{host:slot}}` interpolation.
- Emitted docs and bundled agent prompts use the same `host:` root anywhere
  that artifact kind already accepts normal addressable refs.
- `package:`, `host_contract:`, and `bind:` do not render into Markdown.
- When the package has host-binding truth, `SKILL.contract.json` records the
  host contract and the host paths used by prompt-authored emitted artifacts.
- Package ids come from `metadata.name` when it is present. Otherwise Doctrine
  falls back to the `skill package` declaration key.
- Doctrine first checks visible package ids, then other `SKILL.prompt`
  entrypoints under the active prompt roots. Ambiguous package ids fail loud.
- Supported host-slot families are:
  - `input`
  - `output`
  - `document`
  - `analysis`
  - `schema`
  - `table`
  - `final_output`
- Bind targets may use:
  - `inputs:key`
  - `outputs:key`
  - `analysis`
  - `final_output`
  - ordinary declaration refs such as `SectionMap`
  - addressable child paths on those same roots

This is the clean thin-harness pattern:

- the package keeps the reusable method
- the agent keeps one small typed bind map
- Doctrine owns the link
- emitted Markdown stays flat

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
Use `emit:` instead when the companion file should be authored as a Doctrine
`document` in prompt files.

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
- use `emit:` for other prompt-authored companion docs
- other descendant prompt-bearing subtrees stay compiler-owned, and their
  `.prompt` files are not copied through as ordinary files

## Fail-Loud Boundaries

The package emitter rejects ambiguous or dangerous filesystem states instead of
guessing.

Important fail-loud cases:

- `emit:` paths must end in `.md`
- `emit:` paths must stay under the package source root
- `emit:` refs must point at `document` declarations
- authored bundled files may not collide with emitted `SKILL.md`
- authored bundled files may not collide with emitted `emit:` document paths
- authored bundled files may not collide with compiled bundled agent markdown
  paths such as `agents/reviewer.md`
- path case-collisions fail loudly
- bundled paths must stay relative to the package source root
- bundled paths must use `/` separators
- bundled files preserve their bytes exactly

Examples `102_skill_package_path_case_preservation`,
`122_skill_package_emit_documents`, and
`123_skill_package_emit_documents_mixed_bundle` prove the exact-path,
collision, and explicit-emitted-doc boundaries.

## Example Gallery

The canonical package authoring ladder starts at `95`.

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
- `122_skill_package_emit_documents`: prompt-authored `document` declarations
  emitted as many separate bundled `.md` docs from one `emit:` block
- `123_skill_package_emit_documents_mixed_bundle`: emitted docs, bundled agent
  markdown, runtime metadata, and raw helper files in one package tree

This gallery is generic on purpose, but it is shaped to match the real skill
families Doctrine needs to author in practice: markdown-only skills,
reference-heavy skills, script-backed helpers, runtime metadata packages,
plugin bundles, delegating companion-agent packages, larger compendia, and
path-sensitive bundles, explicit emitted-doc packages, and binary assets.

## First-Party Reference Packages

Doctrine ships two real first-party skill packages under `skills/`:

- `skills/agent-linter/` — the audit counterpart. See
  [AGENT_LINTER.md](AGENT_LINTER.md) for install, usage, and structured
  output proof.
- `skills/doctrine-learn/` — the teaching counterpart. See
  [DOCTRINE_LEARN.md](DOCTRINE_LEARN.md) for install, the reference map, and
  how the skill routes to the right depth for each authoring surface.

Both are good references when you need a larger package that still stays lean.
Use a source checkout for these reference packages. The published Python
package does not ship the repo-owned prompt trees or named emit targets.

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

If you changed bundled Markdown inside a skill package, parse every fenced
Doctrine example through the shipped parser:

```bash
make verify-skill-examples
```

### Fenced Example Convention

Bundled skill Markdown files are pass-through content — the compiler copies
them byte for byte. Readers still expect the Doctrine examples inside to be
correct. Two fence tags make the contract explicit:

- ```prompt` — the block is a complete prompt file. `make verify-skill-examples`
  parses it and fails loud on drift.
- ```prompt-fragment` — the block is a partial teaching snippet (one
  declaration, one clause, or a comparison pair) and must not stand alone.
  The verifier skips it.

Prefer a complete `prompt` block when it is short enough. Reach for
`prompt-fragment` only when the fragment is genuinely illustrative and a
full prompt would dilute the lesson.

`build_ref/` remains the checked-in expected emitted tree for corpus
verification. It is not an authoring requirement and should not shape package
layout decisions.

## Design Notes

These rules exist to keep the `skill package` surface thin and typed.

- `emit:` is an explicit map, never auto-discovery. The compiler refuses to
  guess which prompt files should emit companion docs. That keeps the package
  tree predictable across repos.
- `host_contract:` and `bind:` are bind-by-reference, not expansion. The
  binding data lives in `SKILL.contract.json`, not in the emitted Markdown,
  so fat skills can reach parent typed surfaces without adding always-on
  Markdown bulk.
- Host slots are typed. Missing, wrong-type, or over-broad binds fail loud
  instead of silently drifting.
- Raw file bundling stays byte-exact. The package source root is the truth;
  Doctrine does not re-serialize bundled peers.

These choices match the thin-harness, fat-skills stance in
[THIN_HARNESS_FAT_SKILLS.md](THIN_HARNESS_FAT_SKILLS.md) and the
context-budget rules in [../PRINCIPLES.md](../PRINCIPLES.md).

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
