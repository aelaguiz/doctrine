# Candidate Tests

## `raw/AGENTS.md`

- Doctrine pressure: high-density Rust guardrails and command discipline.
- Candidate example: a root AGENTS file that requires specific tooling to be installed, enforces clippy-friendly style, and blocks edits to sandbox-related env-var code.
- Candidate diagnostic: reject instruction text that turns an implementation note into a blanket permission to ignore repo-defined safety rules.

## `raw/codex-rs/tui/src/bottom_pane/AGENTS.md`

- Doctrine pressure: local instruction scope that adds documentation synchronization rules for a narrow state-machine area.
- Candidate example: a subdirectory AGENTS file that says code changes must be mirrored in module docs and a top-down narrative doc.
- Candidate diagnostic: flag a child instruction file that promises doc updates but does not name the affected modules or behavior axes.

## Good Doctrine Surfaces

- `scope_hierarchy`
- `commands_and_quality_gates`
- `negative_guardrails`
- `skills_tools_and_capabilities`
