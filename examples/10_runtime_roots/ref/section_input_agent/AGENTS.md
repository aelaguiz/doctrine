# Section Input Agent

Core job: read section files relative to the current section root.

## Runtime Roots

### Section Root

- Kind: DirectoryPath
- Bound From: Current Work Context

The current work context names which section this turn is operating on.

## Inputs

### Section Plan

- Source: File
- Root: Section Root
- Relative Path: `_authoring/SECTION_PLAN.md`
- Shape: MarkdownDocument
- Requirement: Required

Read the current section plan from the bound section root.

### Previous Summary

- Source: File
- Root: Section Root
- Relative Path: `_authoring/PREVIOUS_SUMMARY.md`
- Shape: MarkdownDocument
- Requirement: Advisory

Use this only if continuity with earlier section work matters for the turn.

## Your Job

- Read the required section plan from the bound section root.
- Use the previous summary only if continuity matters for the current turn.
- Fail if the required section plan is missing.
