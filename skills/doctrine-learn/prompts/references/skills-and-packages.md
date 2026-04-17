# Skills And Packages

This reference teaches the two skill surfaces that ship: inline `skill` declarations and first-class `skill package` entrypoints. Reach for these when an agent needs reusable capability that lives outside its role prose.

Use an inline `skill` for a capability that stays inside one `AGENTS.prompt` or `SOUL.prompt`. Use a `skill package` when Doctrine should emit a real package tree with `SKILL.md`, bundled references, scripts, runtime metadata, plugin metadata, or bundled agents.

Doctrine also ships a separate runtime package surface under `AGENTS.prompt`. That emits `AGENTS.md`, not `SKILL.md`. Do not mix the two. See `references/imports-and-refs.md` for runtime packages.

## Inline Skill Vs Skill Package

- Inline `skill`: a named capability that agents can cite inside a `skills:` block. It lives in the same prompt file as the agents that use it.
- `skill package`: a full shipped skill. It has its own entrypoint file, metadata, references, and optional emitted companions. Doctrine builds the install tree for you.

The two surfaces are additive. A package can still expose an inline `skill` to its consumers. The inline bridge carries `package: "<name>"` so the harness can load the package tree.

## The SKILL.prompt Entrypoint

A `skill package` lives in a file named `SKILL.prompt`. The directory holding that file is the package source root.

Minimal entrypoint:

```prompt
skill package LayoutChecklist: "Layout Checklist"
    metadata:
        name: "layout-checklist"
        description: "Check layout work against a short reusable checklist."
        version: "1.0.0"
        license: "MIT"
    "Use the [Checklist](references/checklist.md) before shipping layout work."
```

See `examples/95_skill_package_minimal/` for the smallest shipping shape and `examples/96_skill_package_references/` for the ordinary reference bundle.

### Metadata Block

`metadata:` accepts four scalar fields today:

- `name`
- `description`
- `version`
- `license`

Rules:

- `metadata:` may appear at most once.
- Unknown metadata fields fail loud.
- Duplicate metadata fields fail loud.
- If `name` is omitted, the emitter falls back to the declaration key for frontmatter.

### Named Sections

A `skill package` body follows the same shape as an inline `skill`. These named sections are all optional, but each one earns a clear job:

- `when_to_use`: the short list of jobs this skill is for. Keep it under a handful of lines.
- `when_not_to_use`: the short list of jobs that belong elsewhere. Name the other skill when you can.
- `non_negotiables`: the small set of rules the skill must follow every time.
- `first_move`: what the agent does first when this skill loads.
- `workflow`: the ordered steps the skill runs through.
- `output_expectations`: what every turn of this skill should produce.
- `reference_map`: a short index of deeper material with a one-line trigger each.

Use plain-language section titles (`"When to use"`, `"First move"`). The body accepts bare prose lines, keyed bullet rows, and addressable interpolation.

The entrypoint at `skills/agent-linter/prompts/SKILL.prompt` is the working template for a first-party skill. The entrypoint for this teaching skill at `skills/doctrine-learn/prompts/SKILL.prompt` follows the same shape.

### References

Reference files live under `references/` inside the package source root. They are ordinary Markdown files that ship with the package.

```text
prompts/
|-- SKILL.prompt
`-- references/
    `-- checklist.md
```

The root `SKILL.prompt` links them inline with relative Markdown links, like `[Checklist](references/checklist.md)`. The harness loads each reference only when its job triggers. See `examples/96_skill_package_references/`.

A `reference_map` section helps a thin harness decide which reference to open first. Give every reference one trigger line.

## Bundled Files

Three emit behaviors ship today:

- `emit:` entries turn `document` declarations into companion Markdown files
- ordinary bundled files copy through byte for byte
- `.prompt` files under `agents/` compile to Markdown agent companions
- `SKILL.contract.json` is emitted when the package has host-binding truth

### Ordinary Bundled Files

Any file under the package source root that is not a `.prompt` file copies through under the same relative path, byte for byte.

Shipping examples:

- `references/checklist.md`
- `scripts/greet.py`
- `assets/icon.png`
- `agents/openai.yaml`
- `.codex-plugin/plugin.json`

You do not need a compiler declaration for these roots. See `examples/97_skill_package_scripts/`, `examples/103_skill_package_binary_assets/`, and `examples/102_skill_package_path_case_preservation/`.

### Runtime Metadata

Drop `agents/openai.yaml` and peer YAML files beside the package to attach runtime metadata. The emitter copies them through under `agents/`. See `examples/98_skill_package_runtime_metadata/`.

### Plugin Metadata

Plugin metadata lives under hidden roots like `.codex-plugin/plugin.json`. See `examples/99_skill_package_plugin_metadata/`.

### Bundled Agents

A `skill package` can ship markdown agent companions. Every `.prompt` file under `agents/` compiles to one Markdown agent, and other files under `agents/` still bundle normally.

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

Rules:

- Bundled agent prompts must live under `agents/`.
- Each bundled agent prompt must define exactly one concrete agent.
- Other `.prompt` files outside `agents/**` do not copy through as raw files. Use `emit:` for prompt-authored companion docs.

See `examples/100_skill_package_bundled_agents/` and the larger compendium at `examples/101_skill_package_compendium/`.

## Emit Companions

