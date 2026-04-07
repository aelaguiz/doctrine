# Contributing

Thanks for contributing to Doctrine.

This repo is still small and moves quickly, so the best contributions are
usually narrow, explicit changes that keep the shipped implementation, docs,
and verified examples aligned.

## Setup

```bash
uv sync
make verify-examples
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

- Treat `pyprompt/` as the shipped source of truth for parser, compiler, and renderer behavior.
- Treat `examples/` as design and verification inputs, not as proof of shipped behavior on their own.
- Keep new examples disciplined: one new idea at a time, with the smallest example that proves it cleanly.
- Prefer fail-loud behavior over silent fallback when you change grammar or compiler behavior.
- Update docs and instructions when behavior changes.

## Pull requests

- Explain what changed in plain English.
- Say exactly what you ran to verify the change.
- If you did not run a check, say that plainly.
- Keep unrelated cleanup out of the same change when possible.
