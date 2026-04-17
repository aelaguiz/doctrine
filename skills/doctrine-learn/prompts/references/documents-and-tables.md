# Documents And Tables

This reference teaches the readable surfaces: `document`, first-class `table`, readable lists, and `render_profile`. Reach for these when the agent must write prose or structured reference material that a human will read.

Use a `document` when you need typed prose in a named home. Use a `table` when rows share the same shape and must stay aligned. Use readable lists for short sequences and bullets. Use `render_profile` to shape how a typed surface lowers to Markdown.

## Document Blocks

A `document` is a typed home for readable content. It owns titled sections, callouts, definitions, checklists, lists, tables, and the late extension blocks (raw markdown, inline html, footnotes, images).

Minimal shape:

```prompt
document ReleaseGuide: "Release Guide"
    section summary: "Summary"
        "Lead with the release goal."
```

The body can mix block kinds as long as each has a unique key:

```prompt
document ReleaseGuide: "Release Guide"
    callout durable_truth: "Durable Truth" required
        kind: important
        "This file owns the current release checklist."

    section summary: "Summary"
        "Lead with the release goal and the current shipment boundary."

    definitions must_include: "Must Include" required
        verdict: "Verdict"
            "Say whether the release is ready."

        next_owner: "Next Owner"
            "Name who owns the next action."

    checklist checks: "Checks" advisory
        lint: "Run lint."
        tests: "Run tests."

    rule divider
```

Attach the document to an output with `structure:`:

```prompt
output ReleaseGuideFile: "Release Guide File"
    target: File
        path: "release_root/RELEASE_GUIDE.md"
    shape: MarkdownDocument
    structure: ReleaseGuide
    requirement: Required
```

See `examples/58_readable_document_blocks/` for the full mix of block kinds rendered through `structure:`.

## First-Class Named Tables

A table can live as its own named declaration. That makes the contract reusable and keeps the document body short.

Declare the table once:

```prompt
table ReleaseGates: "Release Gates"
    columns:
        gate: "Gate"
            "What must pass before shipment."

        evidence: "Evidence"
            "What proves the gate passed."
```

Use it by name inside a document. The use site carries only the key, the contract ref, and the rows:

```prompt
document ReleaseGuide: "Release Guide"
    table release_gates: ReleaseGates required
        rows:
            release_notes:
                gate: "Release notes"
                evidence: "Linked to the shipped proof."

            package_smoke:
                gate: "Package smoke"
                evidence: "`make verify-package` passed."
```

The use site inherits every column. Addressable refs still work — `{{ReleaseGates:columns.evidence.title}}` and `{{ReleaseGuide:release_gates.rows.package_smoke}}` both resolve.

See `examples/116_first_class_named_tables/`.

## Readable Lists

Three readable list kinds ship: `sequence` (ordered), `bullets` (unordered), and `checklist`. Each supports a titled form and a titleless form.

The titleless form uses bare string items. The list has no heading, so the items read flat:

```prompt
sequence steps:
    "Read `home:issue.md` first."
    "Then read this role's local rules, files, and outputs."
    "Check `rally-memory` only when past work like this could help."

bullets rules:
    "Use `home:issue.md` as the shared ledger for this run."
    "Leave one short saved note only when later readers need it."
```

The titled form adds a heading and keyed items. Keyed items let you reference a row by path:

```prompt
sequence read_order: "Read Order" advisory
    "Read the issue."
    "Read the repo status."

bullets evidence: "Evidence"
    current_status: "Read the current status."
    latest_notes: "Read the latest validation notes."
```

See `examples/113_titleless_readable_lists/` for both forms side by side.

## Workflow-Root Readable Blocks

Readable blocks also sit at the root of a `workflow`. Use this when the workflow itself is the reading order, not the agent's role.

```prompt
workflow RootReadableGuide: "Guide"
    sequence read_first:
        "Read `home:issue.md` first."

    bullets shared_rules:
        "Use `home:issue.md` as the shared ledger."

    callout evidence_note: "Evidence Note"
        kind: note
        "Ground the current claim before you summarize."

    definitions done_when: "Done When"
        summary: "Summary"
            "State the release result."
```

Agents can still address the nested blocks with `{{RootReadableGuide:evidence_note.title}}`. See `examples/114_workflow_root_readable_blocks/`.

## Render Profiles

A `render_profile` controls how a typed surface lowers to Markdown. It is a named declaration with compact `properties` rules and explicit readable guard shells.

```prompt
render_profile CompactComment:
    properties -> sentence
    guarded_sections -> concise_explanatory_shell
    identity.owner -> title_and_key
    identity.enum_wire -> wire_only
```

