# PyPrompt VS Code Extension

Repo-local VS Code language support for `.prompt` files.

## What this extension does

- registers `*.prompt` as the `pyprompt` language
- adds TextMate syntax highlighting for the shipped PyPrompt grammar
- enables `#` comments, off-side folding, and narrow Enter indentation rules
- keeps keyword coverage aligned with `pyprompt/grammars/pyprompt.lark`

## Install in normal VS Code

Build the installable VSIX:

```bash
cd editors/vscode
npm install
npm run package:vsix
```

That writes `pyprompt-language-0.0.1.vsix` into `editors/vscode/`.

Install it with either:

- `Extensions: Install from VSIX...`
- `code --install-extension /absolute/path/to/pyprompt-language-0.0.1.vsix`

## Run the grammar checks directly

If you only want the checks without packaging:

```bash
cd editors/vscode
npm test
uv run --locked python scripts/validate_lark_alignment.py
```

## Development only: Extension Development Host

1. Open `editors/vscode/` in VS Code.
2. Run the `Run Extension` launch configuration.
3. In the Extension Development Host window, open the main repo and a `.prompt` file.

## Refresh after grammar changes

1. Re-run `npm run package:vsix`.
2. Reinstall the new `.vsix` in VS Code.
3. Reload your VS Code window if the old version is still active.
