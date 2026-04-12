# Emit Guide

Doctrine ships two emit commands that share one prompts-root-aware emit
pipeline:

- `doctrine.emit_docs` writes the runtime Markdown tree that existing coding
  agent tools consume.
- `doctrine.emit_flow` writes one workflow data-flow graph as
  deterministic `.flow.d2` plus same-command `.flow.svg`.

Use `emit_docs` when you need the compiled runtime prompt surface. Use
`emit_flow` when you need a reviewable graph of how declared inputs, concrete
agents, outputs, and route edges fit together for one entrypoint.

Important mode split:

- `emit_docs` runs on named targets from `pyproject.toml`.
- `emit_flow` can run on a named target or in direct quick-start mode with
  `--entrypoint` plus `--output-dir`.

Both emit commands reuse one compilation session per entrypoint. `emit_docs`
also compiles concrete root agents with safe default thread fan-out, while
still writing outputs in deterministic authored order.

## Prerequisites

Sync Python dependencies first:

```bash
uv sync
```

Install the pinned repo-local D2 dependency before using `emit_flow`:

```bash
npm ci
```

Important details:

- `emit_docs` only needs the Python environment.
- `emit_flow` also needs a working local `node` runtime plus the pinned
  `@terrastruct/d2` package from `package-lock.json`.
- `emit_flow` writes `.flow.d2` first and then renders `.flow.svg`. If the D2
  dependency is missing, the command exits with `E515` and tells you to run
  `npm ci`.

## Configure Emit Targets

Doctrine reads emit targets from `[tool.doctrine.emit.targets]` in
`pyproject.toml`:

```toml
[tool.doctrine.emit]

[[tool.doctrine.emit.targets]]
name = "example_73_flow_visualizer_showcase"
entrypoint = "examples/73_flow_visualizer_showcase/prompts/AGENTS.prompt"
output_dir = "examples/73_flow_visualizer_showcase/build"
```

Each target field has one job:

- `name`: the stable CLI handle you pass to `--target`
- `entrypoint`: the Doctrine source file to compile
- `output_dir`: the root directory where emitted artifacts land

Important rules:

- `entrypoint` must point at `AGENTS.prompt` or `SOUL.prompt`.
- `entrypoint` must live under a `prompts/` tree. The emit pipeline preserves
  the subdirectory beneath that `prompts/` root.
- `output_dir` must resolve to a directory path, not an existing file.
- Multiple targets may exist in one repo, and both emit commands use the same
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
- `emit_flow` direct mode requires both `--entrypoint` and `--output-dir`.
- `emit_flow` accepts either `--target` or direct mode, but not both at once.
- If `--pyproject` is omitted, Doctrine walks upward from the current working
  directory until it finds `pyproject.toml` for configured target mode.
- Direct `emit_flow` mode resolves compile config from the entrypoint's nearest
  `pyproject.toml` unless `--pyproject` explicitly overrides it.
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
still stays anchored to the entrypoint's own local `prompts/` root.

## Output Layout

Both emitters preserve the entrypoint's path beneath `prompts/`.

For runtime Markdown, Doctrine writes one file per concrete root agent:

```text
<output_dir>/<entrypoint-relative-dir>/<agent-slug>/<ENTRYPOINT_STEM>.md
```

If the entrypoint-relative directory already ends with the agent slug, Doctrine
does not repeat that directory level.

For workflow flow artifacts, Doctrine writes one file pair per emitted
entrypoint:

```text
<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.d2
<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.svg
```

Concrete shipped examples:

```text
examples/07_handoffs/build/project_lead/AGENTS.md
examples/07_handoffs/build/research_specialist/AGENTS.md
examples/07_handoffs/build/writing_specialist/AGENTS.md

examples/73_flow_visualizer_showcase/build/AGENTS.flow.d2
examples/73_flow_visualizer_showcase/build/AGENTS.flow.svg
```

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

The canonical checked-in flow proofs live in:

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
- `E510`: the target entrypoint is not `AGENTS.prompt` or `SOUL.prompt`.
- `E514`: the target entrypoint is not under a `prompts/` tree, so Doctrine
  cannot preserve the relative output layout.
- `E515`: the pinned D2 dependency is missing. Run `npm ci`.
- `E516`: `.flow.d2` was written, but the pinned SVG renderer failed. Inspect
  the `.flow.d2` source and the command output, then rerun after fixing the
  local Node or D2 problem.
- `E517`: `emit_flow` was invoked with both configured-target mode and direct
  mode, or with neither mode.
- `E518`: direct `emit_flow` mode omitted either `--entrypoint` or
  `--output-dir`.

For the full stable error catalog, use
[COMPILER_ERRORS.md](COMPILER_ERRORS.md).