Attach the profile to an output with `render_profile:`:

```prompt
output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: Comment
    render_profile: CompactComment
    requirement: Required

    properties summary: "Summary"
        verdict: "Verdict"
            "Use changes requested when the contract fails."
```

The profile makes property groups lower as tight sentences instead of full subsections. It also shapes enum wire lowering and guard shell prose. Use it to keep long typed comments inside the always-on prompt budget.

Profile-sensitive lowering targets that ship today: `properties`, `guarded_sections`, `identity.owner`, `identity.enum_wire`. See `examples/64_render_profiles_and_properties/` and the semantic variant in `examples/67_semantic_profile_lowering/`.

## Typed Item And Row Schemas

Readable lists and tables can carry a typed descendant schema. Use `item_schema:` on lists and `row_schema:` on tables when every item or row must share the same shape.

```prompt
document LessonPlan: "Lesson Plan"
    sequence read_order: "Read Order" advisory
        item_schema:
            step_label: "Step Label"
                "Say what the reader should do at this step."

        first: "Read the learner goal."
        second: "Check the coaching move."

    table step_arc: "Step Arc" required
        row_schema:
            topic: "Topic"
                "Name the topic that the row covers."

        columns:
            coaching_level: "Coaching Level"
                "Say how much coach guidance the step needs."
```

This gives every row or item typed slots the compiler can check. Duplicates and unknown fields fail loud.

## Late Readable Extensions

Four late extension blocks ship inside `document`: `markdown`, `html`, `footnotes`, and `image`. Table rows can also hold structured nested cells instead of flat strings.

```prompt
document ReleaseAppendix: "Release Appendix"
    markdown appendix_markdown: "Appendix Markdown" advisory
        text: """
## Appendix Notes

Keep the appendix compact.
"""

    html inline_html: "Inline HTML" optional
        text: """
<div class="release-note">HTML stays explicit.</div>
"""

    footnotes references: "References" optional
        note_a: "Capture the shipped proof links."
        note_b: "Name the owner for the next update."

    image evidence: "Evidence" optional
        src: "https://example.com/release.png"
        alt: "Release checklist screenshot"
        caption: "Current release checklist snapshot."

    table follow_up_matrix: "Follow-Up Matrix" required
        columns:
            summary: "Summary"
                "Say what changed."

            details: "Details"
                "Show the follow-up detail."

        rows:
            release_note:
                summary: "Check the release note."
                details:
                    section next_steps: "Next Steps"
                        "Confirm the release note matches the shipped proof."
```

Prefer a structured block (`section`, `definitions`, nested `table`) over raw `markdown` or `html`. Use raw blocks only when you truly need the exact Markdown or HTML text.

## IO Wrapper Title Omission

An IO wrapper (`inputs` or `outputs`) that binds a single named ref can drop its wrapper title. Doctrine lowers the child heading into one clean title.

```prompt
inputs SectionDossierInputs: "Your Inputs"
    issue_ledger: LessonsIssueLedger

outputs SectionDossierOutputs: "Your Outputs"
    section_handoff: SectionHandoff
```

When the wrapper binds only one ref and no extra prose, the render keeps the child's title, not a redundant wrapper heading. This shortens emitted prompts. See `examples/117_io_omitted_wrapper_titles/` for the explicit, keyed-child, and multiple-ref counter cases.

## Common Patterns

- Put the prose a human reads in a `document`. Put the rows that must stay aligned in a `table`.
- Reach for a first-class named `table` when two or more documents need the same shape.
- Use `render_profile` only when the default lowering is too long. Do not ship a profile for every output.
- Use titleless readable lists at a workflow root or inside a role when the list has no meaningful heading.
- Use `item_schema:` or `row_schema:` the moment you notice you are repeating the same columns by hand.

## Pitfalls

- Do not restate prose that a typed section already owns. The compiler emits the typed surface; the prose is slack.
- Do not inline a table inside a document when the same table contract will be reused. Lift it to a named `table` first.
- Do not use `markdown` or `html` blocks to work around a missing feature. Ask which structured block fits and use that instead.
- Do not set a `render_profile` you did not author. Profiles are named declarations, not free-form property maps.
- Guard shells must be explicit. A profile that skips a guard does not silently drop it.

## Related References

- `references/outputs-and-schemas.md` owns `output`, `shape`, and `structure:` attachment.
- `references/skills-and-packages.md` owns `emit:` document companions for skill packages.
- `references/imports-and-refs.md` owns addressable refs and `self:` into document bodies.

**Load when:** the author is shaping readable prose, structured reference material, tables, readable lists, or a render profile.
