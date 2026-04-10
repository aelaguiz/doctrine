# Doctrine

Doctrine is a Python-like DSL and compiler for building agent doctrine as code
instead of hand-maintained Markdown.

It keeps Markdown as the runtime artifact because coding agents can consume
that today, but it moves the source of truth into reusable declarations,
inheritance, typed inputs and outputs, skill contracts, and fail-loud
compilation.

## A Real Agent Example

<p align="center">
  <img src="docs/assets/readme-doctrine-agent-example.png" alt="Side-by-side view of a Doctrine source file for an agent and the compiled AGENTS.md runtime artifact it produces." width="1200">
</p>

This is a real Doctrine authoring flow from an agent repo. The left pane is
the structured source of truth: reusable workflows, typed inputs, inherited
sections, and skill declarations in one reviewable `.prompt` file. The right
pane is the compiled `AGENTS.md` runtime artifact that existing coding-agent
tools actually read.

That split improves working on agents in concrete ways:

- humans and coding agents edit one narrow source file instead of
  hand-maintaining a giant runtime Markdown file
- shared turn rules and handoff policy land once, then compile consistently
  into the emitted `AGENTS.md`
- reviewers can inspect intent in the source and verify the exact downstream
  runtime artifact beside it

## Why this exists

Large agent systems drift fast when the source of truth is copied Markdown:

- shared sections are duplicated across agents and edited inconsistently
- one policy update lands in one file and misses three siblings
- giant role homes become hard for humans to review and hard for coding agents
  to edit without adding noise
- the runtime surface is Markdown, but the authoring problem is structured
  programming

Doctrine turns that maintenance problem into a programming problem.

Read [docs/WHY_DOCTRINE.md](docs/WHY_DOCTRINE.md) for the motivating use case
and anonymized drift examples.

## What ships today

- concrete and abstract `agent` declarations
- reusable and inherited `workflow` declarations
- typed `skill`, `input`, `output`, `input source`, `output target`,
  `output shape`, and `json schema` declarations
- workflow law on `workflow` plus `trust_surface` on `output` for portable
  currentness, invalidation, preservation, basis roles, and law reuse
- ordinary authored slots such as routing and stop rules
- named `skills`, `inputs`, and `outputs` block reuse and inheritance
- imports, dotted refs, agent mentions, and authored-prose interpolation
- manifest-backed verification for examples `01` through `38`

The shipped implementation lives in `doctrine/`. The examples are design
pressure plus proof, not the source of truth by themselves.

For the shipped workflow-law model, start with
[docs/WORKFLOW_LAW.md](docs/WORKFLOW_LAW.md).

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
uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml
```

## Emit Compiled Markdown

The emit pipeline reads configured targets from `pyproject.toml` and writes a
compiled Markdown tree for each concrete agent in the entrypoint. Today the
entrypoint may be either `AGENTS.prompt` or `SOUL.prompt`, and the emitted
basename follows the entrypoint stem.

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth
```

## VS Code Extension

The repo-local VS Code extension lives in `editors/vscode/` and provides
syntax highlighting plus full clickable follow-definition behavior for shipped
Doctrine refs in `.prompt` files: imports, declaration refs, readable refs,
interpolation roots, and structural inheritance keys.

Build the installable VSIX:

```bash
cd editors/vscode
make
```

For extension-specific details, see
[editors/vscode/README.md](editors/vscode/README.md).

## Repo Guide

- Start here: [docs/README.md](docs/README.md)
- Workflow law guide: [docs/WORKFLOW_LAW.md](docs/WORKFLOW_LAW.md)
- Language examples: [examples/README.md](examples/README.md)
- Example agents bank: [example_agents/README.md](example_agents/README.md)
- Language and compiler truth: `doctrine/`
- VS Code extension: [editors/vscode/README.md](editors/vscode/README.md)

## Project Files

- License: [LICENSE](LICENSE)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security policy: [SECURITY.md](SECURITY.md)
