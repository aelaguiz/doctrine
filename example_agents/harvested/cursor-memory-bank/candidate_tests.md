# Candidate Tests

## Good Doctrine Pressures

| Source signal | Doctrine example or diagnostic idea | Why it matters |
| --- | --- | --- |
| `/van -> /plan -> /creative -> /build -> /reflect -> /archive` workflow | Example of ordered delegation with explicit stage boundaries | Pressures orchestration and handoff modeling |
| Shared `memory-bank/` directory | Example where downstream turns read a state artifact and update it before handing off | Good fit for portable currentness and trust surfaces |
| Single-source-of-truth claims | Diagnostic or example where only one file is authoritative and other files are references | Tests truth ownership and duplicate-state avoidance |
| JIT rule loading | Example where only the current phase's rules are active | Pressures scope-aware loading and context reduction |
| Reflection and archive phases | Example of a turn that produces lessons learned plus a durable archive | Useful for output contracts and post-turn state capture |

## Proposed Doctrine Example Ideas

1. Phase ladder example.
   - Show a workflow that moves through initialization, planning, implementation, reflection, and archive with explicit stage-to-stage handoffs.

2. Context-preservation example.
   - Use a shared state artifact that survives phase changes while keeping only the current phase's instructions active.

3. Single-source-of-truth diagnostic.
   - Emit a failure when task status is written in more than one place or when a non-authoritative file is treated as canonical.

4. Selective-loading example.
   - Show a mode or phase that activates only a subset of rules and rejects loading the full stack at once.

5. Archive output example.
   - Model a terminal phase that writes an archive artifact and resets active context for the next task.

## Keep Out

- Do not encode the repo's personal hobby framing into Doctrine examples.
- Do not treat command names as doctrine primitives; they are just a useful pattern for staged workflows.
- Do not overfit to Cursor-specific wording when the underlying pattern is phase-ordered state transfer.
