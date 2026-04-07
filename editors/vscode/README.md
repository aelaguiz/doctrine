# Doctrine VS Code Extension

Repo-local VS Code language support for `.prompt` files.

## What this extension does

- registers `*.prompt` as the `pyprompt` language
- adds TextMate syntax highlighting for the shipped Doctrine grammar
- enables `#` comments, off-side folding, and narrow Enter indentation rules
- keeps keyword coverage aligned with `pyprompt/grammars/pyprompt.lark`

## Install in VS Code or Cursor

Build the installable VSIX:

```bash
cd editors/vscode
make
```

That writes `pyprompt-language-<generated-version>.vsix` into `editors/vscode/`.

`make` installs the extension's npm dependencies if needed, runs the grammar tests, runs the Lark-alignment validator, and packages the final VSIX.
Each packaging run stamps a fresh semver version without editing `package.json`, so reinstalling the newest VSIX always upgrades the local editor copy cleanly.

Install it with either:

- `Extensions: Install from VSIX...`
- `code --install-extension /absolute/path/to/pyprompt-language-<generated-version>.vsix`

The packaged extension declares `engines.vscode: ^1.105.0`, which admits Cursor builds that report VS Code `1.105.x`.

## Remote SSH and Cursor

The syntax-highlighting extension is installed on the local editor side.
If you are editing a remote checkout over SSH, rebuilding the remote repo does not update the extension that Cursor or VS Code is currently running on your laptop.

After grammar changes:

1. Re-run `make`.
2. Reinstall the newest generated `.vsix` locally in VS Code or Cursor.
3. Reload the editor window.

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

1. Re-run `make`.
2. Reinstall the newest generated `.vsix` in VS Code or Cursor.
3. Reload your VS Code window if the old version is still active.
