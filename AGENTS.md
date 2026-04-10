# AGENTS.md

## Build And Verify

- Sync the repo with `uv sync`.
- Run the full shipped corpus with `make verify-examples`.
- Run `make verify-diagnostics` when you change diagnostics.
- For one manifest-backed example, use `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`.
- If you change anything under `editors/vscode/`, run `cd editors/vscode && make`.
- If a dependency is missing or a check cannot run, say that plainly.

## Definition Of Done

- Run the relevant verify command for the surface you changed.
- Keep implementation, examples, docs, and instructions aligned.
- If behavior changed, update the manifest-backed proof or say plainly why it did not need to change.

## Shipped Truth

- The shipped language lives in `doctrine/`, not in draft docs or unchecked examples.
- Start with:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/parser.py`
  - `doctrine/model.py`
  - `doctrine/compiler.py`
  - `doctrine/renderer.py`
  - `doctrine/verify_corpus.py`
- If code, docs, and examples disagree, trust `doctrine/` and the manifest-backed cases.
- The current shipped corpus covers `examples/01_hello_world` through `examples/42_route_only_handoff_capstone`.

## Authoring Rules

- Keep the language example-first.
- Add one new idea per example.
- Prefer explicit typed declarations over magic.
- Prefer fail-loud compiler behavior over silent fallback.
- Model reusable capability as a `skill`, not as ad hoc script prose.
- Keep public docs and examples generic. Do not import product names, internal skill slugs, or company-specific workflow jargon from other repos.

## Communication

- Lead with the concrete answer in 1-3 sentences.
- Use plain, natural English.
- Say what changed, what you ran, what happened, and what happens next.
- If you did not run a check, say that plainly.

## Docs Map

- `docs/README.md`: live docs index
- `docs/WHY_DOCTRINE.md`: product story and motivating use case
- `docs/LANGUAGE_DESIGN_NOTES.md`: current language decisions
- `docs/AGENT_IO_DESIGN_NOTES.md`: shipped I/O model and non-goals
- `docs/COMPILER_ERRORS.md`: canonical error catalog
- `examples/README.md`: how to read the examples and manifests

## Editing Notes

- Examples are design intent plus proof inputs, not shipped truth on their own.
- Treat `examples/*/ref/**` as expected artifacts, not as proof without the manifest.
- When you find drift between implementation, docs, and examples, fix it or say clearly which layer is changing.
