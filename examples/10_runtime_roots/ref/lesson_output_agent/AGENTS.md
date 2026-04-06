# Lesson Output Agent

Core job: write lesson readback files relative to the current lesson root.

## Runtime Roots

### Lesson Root

- Kind: DirectoryPath
- Bound From: Current Work Context

The current work context names which lesson this turn is operating on.

## Outputs

### Lesson Readback Output

- Requirement: Required

#### Files

- File: Lesson Summary
- File Root: Lesson Root
- File Relative Path: `_authoring/LESSON_SUMMARY.md`
- File Shape: MarkdownDocument

- File: Validation Notes
- File Root: Lesson Root
- File Relative Path: `_authoring/VALIDATION_NOTES.md`
- File Shape: MarkdownDocument

#### Must Include

- Lesson Summary: summarize what changed in the lesson.
- Validation Notes: name the checks or readbacks that still matter for the next turn.

#### Owns

This output owns the lesson readback files at the bound lesson root.

## Your Job

- Write the lesson summary and validation notes to the bound lesson root.
