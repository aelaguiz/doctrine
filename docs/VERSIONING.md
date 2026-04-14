# Versioning

This file is the canonical home for Doctrine versioning and breaking-change
guidance.

Doctrine has a few version lines today. They do not all mean the same thing.

## Current Truth

- Doctrine does not yet publish a separate public language version in the live
  docs.
- The live docs also do not yet define a tagged release workflow.
- `pyproject.toml` uses `version = "0.0.0"` for package metadata. Do not
  treat that value as the Doctrine language version.

## Versioned Surfaces Today

### Emitted Contract JSON

`doctrine.emit_docs` writes one `.contract.json` file for each emitted agent.

- Those files use `contract_version`.
- The current value is `1`.
- This version only covers the emitted JSON contract shape.
- It is not the Doctrine language version.
- Bump it only when the emitted JSON contract changes in a way old readers
  cannot use.

For the emitted file layout and fields, use [EMIT_GUIDE.md](EMIT_GUIDE.md).

### Corpus Manifest Schema

`doctrine.verify_corpus` requires `schema_version` in each `cases.toml`
manifest.

- Those manifests use `schema_version`.
- The current value is `1`.
- This version only covers the manifest format used by the corpus verifier.
- It is not the Doctrine language version.
- Bump it only when the manifest format changes in a way old manifests cannot
  use.

For the manifest-backed corpus, use [../examples/README.md](../examples/README.md).

## Breaking Changes

- Do not ship silent breakage.
- If a change breaks authored `.prompt` files, emitted `.contract.json` files,
  or `cases.toml` manifests, update this file in the same change.
- Say who is affected.
- Say what changed.
- Give exact upgrade steps.
- Keep code, docs, examples, and instructions aligned.
- Update manifest-backed proof when behavior changes, or say plainly why it
  did not need to change.
- If you change diagnostics, update
  [COMPILER_ERRORS.md](COMPILER_ERRORS.md) and run `make verify-diagnostics`.

## What Not To Infer

- Do not infer Doctrine language compatibility from `contract_version`.
- Do not infer Doctrine language compatibility from `schema_version`.
- Do not treat the package metadata version in `pyproject.toml` as the
  Doctrine language version.

## Related Docs

- [README.md](../README.md): repo entry docs
- [README.md](README.md): live docs index
- [EMIT_GUIDE.md](EMIT_GUIDE.md): emitted contract files and layout
- [../examples/README.md](../examples/README.md): manifest-backed proof
- [COMPILER_ERRORS.md](COMPILER_ERRORS.md): stable error codes
