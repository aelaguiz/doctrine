# Candidate Tests

## Why this source matters

This catalog is the best source here for packaging doctrine rather than behavior doctrine.
It teaches what a curated skill registry needs to say so that other agents can discover and load the right capability without guessing.

## Candidate Doctrine examples

- **Skill catalog example**: a docs or registry artifact that groups skills by family and keeps metadata compact.
- **Skill package example**: a `SKILL.md`-style file that names the capability, says when to use it, and stays under a token budget.
- **Scoped tools example**: a skill that declares only the tools it actually needs instead of a blanket tool list.
- **Relative-path packaging example**: a skill package that avoids absolute paths and uses portable references.

## Candidate diagnostics

- `INVALID_SKILL_ABSOLUTE_PATH` for portable skill packages that hard-code machine-specific paths.
- `INVALID_SKILL_TOOL_WILDCARD` for skill metadata that asks for every tool instead of explicit scoped tools.
- `INVALID_SKILL_METADATA_TOO_LARGE` for top-level skill metadata that grows beyond the budget the catalog recommends.
- `INVALID_SKILL_INDEX_BODY_MIXUP` for an index page that starts pretending it is the actual skill body.
