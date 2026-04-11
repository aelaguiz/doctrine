# Doctrine VS Code Extension

Repo-local VS Code language support for `.prompt` files.

## What this extension does

- registers `*.prompt` as the `doctrine` language
- adds full TextMate colorization for the shipped Doctrine grammar, including
  first-class `review` declarations and review-local semantic refs
- supports Go to Definition and Ctrl/Cmd-click navigation on raw `import`
  paths
- supports Go to Definition and Ctrl/Cmd-click across the full shipped
  clickable surface:
  parent declaration refs, authored-slot refs and overrides, workflow `use`
  refs, workflow `skills` refs and override refs, route targets, `analysis`,
  `skills`,
  `inputs`, `outputs`, patch-parent refs, `source`, `target`, `shape`,
  owner-aware `schema` refs on `output shape` and `output`, `structure` refs
  on markdown-bearing `input` and `output` surfaces, standalone input/output
  refs in typed I/O bodies, standalone
  readable refs in workflow bodies, interpolation roots, addressable path
  roots and path segments in interpolation / workflow section / generic record
  value surfaces, including trailing `title` segments when they resolve to a
  real definition site, analysis section paths, enum roots and enum members,
  and structural
  `abstract` / `inherit` / local-key `override` sites, plus workflow-law
  surfaces such as law carrier refs, enum-backed mode refs, law-section
  `inherit` / `override` keys, guarded output-section paths, lower-case and
  mixed-case bound roots that resolve through concrete-turn `inputs:` /
  `outputs:` bindings, and route targets inside `law` branches, including
  conditional `route "..." -> Agent when ...` forms, plus trust-surface field
  items, plus review surfaces such as top-level `review` / `abstract review`
  declarations, agent `review:` slots, review-section `inherit` / `override`
  keys, `subject`, `contract`, `comment_output`, `subject_map`, `fields`
  bindings, outcome carrier paths, lower-case bound review carrier roots, and
  review semantic refs such as `contract.<gate>` and `fields.<semantic_field>`
- enables `#` comments, off-side folding, and narrow Enter indentation rules
- keeps keyword coverage aligned with `doctrine/grammars/doctrine.lark`

The extension resolves Doctrine imports from the nearest `prompts/` root using
the same absolute and relative module rules the compiler ships.

Workflow-law support here uses the same vocabulary as
[../../docs/WORKFLOW_LAW.md](../../docs/WORKFLOW_LAW.md): `law`,
`trust_surface`, guarded output headers, carrier refs, trust-surface field
items, enum-backed mode refs, named law subsection `inherit` / `override`
keys, lower-case and mixed-case bound roots in workflow-law carrier and
artifact paths, and route targets inside `law` branches, including conditional
route lines.

Review support here uses the same vocabulary as
[../../docs/REVIEW_SPEC.md](../../docs/REVIEW_SPEC.md): `review`,
`abstract review`, `review:` agent slots, `subject`, `subject_map`,
`contract`, `comment_output`, `fields`, named review sections, outcome
sections, carried `active_mode` / `trigger_reason`, bound review carrier roots,
and semantic refs on the review comment surface.

Second-wave support here also follows the shipped language guides: top-level
`render_profile`, `analysis`, `schema`, and `document` declarations, agent
`analysis:` slots, typed `schema:` / `structure:` / `render_profile:`
attachments, addressable analysis or document paths such as `Decl:section.title`,
family-namespaced schema paths such as
`BuildSurfaceSchema:artifacts.manifest_file.title`, keyed readable descendants
such as `LessonPlan:read_order.first`,
`LessonPlan:read_order.item_schema.step_label.title`,
`LessonPlan:step_arc.columns.coaching_level.title`,
`LessonPlan:step_arc.row_schema.topic.title`, shared readable block headers on
workflow, record, and skill-entry bodies, explicit late block kinds such as
`properties`, `guard`, `markdown`, `html`, `footnotes`, and `image`, and
schema-backed `review contract:` references.

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

