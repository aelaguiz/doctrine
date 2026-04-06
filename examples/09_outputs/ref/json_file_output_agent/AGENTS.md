# JSON File Output Agent

Core job: write the lesson manifest as structured JSON.

## Outputs

### Lesson Manifest Output

- Artifact: Lesson Manifest
- Built Lesson: `lesson_root/_authoring/lesson_manifest.json`
- Built Lesson Shape: Lesson Manifest JSON
- Validation File: `lesson_root/_authoring/MANIFEST_VALIDATION.md`
- Validation File Shape: MarkdownDocument
- Schema: Lesson Manifest Schema
- Schema Profile: `OpenAIStructuredOutput`
- Schema File: `schemas/lesson_manifest.schema.json`
- Requirement: Required

#### Must Include

- Built Lesson: the built lesson in `lesson_manifest.json`.
- Route Choice: in `MANIFEST_VALIDATION.md`, name the route chosen for each step.
- Validation Record: in `MANIFEST_VALIDATION.md`, name the exact validation command or commands that ran and what passed or failed.
- Placeholder Copy Status: in `MANIFEST_VALIDATION.md`, say whether placeholder copy is still present.

#### Support Files

- `GUIDED_WALKTHROUGH_LENGTH_REPORT.md` at `lesson_root/GUIDED_WALKTHROUGH_LENGTH_REPORT.md` when guided-walkthrough pacing is in scope.

#### Owns

This artifact owns the built learner-facing lesson structure, the chosen route for each step, and the validation proof.

#### Standalone Read

A downstream role should be able to read `lesson_manifest.json` and `MANIFEST_VALIDATION.md` and understand what was built and what was validated.

#### Notes

Keep validator command details, validator output, and placeholder-copy status in `MANIFEST_VALIDATION.md` unless a modeled support file truly owns them.

#### JSON Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["title", "steps"],
  "properties": {
    "title": { "type": "string" },
    "steps": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

#### Field Notes

- `title` is the learner-facing title.
- `steps` is the ordered list of step identifiers.

#### Example

```json
{
  "title": "Intro To Pot Odds",
  "steps": ["intro", "quiz", "review"]
}
```

## Your Job

- Write the lesson manifest JSON to the required file.
