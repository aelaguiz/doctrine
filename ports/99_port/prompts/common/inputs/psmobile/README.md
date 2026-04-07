# psmobile Catalog Inputs

This directory models the upstream `psmobile` lesson catalog as reusable input
surfaces.

Scope for this first pass:

- source-of-truth JSON under `agents/lessons/catalog/**`
- the full shipped lesson catalog as one readable input surface
- track metadata
- section metadata
- lesson manifests

Out of scope for this pass:

- generated assets under `packages/game_content/assets/**`
- generated journey metadata
- helper or narrative files under `_authoring/**`
- wiring these surfaces into any existing 99-port role bundle

The real upstream catalog path pattern is:

- `tracks/<track_dir>/track.meta.json`
- `tracks/<track_dir>/sections/<section_dir>/section.meta.json`
- `tracks/<track_dir>/sections/<section_dir>/lessons/<lesson_dir>/lesson_manifest.json`

The semantic surfaces in this directory now support two levels of access:

- one full-catalog surface for lanes that need broad curriculum visibility
- narrower track / section / lesson surfaces for lanes that need one specific
  scope

These declarations intentionally use on-disk directory keys rather than stable
IDs inside the JSON payloads. The repo currently relies on directory location to
find these files, and `section_dir` / `lesson_dir` are not the same thing as
`sectionId` / `lessonId`.

The root binding is intentionally left symbolic in this pass. `catalog_root` is
a placeholder contract key, not yet an environment variable or a fixed
repo-relative path choice.
