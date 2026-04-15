# Doctrine

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.14%2B](https://img.shields.io/badge/python-3.14%2B-3776AB.svg)](pyproject.toml)
[![CI](https://img.shields.io/github/actions/workflow/status/aelaguiz/doctrine/ci.yml?branch=main&label=ci)](https://github.com/aelaguiz/doctrine/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/doctrine-agents.svg)](https://pypi.org/project/doctrine-agents/)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/aelaguiz/doctrine/badge)](https://scorecard.dev/viewer/?uri=github.com/aelaguiz/doctrine)
[![Output: AGENTS.md](https://img.shields.io/badge/output-AGENTS.md-6E56CF.svg)](https://github.com/aelaguiz/doctrine)

[Docs](docs/README.md) · [Versioning](docs/VERSIONING.md) · [Changelog](CHANGELOG.md) · [VS Code extension](editors/vscode/README.md)

Write agent flows as code. Compile them to `AGENTS.md`.

Doctrine is a typed DSL and compiler for reusable agent instructions, workflows, reviews, skills, and I/O contracts. Instead of hand-editing giant `AGENTS.md` files, you author small `.prompt` files and compile deterministic runtime artifacts that current coding-agent tools can already read today.

<p align="center">
  <img src="docs/assets/readme-doctrine-agent-example.png" alt="Side-by-side view of Doctrine source on the left and compiled AGENTS.md output on the right." width="1200">
</p>

Why teams reach for Doctrine:

- one shared rule changes once
- compile-time failures catch drift before runtime
- humans can review source and emitted runtime side by side
- flow diagrams, verification, and editor support ship today

## Runtime boundary

Doctrine is the authoring and compile layer.
It turns typed `.prompt` source into deterministic runtime Markdown such as
`AGENTS.md`.
That output is meant for the agent runtime that fits your stack.
Doctrine does not try to be the runtime, scheduler, or state store.

## Why Doctrine exists

Serious agent systems drift fast when the source of truth is copied Markdown:

- shared sections get duplicated and then edited out of sync
- one policy fix turns into search-and-hope edits
- large prompt trees become hard to review
- runtime Markdown is the delivery format, not the right authoring surface

Doctrine turns that into a language and compiler problem.

## Quick example

```prompt
workflow SharedTurn: "How To Take A Turn"
    "Read the current brief before you act."
    "Leave one honest handoff and stop."

skill RepoSearchSkill: "repo-search"
    purpose: "Find the right repo surface for the current job."

abstract agent ReviewRole:
    read_first: SharedTurn

agent BriefReviewer[ReviewRole]:
    role: "Core job: review the current brief and route the same issue honestly."

    inherit read_first

    skills: "Skills"
        can_run: "Can Run"
            skill search: RepoSearchSkill
                requirement: Advisory
```

That compiles to runtime Markdown:

```md
Core job: review the current brief and route the same issue honestly.

## How To Take A Turn

Read the current brief before you act.
Leave one honest handoff and stop.

## Skills

### Can Run

#### repo-search
```

## Quickstart

When Doctrine is installed from a package index, the distribution name is
`doctrine-agents`. The Python module name stays `doctrine`.

Want the packaged compiler?

```bash
python -m pip install doctrine-agents
```

Need the example corpus, repo proof, or `emit_flow`?

```bash
git clone https://github.com/aelaguiz/doctrine.git
cd doctrine
make setup
```

Use [CONTRIBUTING.md](CONTRIBUTING.md) for the full source-checkout proof
path. `make setup` owns the repo bootstrap commands.
Use [docs/VERSIONING.md](docs/VERSIONING.md) for release rules and
[CHANGELOG.md](CHANGELOG.md) for the public release record.

Want a smaller first proof from a source checkout?

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml
```

Want generated output right away from a source checkout?

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase
```

## What ships today

- concrete and abstract `agent` declarations
- reusable and inherited `workflow` declarations
- first-class `review` and `abstract review` declarations
- typed `skills`, `inputs`, `outputs`, direct `output[...]` inheritance,
  `output schema`, and generated schema contracts
- imports, directory-backed runtime packages, readable refs, interpolation,
  enums, and workflow law
- `emit_docs`, `emit_flow`, `emit_skill`, and structured-output schema
  validation helpers
- manifest-backed verification through `examples/115_runtime_agent_packages`
- a repo-local VS Code extension for `.prompt` files

## Workflow visualizer

<p align="center">
  <img src="examples/73_flow_visualizer_showcase/build_ref/AGENTS.flow.svg" alt="Generated Doctrine workflow diagram showing shared inputs, a route-first handoff lane, and compiler-owned flow output." width="1200">
</p>

The checked-in showcase above comes from `examples/73_flow_visualizer_showcase`. It proves that Doctrine can emit human-readable runtime docs and compiler-owned flow diagrams from the same source graph.

## Read next

- [docs/README.md](docs/README.md)
- [docs/VERSIONING.md](docs/VERSIONING.md)
- [CHANGELOG.md](CHANGELOG.md)
- [docs/WHY_DOCTRINE.md](docs/WHY_DOCTRINE.md)
- [PRINCIPLES.md](PRINCIPLES.md)
- [docs/LANGUAGE_REFERENCE.md](docs/LANGUAGE_REFERENCE.md)
- [docs/AUTHORING_PATTERNS.md](docs/AUTHORING_PATTERNS.md)
- [docs/EMIT_GUIDE.md](docs/EMIT_GUIDE.md)
- [examples/README.md](examples/README.md)
- [editors/vscode/README.md](editors/vscode/README.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Questions and contributions

- Use [Discussions](https://github.com/aelaguiz/doctrine/discussions) for questions and design talk.
- Use [Issues](https://github.com/aelaguiz/doctrine/issues) for clear bugs or scoped proposals.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and proof commands.
- See [SUPPORT.md](SUPPORT.md) for help paths, [SECURITY.md](SECURITY.md) for private vulnerability reports, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for collaboration rules.

If this direction is useful, star the repo and watch releases.
