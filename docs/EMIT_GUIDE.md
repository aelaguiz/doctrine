# Emit Guide

Doctrine ships two emit commands that operate on named targets from
`pyproject.toml`:

- `doctrine.emit_docs` writes the runtime Markdown tree that existing coding
  agent tools consume.
- `doctrine.emit_flow` writes one target-scoped workflow data-flow graph as
  deterministic `.flow.d2` plus same-command `.flow.svg`.

Use `emit_docs` when you need the compiled runtime prompt surface. Use
`emit_flow` when you need a reviewable graph of how declared inputs, concrete
agents, outputs, and route edges fit together for one entrypoint.

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
name = "example_36_invalidation_and_rebuild"
entrypoint = "examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt"
output_dir = "examples/36_invalidation_and_rebuild/build"
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

## Run The Commands

Emit compiled Markdown for one or more configured targets:

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth
```

Emit a target-scoped workflow data-flow graph:

```bash
uv run --locked python -m doctrine.emit_flow --target example_36_invalidation_and_rebuild
```

If you are not running from the repo root, point the command at the config
file explicitly:

```bash
uv run --locked python -m doctrine.emit_flow \
  --pyproject /path/to/pyproject.toml \
  --target example_36_invalidation_and_rebuild
```

Useful CLI rules:

- Repeat `--target` to emit multiple configured targets in one command.
- If `--pyproject` is omitted, Doctrine walks upward from the current working
  directory until it finds `pyproject.toml`.
- The commands fail loudly on config or compiler errors instead of skipping bad
  targets.

## Output Layout

Both emitters preserve the entrypoint's path beneath `prompts/`.

For runtime Markdown, Doctrine writes one file per concrete root agent:

```text
<output_dir>/<entrypoint-relative-dir>/<agent-slug>/<ENTRYPOINT_STEM>.md
```

If the entrypoint-relative directory already ends with the agent slug, Doctrine
does not repeat that directory level.

For workflow flow artifacts, Doctrine writes one file pair per target:

```text
<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.d2
<output_dir>/<entrypoint-relative-dir>/<ENTRYPOINT_STEM>.flow.svg
```

Concrete shipped examples:

```text
examples/07_handoffs/build/project_lead/AGENTS.md
examples/07_handoffs/build/research_specialist/AGENTS.md
examples/07_handoffs/build/writing_specialist/AGENTS.md

examples/36_invalidation_and_rebuild/build/AGENTS.flow.d2
examples/36_invalidation_and_rebuild/build/AGENTS.flow.svg
```

## How To Read `emit_flow` Output

The graph is compiler-owned. Doctrine extracts the structure from the shipped
I/O model and workflow-law semantics; it does not scrape emitted Markdown.

The generated graph includes:

- input nodes for declared `input` and `inputs` surfaces
- agent nodes for concrete root agents in the configured entrypoint
- output nodes for declared `output` and `outputs` surfaces
- consume edges from inputs to agents
- produce edges from agents to outputs
- labeled route edges between agents when authored routing is part of the turn
- currentness, invalidation, and `trust_surface` notes on output nodes when
  workflow law binds them

Reading guidance:

- `.flow.d2` is the deterministic, diff-friendly source artifact.
- `.flow.svg` is the convenience render of the same graph for browsing.
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
uv run --locked python -m doctrine.verify_corpus --manifest examples/36_invalidation_and_rebuild/cases.toml
```

If you changed emit diagnostics or the emit CLI error surface, also run:

```bash
make verify-diagnostics
```

The canonical checked-in flow proof lives in:

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

For the full stable error catalog, use
[COMPILER_ERRORS.md](COMPILER_ERRORS.md).
