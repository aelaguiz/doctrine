# Doctrine

Doctrine is the repo for PyPrompt, a Python-like DSL and compiler for building
agent doctrine as code instead of hand-maintained Markdown.

It keeps `AGENTS.md` as the runtime artifact because coding agents can consume
that today, but it moves the source of truth into reusable declarations,
inheritance, typed inputs and outputs, skill contracts, and fail-loud
compilation.

## Why this exists

Large agent systems drift fast when the source of truth is copied Markdown:

- shared sections are duplicated across agents and edited inconsistently
- one policy update lands in one file and misses three siblings
- giant role homes become hard for humans to review and hard for coding agents
  to edit without adding noise
- the runtime surface is Markdown, but the authoring problem is structured
  programming

PyPrompt turns that maintenance problem into a programming problem.

Read [docs/WHY_DOCTRINE.md](docs/WHY_DOCTRINE.md) for the motivating use case
and anonymized drift examples.

## What ships today

- concrete and abstract `agent` declarations
- reusable and inherited `workflow` declarations
- typed `skill`, `input`, `output`, `input source`, `output target`,
  `output shape`, and `json schema` declarations
- ordinary authored slots such as routing and stop rules
- named `skills`, `inputs`, and `outputs` block reuse and inheritance
- imports, dotted refs, agent mentions, and authored-prose interpolation
- manifest-backed verification for examples `01` through `26`

The shipped implementation lives in `pyprompt/`. The examples are design
pressure plus proof, not the source of truth by themselves.

## Quick Example

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

That compiles to runtime Markdown that existing coding-agent tools can consume:

```md
Core job: review the current brief and route the same issue honestly.

## How To Take A Turn

Read the current brief before you act.
Leave one honest handoff and stop.

## Skills

### Can Run

#### repo-search
```

## Verify The Repo

```bash
uv sync
make verify-examples
```

If you change diagnostics, also run:

```bash
make verify-diagnostics
```

For one manifest-backed example run:

```bash
uv run --locked python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml
```

## Emit Compiled `AGENTS.md`

The emit pipeline reads configured targets from `pyproject.toml` and writes a
compiled `AGENTS.md` tree for each concrete agent in the entrypoint.

```bash
uv run --locked python -m pyprompt.emit_docs --target example_07_handoffs
uv run --locked python -m pyprompt.emit_docs --target example_14_handoff_truth
```

## VS Code Extension

The repo-local VS Code extension lives in `editors/vscode/`.

Build the installable VSIX:

```bash
cd editors/vscode
make
```

For extension-specific details, see
[editors/vscode/README.md](editors/vscode/README.md).

## Repo Guide

- Start here: [docs/README.md](docs/README.md)
- Language examples: [examples/README.md](examples/README.md)
- Language and compiler truth: `pyprompt/`
- VS Code extension: [editors/vscode/README.md](editors/vscode/README.md)

## Project Files

- License: [LICENSE](LICENSE)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security policy: [SECURITY.md](SECURITY.md)
