# AGENTS.md

## First Actions

- Sync the repo environment with `uv sync`.
- Run the full active corpus with `make verify-examples`.
- For a targeted manifest run, use `uv run --locked python -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml`.
- Today, `make verify-examples` discovers active manifests for `examples/01_hello_world` through `examples/16_workflow_string_interpolation`.
- `examples/99_not_clean_but_useful/` is still design pressure only and is not part of the shipped verification surface.
- If a dependency is missing or a check could not run, say that plainly.

## Shipped Truth

- The shipped language support lives in `pyprompt/`, not in the later example drafts.
- Start with these files when you need the real current grammar and compiler behavior:
  - `pyprompt/grammars/pyprompt.lark`
  - `pyprompt/parser.py`
  - `pyprompt/model.py`
  - `pyprompt/compiler.py`
  - `pyprompt/renderer.py`
  - `pyprompt/verify_corpus.py`
- If code, docs, and examples disagree, trust the shipped implementation in `pyprompt/` for what works today. Treat docs and later examples as design intent unless verification proves otherwise.

## Current Bootstrap Scope

- The current shipped parser/compiler covers examples `01` through `16` in this worktree.
- It supports:
  - top-level `agent`, `abstract agent`, `workflow`, `import`, `input source`, `input`, `output target`, `output shape`, `output`, `json schema`, and `skill`
  - `role` as either scalar opening text or a titled block with lines
  - keyed local workflow sections, authored agent slots, keyed `use` composition, explicit `inherit` / `override`, `route "..." -> Target` statements, titled workflow section bodies that mix prose with named declaration refs, and workflow strings that interpolate named declaration contract fields inline
  - named workflow reuse, named workflow inheritance, dotted references, and typed `inputs` / `outputs` / `outcome` / `skills` fields
  - indentation-sensitive blocks and standalone `#` comment lines
- Do not claim anything outside the manifest-backed `01` through `16` corpus is implemented just because it appears under `examples/`.

## Examples

- The examples are authoring drafts used to design the language.
- They are not definitive.
- They are not complete.
- They are not even necessarily debugged.
- Treat an example as verified only when the repo has a checked-in manifest and the compiler path can prove it.
- Treat `examples/*/ref/**` as target or reference output, not as proof that the current compiler can produce it.
- Keep the example sequence disciplined: one new idea at a time, with the smallest example that earns that idea cleanly.
- Do not add a new language primitive just to paper over a bad example. First try to express the idea with the language that already exists. If that fails, name the exact clean gap.

## 99

- `examples/99_not_clean_but_useful/` is the bad web of Markdown that pushed this project into existence.
- It is not a target design.
- It is not a pattern library.
- It is not good.
- Use it as requirement fodder only.
- Use it to find missing language support, missing structure, and places where the old authoring patterns break down.
- The goal is to rebuild much better versions of things like `99`, with cleaner source patterns and fewer bugs.
- Do not preserve `99`'s duplication, awkward structure, or mistakes just because they appear there.

## Current Design Direction

- Keep the language example-first.
- Keep the parser growing in the same order as the examples.
- Prefer explicit typed declarations over magic.
- Current capability modeling is intentionally skill-first.
- If a reusable capability matters enough to name, model it as a skill.
- Do not treat raw script paths or ad hoc Python commands as a parallel first-class language surface unless the design docs explicitly change that rule.

## Communication

- Write for a human reader first.
- Lead with the concrete answer in 1-3 sentences.
- Use plain, natural English.
- Say what changed, what to run, what happened, and what happens next.
- Translate repo shorthand immediately or avoid it.
- Do not make the reader decode house jargon, compressed internal labels, or pseudo-technical wording.
- If a sentence would sound strange spoken aloud, rewrite it.
- Do not narrate your own authoring process in repo docs or instructions.
- If you did not run a check, say so plainly.

## Docs Map

- `docs/LANGUAGE_DESIGN_NOTES.md`: current language decisions and pressure areas
- `docs/COMPILER_ERRORS.md`: current compiler error catalog
- `docs/EXAMPLES_COLD_READ_AUDIT_2026-04-06.md`: where the examples are confusing or inconsistent
- `examples/*/cases.toml`: verified example contracts

## Editing Rules

- Keep live instructions and docs current. Do not leave stale guidance in place just for history.
- When you find drift between implementation, docs, and examples, either fix it or say clearly which layer you are changing.
- When editing the grammar or compiler, prefer fail-loud behavior over silent fallback.
