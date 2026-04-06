# JSON File Output Agent

Core job: write the lesson manifest as structured JSON.

## Outputs

### Lesson Manifest File

- Target: File
- Path: `lesson_root/_authoring/lesson_manifest.json`
- Shape: Lesson Manifest JSON
- Schema: Lesson Manifest Schema
- Schema Profile: `OpenAIStructuredOutput`
- Schema File: `schemas/lesson_manifest.schema.json`
- Requirement: Required

#### Purpose

Write a machine-readable lesson manifest.

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
