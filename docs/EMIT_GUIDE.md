# Emit Guide

Doctrine ships three emit commands that share one prompts-root-aware emit
pipeline:

- `doctrine.emit_docs` writes the runtime Markdown tree plus a versioned
  machine-readable companion contract for each concrete emitted agent.
- `doctrine.emit_skill` writes compiled `SKILL.md` package trees plus bundled
  source-root companion files.
- `doctrine.emit_flow` writes one workflow data-flow graph as
  deterministic `.flow.d2` plus same-command `.flow.svg`.

Use `emit_docs` when you need the compiled runtime prompt surface and its
machine-readable final-output metadata companion. Use `emit_skill` when you
need Doctrine to emit a real skill-package tree from `SKILL.prompt`. Use
`emit_flow` when you need a reviewable graph of how declared inputs, concrete
agents, outputs, and route edges fit together for one entrypoint.

Important mode split:

- `emit_docs` runs on named targets from `pyproject.toml`.
- `emit_skill` runs on named targets from `pyproject.toml`.
- `emit_flow` can run on a named target or in direct quick-start mode with
  `--entrypoint` plus `--output-dir`.

All three emit commands reuse the same prompts-root-aware target plumbing.
`emit_docs` also compiles concrete root agents with safe default thread
fan-out, while still writing outputs in deterministic authored order.

## Prerequisites

Use [../README.md](../README.md) for the package-install command. The Python
module path stays `doctrine`.

Use a source checkout when you need `emit_flow`, the example corpus, or the
contributor proof commands in this repo. Use
[../CONTRIBUTING.md](../CONTRIBUTING.md) for the source-checkout setup path.
`make setup` owns the repo bootstrap commands.

Important details:

- `emit_docs` and `emit_skill` only need the Python environment.
- `emit_flow` also needs a working local `node` runtime plus the pinned
  `@terrastruct/d2` package that `make setup` installs from
  `package-lock.json`.
- `emit_flow` writes `.flow.d2` first and then renders `.flow.svg`. If the D2
  dependency is missing, the command exits with `E515` and tells you to run
  `make setup`.

## Configure Emit Targets

Doctrine reads emit targets from `[tool.doctrine.emit.targets]` in
`pyproject.toml`:

```toml
[tool.doctrine.emit]

[[tool.doctrine.emit.targets]]
name = "example_73_flow_visualizer_showcase"
entrypoint = "examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt"
output_dir = "examples/73_flow_visualizer_showcase/build"

[[tool.doctrine.emit.targets]]
name = "example_95_skill_package_minimal"
entrypoint = "examples/95_skill_package_minimal/prompts/SKILL.prompt"
output_dir = "examples/95_skill_package_minimal/build"
```

Each target field has one job:

- `name`: the stable CLI handle you pass to `--target`
- `entrypoint`: the Doctrine source file to compile
- `output_dir`: the root directory where emitted artifacts land

Important rules:

- `entrypoint` must point at `AGENTS.prompt`, `SOUL.prompt`, or
  `SKILL.prompt`.
- `emit_docs` accepts `AGENTS.prompt` or `SOUL.prompt`.
- `emit_skill` accepts `SKILL.prompt`.
- `emit_flow` remains agent and workflow oriented. It accepts
  `AGENTS.prompt` or `SOUL.prompt` and rejects `SKILL.prompt`.
- `entrypoint` must live under a `prompts/` tree. The emit pipeline preserves
  the subdirectory beneath that `prompts/` root.
- In configured target mode, `entrypoint` must stay within the target project
  root.
- `output_dir` must resolve to a directory path, not an existing file.
- In configured target mode, `output_dir` must stay within the target project
  root.
- Multiple targets may exist in one repo, and all emit commands use the same
  target registry.

## Cross-Root Compile Config

Emit target mode and direct mode both compile through the same shared Doctrine
project-config contract:

```toml
[tool.doctrine.compile]
additional_prompt_roots = ["shared/prompts"]
```

Important rules:

- `additional_prompt_roots` entries resolve relative to the authoritative
  `pyproject.toml`.
- Absolute imports may search the entrypoint-local `prompts/` root plus the
  configured additional roots.
- Relative imports stay inside the importing module's own `prompts/` root.
- Emit output layout does not widen with import search. Doctrine still places
  emitted files relative to the entrypoint's own local `prompts/` root.
- In configured target mode, emit passes the already-resolved target
  `pyproject.toml` through to compilation.
- In direct `emit_flow` mode without `--pyproject`, Doctrine resolves compile
  config from the entrypoint's nearest `pyproject.toml`.

## Run The Commands

