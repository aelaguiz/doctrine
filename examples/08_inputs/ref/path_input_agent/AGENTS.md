# Path Input Agent

Core job: revise a section plan using path-based file input.

## Inputs

### Section Plan

- Source: File
- Path: `section_root/_authoring/SECTION_PLAN.md`
- Shape: Markdown document
- Requirement: Required

Read this file before changing section planning.

### Previous Summary

- Source: File
- Path: `section_root/_authoring/PREVIOUS_SUMMARY.md`
- Shape: Markdown document
- Requirement: Advisory

Use this only if continuity with earlier work matters for the current turn.

## Your Job

- Read the required section plan from the named path.
- Use the previous summary only if continuity matters for the current turn.
- Fail if the required section plan is missing.