If an import path still looks unstyled or Ctrl/Cmd-click does nothing, verify the
local editor is actually running the newest VSIX before changing the grammar.

1. Re-run `make`.
2. Reinstall the newest generated `.vsix`.
3. Reload the editor window.
4. Open `examples/03_imports/prompts/AGENTS.prompt`.
5. Run `Developer: Inspect Editor Tokens and Scopes` on an import path to see
   the emitted scopes and the theme rule that matched.
6. Try Ctrl/Cmd-click on a raw import path and Go to Definition on one supported
   import path, one readable ref, one addressable path segment, one
   addressable `title` segment, one enum member, and one structural
   inheritance key.
7. For the workflow-law ladder, smoke-check:
   `examples/39_guarded_output_sections/prompts/AGENTS.prompt` for guarded
   headers and guarded path clicks,
   `examples/41_route_only_reroute_handoff/prompts/AGENTS.prompt` for routed
   `next_owner` interpolation clicks, and
   `examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt` for
   conditional route target clicks,
   `examples/50_bound_currentness_roots/prompts/AGENTS.prompt` for lower-case
   bound root clicks in `current artifact ... via ...`, and
   `examples/51_inherited_bound_io_roots/prompts/AGENTS.prompt` for inherited
   bound-root clicks.
8. For the review ladder, smoke-check:
   `examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt`
   for `review:` slot clicks and top-level review colorization,
   `examples/47_review_multi_subject_mode_and_trigger_carry/prompts/AGENTS.prompt`
   for `subject_map` and carried-state colorization, and
   `examples/49_review_capstone/prompts/AGENTS.prompt` for Ctrl/Cmd-click on
   `contract.clarity`, `fields.*`, inherited review keys, and review outcome
   carrier paths, plus
   `examples/53_review_bound_carrier_roots/prompts/AGENTS.prompt` for
   lower-case review carrier roots and carried-field path clicks.
9. For the second-wave ladder, smoke-check:
   `examples/54_analysis_attachment/prompts/AGENTS.prompt` for `analysis:`
   slot clicks and `ReleaseAnalysis:stages.title`,
   `examples/55_owner_aware_schema_attachments/prompts/AGENTS.prompt` for
   owner-aware `schema:` clicks on both `output shape` and `output`,
   `examples/56_document_structure_attachments/prompts/AGENTS.prompt` for
   `structure:` clicks on markdown-bearing inputs and outputs, and
   `examples/57_schema_review_contracts/prompts/AGENTS.prompt` for
   schema-backed `contract:` clicks,
   `examples/64_render_profiles_and_properties/prompts/AGENTS.prompt` for
   `render_profile:` clicks plus property-path descendants,
   `examples/65_row_and_item_schemas/prompts/AGENTS.prompt` for
   `item_schema:` / `row_schema:` path clicks,
   `examples/66_late_extension_blocks/prompts/AGENTS.prompt` for
   `footnotes` descendants and late block colorization,
   `examples/63_schema_artifacts_and_groups/prompts/AGENTS.prompt` for
   namespaced schema section/artifact/group path clicks,
   `examples/59_document_inheritance_and_descendants/prompts/AGENTS.prompt`
   for keyed readable descendants on list items, table columns, and table
   rows,
   `examples/60_shared_readable_bodies/prompts/AGENTS.prompt` for skill-entry
   and output-body readable descendants, and
   `examples/61_multiline_code_and_readable_failures/prompts/AGENTS.prompt`
   for output-body readable code-block clicks, and
   `examples/62_identity_titles_keys_and_wire/prompts/AGENTS.prompt` for
   titled-agent `:key` clicks and enum-member `.wire` clicks.

## Development only: Extension Development Host

1. Open `editors/vscode/` in VS Code.
2. Run the `Run Extension` launch configuration.
3. In the Extension Development Host window, open the main repo and a `.prompt` file.

## Refresh after extension changes

1. Re-run `make`.
2. Reinstall the newest generated `.vsix` in VS Code or Cursor.
3. Reload your VS Code window if the old version is still active.