Emit compiled Markdown for one or more configured targets:

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth
```

Emit compiled skill-package trees for one or more configured targets:

```bash
uv run --locked python -m doctrine.emit_skill --target example_95_skill_package_minimal
uv run --locked python -m doctrine.emit_skill --target example_100_skill_package_bundled_agents
```

Emit one workflow data-flow graph from a configured target:

```bash
uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase
```

If you are not running from the repo root, point the command at the config
file explicitly:

```bash
uv run --locked python -m doctrine.emit_flow \
  --pyproject /path/to/pyproject.toml \
  --target example_73_flow_visualizer_showcase
```

Useful CLI rules:

- Repeat `--target` to emit multiple configured targets in one command.
- `emit_docs` and `emit_skill` currently run on configured targets only.
- `emit_flow` direct mode requires both `--entrypoint` and `--output-dir`.
- `emit_flow` accepts either `--target` or direct mode, but not both at once.
- If `--pyproject` is omitted, Doctrine walks upward from the current working
  directory until it finds `pyproject.toml` for configured target mode.
- Direct `emit_flow` mode resolves compile config from the entrypoint's nearest
  `pyproject.toml` unless `--pyproject` explicitly overrides it.
- When direct `emit_flow` resolves a project root, `--output-dir` must stay
  within that root.
- `emit_docs` reuses one indexed prompt graph per target instead of reparsing
  the same imports for each concrete root agent.
- The commands fail loudly on config or compiler errors instead of skipping bad
  targets.

## Quick Start Without A Named Target

When you want a first flow render before adding a permanent target to
`pyproject.toml`, `emit_flow` can resolve one entrypoint directly:

```bash
uv run --locked python -m doctrine.emit_flow \
  --entrypoint examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt \
  --output-dir examples/73_flow_visualizer_showcase/build
```

Direct mode keeps the same prompts-root validation and the same output layout
rules as configured target mode. It only skips the named target lookup.
Compile-time import search may widen through
`[tool.doctrine.compile].additional_prompt_roots`, but emitted output placement
still stays anchored to the entrypoint's own local `prompts/` root. `emit_docs`
and `emit_skill` do not currently provide a direct quick-start mode.

## Output Layout

All emitters preserve the entrypoint's path beneath `prompts/`.

For runtime prompt output, Doctrine writes two files per concrete root agent:

```text
<output_dir>/<entrypoint-relative-dir>/<agent-slug>/<ENTRYPOINT_STEM>.md
<output_dir>/<entrypoint-relative-dir>/<agent-slug>/<ENTRYPOINT_STEM>.contract.json
```

If the entrypoint-relative directory already ends with the agent slug, Doctrine
does not repeat that directory level.

For workflow flow artifacts, Doctrine writes one file pair per emitted
entrypoint:

```text
<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.d2
<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.svg
```

For skill-package output, Doctrine writes one emitted tree per package
entrypoint:

```text
<output_dir>/<entrypoint-relative-dir>/SKILL.md
<output_dir>/<entrypoint-relative-dir>/<bundled-relative-path>
```

Important package rules:

- `SKILL.prompt` compiles to `SKILL.md`.
- The directory that contains `SKILL.prompt` is the package source root.
- Any bundled file that is not a `.prompt` file emits under the same relative
  path from that source root, byte for byte.
- Bundled agent prompts under `agents/**/*.prompt` emit compiled markdown
  companions under the same relative paths, with `.prompt` replaced by `.md`.
- Other files in the same `agents/` tree still emit as ordinary bundled files.
- `SKILL.md` is compiler-owned emitted output, so authored bundled files may
  not collide with that path.

Concrete shipped examples:

```text
examples/07_handoffs/build/project_lead/AGENTS.md
examples/07_handoffs/build/project_lead/AGENTS.contract.json
examples/07_handoffs/build/research_specialist/AGENTS.md
examples/07_handoffs/build/research_specialist/AGENTS.contract.json
examples/07_handoffs/build/writing_specialist/AGENTS.md
examples/07_handoffs/build/writing_specialist/AGENTS.contract.json

examples/73_flow_visualizer_showcase/build/AGENTS.flow.d2
examples/73_flow_visualizer_showcase/build/AGENTS.flow.svg

examples/95_skill_package_minimal/build/SKILL.md
examples/96_skill_package_references/build/references/checklist.md
examples/97_skill_package_scripts/build/scripts/greet.py
examples/99_skill_package_plugin_metadata/build/.codex-plugin/plugin.json
examples/100_skill_package_bundled_agents/build/agents/cold_reviewer.md
examples/100_skill_package_bundled_agents/build/agents/openai.yaml
examples/103_skill_package_binary_assets/build/assets/icon.png
```

Runtime Markdown shape for ordinary outputs:

- This is emitted Markdown layout only. It does not add or change input-side
  syntax.
- A single-artifact ordinary output renders one grouped `Contract | Value`
  table.
- A `files:` output renders the same contract table, then an `Artifacts`
  table.
- Table-friendly sections such as `current_truth`, titled `properties`,
  parseable `notes`, and `support_files` now render as tables.
- `structure:` now renders as one `Artifact Structure` section instead of a
  loose `Structure:` bullet plus a separate peer block.

Single-artifact example:

```md
### Review Comment

