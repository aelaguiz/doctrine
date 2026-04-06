# Section Output Agent

Core job: write the section plan back to the current section root.

## Runtime Roots

### Section Root

- Kind: DirectoryPath
- Bound From: Current Work Context

The current work context names which section this turn is operating on.

## Outputs

### Section Plan Output

- Target: File
- Root: Section Root
- Relative Path: `_authoring/SECTION_PLAN.md`
- Shape: MarkdownDocument
- Requirement: Required

#### Must Include

- Summary: start with a short summary.
- Planned Sections: list the planned sections in order.

#### Support Files

- Support File: Section Flow Audit
- Support File Root: Section Root
- Support File Relative Path: `_authoring/SECTION_FLOW_AUDIT.md`
- Support File When: section sizing or ordering constraints matter.

#### Owns

This output owns the current section plan at the bound section root.

## Your Job

- Write the section plan to the bound section root.
