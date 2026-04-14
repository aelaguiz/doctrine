# Contributing

Thanks for contributing to Doctrine.

This repo moves quickly, but the bar is simple: keep the shipped language, docs,
and verified examples aligned.

## Setup

```bash
uv sync
npm ci
make check
```

If you only need the fastest proof path while you are iterating:

```bash
make tests
```

If you change diagnostics, also run:

```bash
make verify-diagnostics
```

If you change the VS Code extension under `editors/vscode/`, also run:

```bash
cd editors/vscode
make
```

## Repo rules

- Treat `doctrine/` as the shipped source of truth for parser, compiler, and renderer behavior.
- Treat `examples/` as design and verification inputs, not as proof on their own.
- Keep new examples narrow. Add one new idea at a time.
- Prefer fail-loud behavior over silent fallback.
- Keep public docs and examples generic. Do not import private product names or company-only jargon from other repos.
- Update docs and instructions when behavior changes.

## Questions, bugs, and proposals

- Use GitHub Discussions for questions, setup help, and open design talk.
- Use GitHub Issues for bugs and scoped feature requests.

## Pull requests

- Explain what changed in plain English.
- Say exactly what you ran to verify the change.
- If you did not run a check, say that plainly.
- Keep unrelated cleanup out of the same change when possible.
