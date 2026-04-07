# Examples

The examples are both the language teaching surface and the verification corpus.

Each numbered example may contain:

- `prompts/`: authored `.prompt` source
- `cases.toml`: manifest-backed proof used by `doctrine.verify_corpus`
- `ref/`: checked-in expected render or error output
- `build_ref/`: checked-in emitted tree output when the emit pipeline matters

Read the examples in numeric order. The sequence is intentional.

## Reading Order

- `01` through `06`: core agent and workflow syntax, imports, inheritance, and
  explicit patching
- `07` through `14`: authored slots, routing, typed inputs and outputs, skills,
  role-home composition, and handoff truth
- `15` through `20`: readable refs, interpolation, and richer authored prose
  surfaces
- `21` through `26`: first-class block reuse, inheritance, and abstract
  authored-slot requirements

## Important Rules

- A checked-in ref file is not proof on its own. The manifest is the proof
  surface.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- Keep new examples narrow: one new idea at a time.
- Do not add a new language primitive just to paper over a bad example.

## Useful Commands

Verify the whole active corpus:

```bash
make verify-examples
```

Verify one example manifest:

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml
```

Emit configured example trees:

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth
```
