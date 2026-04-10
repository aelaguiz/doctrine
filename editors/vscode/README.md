# Doctrine VS Code Extension

Repo-local VS Code language support for `.prompt` files.

## What this extension does

- registers `*.prompt` as the `doctrine` language
- adds TextMate syntax highlighting for the shipped Doctrine grammar
- supports Go to Definition and click navigation on raw `import` paths
- supports Go to Definition across the full shipped clickable surface:
  parent declaration refs, authored-slot refs and overrides, workflow `use`
  refs, workflow `skills` refs and override refs, route targets, `skills`,
  `inputs`, `outputs`, patch-parent refs, `source`, `target`, `shape`,
  `schema`, standalone input/output refs in typed I/O bodies, standalone
  readable refs in workflow bodies, interpolation roots, addressable path
  roots and path segments in interpolation / workflow section / generic record
  value surfaces, including trailing `title` segments when they resolve to a
  real definition site, enum roots and enum members, and structural
  `abstract` / `inherit` / local-key `override` sites, plus workflow-law and
  trust-surface surfaces such as law carrier refs, trust-surface field items,
  enum-backed mode refs, law-section `inherit` / `override` keys, and route
  targets inside `law` branches
- enables `#` comments, off-side folding, and narrow Enter indentation rules
- keeps keyword coverage aligned with `doctrine/grammars/doctrine.lark`

The extension resolves Doctrine imports from the nearest `prompts/` root using
the same absolute and relative module rules the compiler ships.

Workflow-law support here uses the same vocabulary as
[../../docs/WORKFLOW_LAW.md](../../docs/WORKFLOW_LAW.md): `law`,
`trust_surface`, carrier refs, trust-surface field items, enum-backed mode
refs, named law subsection `inherit` / `override` keys, and route targets
inside `law` branches.

## What it does not do yet

- synthetic destinations for built-in `source:` or `target:` names such as
  `File`, `Prompt`, `EnvVar`, or `TurnResponse`
- synthetic destinations for compiler-derived built-in `...:title` hops that
  do not resolve to a declaration or authored keyed line
- synthetic destinations for undeclared dynamic prompt-object fields such as
  `CurrentHandoff.active_mode` when the root declaration exists but the segment
  is runtime-only rather than an authored keyed field
- completion, hover, rename, symbol search, or a full language server

## Install in VS Code or Cursor

Build the installable VSIX:

```bash
cd editors/vscode
make
```

That writes `doctrine-language-<generated-version>.vsix` into `editors/vscode/`.

`make` installs the extension's npm dependencies if needed, runs the grammar
tests, runs the extension-host navigation tests, runs the Lark-alignment
validator, and packages the final VSIX.
Each packaging run stamps a fresh semver version without editing `package.json`, so reinstalling the newest VSIX always upgrades the local editor copy cleanly.

Install it with either:

- `Extensions: Install from VSIX...`
- `code --install-extension /absolute/path/to/doctrine-language-<generated-version>.vsix`

The packaged extension declares `engines.vscode: ^1.105.0`, which admits Cursor builds that report VS Code `1.105.x`.

## Remote SSH and Cursor

The extension is installed on the local editor side.
If you are editing a remote checkout over SSH, rebuilding the remote repo does not update the extension that Cursor or VS Code is currently running on your laptop.

After extension changes:

1. Re-run `make`.
2. Reinstall the newest generated `.vsix` locally in VS Code or Cursor.
3. Reload the editor window.

## Run the checks directly

If you only want the checks without packaging:

```bash
cd editors/vscode
npm test
uv run --locked python scripts/validate_lark_alignment.py
```

## Check highlighting or clicking in a live editor

If an import path still looks unstyled or Cmd-click does nothing, verify the
local editor is actually running the newest VSIX before changing the grammar.

1. Re-run `make`.
2. Reinstall the newest generated `.vsix`.
3. Reload the editor window.
4. Open `examples/03_imports/prompts/AGENTS.prompt`.
5. Run `Developer: Inspect Editor Tokens and Scopes` on an import path to see
   the emitted scopes and the theme rule that matched.
6. Try Cmd-click on a raw import path and Go to Definition on one supported
   import path, one readable ref, one addressable path segment, one
   addressable `title` segment, one enum member, and one structural
   inheritance key.

## Development only: Extension Development Host

1. Open `editors/vscode/` in VS Code.
2. Run the `Run Extension` launch configuration.
3. In the Extension Development Host window, open the main repo and a `.prompt` file.

## Refresh after extension changes

1. Re-run `make`.
2. Reinstall the newest generated `.vsix` in VS Code or Cursor.
3. Reload your VS Code window if the old version is still active.
