# Psmobile Skill Drift Use Case

This document started as the use case. It explains the source-of-truth
problem and why Doctrine needs to understand it. The end now records the
Doctrine support that implements the use case.

## Use Case

`psmobile` owns several repo-bound skill packages. Those skills describe
primitive tools, command surfaces, owned files, reference docs, and strict
failure rules for working with psmobile content. A separate authoring studio
repo consumes those skills so an agent can work in the studio while editing a
mounted psmobile checkout.

The intended ownership is simple:

- `psmobile` is the source of truth for psmobile skill source.
- the studio is a downstream consumer of those skills.
- the studio may emit local runtime copies for its own `.claude/skills` and
  `.agents/skills` wiring.
- the studio should not carry a second editable copy of a psmobile skill.

The current failure mode appears when the downstream repo has its own authored
copy of a psmobile skill package. The upstream repo changes its primitive
script, reference doc, command list, or skill prompt. The downstream copy does
not change. Both copies still look valid because they are ordinary files. The
downstream agent then loads a stale `SKILL.md` and acts from old doctrine.

This is not just stale generated output. It can be stale authored truth.

The concrete shape:

- upstream psmobile skill source lives under `psmobile/skills/<name>/prompts/`.
- downstream studio skill output lives under `lessons_studio/skills/<name>/build/`.
- the downstream runtime loads `SKILL.md`, not `SKILL.prompt`.
- a change to upstream `SKILL.prompt` or a bundled reference file does not, by
  itself, prove that downstream `SKILL.md` is stale.
- a change to an upstream primitive script can make both upstream and
  downstream skill prose stale unless the skill package source is updated.

The author experience is worse than an obvious missing file. Everything looks
installed. The stale skill still has a name, a description, references, and
commands. The agent can follow it confidently. The failure only appears later,
when the agent uses the wrong owner, misses a new primitive, calls a retired
primitive, or repeats a rule that was already moved.

## Why We Need It

Doctrine exists to keep agent systems small, shared, typed, and reviewable.
This use case hits all four goals.

First, copied skill packages grow always-on and load-on-demand context in the
wrong place. The same capability is taught twice. Each copy must carry enough
detail to be believable, so prompt bulk grows in more than one repo. The
runtime still sees a clean skill, but authors no longer have one clean owner.

Second, copied skill packages break shared doctrine. A psmobile primitive skill
is not generic advice. It is the contract for a real tool surface. When a
downstream repo copies that contract, one fix no longer lands once. The copy
can preserve an old command list, old boundary, old validation rule, or old
reference map after the source repo has moved on.

Third, the drift is silent. A stale emitted skill is dangerous because it is
formatted like grounded truth. It has frontmatter, sections, and reference
links. Nothing in the loaded artifact tells the agent that an upstream source
changed after the artifact was emitted. The stale copy can therefore produce a
plausible answer with the shape of a receipt and the truth of an old checkout.

Fourth, this is not harness behavior alone. A harness can decide when to load a
skill, and it can run build commands before a session starts. But the harness
does not know which authored Doctrine files and bundled peers made a given
skill artifact. That relationship is created by Doctrine when it resolves
imports, compiles the package, emits companion docs, and copies bundled files.
The source-to-artifact relationship is compiler knowledge.

Fifth, the downstream repo needs a hard distinction between two states:

- the downstream runtime artifact was emitted from the current upstream source.
- the downstream runtime artifact was emitted from some older upstream source.

Without that distinction, downstream consumers cannot tell a valid generated
skill from a stale generated skill. They can only rebuild everything by habit
or trust that someone remembered to rebuild. That is exactly the kind of
manual synchronization Doctrine is meant to retire.

This matters most for repo-bound skills because they sit at the boundary
between prose and deterministic tools. The skill tells the agent which command
owns which mutation, which files are off limits, which validation step is
required, and which sibling skill owns a nearby concern. If that contract
drifts, the agent may still run successfully while violating the real repo
boundary.

The needed Doctrine-level guarantee is therefore not automatic tool execution
and not runtime session control. The needed guarantee is that a downstream
emitted skill artifact can be judged against the upstream authored sources and
their bundled package inputs. If the upstream truth changed, downstream stale
state must become visible before the agent relies on it.

## Implemented Doctrine Support

Doctrine now supports this shape through skill-package source receipts.

Every `emit_skill` run writes `SKILL.source.json` beside `SKILL.md`.
The receipt records the package identity, Doctrine language version, source id,
source root, entrypoint, hashed source inputs, hashed emitted outputs, one
source tree hash, and one output tree hash.

A package may name extra source-only inputs:

```prompt
skill package PsmobilePrimitiveSkill: "Psmobile Primitive Skill"
    metadata:
        name: "psmobile-primitive-skill"
    source:
        id: "psmobile.primitive-skill"
        track:
            "content/primitive-index.md"
            "tools"
    "Use the psmobile primitives from the tracked source."
```

A downstream studio target may point at the upstream checkout:

```toml
[[tool.doctrine.emit.targets]]
name = "psmobile_primitive_skill"
entrypoint = "../psmobile/skills/primitive/prompts/SKILL.prompt"
output_dir = ".agents/skills/psmobile-primitive"
source_root = "../psmobile"
source_id = "psmobile.primitive-skill"
lock_file = "doctrine.skill.lock"
```

The downstream runtime can still load `SKILL.md`.
The downstream repo can also check the source receipt before the runtime trusts
that file:

```bash
uv run --locked python -m doctrine.verify_skill_receipts --target psmobile_primitive_skill
```

The verifier reports `current` when the downstream emitted tree matches the
current upstream source graph. It reports stale or edited states when the
source changed, the artifact was hand-edited, an extra artifact appeared, the
receipt belongs to a different package, or the lock entry is out of date.

This keeps ownership clean:

- psmobile owns `SKILL.prompt`, bundled references, and tracked tool docs.
- the studio owns the emitted local runtime tree.
- `SKILL.source.json` proves how the runtime tree was built.
- `doctrine.skill.lock` lets the studio pin the expected source and output
  hashes when it wants a checked CI gate.
