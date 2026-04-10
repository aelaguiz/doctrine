# Notes

This source is a strong match for Doctrine's context and handoff surfaces. It treats workflow state as a shared artifact, breaks the workflow into named phases, and repeatedly argues for loading only the rules that matter at the current stage.

The selected files show four distinct signals:

- the root README explains the full command ladder and the shared memory-bank directory
- the command docs show the explicit lifecycle and how each phase hands work to the next
- the upgrade guide explains why the system moved from a monolithic bundle to a modular, phase-aware design
- the optimization docs make the token-efficiency and selective-loading story concrete
- the single-source-of-truth note is useful for examples where one file is authoritative and others only reference it

For Doctrine purposes, the most useful parts are not the project-specific file names but the pattern: stage transitions, context preservation, and a single authoritative state source.
