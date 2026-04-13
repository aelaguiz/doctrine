# AGENTS.md

## Build And Verify

- Sync the repo with `uv sync`.
- Install the pinned flow-render dependency with `npm ci`.
- Run the full shipped corpus with `make verify-examples`.
- Run `make verify-diagnostics` when you change diagnostics.
- For one manifest-backed example, use `uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml`.
- If you change anything under `editors/vscode/`, run `cd editors/vscode && make`.
- If a dependency is missing or a check cannot run, say that plainly.

## Definition Of Done

- Run the relevant verify command for the surface you changed.
- Keep implementation, examples, docs, and instructions aligned.
- If behavior changed, update the manifest-backed proof or say plainly why it did not need to change.

## Doc Deletion Safety

- Never delete docs without first making a restore-point commit that contains the pre-deletion state.
- Do this even when the docs look stale, low-quality, or obviously wrong.
- If you are not making that commit in the current task, do not delete the docs.
- After that restore-point commit, delete stale docs instead of moving them into an archive directory.
- Git history is the archive. Do not keep or create `docs/archive/` as a long-term holding area.

## Shipped Truth

- The shipped language lives in `doctrine/`, not in draft docs or unchecked examples.
- Start with:
  - `doctrine/grammars/doctrine.lark`
  - `doctrine/parser.py`
  - `doctrine/model.py`
  - `doctrine/compiler.py`
  - `doctrine/emit_common.py`
- `doctrine/emit_flow.py`
- `doctrine/renderer.py`
- `doctrine/verify_corpus.py`
- If code, docs, and examples disagree, trust `doctrine/` and the manifest-backed cases.
- The current shipped corpus covers `examples/01_hello_world` through `examples/91_handoff_routing_route_output_binding`.

## Authoring Rules

- Keep the language example-first.
- Add one new idea per example.
- Prefer explicit typed declarations over magic.
- Prefer fail-loud compiler behavior over silent fallback.
- Model reusable capability as a `skill`, not as ad hoc script prose.
- Keep public docs and examples generic. Do not import product names, internal skill slugs, or company-specific workflow jargon from other repos.

## Plain Language Hard Requirement

- Treat 7th grade reading level as a hard requirement for shipped bundled Markdown prose and agent replies.
- Prefer short sentences, common words, and direct verbs.
- Split dense instructions into two sentences when that keeps the meaning clear.
- Keep Doctrine terms that carry exact meaning, but simplify the rest of the sentence around them.
- Bad: `A downstream owner should be able to read this review alone and understand the verdict, current artifact, and next owner.`
- Good: `This review should stand on its own. A downstream owner should know the verdict, current artifact, and next owner.`
- Bad: `Rendered only when route facts section status is new or full rewrite.`
- Good: `Show this only when the route facts say the section is new or a full rewrite.`

## Communication

- Lead with the concrete answer in 1-3 sentences.
- Use plain, natural English at about a 7th grade reading level.
- Say what changed, what you ran, what happened, and what happens next.
- If you did not run a check, say that plainly.

## Docs Map

- `docs/README.md`: live docs index
- `docs/WHY_DOCTRINE.md`: product story and motivating use case
- `docs/EMIT_GUIDE.md`: canonical guide to emit targets, `emit_docs`, `emit_flow`, and output layout
- `docs/LANGUAGE_DESIGN_NOTES.md`: current language decisions
- `docs/AGENT_IO_DESIGN_NOTES.md`: shipped I/O model and non-goals
- `docs/COMPILER_ERRORS.md`: canonical error catalog
- `examples/README.md`: how to read the examples and manifests

## Editing Notes

- Examples are design intent plus proof inputs, not shipped truth on their own.
- Treat `examples/*/ref/**` as expected artifacts, not as proof without the manifest.
- When you find drift between implementation, docs, and examples, fix it or say clearly which layer is changing.
