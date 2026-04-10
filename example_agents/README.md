# Example Agents Bank

This directory is a source bank for real-world agent instruction artifacts that
can feed Doctrine examples, diagnostics, and design notes.

It is not the numbered Doctrine language corpus under `examples/`.
It does not participate in `doctrine.verify_corpus`.
Treat it as harvest-and-distill material, not as shipped language truth.

## Purpose

Use this bank to:

- collect substantive external instruction files in one predictable place
- tag them by the Doctrine surfaces they can teach or stress
- write extracted candidate test cases before those ideas become numbered
  Doctrine examples
- avoid losing high-signal real-world patterns in ad hoc research notes

## Layout

- `inventory.toml`: canonical source inventory and triage backlog
- `test_case_buckets.md`: the Doctrine-facing buckets used to classify harvests
- `markdown_agents.md`: curated index of the complex markdown-native agent
  systems in the bank
- `harvested/`: one directory per curated source package
- `harvested/index.md`: the current curated harvest index and pressure map
- `templates/`: starter files for new harvested packages

## Lifecycle

Use these statuses in `inventory.toml` and per-source `SOURCE.toml` files:

- `candidate`: known source, not yet pulled locally
- `harvested`: raw upstream file or excerpt saved locally
- `distilled`: Doctrine-facing notes written
- `extracted`: one or more candidate Doctrine test cases written from the source

## Harvest Package Contract

Each harvested source should live under:

`harvested/<slug>/`

and contain:

- `SOURCE.toml`: source metadata and classification
- `raw/`: raw upstream files or small excerpts with source context
- `notes.md`: what the source is actually teaching
- `candidate_tests.md`: Doctrine-facing test cases to pull from later

In `SOURCE.toml`:

- `expected_artifacts`: the upstream artifacts we intentionally selected from
  the source repo
- `local_raw_paths`: where those selections were copied under `raw/`

## Rules

- Keep upstream text in `raw/`. Keep Doctrine interpretation in `notes.md` and
  `candidate_tests.md`.
- Curate, do not mirror. Pull the smallest upstream slice that still preserves
  the doctrine pressure we care about.
- Do not treat harvested instruction files as shipped truth. The shipped truth
  still lives in `doctrine/` and the manifest-backed numbered corpus.
- Extract generic patterns into Doctrine examples. Do not cargo-cult product
  names or internal jargon into public Doctrine examples.
- Keep candidate tests narrow. One recurring instruction pattern should map to
  one main Doctrine surface whenever possible.
- Prefer high-signal sources that contain concrete commands, explicit
  guardrails, hierarchy rules, or output/handoff contracts over vague prose.

## Curation Workflow

The normal curation flow is:

1. Clone the upstream repo into a temp cache such as
   `/tmp/doctrine-example-agents/<slug>`.
2. Read the source manually and choose the smallest set of files that preserves
   the instruction pattern.
3. Copy only those files or excerpts into `harvested/<slug>/raw/`.
4. Write `notes.md` and `candidate_tests.md` in Doctrine terms.
5. Mark the source `extracted` once the package has raw files, notes, and
   concrete candidate tests.

## Suggested Flow

1. Pick a `candidate` source from `inventory.toml`.
2. Clone it into `/tmp/doctrine-example-agents/<slug>` or another temp cache.
3. Create `harvested/<slug>/` from the templates.
4. Save the selected raw instruction files or excerpts under `raw/`.
5. Tag the source with one or more buckets from `test_case_buckets.md`.
6. Write `candidate_tests.md` in Doctrine terms.
7. Only after that, decide whether any candidate belongs in the numbered
   Doctrine corpus or a design note.
