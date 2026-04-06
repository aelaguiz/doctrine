# File Output Agent

Core job: write the section plan to a markdown file.

## Outputs

### Section Plan Output

- Target: File
- Path: `section_root/_authoring/SECTION_PLAN.md`
- Shape: Section Plan Document
- Requirement: Required

#### Must Include

- Summary: start with a short summary.
- Planned Sections: list the planned sections in order.
- Unresolved Risks Or Decisions: list unresolved risks or decisions.

#### Support Files

- `SECTION_FLOW_AUDIT.md` at `section_root/_authoring/SECTION_FLOW_AUDIT.md` when section sizing or ordering constraints matter.

#### Owns

This output owns the current section plan and the unresolved decisions that still matter.

#### Standalone Read

The next role should be able to read `SECTION_PLAN.md` alone and understand the current plan.

#### Example

```md
# Section Plan
## Summary
...
```

## Your Job

- Write the section plan to the required file.
