# Harvested Source Packages

Each subdirectory here is one harvested source package.

See `index.md` for the current curated set and the cross-source doctrine
pressure map.

Use this shape:

`harvested/<slug>/`

- `SOURCE.toml`
- `raw/`
- `notes.md`
- `candidate_tests.md`

## What Goes Here

- `raw/`: the upstream instruction file or a small excerpt with enough context
  to preserve meaning
- `notes.md`: what the source is doing in plain Doctrine terms
- `candidate_tests.md`: concrete example, diagnostic, or docs ideas we may later
  pull into the numbered Doctrine corpus
- `SOURCE.toml`: selected upstream artifacts plus local raw paths

## What Does Not Go Here

- full upstream repo mirrors
- giant raw dumps without classification
- Doctrine implementation plans
- numbered Doctrine examples under `examples/`
- silent auto-detected file floods with no human curation