Use `emit:` when a companion `.md` should come from a Doctrine-authored `document` instead of a hand-written file.

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

The source tree beside `SKILL.prompt`:

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

Rules:

- `emit:` is optional and may appear at most once.
- Each entry is `"relative/path.md": DocumentRef`.
- Each path must end in `.md` and stay under the package source root.
- Each ref must point at a `document` declaration.
- `emit:` paths may not collide with `SKILL.md`, bundled files, or compiled bundled-agent Markdown.

See `examples/122_skill_package_emit_documents/` for the minimal emit surface and `examples/123_skill_package_emit_documents_mixed_bundle/` for emit mixed with ordinary bundled files.

## Host Binding

Use host binding when one fat skill package needs typed host facts from the agent that consumes it. This keeps the package reusable and the agent typed.

The authoring model has four moves:

1. Declare `host_contract:` once on the root `skill package`.
2. Point the inline `skill` at that package with `package:`.
3. Bind each slot once at the consuming `skill` entry with `bind:`.
4. Use `{{host:slot}}` refs inside the package's emitted tree.

Package side:

```prompt
from refs.query_patterns import QueryPatterns

skill package HostBoundSkillPackage: "Host Bound Skill"
    metadata:
        name: "host-bound-skill"
        description: "Bind host facts once and reuse them across the whole package."
    emit:
        "references/query-patterns.md": QueryPatterns
    host_contract:
        document section_map: "Section Map"
        final_output final_response: "Final Response"
    "Read {{host:section_map.title}}."
    "Emit through {{host:final_response}}."
```

Agent side:

```prompt
skill HostBoundSkill: "Host Bound Skill"
    purpose: "Run the host-bound package."
    package: "host-bound-skill"

agent BoundDemo:
    role: "Use the bound package."
    outputs: "Outputs"
        FinalResponse
    final_output: FinalResponse
    skills: "Skills"
        skill host_bound: HostBoundSkill
            bind:
                section_map: SectionMap
                final_response: final_output
```

Rules:

- `host_contract:` is optional, but once a package declares slots, every slot must be bound exactly once by each consuming skill entry.
- The root `SKILL.prompt` body uses `{{host:slot}}` interpolation.
- Emitted docs and bundled agent prompts use the same `host:` root.
- `package:`, `host_contract:`, and `bind:` do not render into Markdown.
- When host-binding truth exists, Doctrine emits a `SKILL.contract.json` sidecar beside `SKILL.md`.

Supported host-slot families today: `input`, `output`, `document`, `analysis`, `schema`, `table`, `final_output`.

Bind targets may use `inputs:key`, `outputs:key`, `analysis`, `final_output`, ordinary declaration refs (`SectionMap`), or addressable child paths on those roots.

See `examples/124_skill_package_host_binding/` for the whole `host_contract:` + `bind:` + `host:` flow including the `SKILL.contract.json` sidecar and the fail-loud counter cases.

## Install Tree And Emit

Run the emitter from the repo root to build one package tree:

```bash
uv run --locked python -m doctrine.emit_skill --target <pyproject-target-name>
```

Each `skill package` needs its own entry under `[[tool.doctrine.emit.targets]]` in `pyproject.toml`:

```toml
[[tool.doctrine.emit.targets]]
name = "example_95_skill_package_minimal"
entrypoint = "examples/95_skill_package_minimal/prompts/SKILL.prompt"
output_dir = "examples/95_skill_package_minimal/build"
```

For a first-party repo skill, the curated install tree lives at `skills/.curated/<name>/`. The harness installs from there. See the existing `agent-linter` entries in `pyproject.toml` for the pattern.

## Working Templates In This Repo

- `skills/agent-linter/` is the shipped first-party template. Copy its `SKILL.prompt` shape when starting a new skill.
- `skills/doctrine-learn/` (this skill) uses the same pattern: a short root entrypoint with a `reference_map`, one reference file per surface, and references loaded on demand.

## Pitfalls

- Do not model a runtime home with `SKILL.prompt`. Runtime homes live under `AGENTS.prompt`.
- Do not dump every reference into the root `SKILL.prompt`. Keep the root short and point at references by relative link.
- Do not use `emit:` paths that escape the package source root or skip `.md`. Both fail loud.
- Do not bind `host_contract:` slots from two places. Each slot must be bound exactly once by each consuming skill entry.
- Do not commit `build/` as shipped truth. It is verifier-owned proof. Curated install trees go under `skills/.curated/<name>/`.
- Do not collide a bundled file with an `emit:` path or a compiled bundled-agent file. The emitter rejects collisions.

## Related References

- `references/principles.md` owns the thin-harness and prompt-budget rules that govern every skill.
- `references/agents-and-workflows.md` owns the `agent`, `skills:` block, and inline `skill` use sites.
- `references/outputs-and-schemas.md` owns the `output`, `final_output`, and `analysis` families that appear in `host_contract:` slots.
- `references/documents-and-tables.md` owns the `document` and `table` declarations you reach through `emit:`.
- `references/imports-and-refs.md` owns module imports, symbol imports, and multi-root resolution for cross-package refs.
- `references/emit-targets.md` owns `pyproject.toml` emit targets, `emit_skill`, and the curated install tree layout.

**Load when:** the author is building a reusable capability, shipping a first-class skill package, wiring `emit:` companions, binding host facts, or choosing between inline `skill` and `skill package`.
