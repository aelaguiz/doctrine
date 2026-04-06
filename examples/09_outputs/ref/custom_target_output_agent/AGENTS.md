# Custom Target Output Agent

Core job: leave an owner update on the project tracker.

## Outputs

### Project Tracker Update

- Target: Tracker Comment
- Issue: `CURRENT_ISSUE`
- Shape: Owner Update Comment
- Requirement: Required

#### Must Include

- What Changed: say what changed.
- Current Source Of Truth: name the current source of truth.
- Next Owner: name the next owner.

#### Owns

This output owns the owner-change summary and the current source of truth for the next owner.

#### Standalone Read

A downstream reader should be able to read this comment alone and understand what changed, what to trust now, and who owns next.

#### Example

```text
- changed: updated the section plan
- use now: SECTION_PLAN.md
- next owner: Writing Specialist
```

## Your Job

- Write the owner update using the custom tracker comment target.
