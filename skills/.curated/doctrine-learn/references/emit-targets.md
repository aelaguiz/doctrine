# Emit Targets

Doctrine is a compile step. Authors write `.prompt` files. The compiler
emits runtime Markdown and typed sidecar files. Harnesses load the
emitted tree, not the source tree.

This reference teaches the named-target surface. It covers how to wire a
target, how to run each emit command, what artifacts land on disk, and
how a harness consumes them. For deep output-layout detail, use
`/Users/aelaguiz/workspace/doctrine/docs/EMIT_GUIDE.md`.

## Why Emit Exists

- `.prompt` is the maintenance source. It is typed, testable, and
  reusable.
- Markdown is the runtime artifact. Models read the emitted tree at run
  time, not the `.prompt` tree.
- The compiler owns the translation. It lowers the typed surface into a
  reviewable Markdown layout and a set of stable sidecar files.
- Never hand-edit emitted Markdown. Edit the `.prompt`, then re-emit.
- Emitted trees should land in a build output directory that is safe to
  delete and re-create.

## The Emit Config Block

All emit targets live in one block in the repo's `pyproject.toml`:

```toml
[tool.doctrine.emit]

[[tool.doctrine.emit.targets]]
name = "example_07_handoffs"
entrypoint = "examples/07_handoffs/prompts/AGENTS.prompt"
output_dir = "examples/07_handoffs/build"
```

Each `[[tool.doctrine.emit.targets]]` stanza has three required fields:

- `name`: the stable CLI handle you pass to `--target`. Keep it unique.
- `entrypoint`: the Doctrine source file the target compiles. Must live
  under a `prompts/` tree.
- `output_dir`: the root directory for emitted artifacts. Must not
  already exist as a file.

Rules the compiler enforces:

- `entrypoint` must be `AGENTS.prompt`, `SOUL.prompt`, or
  `SKILL.prompt`.
- `emit_docs` accepts `AGENTS.prompt` or `SOUL.prompt`.
- `emit_skill` accepts `SKILL.prompt`.
- `emit_flow` accepts `AGENTS.prompt` or `SOUL.prompt`, not
  `SKILL.prompt`.
- `entrypoint` and `output_dir` both stay inside the target project
  root.

Add one stanza per emitted artifact tree. Do not share one target
across two entrypoints.

## Running Emit Commands

All emit commands use the same locked Python env:

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_skill --target example_122_skill_package_emit_documents
uv run --locked python -m doctrine.emit_flow --target example_73_flow_visualizer_showcase
```

Useful rules:

- Repeat `--target` to emit several targets in one command.
- `emit_docs` and `emit_skill` run on configured targets only.
- `emit_flow` also accepts direct mode with `--entrypoint` plus
  `--output-dir`, but not both modes at once.
- All commands fail loud on config or compiler errors. They do not
  skip bad targets.

## Common Target Kinds

### Agent Home Target

Compiles an `AGENTS.prompt` entrypoint into runtime `AGENTS.md` files:

```toml
[[tool.doctrine.emit.targets]]
name = "example_07_handoffs"
entrypoint = "examples/07_handoffs/prompts/AGENTS.prompt"
output_dir = "examples/07_handoffs/build"
```

Emitted proof lives at
`/Users/aelaguiz/workspace/doctrine/examples/07_handoffs/build/`. Run
with `doctrine.emit_docs`.

### Workflow Flow Target

Same config shape, different emit command. `emit_flow` writes one
`.flow.d2` plus one `.flow.svg` per entrypoint. Use it when you want a
reviewable graph of inputs, agents, outputs, and route edges.

### Skill Package Target

Compiles a `SKILL.prompt` into a `SKILL.md` tree plus any bundled peer
files:

```toml
[[tool.doctrine.emit.targets]]
name = "example_122_skill_package_emit_documents"
entrypoint = "examples/122_skill_package_emit_documents/prompts/SKILL.prompt"
output_dir = "examples/122_skill_package_emit_documents/build"
```

Shipped proof lives at
`/Users/aelaguiz/workspace/doctrine/examples/122_skill_package_emit_documents/`.
Run with `doctrine.emit_skill`.

## Dual Emit Pattern For First-Party Skills

First-party skills in this repo ship two targets: one local `build/`
target for verify, and one curated install tree for `npx skills`.

The `agent-linter` pair (copied from the live `pyproject.toml`):

```toml
[[tool.doctrine.emit.targets]]
name = "doctrine_agent_linter_skill"
entrypoint = "skills/agent-linter/prompts/SKILL.prompt"
output_dir = "skills/agent-linter/build"

[[tool.doctrine.emit.targets]]
name = "doctrine_agent_linter_public_skill"
entrypoint = "skills/agent-linter/prompts/SKILL.prompt"
output_dir = "skills/.curated/agent-linter"
```

The `doctrine-learn` pair uses the same pattern:

```toml
[[tool.doctrine.emit.targets]]
name = "doctrine_learn_skill"
entrypoint = "skills/doctrine-learn/prompts/SKILL.prompt"
output_dir = "skills/doctrine-learn/build"

