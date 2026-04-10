# Docs

Start here if you are new to the repo:

- [WHY_DOCTRINE.md](WHY_DOCTRINE.md): what problem Doctrine solves and why the
  runtime stays `AGENTS.md`
- [../examples/README.md](../examples/README.md): how to read the numbered
  example corpus and its manifests
- [../example_agents/README.md](../example_agents/README.md): external
  instruction bank for harvesting real-world test cases and design pressure

Reference docs:

- [LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md): current language
  decisions and design pressure
- [AGENT_IO_DESIGN_NOTES.md](AGENT_IO_DESIGN_NOTES.md): shipped I/O model and
  explicit non-goals
- [COMPILER_ERRORS.md](COMPILER_ERRORS.md): canonical parse, compile, and emit
  error catalog
- [../editors/vscode/README.md](../editors/vscode/README.md): repo-local editor
  support for `.prompt` files

The live docs set is intentionally small. Active plan docs and worklogs may
remain in `docs/` while work is in flight, but the shipped language truth
stays anchored in `doctrine/`, the manifest-backed examples, and the current
docs index. The shipped numbered corpus now runs through
`examples/38_metadata_polish_capstone`, including the workflow-law cutover.
