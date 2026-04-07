# Doctrine

Doctrine is a small Python bootstrap for an indentation-sensitive prompt language, its parser and compiler, and a verified example corpus.

## Verify the repo

```bash
uv sync
make verify-examples
```

## Install the VS Code extension

The VS Code extension lives in `editors/vscode/`.

Build the installable VSIX:

```bash
cd editors/vscode
make
```

That writes `pyprompt-language-0.0.1.vsix` into `editors/vscode/`.

Install it in normal VS Code with either:

- `Extensions: Install from VSIX...`
- `code --install-extension /absolute/path/to/pyprompt-language-0.0.1.vsix`

For extension-specific details, see `editors/vscode/README.md`.

## Project files

- License: [LICENSE](LICENSE)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security policy: [SECURITY.md](SECURITY.md)
