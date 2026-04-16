---
title: authored-slot workflows with root readable blocks crash compile
date: 2026-04-15
status: resolved
owners:
  - codex
reviewers: []
related:
  - docs/AGENT_IO_DESIGN_NOTES.md
  - examples/114_workflow_root_readable_blocks
---

<!-- bugs:block:tldr:start -->
## TL;DR

- Symptom: a custom authored workflow slot such as `read_first` crashes with `E901` when its workflow has root readable blocks.
- Impact: legal Doctrine prompts can fail during emit with an internal compiler error.
- Most likely cause: the custom authored-slot compile path calls workflow compilation without `unit` and `owner_label`.
- Next action: return to the audit-loop naming map; the bug fix is verified.
- Status: resolved
<!-- bugs:block:tldr:end -->

<!-- bugs:block:analysis:start -->
## Bug North Star

Legal authored-slot workflows must compile the same readable workflow body shape as the built-in `workflow` slot.

## Bug Summary

The user reported a Rally repro where `read_first` and `how_to_take_a_turn`
point at workflows that contain root readable blocks. After porting
`rally.turn_results` to `output schema`, `emit_docs` failed for a stdlib smoke
target with:

- `E901 compile error: Internal compiler error`
- `workflow readable block compilation requires unit and owner label`
- failing agent: `PlanAuthor`

This is a Doctrine bug because the failure is an internal compiler guard, not a
validation error.

## Evidence

- Local minimal repro confirmed the same `E901` with a `read_first` slot that
  points at a workflow containing root `sequence` block.
- `doctrine/_compiler/compile/workflows.py` requires `unit` and `owner_label`
  when compiling workflow root readable blocks.
- `doctrine/_compiler/compile/agent.py` passes that context for `workflow` and
  `handoff_routing`, but not for other custom authored slots.
- `examples/114_workflow_root_readable_blocks` already proves the root readable
  block shape for the built-in `workflow` slot.

## Investigation

The crash is localized to the custom authored-slot branch in
`_compile_agent_field`. For non-`workflow` and non-`handoff_routing` slots, it
calls:

```python
self._compile_resolved_workflow(spec.slot_body, slot_key=field.key)
```

That loses the current module and owner label. Root readable blocks need that
context so nested section bodies can resolve addressable authored content.
<!-- bugs:block:analysis:end -->

<!-- bugs:block:fix_plan:start -->
## Fix Plan

1. Update the custom authored-slot compile path to pass `unit` and a clear
   `owner_label`.
2. Keep the existing law rejection for custom slots.
3. Add one focused regression that compiles a custom `read_first` slot pointing
   at a workflow with a root readable block.
4. Run the focused rendering test, the existing root-readable example manifest,
   and the full corpus if the focused checks pass.
<!-- bugs:block:fix_plan:end -->

<!-- bugs:block:implementation:start -->
## Implementation

- Changed `doctrine/_compiler/compile/agent.py` so custom authored slots pass
  `unit`, `agent_contract`, and `owner_label` into `_compile_resolved_workflow`.
- Kept the existing law rejection for custom slots. This is not a fallback.
- Added
  `tests.test_output_rendering.OutputRenderingTests.test_custom_authored_slot_workflow_root_readable_blocks_render`.
  The test compiles a `read_first` slot that points at a workflow with root
  readable blocks and checks the rendered Markdown.
- Added a manifest-backed case to `examples/114_workflow_root_readable_blocks`
  for a custom authored slot that uses the same root readable workflow.

## Verification

- Local minimal repro failed before the fix with the reported `E901`.
- `uv run --locked python -m unittest tests.test_output_rendering.OutputRenderingTests.test_custom_authored_slot_workflow_root_readable_blocks_render`
  passed.
- `uv run --locked python -m unittest tests.test_output_rendering tests.test_emit_docs`
  passed with 28 tests.
- `uv run --locked python -m doctrine.verify_corpus --manifest examples/114_workflow_root_readable_blocks/cases.toml`
  passed with both root-readable cases.
- `make verify-examples` passed.
- `git diff --check` passed.
<!-- bugs:block:implementation:end -->