[[tool.doctrine.emit.targets]]
name = "doctrine_learn_public_skill"
entrypoint = "skills/doctrine-learn/prompts/SKILL.prompt"
output_dir = "skills/.curated/doctrine-learn"
```

How to read this:

- One entrypoint, two output trees. The source is the same.
- `skills/<name>/build/` is the dev output. It is safe to delete.
- `skills/.curated/<name>/` is the public install tree that
  `npx skills add .` discovers.
- Both targets must stay in sync. Re-emit both when the `.prompt`
  changes.

## Runtime Agent Packages

A thin `AGENTS.prompt` build handle may import directory-backed
packages and let each package own its own emitted runtime home.

Rules:

- A runtime package is a directory with its own `AGENTS.prompt` file.
- `emit_docs` writes `AGENTS.md` at the package root.
- A sibling `SOUL.prompt` emits `SOUL.md` only when it declares one
  concrete agent with the same name as the `AGENTS.prompt` sibling.
- Ordinary peer files under the package root bundle byte for byte.
- Extra stray `.prompt` files under a package root fail loud. They are
  not copied through.
- Plain file modules such as `shared.prompt` stay compile-only. They
  do not emit their own runtime tree.

Shipped proof:

- `/Users/aelaguiz/workspace/doctrine/examples/115_runtime_agent_packages/`

## Provider-Supplied Prompt Roots

Hosts add import search roots two ways:

1. `additional_prompt_roots` in `[tool.doctrine.compile]` for host-owned
   source roots.
2. Provider-supplied roots through the Python API for framework-owned
   roots that should not leak into host config.

Both kinds follow the same rules:

- Each root is an existing directory named `prompts`.
- Absolute imports search the entrypoint-local root, configured roots,
  and provider roots as one active set.
- There is no precedence order. Duplicate dotted modules across roots
  fail loud.
- Emit output placement still anchors to the entrypoint's own local
  `prompts/` root, not to the importing root.

## Generated Contract Artifacts

### `final_output.contract.json`

`emit_docs` writes this companion when an agent declares
`final_output:`, a review contract, or a resolved previous-turn input
contract. It lands next to `AGENTS.md` in the agent's emitted folder.

Top-level blocks:

- `route`: route metadata for the turn-ending response. Fields include
  `exists`, `behavior` (`always`, `never`, or `conditional`),
  `has_unrouted_branch`, `unrouted_review_verdicts`, `selector`, and
  `branches`.
- `io`: resolved IO metadata. Fields include `previous_turn_inputs`,
  `outputs`, and `output_bindings`.

Harness guidance:

- Read `route.selector` to find where the route value lives on the
  response (for example `final_output.route:`).
- Read `route.branches` for compiler-resolved next-owner identity. Do
  not ask the model to copy the next owner into a custom field.
- Read `io.previous_turn_inputs` for resolved previous-turn contracts
  per agent.
- Read `io.outputs` and `io.output_bindings` for emitted output shape
  and readback paths.

Shipped proof:

- `/Users/aelaguiz/workspace/doctrine/examples/119_route_only_final_output_contract/`
- `/Users/aelaguiz/workspace/doctrine/examples/120_route_field_final_output_contract/`
- `/Users/aelaguiz/workspace/doctrine/examples/121_nullable_route_field_final_output_contract/`

### `schemas/<output-slug>.schema.json`

For structured final outputs, `emit_docs` also writes the exact lowered
JSON schema the harness should pass to the model. The file lands at:

```text
<output_dir>/<agent-slug>/schemas/<output-slug>.schema.json
```

The schema follows the OpenAI structured-output wire shape. The
compiler lowers the authored `output schema` into that shape and
validates any authored `example:` block against the lowered schema
before rendering Markdown.

Shipped proof:

- `/Users/aelaguiz/workspace/doctrine/examples/79_final_output_output_schema/`

### `SKILL.contract.json`

`emit_skill` writes this sidecar only when the package has host-binding
truth through `host_contract:` or `host:` refs. It records:

- the package name and title
- the package host contract
- the host paths used by each prompt-authored emitted artifact

Do not author a real source file at that path. The compiler owns it.

Shipped proof:

- `/Users/aelaguiz/workspace/doctrine/examples/124_skill_package_host_binding/`

## Schema Validator CLI

Validate any emitted schema file with:

```bash
uv run --locked python -m doctrine.validate_output_schema \
  --schema examples/79_final_output_output_schema/build/repo_status_agent/schemas/repo_status_final_response.schema.json
```

The validator runs Draft 2020-12 plus Doctrine's OpenAI subset checks.
Use it whenever you hand a schema file to an external tool or model.

## Multi-Root Collision Rules

Doctrine is fail-loud on collisions across active roots. If two roots
define the same dotted module, the compiler raises an error. It does
not silently prefer one root. Fix the duplicate at the source.

## Pitfalls

- Do not hand-edit `build/` or `.curated/` trees. Re-emit instead.
- Do not author a file at `SKILL.md`, `AGENTS.md`, `SOUL.md`, or
  `SKILL.contract.json` paths. The compiler owns these.
- Do not place the entrypoint outside the target project root.
- Do not place `output_dir` outside the target project root.
- Do not drop extra `.prompt` files under a runtime package root. They
  fail loud.
- Do not rely on root precedence. Fix duplicate dotted modules at the
  source.
- Do not skip the dual-emit refresh when you edit a first-party skill.
  The public curated tree must stay in sync with the `build/` tree.

## Related References

- `references/skills-and-packages.md`: `skill`, `skill package`, and
  host-binding authoring.
- `references/outputs-and-schemas.md`: `output schema`, `route field`,
  and `final_output`.
- `references/verify-and-ship.md`: verify commands, Definition of Done,
  and release flow.
- `/Users/aelaguiz/workspace/doctrine/docs/EMIT_GUIDE.md`: canonical
  emit guide.
- `/Users/aelaguiz/workspace/doctrine/docs/COMPILER_ERRORS.md`: stable
  error catalog for emit and compile errors.

**Load when:** The author is configuring an emit target, running an
emit command, or wiring a harness to consume emitted contract files.
