# Docs

Start here if you are new to the repo:

- [WHY_DOCTRINE.md](WHY_DOCTRINE.md): what problem Doctrine solves and why the
  runtime stays `AGENTS.md`
- [WORKFLOW_LAW.md](WORKFLOW_LAW.md): canonical shipped reference for `law`,
  `trust_surface`, guarded output sections, conditional routes, carriers,
  currentness, invalidation, and law reuse
- [REVIEW_SPEC.md](REVIEW_SPEC.md): canonical shipped reference for first-class
  `review`, shared review contracts, exact failing gates, carried review
  state, and review inheritance
- [../examples/README.md](../examples/README.md): how to read the numbered
  example corpus and its manifests
- [../example_agents/README.md](../example_agents/README.md): external
  instruction bank for harvesting real-world test cases and design pressure

Reference docs:

- [LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md): current language
  decisions and design pressure
- [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md): shipped I/O model and
  explicit non-goals
- [STDLIB_LAYERS.md](STDLIB_LAYERS.md): shipped four-layer direction plus the
  current shared-root stdlib and public-pack layout
- [COMPILER_ERRORS.md](COMPILER_ERRORS.md): canonical parse, compile, and emit
  error catalog
- [../editors/vscode/README.md](../editors/vscode/README.md): repo-local editor
  support for `.prompt` files

The live docs set is intentionally small. The shipped language truth stays
anchored in `doctrine/`, the manifest-backed examples, and this docs index.
Historical proposal, planning, and worklog material lives under
[archive/](archive/README.md) and is not part of the live docs path. The
shipped numbered corpus now runs through
`examples/52_public_code_review_pack`, including the workflow-law cutover, the
staged route-only setup ladder, the guarded route-only handoff capstone, the
full first-class `review` ladder through blocked review, exact contract gates,
current truth, carried mode and trigger state, inheritance, and the shared-root
stdlib plus public-pack proof lane under `prompts/doctrine/std/**` and
`prompts/doctrine/packs_public/**`.