| Contract | Value |
| --- | --- |
| Target | Turn Response |
| Shape | Comment |
| Requirement | Required |
```

File-set example:

```md
### Lesson Manifest Output

| Contract | Value |
| --- | --- |
| Target | File Set |
| Requirement | Required |

#### Artifacts

| Artifact | Path | Shape |
| --- | --- | --- |
| Built Lesson | `lesson_root/_authoring/lesson_manifest.json` | Lesson Manifest JSON |
| Validation File | `lesson_root/_authoring/MANIFEST_VALIDATION.md` | Markdown Document |
```

The companion contract is compiler-owned emitted truth. In v1 it carries:

- `contract_version = 1` for the emitted JSON contract shape only. It is not
  the Doctrine language version. For the repo-wide versioning guide, use
  [VERSIONING.md](VERSIONING.md).

- concrete agent identity
- whether `final_output` exists
- final-output declaration key and name
- `format_mode`
- `schema_profile`

Keep `contract_version` narrow. Public release tags and Doctrine language
versions live in the versioning guide and release history instead:

- [VERSIONING.md](VERSIONING.md)
- [../CHANGELOG.md](../CHANGELOG.md)
- stable project-relative `schema_file` and `example_file` paths when the final
  output is schema-backed
- for review-driven agents, a root `review` object that says:
  - which output is the review carrier
  - which output is the final response
  - whether the final response is the carrier, a split response, or absent
  - which carrier and final-response fields map to review semantics
  - whether a split final response is `control_ready`
  - normalized outcome summaries for `accept`, `changes_requested`, and
    `blocked`, including route behavior

## How To Read `emit_flow` Output

The graph is compiler-owned. Doctrine extracts the structure from the shipped
I/O model and workflow-law semantics; it does not scrape emitted Markdown.

The generated graph includes:

- input nodes for declared `input` and `inputs` surfaces
- agent nodes for concrete root agents in the resolved entrypoint
- output nodes for declared `output` and `outputs` surfaces
- consume edges from inputs to agents
- produce edges from agents to outputs
- labeled route edges between agents when authored routing is part of the turn
- currentness, invalidation, and `trust_surface` notes on output nodes when
  workflow law binds them
- section groupings for shared inputs, local inputs, route-first agent
  handoffs, shared outputs or carriers, and local outputs

Reading guidance:

- `.flow.d2` is the deterministic, diff-friendly source artifact.
- `.flow.svg` is the convenience render of the same graph for browsing.
- when route edges exist, the agent section renders as a route-first lane:
  the first routed owner anchors the main lane, loop-backs stay attached to
  that lane, and additional routed starts or standalone agents render as
  secondary stacks instead of one flat strip
- If you care about reviewable truth in version control, inspect `.flow.d2`
  first.

## Verify The Surface

When you change shipped language behavior or checked-in emit proof, run the
same verification path the repo uses:

```bash
make verify-examples
```

For one manifest-backed example:

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/73_flow_visualizer_showcase/cases.toml
```

If you changed emit diagnostics or the emit CLI error surface, also run:

```bash
make verify-diagnostics
```

The canonical checked-in build proofs live in `build_ref/` trees and may
include compiled Markdown, `SKILL.md` package trees, companion
`.contract.json` files, and target-scoped flow artifacts. `build_ref/` is
verifier-owned checked-in proof, not part of Doctrine's public authoring model.
Representative checked-in proofs live in:

- `examples/95_skill_package_minimal/build_ref/SKILL.md`
- `examples/100_skill_package_bundled_agents/build_ref/agents/cold_reviewer.md`
- `examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.d2`
- `examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.svg`
- `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.d2`
- `examples/36_invalidation_and_rebuild/build_ref/AGENTS.flow.svg`

## Troubleshooting

Common emit failures:

- `E501` unknown emit target: the requested target name is not defined in
  `pyproject.toml`.
- `E503` or `E504`: Doctrine could not find or load the emit config. Run from
  the repo root or pass `--pyproject`.
- `E510`: the target entrypoint does not match the emitter surface.
- `E514`: the target entrypoint is not under a `prompts/` tree, so Doctrine
  cannot preserve the relative output layout.
- `E515`: the pinned D2 dependency is missing. Run `make setup`.
- `E516`: `.flow.d2` was written, but the pinned SVG renderer failed. Inspect
  the `.flow.d2` source and the command output, then rerun after fixing the
  local Node or D2 problem.
- `E517`: `emit_flow` was invoked with both configured-target mode and direct
  mode, or with neither mode.
- `E518`: direct `emit_flow` mode omitted either `--entrypoint` or
  `--output-dir`.

For the full stable error catalog, use
[COMPILER_ERRORS.md](COMPILER_ERRORS.md).
