# Reference Integrity Language Proposal

Date: 2026-04-09

## Status

This document records the design rationale behind Doctrine's reference-integrity
expansion.

Shipped truth lives in:

- [LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md)
- [examples/27_addressable_record_paths](../examples/27_addressable_record_paths)
- [examples/28_addressable_workflow_paths](../examples/28_addressable_workflow_paths)
- [examples/29_enums](../examples/29_enums)

## Why This Exists

Some Doctrine corpora need stronger referential integrity than top-level
declaration refs alone provide.

The recurring drift pattern was:

- named subparts of an output or workflow were reused as bare strings
- closed vocabularies were copied through prose and scalar values
- renames silently drifted because the compiler had no owned object to target

The goal was to improve integrity without turning Doctrine into a packet
language, a Markdown AST, or a general schema DSL.

## What Existed Before

Before this expansion, Doctrine already supported:

- whole declaration refs in workflow bodies
- authored-prose interpolation like `{{Ref}}`
- scalar field lookup like `{{Ref:target.path}}`
- typed inputs, outputs, routes, and skills

Grounding:

- [examples/15_workflow_body_refs/prompts/AGENTS.prompt](../examples/15_workflow_body_refs/prompts/AGENTS.prompt)
- [examples/16_workflow_string_interpolation/prompts/AGENTS.prompt](../examples/16_workflow_string_interpolation/prompts/AGENTS.prompt)
- [LANGUAGE_DESIGN_NOTES.md](LANGUAGE_DESIGN_NOTES.md)
- [compiler.py](../doctrine/compiler.py)

The missing piece was addressable ownership for named nested items and fixed
literal vocabularies.

## Proposed Surface 1: Addressable Nested Items

The core language need was not a mandatory new top-level noun.

The core need was to let explicitly defined nested items on existing owners be
addressable through stable paths.

That covers things like:

- headings inside output contracts
- named proof blocks
- named review gates
- nested workflow sections

### Shape

Keep the structure under the existing owner:

```prompt
output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required

    must_include: "Must Include"
        analysis: "Analysis"
            tables: "Tables"
                concept_ladder_table: "Concept Ladder Table"
                    "Capture the current concept ladder before review."
```

Then reference it with a narrow owned path:

```prompt
workflow ReadFirst: "Read First"
    review_now: "Review Now"
        ReviewComment:must_include.analysis.tables.concept_ladder_table
        "Build {{ReviewComment:must_include.analysis.tables.title}} inside {{ReviewComment:title}}."
```

### Why This Was Chosen

- one owner stays responsible for the nested thing
- authors can still read the structure inline where it is defined
- the compiler gets fail-loud renames and unknown-path errors
- the syntax reuses existing `Ref:path.to.child` structure instead of adding a
  second embedded language

### Non-goals

- no separate `artifact` primitive
- no separate `root` primitive
- no arbitrary prose-line addressing
- no general object-walking language beyond explicitly keyed nested items

## Proposed Surface 2: `enum`

`enum` owns closed vocabularies that should stop drifting as copied prose.

### Shape

```prompt
enum CriticVerdict: "Critic Verdict"
    accept: "accept"
    changes_requested: "changes requested"

workflow VerdictRules: "Verdict Rules"
    "Return {{CriticVerdict:accept}} only when no gate failed."
```

### Why This Was Chosen

- it gives repeated literals one owner
- it keeps closed vocabularies out of ad hoc prose
- it solves a real integrity problem without introducing full schema machinery

## Why Not More Primitives

The design bar was: only add a primitive if the concept survives renaming the
example domain.

`addressable nested items` and `enum` met that bar.

Other ideas did not:

- support-file status policy
- symbolic path-root declarations
- domain-specific gate or handoff primitives

Those may still become real later, but they were not earned by the evidence
that motivated this expansion.
